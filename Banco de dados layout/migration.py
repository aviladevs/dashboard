"""
Módulo para migração de dados CSV para Azure SQL Database
"""
import pandas as pd
import streamlit as st
import os
from typing import Optional
from azure_db import azure_db
from azure_config import AzureConfig

class DataMigration:
    """Classe para migração de dados CSV para Azure"""
    
    def __init__(self):
        self.csv_base_path = "base.csv"
        self.csv_financeiro_path = "data/base_financeira.csv"
    
    def migrate_fretes_data(self) -> bool:
        """Migra dados de fretes do CSV para Azure"""
        try:
            if not os.path.exists(self.csv_base_path):
                st.warning("⚠️ Arquivo base.csv não encontrado")
                return False
            
            # Carrega dados do CSV
            df = pd.read_csv(self.csv_base_path, sep=";", encoding="utf-8")
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            
            # Limpa e normaliza as colunas
            df.columns = [self._normalize_column_name(col) for col in df.columns]
            
            # Processa colunas específicas
            df = self._process_frete_columns(df)
            
            # Verifica se a tabela existe
            if not azure_db.table_exists('fretes'):
                st.error("❌ Tabela 'fretes' não existe. Execute o script create_tables.sql primeiro")
                return False
            
            # Verifica se já foi migrado
            existing_count = azure_db.execute_query("SELECT COUNT(*) as count FROM fretes")
            if not existing_count.empty and existing_count['count'].iloc[0] > 0:
                st.info("ℹ️ Dados de fretes já foram migrados")
                return True
            
            # Mapeia colunas do CSV para o banco
            df_mapped = self._map_frete_columns(df)
            
            # Insere no banco
            success = azure_db.insert_dataframe(df_mapped, 'fretes', if_exists='append')
            
            if success:
                st.success(f"✅ {len(df_mapped)} registros de fretes migrados com sucesso")
                return True
            else:
                st.error("❌ Falha na migração dos dados de fretes")
                return False
        
        except Exception as e:
            st.error(f"❌ Erro na migração de fretes: {e}")
            return False
    
    def migrate_financial_data(self) -> bool:
        """Migra dados financeiros do CSV para Azure"""
        try:
            if not os.path.exists(self.csv_financeiro_path):
                st.warning("⚠️ Arquivo de dados financeiros não encontrado")
                return True  # Não é crítico se não existir
            
            # Carrega dados financeiros
            df = pd.read_csv(self.csv_financeiro_path, sep=";", encoding="utf-8")
            
            # Verifica se a tabela existe
            if not azure_db.table_exists('transacoes_financeiras'):
                st.error("❌ Tabela 'transacoes_financeiras' não existe")
                return False
            
            # Verifica se já foi migrado
            existing_count = azure_db.execute_query("SELECT COUNT(*) as count FROM transacoes_financeiras")
            if not existing_count.empty and existing_count['count'].iloc[0] > 0:
                st.info("ℹ️ Dados financeiros já foram migrados")
                return True
            
            # Mapeia colunas para o banco
            df_mapped = self._map_financial_columns(df)
            
            # Insere no banco
            success = azure_db.insert_dataframe(df_mapped, 'transacoes_financeiras', if_exists='append')
            
            if success:
                st.success(f"✅ {len(df_mapped)} transações financeiras migradas com sucesso")
                return True
            else:
                st.error("❌ Falha na migração dos dados financeiros")
                return False
        
        except Exception as e:
            st.error(f"❌ Erro na migração financeira: {e}")
            return False
    
    def _normalize_column_name(self, col_name: str) -> str:
        """Normaliza nomes de colunas"""
        return col_name.strip().replace(' ', '_').replace('-', '_').lower()
    
    def _process_frete_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processa colunas específicas de frete"""
        # Processa valor do frete
        frete_cols = [col for col in df.columns if 'frete' in col.lower() and 'valor' in col.lower()]
        if frete_cols:
            col = frete_cols[0]
            df[col] = (
                df[col].astype(str)
                .str.replace("R$", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".")
            )
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Processa datas
        date_cols = [col for col in df.columns if 'data' in col.lower() or 'emissao' in col.lower()]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
        
        # Processa campos numéricos
        numeric_fields = ['soma_dos_volumes', 'soma_das_notas', 'soma_dos_pesos']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)
        
        return df
    
    def _map_frete_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Mapeia colunas do CSV para a tabela fretes"""
        column_mapping = {
            'data_de_emissao': 'data_emissao',
            'numero': 'numero',
            'pagador_do_frete___nome': 'pagador_nome',
            'valor_do_frete': 'valor_frete',
            'notas_fiscais': 'notas_fiscais',
            'remetente___nome': 'remetente_nome',
            'remetente___cidade': 'remetente_cidade',
            'destinatario___nome': 'destinatario_nome',
            'destinatario___cidade': 'destinatario_cidade',
            'soma_dos_volumes': 'soma_volumes',
            'soma_das_notas': 'soma_notas',
            'soma_dos_pesos': 'soma_pesos'
        }
        
        # Seleciona apenas colunas que existem
        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        
        df_mapped = df[list(existing_cols.keys())].copy()
        df_mapped.rename(columns=existing_cols, inplace=True)
        
        return df_mapped
    
    def _map_financial_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Mapeia colunas do CSV financeiro para a tabela transacoes_financeiras"""
        column_mapping = {
            'Data': 'data_transacao',
            'Descrição': 'descricao',
            'Valor': 'valor',
            'Tipo': 'tipo',
            'Categoria': 'categoria',
            'Setor': 'setor',
            'Centro de Custo': 'centro_custo',
            'ID Transação': 'id_transacao_externa',
            'Conciliado com': 'conciliado_com'
        }
        
        # Seleciona apenas colunas que existem
        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        
        df_mapped = df[list(existing_cols.keys())].copy()
        df_mapped.rename(columns=existing_cols, inplace=True)
        
        return df_mapped
    
    def run_full_migration(self) -> bool:
        """Executa migração completa dos dados"""
        st.info("🔄 Iniciando migração de dados para Azure Database...")
        
        success = True
        
        # Migra dados de fretes
        if not self.migrate_fretes_data():
            success = False
        
        # Migra dados financeiros
        if not self.migrate_financial_data():
            success = False
        
        if success:
            # Atualiza configuração indicando que a migração foi feita
            azure_db.execute_non_query(
                "UPDATE configuracoes SET valor = 'true' WHERE chave = 'migrado_csv'"
            )
            st.success("🎉 Migração completa realizada com sucesso!")
        else:
            st.error("❌ Falha na migração. Verifique os logs acima.")
        
        return success

# Instância global da migração
data_migration = DataMigration()