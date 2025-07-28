import pandas as pd
import streamlit as st
import os

# Tenta importar módulos do Azure, mas continua sem eles
try:
    from azure_config import AzureConfig
    from azure_db import azure_db
    from migration import data_migration
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    # Mock classes para quando Azure não está disponível
    class MockAzureConfig:
        USE_AZURE_DB = False
        FALLBACK_TO_CSV = True
        @classmethod
        def is_configured(cls): return False
    AzureConfig = MockAzureConfig

ARQ_BASE = "base.csv"
ARQ_BASE_DATA = "data/base.csv"

@st.cache_data(show_spinner=False)
def carregar_base():
    """
    Carrega dados da base - prioriza Azure Database se configurado,
    senão usa CSV como fallback
    """
    try:
        # Verifica se deve usar Azure Database
        if AZURE_AVAILABLE and AzureConfig.USE_AZURE_DB and AzureConfig.is_configured():
            return carregar_base_azure()
        else:
            return carregar_base_csv()
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar base de dados: {e}")
        
        # Tenta fallback para CSV se configurado
        if AzureConfig.FALLBACK_TO_CSV:
            st.warning("⚠️ Tentando carregar dados do CSV como fallback...")
            return carregar_base_csv()
        
        return pd.DataFrame()

def carregar_base_azure() -> pd.DataFrame:
    """Carrega dados do Azure SQL Database"""
    try:
        if not AZURE_AVAILABLE:
            st.warning("⚠️ Módulos do Azure não disponíveis")
            return pd.DataFrame()
            
        # Verifica se a migração já foi feita
        config_result = azure_db.execute_query(
            "SELECT valor FROM configuracoes WHERE chave = 'migrado_csv'"
        )
        
        migrado = False
        if not config_result.empty:
            migrado = config_result['valor'].iloc[0].lower() == 'true'
        
        # Se não foi migrado e existe CSV, executa migração
        if not migrado and (os.path.exists(ARQ_BASE) or os.path.exists(ARQ_BASE_DATA)):
            st.info("🔄 Executando migração inicial dos dados CSV para Azure...")
            if data_migration.run_full_migration():
                migrado = True
        
        # Carrega dados de fretes do Azure
        query_fretes = """
        SELECT 
            data_emissao as "Data de Emissão",
            numero as "Número",
            pagador_nome as "Pagador do Frete - Nome",
            valor_frete as "Valor do frete",
            notas_fiscais as "Notas Fiscais",
            remetente_nome as "Remetente - Nome",
            remetente_cidade as "Remetente - Cidade",
            destinatario_nome as "Destinatário - Nome",
            destinatario_cidade as "Destinatário - Cidade",
            soma_volumes as "Soma dos Volumes",
            soma_notas as "Soma das Notas",
            soma_pesos as "Soma dos Pesos"
        FROM fretes
        ORDER BY data_emissao DESC
        """
        
        df = azure_db.execute_query(query_fretes)
        
        if df.empty:
            st.warning("⚠️ Nenhum dado encontrado no Azure Database")
            return pd.DataFrame()
        
        # Processa os dados carregados
        df = processar_dados_carregados(df)
        
        st.success(f"✅ {len(df)} registros carregados do Azure Database")
        return df
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar do Azure Database: {e}")
        raise e

