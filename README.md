# Dashboard Ávila Transportes

Sistema de dashboard unificado para gestão de transportes e fretes com integração ao Azure SQL Database.

## ✨ Funcionalidades

- 📊 Dashboard geral com métricas e gráficos
- 🔍 Consulta de faturas e minutas
- 💰 Gestão financeira integrada
- 📋 Emissão de documentos
- 🔄 Conciliação automática
- ☁️ **Integração com Azure SQL Database**
- 📁 Fallback para arquivos CSV locais

## 🚀 Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Azure Database (Opcional)

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` com suas credenciais do Azure:
```env
AZURE_SQL_SERVER=seu-servidor.database.windows.net
AZURE_SQL_DATABASE=nome-do-banco
AZURE_SQL_USERNAME=seu-usuario
AZURE_SQL_PASSWORD=sua-senha
USE_AZURE_DB=true
```

### 3. Criar tabelas no Azure (se usando Azure Database)

Execute o script SQL no seu Azure SQL Database:
```bash
# Conecte-se ao seu Azure SQL Database e execute:
Banco de dados layout/create_tables.sql
```

### 4. Executar a aplicação

```bash
cd "Banco de dados layout"
streamlit run main.py
```

## 🔧 Configuração

### Usando Azure SQL Database

1. Acesse a aba "⚙️ Configuração Azure" no menu lateral
2. Preencha as credenciais do seu Azure SQL Database
3. Teste a conexão
4. Execute a migração dos dados CSV (se necessário)

### Usando apenas CSV (modo local)

Se não configurar o Azure Database, o sistema funcionará normalmente com arquivos CSV locais.

## 📁 Estrutura do Projeto

```
dashboard/
├── requirements.txt              # Dependências Python
├── .env.example                 # Exemplo de configuração
├── Banco de dados layout/
│   ├── main.py                  # Aplicação principal
│   ├── data_loader.py           # Carregamento de dados (CSV + Azure)
│   ├── azure_config.py          # Configurações Azure
│   ├── azure_db.py              # Conexão Azure Database
│   ├── azure_setup.py           # Interface de configuração
│   ├── migration.py             # Migração CSV → Azure
│   ├── create_tables.sql        # Scripts de criação de tabelas
│   ├── dashboard.py             # Dashboard principal
│   ├── financas.py              # Módulo financeiro
│   └── ...                      # Outros módulos
```

## 🔄 Migração de Dados

O sistema migra automaticamente os dados CSV para o Azure Database na primeira execução. Você também pode executar a migração manualmente através da interface web.

## 🛠️ Tecnologias

- **Frontend**: Streamlit
- **Backend**: Python, Pandas
- **Database**: Azure SQL Database + pyodbc
- **Cache**: Streamlit cache
- **Config**: python-dotenv

## 📋 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `AZURE_SQL_SERVER` | Servidor Azure SQL | - |
| `AZURE_SQL_DATABASE` | Nome do banco | - |
| `AZURE_SQL_USERNAME` | Usuário | - |
| `AZURE_SQL_PASSWORD` | Senha | - |
| `USE_AZURE_DB` | Usar Azure DB | `false` |
| `FALLBACK_TO_CSV` | Fallback para CSV | `true` |
| `CONNECTION_POOL_SIZE` | Tamanho do pool | `5` |
| `CONNECTION_TIMEOUT` | Timeout (segundos) | `30` |

## 🔍 Troubleshooting

### Erro de conexão com Azure
- Verifique as credenciais no arquivo `.env`
- Confirme que o servidor Azure permite conexões externas
- Verifique se o driver ODBC está instalado

### Dados não aparecem
- Verifique se as tabelas foram criadas com `create_tables.sql`
- Execute a migração manual na interface web
- Verifique os logs de erro na aplicação

### Performance lenta
- Ajuste o `CONNECTION_POOL_SIZE`
- Verifique os índices das tabelas
- Consider usar o modo CSV para desenvolvimento local
