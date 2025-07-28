"""
Interface de configuração do Azure Database para Streamlit
"""
import streamlit as st
import os
from azure_config import AzureConfig
from azure_db import azure_db
from data_loader import verificar_conexao_azure, obter_estatisticas_dados

def mostrar_configuracao_azure():
    """Interface para configuração do Azure Database"""
    st.header("⚙️ Configuração Azure Database")
    
    # Status atual
    col1, col2 = st.columns(2)
    
    with col1:
        if AzureConfig.is_configured():
            if verificar_conexao_azure():
                st.success("✅ Azure Database conectado")
            else:
                st.error("❌ Azure Database configurado mas não conectado")
        else:
            st.warning("⚠️ Azure Database não configurado")
    
    with col2:
        stats = obter_estatisticas_dados()
        st.info(f"📊 Fonte atual: {stats['fonte']}")
        st.metric("Total de registros", stats['total_registros'])
    
    # Formulário de configuração
    with st.expander("🔧 Configurar Conexão Azure", expanded=not AzureConfig.is_configured()):
        with st.form("azure_config"):
            st.markdown("### Configurações do Azure SQL Database")
            
            server = st.text_input(
                "Servidor",
                value=AzureConfig.SERVER,
                placeholder="servidor.database.windows.net",
                help="Nome do servidor Azure SQL Database"
            )
            
            database = st.text_input(
                "Nome do Banco",
                value=AzureConfig.DATABASE,
                placeholder="nome-do-banco",
                help="Nome do banco de dados"
            )
            
            username = st.text_input(
                "Usuário",
                value=AzureConfig.USERNAME,
                placeholder="usuario",
                help="Nome de usuário para conexão"
            )
            
            password = st.text_input(
                "Senha",
                type="password",
                help="Senha do usuário"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                use_azure = st.checkbox(
                    "Usar Azure Database",
                    value=AzureConfig.USE_AZURE_DB,
                    help="Ativar uso do Azure Database"
                )
            
            with col2:
                fallback_csv = st.checkbox(
                    "Fallback para CSV",
                    value=AzureConfig.FALLBACK_TO_CSV,
                    help="Usar CSV como backup se Azure falhar"
                )
            
            submitted = st.form_submit_button("💾 Salvar Configuração")
            
            if submitted:
                if salvar_configuracao_azure(server, database, username, password, use_azure, fallback_csv):
                    st.success("✅ Configuração salva! Recarregue a página para aplicar.")
                    st.experimental_rerun()
    
    # Ferramentas de gerenciamento
    st.markdown("### 🛠️ Ferramentas de Gerenciamento")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Testar Conexão"):
            if verificar_conexao_azure():
                st.success("✅ Conexão bem-sucedida!")
            else:
                st.error("❌ Falha na conexão")
    
    with col2:
        if st.button("📊 Verificar Tabelas"):
            verificar_tabelas_azure()
    
    with col3:
        if st.button("🔄 Migrar Dados CSV"):
            executar_migracao_manual()
    
    # Informações detalhadas
    if AzureConfig.is_configured():
        with st.expander("📋 Informações da Conexão"):
            st.code(f"""
Servidor: {AzureConfig.SERVER}
Banco: {AzureConfig.DATABASE}
Usuário: {AzureConfig.USERNAME}
Driver: {AzureConfig.DRIVER}
Timeout: {AzureConfig.TIMEOUT}s
Pool Size: {AzureConfig.POOL_SIZE}
            """)

def salvar_configuracao_azure(server, database, username, password, use_azure, fallback_csv):
    """Salva configuração do Azure em arquivo .env"""
    try:
        env_content = f"""# Azure Database Configuration
AZURE_SQL_SERVER={server}
AZURE_SQL_DATABASE={database}
AZURE_SQL_USERNAME={username}
AZURE_SQL_PASSWORD={password}
AZURE_SQL_DRIVER=ODBC Driver 17 for SQL Server

# Connection Pool Settings
CONNECTION_POOL_SIZE=5
CONNECTION_TIMEOUT=30

# Application Settings
USE_AZURE_DB={str(use_azure).lower()}
FALLBACK_TO_CSV={str(fallback_csv).lower()}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        return True
    
    except Exception as e:
        st.error(f"❌ Erro ao salvar configuração: {e}")
        return False

def verificar_tabelas_azure():
    """Verifica se as tabelas necessárias existem no Azure"""
    try:
        if not verificar_conexao_azure():
            st.error("❌ Não é possível conectar ao Azure Database")
            return
        
        tabelas_necessarias = ['fretes', 'transacoes_financeiras', 'conciliacoes', 'configuracoes']
        
        for tabela in tabelas_necessarias:
            existe = azure_db.table_exists(tabela)
            if existe:
                st.success(f"✅ Tabela '{tabela}' existe")
                
                # Mostra contagem de registros
                count_result = azure_db.execute_query(f"SELECT COUNT(*) as count FROM {tabela}")
                if not count_result.empty:
                    count = count_result['count'].iloc[0]
                    st.info(f"   📊 {count} registros")
            else:
                st.error(f"❌ Tabela '{tabela}' não encontrada")
        
        st.markdown("---")
        st.info("💡 Se alguma tabela não existe, execute o script `create_tables.sql` no seu Azure SQL Database")
    
    except Exception as e:
        st.error(f"❌ Erro ao verificar tabelas: {e}")

def executar_migracao_manual():
    """Executa migração manual dos dados CSV para Azure"""
    try:
        if not verificar_conexao_azure():
            st.error("❌ Não é possível conectar ao Azure Database")
            return
        
        from migration import data_migration
        
        with st.spinner("🔄 Executando migração..."):
            if data_migration.run_full_migration():
                st.success("🎉 Migração executada com sucesso!")
            else:
                st.error("❌ Falha na migração")
    
    except Exception as e:
        st.error(f"❌ Erro na migração: {e}")

def mostrar_status_azure():
    """Mostra status resumido do Azure na sidebar"""
    if AzureConfig.USE_AZURE_DB:
        if verificar_conexao_azure():
            st.sidebar.success("🔗 Azure Connected")
        else:
            st.sidebar.error("🔗 Azure Disconnected")
        
        stats = obter_estatisticas_dados()
        st.sidebar.metric("Registros", stats['total_registros'])
    else:
        st.sidebar.info("📁 Usando CSV local")