def carregar_base_csv() -> pd.DataFrame:
    """Carrega dados do arquivo CSV (método original)"""
    try:
        # Tenta carregar do diretório atual primeiro, depois do data/
        arquivo_base = ARQ_BASE if os.path.exists(ARQ_BASE) else ARQ_BASE_DATA
        
        if not os.path.exists(arquivo_base):
            return pd.DataFrame(columns=[
                "Data de Emissão", "Descrição", "Valor do frete", "Valor", "Tipo",
                "Categoria", "Centro de Custo", "Setor", "ID Transação", "Conciliado com"
            ])
        
        df = pd.read_csv(arquivo_base, sep=";", encoding="utf-8")
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.columns = [c.strip() for c in df.columns]

        # Processa valor do frete
        col_frete = [c for c in df.columns if "valor do frete" in c.lower()]
        if not col_frete:
            col_frete = [c for c in df.columns if "frete" in c.lower() and "valor" in c.lower()]

        if col_frete:
            col = col_frete[0]
            df[col] = (
                df[col].astype(str)
                .str.replace("R$", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".")
            )
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df.rename(columns={col: "Valor do frete"}, inplace=True)
        else:
            df["Valor do frete"] = 0.0
            st.warning("⚠️ Coluna de frete não encontrada. Criada com valor 0.0.")

        # Processa os dados carregados
        df = processar_dados_carregados(df)
        
        st.info(f"📁 {len(df)} registros carregados do arquivo CSV")
        return df

    except Exception as e:
        st.error(f"❌ Erro ao carregar CSV: {e}")
        return pd.DataFrame()

def processar_dados_carregados(df: pd.DataFrame) -> pd.DataFrame:
    """Processa dados comuns independente da origem"""
    try:
        # Processa datas
        if "Data de Emissão" in df.columns:
            df["Data de Emissão"] = pd.to_datetime(df["Data de Emissão"], dayfirst=True, errors="coerce")
            df = df[df["Data de Emissão"].notnull()]
            df["Quinzena"] = df["Data de Emissão"].apply(
                lambda x: f"{x.month:02d}/1ª" if x.day <= 15 else f"{x.month:02d}/2ª"
            )
            df["Data de Vencimento"] = df["Data de Emissão"] + pd.Timedelta(days=10)
        else:
            st.warning("⚠️ Coluna 'Data de Emissão' não encontrada.")

        # Processa campos numéricos
        for campo in ["Soma dos Volumes", "Soma das Notas", "Soma dos Pesos"]:
            if campo in df.columns:
                df[campo] = pd.to_numeric(df[campo], errors="coerce").fillna(0)

        return df

    except Exception as e:
        st.error(f"❌ Erro ao processar dados: {e}")
        return df

def salvar_base(df):
    """
    Salva dados na base - prioriza Azure Database se configurado,
    senão usa CSV como fallback
    """
    try:
        # Verifica se deve usar Azure Database
        if AZURE_AVAILABLE and AzureConfig.USE_AZURE_DB and AzureConfig.is_configured():
            return salvar_base_azure(df)
        else:
            return salvar_base_csv(df)
    
    except Exception as e:
        st.error(f"❌ Erro ao salvar base de dados: {e}")
        
        # Tenta fallback para CSV se configurado
        if AzureConfig.FALLBACK_TO_CSV:
            st.warning("⚠️ Tentando salvar no CSV como fallback...")
            return salvar_base_csv(df)
        
        return False

def salvar_base_azure(df: pd.DataFrame) -> bool:
    """Salva dados no Azure SQL Database"""
    try:
        if not AZURE_AVAILABLE:
            st.warning("⚠️ Módulos do Azure não disponíveis")
            return False
            
        # Mapeia colunas do DataFrame para a tabela
        df_mapped = mapear_colunas_para_azure(df)
        
        # Primeiro, limpa a tabela (ou implementa lógica de update)
        azure_db.execute_non_query("DELETE FROM fretes")
        
        # Insere os novos dados
        success = azure_db.insert_dataframe(df_mapped, 'fretes', if_exists='append')
        
        if success:
            st.success("✅ Dados salvos no Azure Database com sucesso!")
            # Limpa cache do Streamlit
            carregar_base.clear()
            return True
        else:
            st.error("❌ Falha ao salvar no Azure Database")
            return False
    
    except Exception as e:
        st.error(f"❌ Erro ao salvar no Azure: {e}")
        return False

