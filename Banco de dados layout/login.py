import streamlit as st
import hashlib

def hash_password(password):
    """Cria hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

# Credenciais do sistema (em produção, essas deveriam estar em um banco de dados seguro)
USUARIOS_SISTEMA = {
    "admin": hash_password("admin123"),
    "avila": hash_password("avila2024"),
    "gerente": hash_password("gerente@123"),
    "operador": hash_password("operador2024")
}

def verificar_credenciais(usuario, senha):
    """Verifica se as credenciais são válidas"""
    if usuario in USUARIOS_SISTEMA:
        senha_hash = hash_password(senha)
        return USUARIOS_SISTEMA[usuario] == senha_hash
    return False

def mostrar_login():
    """Página de login do sistema"""
    
    # Configuração da página
    st.set_page_config(
        page_title="Login - Ávila Transportes",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # CSS personalizado para a página de login
    st.markdown("""
    <style>
        .login-container {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: 2rem auto;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-title {
            color: #1f4e79;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            color: #666;
            font-size: 1rem;
        }
        .stButton > button {
            background: linear-gradient(90deg, #1f4e79, #2a6ba0);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            font-weight: bold;
            width: 100%;
            margin-top: 1rem;
        }
        .stButton > button:hover {
            background: linear-gradient(90deg, #2a6ba0, #1f4e79);
            border: none;
        }
        .back-link {
            text-align: center;
            margin-top: 2rem;
        }
        .back-link a {
            color: #2a6ba0;
            text-decoration: none;
            font-size: 0.9rem;
        }
        .back-link a:hover {
            text-decoration: underline;
        }
        .credentials-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #28a745;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Container principal
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Header do login
    st.markdown("""
    <div class="login-header">
        <div class="login-title">🔐 Login</div>
        <div class="login-subtitle">Ávila Transportes - Sistema Unificado</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulário de login
    with st.form("login_form", clear_on_submit=False):
        usuario = st.text_input("👤 Usuário", placeholder="Digite seu nome de usuário")
        senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("🚀 Entrar")
        with col2:
            voltar = st.form_submit_button("← Voltar")
    
    # Informações de credenciais para demonstração
    st.markdown("""
    <div class="credentials-info">
        <strong>💡 Credenciais de Demonstração:</strong><br>
        • admin / admin123<br>
        • avila / avila2024<br>
        • gerente / gerente@123<br>
        • operador / operador2024
    </div>
    """, unsafe_allow_html=True)
    
    # Processamento do formulário
    if submitted:
        if usuario and senha:
            if verificar_credenciais(usuario, senha):
                st.session_state.authenticated = True
                st.session_state.username = usuario
                st.session_state.show_login = False
                st.success("✅ Login realizado com sucesso!")
                st.balloons()
                # Pequeno delay para mostrar a mensagem de sucesso
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos!")
        else:
            st.warning("⚠️ Por favor, preencha todos os campos!")
    
    if voltar:
        st.session_state.show_login = False
        if 'authenticated' in st.session_state:
            del st.session_state.authenticated
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0 1rem 0; font-size: 0.9rem;">
        <p>© 2024 Ávila Transportes - Sistema Seguro</p>
    </div>
    """, unsafe_allow_html=True)

def logout():
    """Função para fazer logout do sistema"""
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    if 'username' in st.session_state:
        del st.session_state.username
    if 'show_login' in st.session_state:
        del st.session_state.show_login
    st.rerun()

def verificar_autenticacao():
    """Verifica se o usuário está autenticado"""
    return st.session_state.get('authenticated', False)

def get_usuario_logado():
    """Retorna o nome do usuário logado"""
    return st.session_state.get('username', 'Usuário')