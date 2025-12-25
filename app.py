import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ---------------- CONFIGURAÇÃO ----------------
st.set_page_config(
    page_title="Dashboard de Vendas",
    layout="wide"
)

# ---------------- TÍTULO ----------------
st.title("📊 Dashboard de Vendas com Previsão")

# ---------------- CARREGAR DADOS ----------------
df = pd.read_csv("dados_vendas.csv", parse_dates=["data"])

# ---------------- FILTROS ----------------
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

# ---------------- KPIs ----------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "💰 Faturamento Total",
    f"R$ {df_filtrado['valor'].sum():,.2f}"
)

col2.metric(
    "📦 Qtde Vendas",
    df_filtrado.shape[0]
)

col3.metric(
    "👥 Vendedores",
    df_filtrado["vendedor"].nunique()
)

# ---------------- TABELA ----------------
st.subheader("📋 Detalhamento das Vendas")
st.dataframe(df_filtrado, width="stretch")

# ---------------- VENDAS POR PRODUTO ----------------
st.subheader("📊 Vendas por Produto")
vendas_produto = df_filtrado.groupby("produto")["valor"].sum()
st.bar_chart(vendas_produto)

# ===================================================
# 🔮 PREVISÃO DE VENDAS
# ===================================================

st.subheader("🔮 Previsão de Vendas")

# -------- Agregar vendas por data --------
df_diario = (
    df_filtrado
    .groupby("data", as_index=False)["valor"]
    .sum()
    .sort_values("data")
)

# Se não tiver dados suficientes
if df_diario.shape[0] < 2:
    st.warning("⚠️ Dados insuficientes para gerar previsão.")
    st.stop()

# -------- Criar variável numérica --------
df_diario["dia_num"] = np.arange(len(df_diario))

X = df_diario[["dia_num"]]
y = df_diario["valor"]

# -------- Treinar modelo --------
modelo = LinearRegression()
modelo.fit(X, y)

# -------- Horizonte de previsão --------
dias_previsao = st.slider(
    "Quantos dias deseja prever?",
    min_value=1,
    max_value=30,
    value=7
)

# -------- Gerar previsão --------
ultimo_dia = df_diario["dia_num"].max()

dias_futuros = np.arange(
    ultimo_dia + 1,
    ultimo_dia + 1 + dias_previsao
).reshape(-1, 1)

previsao = modelo.predict(dias_futuros)

datas_futuras = pd.date_range(
    start=df_diario["data"].max() + pd.Timedelta(days=1),
    periods=dias_previsao
)

df_previsao = pd.DataFrame({
    "data": datas_futuras,
    "valor_previsto": previsao
})

# ---------------- REAL x PREVISTO ----------------
st.subheader("📈 Real x Previsto")

df_real = df_diario[["data", "valor"]].set_index("data")
df_prev = df_previsao.set_index("data")

st.line_chart(
    pd.concat([df_real, df_prev], axis=1)
)

# ---------------- KPI PREVISÃO ----------------
st.metric(
    "💰 Total Previsto",
    f"R$ {df_previsao['valor_previsto'].sum():,.2f}"
)

# ===================================================
# 🔮 PREVISÃO POR PRODUTO
# ===================================================

st.subheader("🔮 Previsão por Produto")

produto_prev = st.selectbox(
    "Selecione um produto para prever",
    df_filtrado["produto"].unique()
)

df_prod = df_filtrado[df_filtrado["produto"] == produto_prev]

df_prod_diario = (
    df_prod
    .groupby("data", as_index=False)["valor"]
    .sum()
    .sort_values("data")
)

if df_prod_diario.shape[0] >= 2:
    df_prod_diario["dia_num"] = np.arange(len(df_prod_diario))

    Xp = df_prod_diario[["dia_num"]]
    yp = df_prod_diario["valor"]

    modelo_p = LinearRegression()
    modelo_p.fit(Xp, yp)

    ultimo_dia_p = df_prod_diario["dia_num"].max()

    dias_futuros_p = np.arange(
        ultimo_dia_p + 1,
        ultimo_dia_p + 1 + dias_previsao
    ).reshape(-1, 1)

    previsao_p = modelo_p.predict(dias_futuros_p)

    datas_futuras_p = pd.date_range(
        start=df_prod_diario["data"].max() + pd.Timedelta(days=1),
        periods=dias_previsao
    )

    df_prev_prod = pd.DataFrame({
        "data": datas_futuras_p,
        "valor_previsto": previsao_p
    })

    st.line_chart(
        pd.concat([
            df_prod_diario.set_index("data")[["valor"]],
            df_prev_prod.set_index("data")
        ])
    )

else:
    st.warning("⚠️ Dados insuficientes para previsão deste produto.")

