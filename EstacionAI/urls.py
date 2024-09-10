"""
URL configuration for EstacionAI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from apps.api.viewsets import *
from apps.api.views import *
route = routers.DefaultRouter()
route.register(r'estacionamento_aespi', EstacionamentoViewsets, basename = 'Estacionamento')
route.register(r'vagas', VagasViewSet, basename='vagas')



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(route.urls)),  # Inclui as rotas do DefaultRouter
    path('estacionamento_aespi/delete/<str:vaga>', EstacionamentoDelete.as_view(), name='estacionamento-delete'),
    path('estacionamento_aespi/delete/vagas/all', EstacionamentoDeleteAll.as_view(), name='estacionamento-delete-all'),
    path('estacionamento_aespi/<str:vaga>', Estacionamento_Info.as_view(), name='estacionamento_info'),
    path('estacionamento_aespi/info/status', Estacionamento_Status.as_view(), name='estacionamento'),
    path('estacionamento_aespi/info/vagas', VagasCadastradas.as_view(), name='vagas'),
    path('endpoint', Hello_World.as_view(), name='endpoint_teste'),
]



 
 

