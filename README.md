# Sistema de Parcerias

Aplicação web para cadastro e gerenciamento de propostas de parceria empresarial, desenvolvida com Python, Streamlit e SQLite.

## Funcionalidades

- **Cadastro de Propostas**: Formulário completo para registro de novas parcerias
- **Validações**: CPF/CNPJ, e-mail, telefone, CEP e campos obrigatórios
- **Consulta de Registros**: Listagem de todas as propostas cadastradas
- **Busca**: Pesquisa por razão social ou CPF/CNPJ
- **Exportação**: Download dos dados em formato CSV
- **Interface Moderna**: Design responsivo e profissional

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone ou baixe o projeto para sua máquina:

```bash
cd projeto-parcerias
```

2. Crie um ambiente virtual (recomendado):

```bash
python -m venv venv
```

3. Ative o ambiente virtual:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como Executar

Execute o seguinte comando na raiz do projeto:

```bash
streamlit run app.py
```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`.

## Estrutura do Projeto

```
projeto-parcerias/
│
├── app.py              # Aplicação principal Streamlit
├── database.py         # Módulo de gerenciamento do banco de dados
├── requirements.txt    # Dependências do projeto
├── parcerias.db        # Banco de dados SQLite (criado automaticamente)
└── README.md           # Documentação do projeto
```

## Descrição dos Arquivos

### app.py

Arquivo principal da aplicação contendo:
- Configuração da interface Streamlit
- Funções de validação (CPF, CNPJ, e-mail, telefone, CEP)
- Formulário de cadastro com validações
- Página de consulta e exportação

### database.py

Módulo de banco de dados contendo:
- Inicialização automática do banco SQLite
- Funções CRUD para propostas
- Exportação para CSV
- Funções de busca e listagem

## Campos do Formulário

### Dados da Empresa
- CPF ou CNPJ (validado)
- Razão Social

### Endereço
- Rua
- Número
- Complemento
- CEP (validado)
- Ponto de Referência

### Contato
- Telefone (validado)
- E-mail (validado)
- Nome do Contato

## Validações Implementadas

| Campo | Validação |
|-------|-----------|
| CPF | Algoritmo de verificação de dígitos |
| CNPJ | Algoritmo de verificação de dígitos |
| E-mail | Formato válido (regex) |
| Telefone | 10 ou 11 dígitos |
| CEP | 8 dígitos |

## Tecnologias Utilizadas

- **Python 3.x**: Linguagem de programação
- **Streamlit**: Framework para interface web
- **SQLite3**: Banco de dados embutido

## Licença

Este projeto é livre para uso e modificação.
