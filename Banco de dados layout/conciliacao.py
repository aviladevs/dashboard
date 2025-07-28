import streamlit as st
import pandas as pd
import re

# Tenta importar PyMuPDF, mas continua sem ele
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

@st.cache_data
def extrair_dados_fatura_mello():
    try:
        if not PYMUPDF_AVAILABLE:
            st.warning("⚠️ PyMuPDF não disponível. Funcionalidade de PDF limitada.")
            return pd.DataFrame()
            
        with fitz.open("AVILA TRANSPORTES.pdf") as doc:
            texto = "\n".join([page.get_text() for page in doc])

        # Expressão para capturar: nota, valor e data
        padrao = re.compile(r"(\d{5,})\s+.*?\s+(\d{2}/\d{2}/\d{4}).*?([\d\.]+,[\d]{2})")
        linhas = padrao.findall(texto)

        dados = []
        for nota, data, valor in linhas:
            valor_float = float(valor.replace(".", "").replace(",", "."))
            dados.append({"Número": nota, "Data": data, "Valor do frete (PDF)": valor_float})

        df_pdf = pd.DataFrame(dados)
        df_pdf["Data"] = pd.to_datetime(df_pdf["Data"], dayfirst=True, errors="coerce")
        return df_pdf

    except Exception as e:
        st.error(f"Erro ao extrair dados do PDF: {e}")
        return pd.DataFrame()

def mostrar_conciliacao(base):
    st.header("🔁 Conciliação de Fretes - Mello")

    if not PYMUPDF_AVAILABLE:
        st.warning("⚠️ PyMuPDF não disponível. Para usar funcionalidades de PDF, instale: pip install PyMuPDF")
        st.info("Funcionalidade limitada - apenas conciliação manual disponível.")
    
    df_fatura = extrair_dados_fatura_mello()
    if df_fatura.empty:
        st.warning("Nenhum dado extraído do PDF.")
        # Mostra apenas a interface de conciliação manual
        if "ID Transação" in base.columns:
            exibir_conciliacao(base, lambda x: None)  # Mock da função salvar
        return

    base["Número"] = base["Número"].astype(str)
    df_fatura["Número"] = df_fatura["Número"].astype(str)

    conciliado = df_fatura.merge(base, on="Número", how="left", suffixes=("_fatura", "_base"))
    conciliado["Diferença"] = (conciliado["Valor do frete (PDF)"] - conciliado["Valor do frete"]).round(2)

    conciliado["Status"] = conciliado["Valor do frete"].apply(
        lambda x: "Não encontrado" if pd.isna(x) else "OK"
    )
    conciliado.loc[conciliado["Status"] == "OK", "Status"] = conciliado["Diferença"].apply(
        lambda x: "Conciliado" if abs(x) < 1 else "Divergente"
    )

    st.dataframe(conciliado, use_container_width=True)
    st.write("\nResumo:")
    st.dataframe(conciliado["Status"].value_counts().rename("Qtd"))
    
    # Download CSV
    csv = conciliado.to_csv(index=False, sep=";").encode("utf-8")
    st.download_button("📥 Baixar Conciliação (CSV)", csv, "conciliacao_mello.csv", mime="text/csv")

def exibir_conciliacao(base, salvar_func):
    trans = base[base["Conciliado com"].isna() | (base["Conciliado com"] == "")] if "Conciliado com" in base.columns else pd.DataFrame()
    if trans.empty: 
        return

    st.markdown("### 🔗 Conciliação de Transações")
    with st.form("form_conciliacao"):
        id_sel = st.selectbox("Selecione ID", trans["ID Transação"].tolist())
        doc = st.text_input("Minuta ou CT‑e")
        submit = st.form_submit_button("Conciliar")
    if submit:
        idx = base[base["ID Transação"] == id_sel].index
        base.loc[idx, "Conciliado com"] = doc
        if salvar_func:
            salvar_func(base)
        st.success("Conciliação salva com sucesso!")
