import streamlit as st
import os  
import conciliacao
import consulta_faturas 
import consulta_minuta
import dashboard
import data_loader
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
from apresentacao import mostrar_apresentacao
from login import mostrar_login, verificar_autenticacao, get_usuario_logado, logout

def main():
    """Função principal que controla o fluxo da aplicação"""
    
    # Inicialização do estado da sessão
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Controle de fluxo da aplicação
    if not st.session_state.show_login and not verificar_autenticacao():
        # Mostrar página de apresentação
        mostrar_apresentacao()
    elif st.session_state.show_login and not verificar_autenticacao():
        # Mostrar página de login
        mostrar_login()
    elif verificar_autenticacao():
        # Mostrar dashboard principal (usuário autenticado)
        mostrar_dashboard_principal()

def mostrar_dashboard_principal():
    """Dashboard principal do sistema após autenticação"""
    
    # Configuração da página
    st.set_page_config(page_title="Ávila Transportes - Dashboard", layout="wide")
    
    # Header com informações do usuário
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🚛 Sistema Unificado - Ávila Transportes")
    with col2:
        st.write(f"👤 **{get_usuario_logado()}**")
    with col3:
        if st.button("🚪 Sair", help="Fazer logout do sistema"):
            logout()
    
    # Menu lateral
    with st.sidebar:
        st.markdown("### 📋 Menu Principal")
        aba = st.radio("Escolha a funcionalidade:", [
            "Dashboard Geral", 
            "Consulta de Faturas", 
            "Consulta de Minuta", 
            "Financeiro", 
            "Emissões"
        ])
        
        st.markdown("---")
        st.markdown("### ℹ️ Informações")
        st.info(f"**Usuário:** {get_usuario_logado()}\n**Status:** Conectado")
    
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

if __name__ == "__main__":
    main()
