import streamlit as st
import pandas as pd

def exibir_consulta(base, tipo):
    st.markdown(f"### 🔍 Consulta de {tipo.title()}")
    termo = st.text_input(f"Buscar {tipo}", "")
    if termo:
        resultado = base[base["Descrição"].str.contains(termo, case=False, na=False)]
        st.dataframe(resultado)
        
def mostrar_faturas(base):
    st.header("📄 Consulta de Faturas")
    data_ini = st.date_input("Data de Vencimento Início")
    data_fim = st.date_input("Data de Vencimento Fim")
    base["Data de Vencimento"] = pd.to_datetime(base.get("Data de Vencimento", pd.NaT), dayfirst=True, errors="coerce")
    base_filtrado = base[
        (base["Data de Vencimento"] >= pd.to_datetime(data_ini)) &
        (base["Data de Vencimento"] <= pd.to_datetime(data_fim))
    ]

    faturas = base_filtrado.groupby("Nº Fatura", as_index=False).agg({
        "Pagador do Frete - Nome": "first",
        "Valor do frete": "sum",
        "Número": "max",
        "Quinzena": "first"
    }).rename(columns={
        "Pagador do Frete - Nome": "Empresa Pagadora",
        "Valor do frete": "Total do Frete",
        "Número": "Número Fatura"
    })

    st.dataframe(faturas, use_container_width=True)

    fat_selecionada = st.selectbox("Selecione uma fatura:", faturas["Nº Fatura"])
    if fat_selecionada:
        detalhes = base_filtrado[base_filtrado["Nº Fatura"] == fat_selecionada][
            ["Número", "Remetente - Nome", "Destinatário - Nome", "Soma dos Volumes", "Notas Fiscais", "Valor do frete", "Data de Vencimento"]
        ]
        st.dataframe(detalhes, use_container_width=True)


