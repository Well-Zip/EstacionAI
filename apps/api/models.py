from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.db.models import PROTECT
from datetime import timedelta
#from django.db.models import Q

from rest_framework.response import Response
from rest_framework import status
# Create your models here.
class Vagas(models.Model):
    vaga = models.CharField(max_length=4, verbose_name="Nome da Vaga", primary_key=True)
    em_uso = models.BooleanField(verbose_name="Vaga em uso",default=False)

    def save(self, *args, **kwargs):
        if self.vaga:
            self.vaga = self.vaga.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Cadastro de Vaga"
        verbose_name_plural = "Cadastro de Vagas"
        ordering = ["vaga"]

    
    def __str__(self):
        return  str(self.vaga)

class historico_Estacionamento(models.Model):
    vaga_Ocupada = models.ForeignKey(Vagas, on_delete=PROTECT)
    placa = models.CharField(max_length=8,verbose_name="Placa do Veiculo",blank=True,null=True)
    horario_Entrada = models.DateTimeField(verbose_name="Data e Hora de Entrada")
    horario_Saida = models.DateTimeField(verbose_name="Data e Hora de Saida")
    tempo_Estacionado = models.DurationField(verbose_name="Tempo Estacionado", blank=True, null=True,editable=False)


    def save(self, *args, **kwargs):

        if self.placa:
            self.placa = self.placa.upper()

        if self.horario_Saida and self.horario_Entrada:
            self.tempo_Estacionado = self.horario_Saida - self.horario_Entrada
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Historico do Estacionamento"
        verbose_name_plural = "Historico do Estacionamento"
        ordering = ["-horario_Entrada"]

    def __str__(self):
        return f'Histórico para {self.vaga_Ocupada} - Placa: {self.placa}'
           
class Estacionamento(models.Model):
    vaga_Ocupada = models.ForeignKey(Vagas, on_delete=PROTECT)
    placa = models.CharField(max_length=8, verbose_name="Placa do Veiculo", blank=True, null=True)
    horario_Entrada = models.DateTimeField(verbose_name="Data e Hora de Entrada")
    horario_Saida_Estimada = models.DateTimeField(verbose_name="Data e Hora de Saída Estimada", blank=True, null=True)
    horario_Saida = models.DateTimeField(verbose_name="Data e Hora de Saída", blank=True, null=True, editable=False)


    def clean(self):
        # Verificar se a vaga já está em uso em outro registro ativo (sem horario_Saida)
        conflito = Estacionamento.objects.filter(
            vaga_Ocupada=self.vaga_Ocupada,
            horario_Saida__isnull=True
        ).exclude(pk=self.pk).exists()

        if conflito:
            raise ValidationError(("A vaga já está ocupada por outro veículo."))
        
    def save(self, *args, **kwargs):
        
        # Ajuste do horário estimado de saída
        if not self.horario_Saida_Estimada:
            self.horario_Saida_Estimada = self.horario_Entrada + timedelta(minutes=4) 
        
        self.clean()
        vaga = self.vaga_Ocupada
        vaga.em_uso = True
        vaga.save()

        if self.placa:
            self.placa = self.placa.upper()

        super().save(*args, **kwargs)

    def salvar_historico_deletar_estacionamento(self):
        historico = historico_Estacionamento(
            vaga_Ocupada=self.vaga_Ocupada,
            placa=self.placa,
            horario_Entrada=self.horario_Entrada,
            horario_Saida=timezone.now()
        )

        vaga = Vagas.objects.get(vaga=self.vaga_Ocupada)
        vaga.em_uso = False
        vaga.save()


        historico.save()
        self.delete()

    
    class Meta:
        verbose_name = "Estacionamento"
        verbose_name_plural = "Estacionamento"
        ordering = ["-horario_Entrada"]
        constraints = [
            models.UniqueConstraint(
                fields=['vaga_Ocupada'],
                condition=models.Q(horario_Saida__isnull=True),  # Verifica se o horário de saída ainda não foi registrado
                name='A vaga atualmente esta ocupada'
            )
        ]

    def __str__(self):
        return f'Informações da Vaga: {self.vaga_Ocupada} - Placa: {self.placa}'
