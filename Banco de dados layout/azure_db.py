"""
Módulo de conexão com Azure SQL Database
"""
import pandas as pd
from typing import Optional, Dict, Any
from azure_config import AzureConfig

# Tenta importar dependências do Azure, mas continua sem elas
try:
    import pyodbc
    import sqlalchemy
    import streamlit as st
    AZURE_DEPENDENCIES_AVAILABLE = True
except ImportError:
    AZURE_DEPENDENCIES_AVAILABLE = False
    # Mock do streamlit se não disponível
    class MockStreamlit:
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
    st = MockStreamlit()

class AzureDBConnection:
    """Gerenciador de conexão com Azure SQL Database"""
    
    def __init__(self):
        self.engine = None
        self.connection_string = None
        self.available = AZURE_DEPENDENCIES_AVAILABLE
        
        if self.available:
            self._initialize_connection()
        else:
            st.warning("⚠️ Dependências do Azure não disponíveis. Usando modo CSV.")
    
    def _initialize_connection(self):
        """Inicializa a conexão com o banco de dados"""
        try:
            if not self.available:
                return
                
            if not AzureConfig.is_configured():
                st.warning("⚠️ Configurações do Azure SQL Database não encontradas")
                return
            
            self.connection_string = AzureConfig.get_connection_string()
            sqlalchemy_url = AzureConfig.get_sqlalchemy_url()
            
            self.engine = sqlalchemy.create_engine(
                sqlalchemy_url,
                pool_size=AzureConfig.POOL_SIZE,
                max_overflow=10,
                pool_timeout=AzureConfig.TIMEOUT,
                pool_recycle=3600
            )
            
            # Testa a conexão
            self.test_connection()
            
        except Exception as e:
            st.error(f"❌ Erro ao conectar com Azure Database: {e}")
            self.engine = None
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados"""
        try:
            if not self.available or self.engine is None:
                return False
            
            with self.engine.connect() as conn:
                result = conn.execute(sqlalchemy.text("SELECT 1"))
                result.fetchone()
            
            return True
        except Exception as e:
            st.error(f"❌ Falha no teste de conexão: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Executa uma query SELECT e retorna um DataFrame"""
        try:
            if not self.available:
                st.warning("⚠️ Azure Database não disponível")
                return pd.DataFrame()
                
            if self.engine is None:
                raise Exception("Conexão com banco de dados não disponível")
            
            return pd.read_sql_query(query, self.engine, params=params)
        
        except Exception as e:
            st.error(f"❌ Erro ao executar query: {e}")
            return pd.DataFrame()
    
    def execute_non_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Executa uma query INSERT/UPDATE/DELETE"""
        try:
            if not self.available:
                st.warning("⚠️ Azure Database não disponível")
                return False
                
            if self.engine is None:
                raise Exception("Conexão com banco de dados não disponível")
            
            with self.engine.connect() as conn:
                conn.execute(sqlalchemy.text(query), params or {})
                conn.commit()
            
            return True
        
        except Exception as e:
            st.error(f"❌ Erro ao executar comando: {e}")
            return False
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append') -> bool:
        """Insere um DataFrame no banco de dados"""
        try:
            if not self.available:
                st.warning("⚠️ Azure Database não disponível")
                return False
                
            if self.engine is None:
                raise Exception("Conexão com banco de dados não disponível")
            
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=1000
            )
            
            return True
        
        except Exception as e:
            st.error(f"❌ Erro ao inserir dados: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """Verifica se uma tabela existe no banco de dados"""
        try:
            if not self.available or self.engine is None:
                return False
            
            query = """
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = :table_name
            """
            
            result = self.execute_query(query, {'table_name': table_name})
            return result['count'].iloc[0] > 0 if not result.empty else False
        
        except Exception:
            return False
    
    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        """Retorna o schema de uma tabela"""
        if not self.available:
            return pd.DataFrame()
            
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = :table_name
        ORDER BY ORDINAL_POSITION
        """
        
        return self.execute_query(query, {'table_name': table_name})
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.available and self.engine:
            self.engine.dispose()
            self.engine = None

# Instância global da conexão
azure_db = AzureDBConnection()