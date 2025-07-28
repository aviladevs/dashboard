import streamlit as st
import pandas as pd
import os
from parser_ofx import extrair_transacoes  # Função que você deve ter para extrair OFX

# Garantir pasta 'data' para salvar arquivos
os.makedirs("data", exist_ok=True)

ARQ_BASE = "data/base_financeira.csv"

# Função para carregar base CSV
def carregar_base():
    try:
        if os.path.exists(ARQ_BASE):
            return pd.read_csv(ARQ_BASE, sep=";")
        else:
            cols = ["Data", "Descrição", "Valor", "Tipo", "Categoria",
                    "Setor", "Centro de Custo", "ID Transação", "Conciliado com"]
            return pd.DataFrame(columns=cols)
    except Exception as e:
        st.error(f"Erro ao carregar a base: {e}")
        return pd.DataFrame()

# Função para salvar base CSV
def salvar_base(df):
    try:
        df.to_csv(ARQ_BASE, sep=";", index=False)
    except Exception as e:
        st.error(f"Erro ao salvar a base: {e}")

# Atualiza base com transações novas do OFX
def atualizar_com_ofx(df_ofx):
    base = carregar_base()
    if df_ofx.empty:
        st.warning("⚠️ Nenhum dado OFX carregado.")
        return base, 0

    # Filtrar apenas transações ainda não importadas
    for idx, row in df_ofx.iterrows():
        existe = base[base["ID Transação"] == row["ID Transação"]]
        if existe.empty:
            # Nova transação: adicionar à base
            base = pd.concat([base, row.to_frame().T], ignore_index=True)
    
    # Salvar base atualizada
    salvar_base(base)
    return base, len(df_ofx)

def mostrar_financeiro():
    """Função principal do módulo financeiro"""
    
    # Configuração da página
    st.header("💳 Dashboard Financeiro Integrado")
    
    # Upload de arquivos OFX
    st.markdown("### 📥 Importar arquivo OFX")
    upload_ofx = st.file_uploader("", type=["ofx"], key="uploader_ofx")
    
    if upload_ofx:
        try:
            # Extrair dados do OFX usando parser
            df_ofx = extrair_transacoes(upload_ofx)
            if not df_ofx.empty:
                st.success(f"✅ {len(df_ofx)} transações extraídas do OFX!")
                
                # Atualizar base com dados do OFX
                base, novas = atualizar_com_ofx(df_ofx)
                if novas > 0:
                    st.success(f"✅ {novas} novas transações importadas!")
                else:
                    st.info("ℹ️ Nenhuma transação nova encontrada.")
            else:
                st.warning("⚠️ Nenhuma transação encontrada no arquivo OFX.")
        except Exception as e:
            st.error(f"❌ Erro ao processar OFX: {e}")

    # Carregar base existente
    base = carregar_base()
    
    if base.empty:
        st.warning("⚠️ Base de dados vazia. Importe dados para continuar.")
        return

    # Filtros lateral (multiselect)
    if 'Setor' in base.columns:
        setores = sorted(base["Setor"].dropna().unique())
        if setores:
            setor_sel = st.sidebar.multiselect("Setores", setores, default=setores)
            base = base[base["Setor"].isin(setor_sel)]

    if 'Centro de Custo' in base.columns:
        centros = sorted(base["Centro de Custo"].dropna().unique())
        if centros:
            centro_sel = st.sidebar.multiselect("Centros de Custo", centros, default=centros)
            base = base[base["Centro de Custo"].isin(centro_sel)]

    if 'Categoria' in base.columns:
        categorias = sorted(base["Categoria"].dropna().unique())
        if categorias:
            cat_sel = st.sidebar.multiselect("Categorias", categorias, default=categorias)
            base = base[base["Categoria"].isin(cat_sel)]

    # Tabela principal
    st.markdown(f"### 📋 Transações Financeiras (Total: {len(base)})")
    st.dataframe(base, use_container_width=True)

    # Conciliação simples
    if not base.empty and "ID Transação" in base.columns:
        st.markdown("### 🔗 Conciliação Simples")
        
        # Selecionar transação para conciliar
        transacoes_nao_conciliadas = base[base["Conciliado com"].isna() | (base["Conciliado com"] == "")]
        
        if not transacoes_nao_conciliadas.empty:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                opcoes_trans = transacoes_nao_conciliadas["ID Transação"].tolist()
                trans_selecionada = st.selectbox("Escolha uma transação para conciliar", opcoes_trans)
            
            with col2:
                numero_minuta = st.text_input("Número da Minuta ou CT-e")
            
            with col3:
                if st.button("Conciliar"):
                    if trans_selecionada and numero_minuta:
                        # Atualizar a base com a conciliação
                        base.loc[base["ID Transação"] == trans_selecionada, "Conciliado com"] = numero_minuta
                        salvar_base(base)
                        st.success(f"✅ Transação {trans_selecionada} conciliada com {numero_minuta}")
                        st.rerun()
                    else:
                        st.warning("⚠️ Selecione uma transação e digite o número da minuta!")

    # Resumos financeiros
    if not base.empty and "Valor" in base.columns:
        st.markdown("### 📊 Resumo Financeiro")
        
        # Converter valores para numérico
        base["Valor"] = pd.to_numeric(base["Valor"], errors='coerce').fillna(0)
        
        # Calcular totais
        total_receitas = base[base["Valor"] > 0]["Valor"].sum()
        total_despesas = base[base["Valor"] < 0]["Valor"].sum()
        saldo_total = base["Valor"].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Receitas", f"R$ {total_receitas:,.2f}")
        with col2:
            st.metric("Total Despesas", f"R$ {total_despesas:,.2f}")
        with col3:
            st.metric("Saldo Total", f"R$ {saldo_total:,.2f}")

        # Resumo por Categoria
        if "Categoria" in base.columns:
            st.markdown("### 📊 Resumo por Categoria")
            resumo_categoria = base.groupby("Categoria")["Valor"].sum().sort_values(ascending=False)
            st.dataframe(resumo_categoria.to_frame("Valor"), use_container_width=True)

    # Transações sem Centro de Custo ou Setor definidos
    if not base.empty:
        faltando = base[(base.get("Centro de Custo", "") == "❗Definir") | (base.get("Setor", "") == "❗Definir")]
        if not faltando.empty:
            st.markdown("### ⚠️ Transações sem Centro de Custo ou Setor definidos")
            st.markdown("Complete os dados abaixo:")
            
            # Editor de dados
            edit_df = st.data_editor(faltando, num_rows="dynamic", key="editor_cc_setor")
            
            if st.button("✅ Confirmar Classificações Manuais"):
                # Atualizar a base principal com as edições
                for idx, row in edit_df.iterrows():
                    if idx in base.index:
                        if "Centro de Custo" in row:
                            base.loc[idx, "Centro de Custo"] = row["Centro de Custo"]
                        if "Setor" in row:
                            base.loc[idx, "Setor"] = row["Setor"]
                
                salvar_base(base)
                st.success("✅ Classificações salvas com sucesso!")
                st.rerun()

    # Botão para salvar alterações
    if st.button("💾 Salvar Alterações"):
        salvar_base(base)
        st.success("✅ Base salva com sucesso!")