# 🚛 Dashboard Ávila Transportes

Sistema unificado de dashboard para gestão de transportes, financeiro e emissões da Ávila Transportes.

## 📋 Funcionalidades

- **Dashboard Geral**: Visão geral dos dados de transporte
- **Consulta de Faturas**: Busca e análise de faturas
- **Consulta de Minuta**: Consulta de minutas de transporte
- **Financeiro**: Gestão financeira e conciliação
- **Emissões**: Módulo para emissão de documentos (CT-e, Notas Fiscais, etc.)

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação e Execução

#### Linux/MacOS
```bash
# Clone o repositório (se ainda não clonou)
git clone <repository-url>
cd dashboard

# Execute o script de inicialização
./run.sh
```

#### Windows
```bash
# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run main.py
```

#### Manual
```bash
# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação Streamlit
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

## 📁 Estrutura do Projeto

```
dashboard/
├── main.py                    # Aplicação principal
├── dashboard.py               # Módulo do dashboard geral
├── consulta_faturas.py        # Módulo de consulta de faturas
├── consulta_minuta.py         # Módulo de consulta de minutas
├── financas.py                # Módulo financeiro
├── emissoes.py                # Módulo de emissões
├── conciliacao.py             # Módulo de conciliação
├── data_loader.py             # Carregador de dados
├── parser_ofx.py              # Parser de arquivos OFX
├── requirements.txt           # Dependências Python
├── run.sh                     # Script de execução (Linux/MacOS)
├── data/                      # Dados da aplicação
│   └── base_financeira.csv
├── base.csv                   # Base principal de dados
├── contatos.csv               # Base de contatos
├── extrato.csv                # Extratos financeiros
└── controle_financeiro.xlsx   # Controle financeiro
```

## 🔧 Configuração

A aplicação utiliza arquivos CSV como fonte de dados:
- `base.csv`: Base principal com dados de transporte
- `data/base_financeira.csv`: Dados financeiros
- `extrato.csv`: Extratos bancários
- `contatos.csv`: Base de contatos

## 📊 Tecnologias Utilizadas

- **Streamlit**: Framework para criação da interface web
- **Pandas**: Manipulação e análise de dados
- **PyMuPDF**: Processamento de arquivos PDF
- **ofxparse**: Parser de arquivos OFX bancários
- **openpyxl**: Manipulação de arquivos Excel

## 🌐 Acesso

Após executar a aplicação, acesse:
- **Local**: http://localhost:8501
- **Rede**: http://0.0.0.0:8501

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação dos módulos individuais ou entre em contato com a equipe de desenvolvimento.
