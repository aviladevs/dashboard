import streamlit as st

def mostrar_apresentacao():
    """Página de apresentação da empresa Ávila Transportes"""
    
    # Configuração da página
    st.set_page_config(
        page_title="Ávila Transportes - Sistema Unificado",
        page_icon="🚛",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # CSS personalizado para estilização
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(90deg, #1f4e79, #2a6ba0);
            color: white;
            margin: -1rem -1rem 2rem -1rem;
            border-radius: 0 0 20px 20px;
        }
        .feature-box {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #2a6ba0;
        }
        .btn-login {
            background: #2a6ba0;
            color: white;
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 25px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            width: 200px;
            margin: 2rem auto;
            display: block;
        }
        .company-info {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🚛 Ávila Transportes</h1>
        <h3>Sistema Unificado de Gestão</h3>
        <p>Soluções completas em transporte e logística</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Informações da empresa
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="company-info">
            <h2>🏢 Sobre a Ávila Transportes</h2>
            <p style="font-size: 1.1rem; line-height: 1.6;">
                A <strong>Ávila Transportes</strong> é uma empresa consolidada no mercado de transporte e logística, 
                oferecendo soluções completas para atender às necessidades de nossos clientes com eficiência, 
                segurança e pontualidade.
            </p>
            
            <h3>✨ Nossos Serviços</h3>
            <ul style="font-size: 1rem; line-height: 1.8;">
                <li><strong>Transporte Rodoviário:</strong> Frota moderna e rastreada</li>
                <li><strong>Logística Integrada:</strong> Soluções completas de armazenagem</li>
                <li><strong>Gestão de Cargas:</strong> Controle total da operação</li>
                <li><strong>Consultoria:</strong> Otimização de rotas e custos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="company-info">
            <h3>📞 Contato</h3>
            <p><strong>Website:</strong><br>
            🌐 aviladevops.com.br<br>
            🌐 avilatransportes.com.br</p>
            
            <p><strong>Atendimento:</strong><br>
            📧 contato@avilatransportes.com.br<br>
            📞 (11) 9999-9999</p>
            
            <p><strong>Endereço:</strong><br>
            📍 São Paulo - SP<br>
            Brasil</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Seção de funcionalidades do sistema
    st.markdown("## 💼 Sistema de Gestão Unificado")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h4>📊 Dashboard Geral</h4>
            <p>Visão completa dos indicadores operacionais, financeiros e de performance em tempo real.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h4>📋 Gestão de Faturas</h4>
            <p>Controle completo de faturas, minutas e documentação fiscal integrada.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <h4>💰 Controle Financeiro</h4>
            <p>Gestão financeira completa com conciliação bancária e controle de fluxo de caixa.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Seção de acesso ao sistema
    st.markdown("---")
    st.markdown("## 🔐 Acesso ao Sistema")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <p style="font-size: 1.2rem; margin-bottom: 1.5rem;">
                Para acessar o sistema completo de gestão, faça seu login com suas credenciais.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Acessar Sistema", key="btn_login", help="Clique para fazer login no sistema"):
            st.session_state.show_login = True
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>© 2024 Ávila Transportes - Todos os direitos reservados</p>
        <p>Sistema desenvolvido para otimização de processos logísticos</p>
    </div>
    """, unsafe_allow_html=True)