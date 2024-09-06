# EstacionAI 🚗

EstacionAI é um projeto desenvolvido com o objetivo de utilizar Inteligência Artificial para determinar e gerenciar um estacionamento. A aplicação oferece uma API em Django para gerenciar as vagas de estacionamento, além de uma interface web que será responsável por consumir os dados da API e realizar interações relevantes.

## Funcionalidades

- **Gerenciamento de Vagas:** Controle de entrada e saída de veículos nas vagas do estacionamento.
- **Histórico de Vagas:** Registro de dados históricos de ocupação de vagas, facilitando a análise de uso do estacionamento.
- **Inteligência Artificial:** Futuramente, IA será integrada para auxiliar na determinação da disponibilidade de vagas e no gerenciamento eficiente.
- **Interface Web:** Um aplicativo web que permitirá a interação com o sistema de forma intuitiva, consumindo a API para apresentar informações relevantes.

## Tecnologias Utilizadas

- **Back-End:**
  - [Django](https://www.djangoproject.com/) (Framework Web)
  - API RESTful utilizando Django REST Framework
  - Banco de Dados relacional

- **Front-End:**
  - HTML, CSS, JavaScript
  - Framework para consumir a API e exibir dados dinâmicos (futuro desenvolvimento)

- **Inteligência Artificial:**
  - Em desenvolvimento, será integrada para otimizar a ocupação de vagas.

## Estrutura do Projeto

```bash
├── apps/
│   ├── api/                # Aplicação Django responsável pela API
├── EstacionAI/             # Aplicação responsável pela lógica de negócios do estacionamento
├── manage.py               # Script de gerenciamento do Django
├── requirements.txt        # Requerimentos para rodar o projeto
└── README.md      
db.sqlite3      
```

# 🚀 Como executar o projeto

## Clonando o repositório
```bash
$ git clone https://github.com/Well-Zip/EstacionAI.git
```
## Entrando no diretório 
```bash
$ cd EstacionAI
```
## Criando a máquina virtual dentro da pasta do projeto
```python
python -m venv .venv 

# Ativando a máquina virtual
.venv\Scripts\activate

# Instalando os requisitos necessários 
pip install -r requirements.txt
```
```python
# Rodando o código 
python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser # Adicionar o usuario para o acesso ao django admin

python manage.py runserver
```

## URLs

Aqui estão as principais rotas disponíveis na API desenvolvida em Django para o gerenciamento do estacionamento. Cada URL suporta métodos específicos, que estão indicados abaixo:

- **[Página Inicial da API](http://127.0.0.1:8000/):**  
  Acesse a página inicial da API para visualizar informações gerais e testar o funcionamento básico.

- **[Admin Django](http://127.0.0.1:8000/admin):**  
  Acesso ao painel de administração do Django, onde os administradores podem gerenciar os dados do estacionamento.

- **Deletar e Liberar Vaga:**  
  `DELETE http://127.0.0.1:8000/estacionamento_aespi/delete/<str:vaga>`  
  Substitua `<str:vaga>` pelo nome da vaga. Essa rota utiliza o método **DELETE** e é responsável por deletar o registro da vaga e liberar a mesma no sistema.

- **Informações da Vaga (GET e PUT):**  
  `GET | PUT http://127.0.0.1:8000/estacionamento_aespi/<str:vaga>`  
  Substitua `<str:vaga>` pelo nome da vaga para obter ou atualizar informações da vaga ocupada. O método **GET** retorna os detalhes da vaga, enquanto o método **PUT** permite modificar, por exemplo, a data e hora de saída estimada.

- **Status Geral do Estacionamento:**  
  `GET http://127.0.0.1:8000/estacionamento_aespi/info/status`  
  Exibe informações gerais sobre o estacionamento, como o número de vagas livres e ocupadas.

- **Listagem de Vagas Cadastradas:**  
  `GET http://127.0.0.1:8000/estacionamento_aespi/info/vagas`  
  Fornece uma listagem completa de todas as vagas cadastradas no sistema.

- **Hello World (Teste):**  
  `GET http://127.0.0.1:8000/endpoint/`  
  Um endpoint básico que retorna uma resposta de "Hello World" para testar a configuração da API.
