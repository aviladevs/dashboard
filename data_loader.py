import pandas as pd
import streamlit as st
import os

ARQ_BASE = "base.csv"

@st.cache_data(show_spinner=False)
def carregar_base():
    try:
        if not os.path.exists(ARQ_BASE):
            return pd.DataFrame(columns=[
                "Data de Emissão", "Descrição", "Valor do frete", "Valor", "Tipo",
                "Categoria", "Centro de Custo", "Setor", "ID Transação", "Conciliado com"
            ])
        df = pd.read_csv(ARQ_BASE, sep=";", encoding="utf-8")
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.columns = [c.strip() for c in df.columns]

        col_frete = [c for c in df.columns if "valor do frete" in c.lower()]
        if not col_frete:
            col_frete = [c for c in df.columns if "frete" in c.lower() and "valor" in c.lower()]

        if col_frete:
            col = col_frete[0]
            df[col] = (
                df[col].astype(str)
                .str.replace("R$", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".")
            )
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df.rename(columns={col: "Valor do frete"}, inplace=True)
        else:
            df["Valor do frete"] = 0.0
            st.warning("⚠️ Coluna de frete não encontrada. Criada com valor 0.0.")

        if "Data de Emissão" in df.columns:
            df["Data de Emissão"] = pd.to_datetime(df["Data de Emissão"], dayfirst=True, errors="coerce")
            df = df[df["Data de Emissão"].notnull()]
            df["Quinzena"] = df["Data de Emissão"].apply(
                lambda x: f"{x.month:02d}/1ª" if x.day <= 15 else f"{x.month:02d}/2ª"
            )
            df["Data de Vencimento"] = df["Data de Emissão"] + pd.Timedelta(days=10)
        else:
            st.warning("⚠️ Coluna 'Data de Emissão' não encontrada.")

        for campo in ["Soma dos Volumes", "Soma das Notas", "Soma dos Pesos"]:
            if campo in df.columns:
                df[campo] = pd.to_numeric(df[campo], errors="coerce").fillna(0)

        return df

    except Exception as e:
        st.error(f"❌ Erro ao carregar base: {e}")
        return pd.DataFrame()

def salvar_base(df):
    pasta = os.path.dirname(ARQ_BASE)
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    df.to_csv(ARQ_BASE, sep=";", index=False)
    st.success("Base salva com sucesso!")