def salvar_base_csv(df: pd.DataFrame) -> bool:
    """Salva dados no arquivo CSV (método original)"""
    try:
        # Determina qual arquivo usar
        arquivo_base = ARQ_BASE if os.path.exists(ARQ_BASE) else ARQ_BASE_DATA
        
        pasta = os.path.dirname(arquivo_base)
        if pasta and not os.path.exists(pasta):
            os.makedirs(pasta)
        
        df.to_csv(arquivo_base, sep=";", index=False)
        st.success("✅ Base CSV salva com sucesso!")
        
        # Limpa cache do Streamlit
        carregar_base.clear()
        return True
    
    except Exception as e:
        st.error(f"❌ Erro ao salvar CSV: {e}")
        return False

def mapear_colunas_para_azure(df: pd.DataFrame) -> pd.DataFrame:
    """Mapeia colunas do DataFrame para o formato do Azure"""
    column_mapping = {
        "Data de Emissão": "data_emissao",
        "Número": "numero",
        "Pagador do Frete - Nome": "pagador_nome",
        "Valor do frete": "valor_frete",
        "Notas Fiscais": "notas_fiscais",
        "Remetente - Nome": "remetente_nome",
        "Remetente - Cidade": "remetente_cidade",
        "Destinatário - Nome": "destinatario_nome",
        "Destinatário - Cidade": "destinatario_cidade",
        "Soma dos Volumes": "soma_volumes",
        "Soma das Notas": "soma_notas",
        "Soma dos Pesos": "soma_pesos"
    }
    
    # Seleciona apenas colunas que existem no DataFrame
    existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
    
    df_mapped = df[list(existing_cols.keys())].copy()
    df_mapped.rename(columns=existing_cols, inplace=True)
    
    return df_mapped

def verificar_conexao_azure() -> bool:
    """Verifica se a conexão com Azure está funcionando"""
    try:
        if not AZURE_AVAILABLE or not AzureConfig.is_configured():
            return False
        
        return azure_db.test_connection()
    
    except Exception:
        return False

def obter_estatisticas_dados():
    """Retorna estatísticas dos dados (Azure ou CSV)"""
    try:
        if AZURE_AVAILABLE and AzureConfig.USE_AZURE_DB and AzureConfig.is_configured():
            # Estatísticas do Azure
            stats = azure_db.execute_query("""
                SELECT 
                    COUNT(*) as total_registros,
                    COUNT(DISTINCT destinatario_cidade) as cidades_distintas,
                    MIN(data_emissao) as data_mais_antiga,
                    MAX(data_emissao) as data_mais_recente,
                    SUM(valor_frete) as valor_total_fretes
                FROM fretes
            """)
            
            if not stats.empty:
                return {
                    'fonte': 'Azure Database',
                    'total_registros': stats['total_registros'].iloc[0],
                    'cidades_distintas': stats['cidades_distintas'].iloc[0],
                    'data_mais_antiga': stats['data_mais_antiga'].iloc[0],
                    'data_mais_recente': stats['data_mais_recente'].iloc[0],
                    'valor_total_fretes': stats['valor_total_fretes'].iloc[0]
                }
        
        # Estatísticas do CSV
        df = carregar_base_csv()
        if not df.empty:
            return {
                'fonte': 'Arquivo CSV',
                'total_registros': len(df),
                'cidades_distintas': df['Destinatário - Cidade'].nunique() if 'Destinatário - Cidade' in df.columns else 0,
                'data_mais_antiga': df['Data de Emissão'].min() if 'Data de Emissão' in df.columns else None,
                'data_mais_recente': df['Data de Emissão'].max() if 'Data de Emissão' in df.columns else None,
                'valor_total_fretes': df['Valor do frete'].sum() if 'Valor do frete' in df.columns else 0
            }
        
        return {'fonte': 'Nenhuma', 'total_registros': 0}
    
    except Exception as e:
        st.error(f"❌ Erro ao obter estatísticas: {e}")
        return {'fonte': 'Erro', 'total_registros': 0}
