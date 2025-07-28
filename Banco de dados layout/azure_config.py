"""
Módulo de configuração para Azure Database
"""
import os

# Tenta carregar python-dotenv, mas continua se não estiver disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

class AzureConfig:
    """Configurações para Azure SQL Database"""
    
    # Configurações de conexão Azure SQL
    SERVER = os.getenv('AZURE_SQL_SERVER', '')
    DATABASE = os.getenv('AZURE_SQL_DATABASE', '')
    USERNAME = os.getenv('AZURE_SQL_USERNAME', '')
    PASSWORD = os.getenv('AZURE_SQL_PASSWORD', '')
    DRIVER = os.getenv('AZURE_SQL_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # Configurações de pool de conexão
    POOL_SIZE = int(os.getenv('CONNECTION_POOL_SIZE', '5'))
    TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', '30'))
    
    # Configurações da aplicação
    USE_AZURE_DB = os.getenv('USE_AZURE_DB', 'false').lower() == 'true'
    FALLBACK_TO_CSV = os.getenv('FALLBACK_TO_CSV', 'true').lower() == 'true'
    
    @classmethod
    def get_connection_string(cls):
        """Retorna a string de conexão para Azure SQL Database"""
        if not all([cls.SERVER, cls.DATABASE, cls.USERNAME, cls.PASSWORD]):
            raise ValueError("Configurações do Azure SQL Database não estão completas")
        
        return (
            f"Driver={{{cls.DRIVER}}};"
            f"Server=tcp:{cls.SERVER},1433;"
            f"Database={cls.DATABASE};"
            f"Uid={cls.USERNAME};"
            f"Pwd={cls.PASSWORD};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout={cls.TIMEOUT};"
        )
    
    @classmethod
    def get_sqlalchemy_url(cls):
        """Retorna a URL do SQLAlchemy para Azure SQL Database"""
        if not all([cls.SERVER, cls.DATABASE, cls.USERNAME, cls.PASSWORD]):
            raise ValueError("Configurações do Azure SQL Database não estão completas")
        
        driver = cls.DRIVER.replace(' ', '+')
        return (
            f"mssql+pyodbc://{cls.USERNAME}:{cls.PASSWORD}@{cls.SERVER}:1433/"
            f"{cls.DATABASE}?driver={driver}&encrypt=yes&trustServerCertificate=no"
        )
    
    @classmethod
    def is_configured(cls):
        """Verifica se as configurações do Azure estão completas"""
        return all([cls.SERVER, cls.DATABASE, cls.USERNAME, cls.PASSWORD])
    
    @classmethod
    def dependencies_available(cls):
        """Verifica se as dependências do Azure estão disponíveis"""
        try:
            import pyodbc
            import sqlalchemy
            return True
        except ImportError:
            return False