import streamlit as st
import pandas as pd

def exibir_dashboard(df):
    st.markdown("### 📋 Transações Financeiras")
    st.dataframe(df, use_container_width=True)
    st.markdown("### 📊 Resumo por Categoria")
    st.markdown(df.groupby("Categoria")["Valor"].sum().to_markdown())
    st.markdown("### 📈 Gráfico por Categoria")
    st.bar_chart(df.groupby("Categoria")["Valor"].sum())

def mostrar_dashboard(base):
    st.header("📊 Dashboard Geral")

    if base.empty:
        st.warning("Base de dados está vazia.")
        return

    # Mostrar colunas disponíveis
    st.write("Colunas da base:", base.columns.tolist())

    # Tratamento de datas
    if "Data de Emissão" in base.columns:
        try:
            base["Data de Emissão"] = pd.to_datetime(base["Data de Emissão"], dayfirst=True, errors="coerce")
            base["Ano"] = base["Data de Emissão"].dt.year
            base["Mês"] = base["Data de Emissão"].dt.strftime("%Y-%m")
        except Exception as e:
            st.error(f"Erro ao processar datas: {e}")

        # Métricas principais
        if "Valor do frete" in base.columns:
            try:
                base["Valor do frete"] = base["Valor do frete"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".").astype(float)
                st.metric("Total de Frete", f"R${base['Valor do frete'].sum():,.2f}")
            except Exception as e:
                st.error(f"Erro ao calcular valor total de frete: {e}")

        if "Soma dos Volumes" in base.columns:
            try:
                total_volumes = pd.to_numeric(base["Soma dos Volumes"], errors='coerce').fillna(0)
                st.metric("Total de Volumes", int(total_volumes.sum()))
            except Exception as e:
                st.error(f"Erro ao calcular total de volumes: {e}")

        # Gráficos
        if "Valor do frete" in base.columns:
            try:
                st.subheader("📅 Frete por Mês")
                st.bar_chart(base.groupby("Mês")["Valor do frete"].sum())

                st.subheader("📈 Média de Frete por Ano")
                st.line_chart(base.groupby("Ano")["Valor do frete"].mean())
            except Exception as e:
                st.error(f"Erro ao gerar gráficos de frete: {e}")

        if "Destinatário - Cidade" in base.columns and "Valor do frete" in base.columns:
            try:
                st.subheader("📍 Frete por Cidade Destinatária")
                st.bar_chart(base.groupby("Destinatário - Cidade")["Valor do frete"].sum().sort_values(ascending=False))
            except Exception as e:
                st.error(f"Erro ao gerar gráfico por cidade: {e}")
    else:
        st.warning("A coluna 'Data de Emissão' não está disponível na base.")
