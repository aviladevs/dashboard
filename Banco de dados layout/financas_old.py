import streamlit as st
import pandas as pd
import os
from parser_ofx import extrair_transacoes  # Função que você deve ter para extrair OFX

# Configuração da página
st.set_page_config("Financeiro Inteligente", layout="wide")
st.title("💳 Dashboard Financeiro Integrado")

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
    # Evita duplicidade pela chave "ID Transação"
    novos = df_ofx[~df_ofx["ID Transação"].isin(base["ID Transação"])]
    if novos.empty:
        return base, 0
    final = pd.concat([base, novos], ignore_index=True)
    salvar_base(final)
    return final, len(novos)

# Upload OFX e processamento
uploaded_file = st.file_uploader("📥 Importar arquivo OFX", type=["ofx"])
if uploaded_file:
    df_ofx = extrair_transacoes(uploaded_file)
    st.success(f"{len(df_ofx)} transações lidas.")
    base, novos = atualizar_com_ofx(df_ofx)
    st.info(f"{novos} novas transações adicionadas.")
else:
    base = carregar_base()

if base.empty:
    st.warning("⚠️ Base de dados vazia. Carregue um arquivo OFX.")
    st.stop()

# Filtros na sidebar
setores = sorted(base["Setor"].dropna().unique())
centros = sorted(base["Centro de Custo"].dropna().unique())
categorias = sorted(base["Categoria"].dropna().unique())

setor_sel = st.sidebar.multiselect("Setores", setores, default=setores)
centro_sel = st.sidebar.multiselect("Centros de Custo", centros, default=centros)
cat_sel = st.sidebar.multiselect("Categorias", categorias, default=categorias)

df = base[
    base["Setor"].isin(setor_sel) &
    base["Centro de Custo"].isin(centro_sel) &
    base["Categoria"].isin(cat_sel)
]

# Exibição tabela
st.markdown(f"### 📋 Transações Financeiras (Total: {len(df)})")
st.dataframe(df, use_container_width=True)

# Conciliação manual com documento interno
transacoes_nao_conciliadas = df[df["Conciliado com"].isna() | (df["Conciliado com"] == "")]
if not transacoes_nao_conciliadas.empty:
    with st.form("form_conciliacao"):
        id_escolhido = st.selectbox("Escolha uma transação para conciliar", transacoes_nao_conciliadas["ID Transação"].tolist())
        doc = st.text_input("Número da Minuta ou CT-e")
        submit_conciliar = st.form_submit_button("Conciliar")

    if submit_conciliar:
        idx = base[base["ID Transação"] == id_escolhido].index
        base.loc[idx, "Conciliado com"] = doc
        salvar_base(base)
        st.success(f"Transação {id_escolhido} conciliada com documento {doc}")

# Resumo financeiro
st.markdown("### 📊 Resumo Financeiro")
total_receitas = base[base["Tipo"] == "Receita"]["Valor"].sum()
total_despesas = base[base["Tipo"] == "Despesa"]["Valor"].sum()
saldo_total = base["Valor"].sum()
st.markdown(f"**Total Receitas:** R$ {total_receitas:,.2f}")
st.markdown(f"**Total Despesas:** R$ {total_despesas:,.2f}")
st.markdown(f"**Saldo Total:** R$ {saldo_total:,.2f}")

# Resumo por Categoria (markdown)
st.markdown("### 📊 Resumo por Categoria")
st.markdown(base.groupby("Categoria")["Valor"].sum().to_markdown())

# Transações sem Centro de Custo ou Setor definidos
faltando = base[(base["Centro de Custo"] == "❗Definir") | (base["Setor"] == "❗Definir")]
if not faltando.empty:
    st.markdown("### ⚠️ Transações sem Centro de Custo ou Setor definidos")
    st.markdown("Complete os dados abaixo:")

    edit_df = st.experimental_data_editor(faltando, num_rows="dynamic", key="editor_cc_setor")

    if st.button("✅ Confirmar Classificações Manuais"):
        for idx, row in edit_df.iterrows():
            base.loc[row.name, "Centro de Custo"] = row["Centro de Custo"]
            base.loc[row.name, "Setor"] = row["Setor"]
        salvar_base(base)
        st.success("Dados atualizados com sucesso!")

# Gráfico resumo por Categoria
st.markdown("### 📈 Gráfico por Categoria")
st.bar_chart(base.groupby("Categoria")["Valor"].sum())
