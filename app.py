import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

# Título
st.title("📊 Dashboard de Vendas")

# Carregar dados
df = pd.read_csv("dados_vendas.csv", parse_dates=["data"])

# Filtros
st.sidebar.header("Filtros")

produtos = st.sidebar.multiselect(
    "Produto",
    options=df["produto"].unique(),
    default=df["produto"].unique()
)

vendedores = st.sidebar.multiselect(
    "Vendedor",
    options=df["vendedor"].unique(),
    default=df["vendedor"].unique()
)

df_filtrado = df[
    (df["produto"].isin(produtos)) &
    (df["vendedor"].isin(vendedores))
]

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("💰 Faturamento", f"R$ {df_filtrado['valor'].sum():,.2f}")
col2.metric("📦 Qtde Vendas", df_filtrado.shape[0])
col3.metric("👥 Vendedores", df_filtrado["vendedor"].nunique())

# Tabela
st.subheader("Detalhamento")
st.dataframe(df_filtrado, use_container_width=True)

# Gráfico
st.subheader("Vendas por Produto")
st.bar_chart(
    df_filtrado.groupby("produto")["valor"].sum()
)
