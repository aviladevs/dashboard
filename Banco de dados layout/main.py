import streamlit as st
import os  
import conciliacao
import consulta_faturas 
import consulta_minuta
import dashboard
import data_loader
import streamlit as st
import financas
import emissoes
import pandas as pd
from conciliacao import mostrar_conciliacao
from consulta_faturas import mostrar_faturas
from consulta_minuta import mostrar_minutas
from dashboard import mostrar_dashboard
from financas import mostrar_financeiro
from emissoes import mostrar_emissao
from data_loader import carregar_base, salvar_base

# Tenta importar módulos do Azure, mas continua sem eles
try:
    from azure_setup import mostrar_configuracao_azure, mostrar_status_azure
    AZURE_SETUP_AVAILABLE = True
except ImportError:
    AZURE_SETUP_AVAILABLE = False
    def mostrar_configuracao_azure():
        st.error("❌ Módulos do Azure não disponíveis. Instale as dependências: pip install -r requirements.txt")
    def mostrar_status_azure():
        st.sidebar.info("📁 Modo CSV (Azure indisponível)")
    
    st.write("Selecione uma fatura para ver os detalhes.")



# Configuração inicial da página
st.set_page_config(page_title="Avila Transportes", layout="wide")
st.title("🚛 Sistema Unificado - Ávila Transportes")

# Mostra status do Azure na sidebar
mostrar_status_azure()

# Menu lateral
aba = st.sidebar.radio("Escolha a funcionalidade:", [
    "Dashboard Geral", 
    "Consulta de Faturas", 
    "Consulta de Minuta", 
    "Financeiro", 
    "Emissões",
    "⚙️ Configuração Azure"
])

# Carregamento da base de dados
try:
    base = carregar_base()
except Exception as e:
    st.error(f"Erro ao carregar base de dados: {e}")
    base = None

# Roteamento entre as abas
if aba == "Dashboard Geral":
    if base is not None:
        mostrar_dashboard(base)
    else:
        st.warning("⚠️ Base de dados não carregada.")
elif aba == "Consulta de Faturas":
    if base is not None:
        mostrar_faturas(base)
    else:
        st.warning("⚠️ Base de dados não carregada.")
elif aba == "Consulta de Minuta":
    if base is not None:
        mostrar_minutas(base)
    else:
        st.warning("⚠️ Base de dados não carregada.")
elif aba == "Financeiro":
    mostrar_financeiro()
elif aba == "Emissões":
    mostrar_emissao()
elif aba == "⚙️ Configuração Azure":
    mostrar_configuracao_azure()
