import streamlit as st
import os
import pandas as pd

# Import modules
from consulta_faturas import mostrar_faturas
from consulta_minuta import mostrar_minutas
from dashboard import mostrar_dashboard
from financas import mostrar_financeiro
from emissoes import mostrar_emissao
from data_loader import carregar_base, salvar_base

# Configuração inicial da página
st.set_page_config(page_title="Ávila Transportes", layout="wide")
st.title("🚛 Sistema Unificado - Ávila Transportes")

# Menu lateral
aba = st.sidebar.radio("Escolha a funcionalidade:", [
    "Dashboard Geral", 
    "Consulta de Faturas", 
    "Consulta de Minuta", 
    "Financeiro", 
    "Emissões"
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
