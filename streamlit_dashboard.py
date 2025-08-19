import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df["Data"] = pd.to_datetime(df["Data"])
    df["Settimana"] = df["Data"].dt.to_period("W").apply(lambda r: r.start_time)
    return df

st.sidebar.header("Filtri")

species = st.sidebar.radio("Seleziona la specie:", ["Raspberry", "Blackberry"])

if species == "Raspberry":
    df = load_data("/Users/admin/Desktop/analisi_lampone_rifiorente.xlsx")
else:
    df = load_data("/Users/admin/Desktop/analisi_mora_unifera.xlsx")

varieta_list = df["Varietà"].unique()
varieta_sel = st.sidebar.multiselect("Seleziona le varietà", varieta_list)
df_filtered = df[df["Varietà"].isin(varieta_sel)]

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Produzione Settimanale", 
    "📊 Produzione Cumulata", 
    "🍓 Produzione vs Scarto", 
    "⚖️ Pezzatura Media"
])

with tab1:
    st.header("Produzione Settimanale")
    settimanale_var = df_filtered.groupby(["Varietà", "Settimana"])["Produzione"].sum().reset_index()
    fig1 = px.line(settimanale_var, x="Settimana", y="Produzione", color="Varietà", markers=True)
    st.plotly_chart(fig1, use_container_width=True, key = "weekly")

with tab2:
    st.header("Produzione Cumulata")
    settimanale_var = settimanale_var.sort_values("Settimana")
    settimanale_var["Produzione Cumulata"] = settimanale_var.groupby("Varietà")["Produzione"].cumsum()
    fig2 = px.line(settimanale_var, x="Settimana", y="Produzione Cumulata", color="Varietà", markers=True)
    st.plotly_chart(fig2, use_container_width=True, key = "cumulative")

with tab3:
    st.header("Produzione vs Scarto")
    cumulati_varieta = df_filtered.groupby("Varietà")[["Produzione", "Scarto"]].sum().reset_index() 
    fig3 = px.bar(cumulati_varieta, x="Varietà", y=["Produzione", "Scarto"], barmode="group")
    st.plotly_chart(fig3, use_container_width=True, key = "production_vs_waste")

with tab4:  
    st.header("Pezzatura Media")
    pezzatura = df_filtered.groupby(["Settimana", "Varietà"])["Pezzatura"].mean().reset_index()
    fig4 = px.line(pezzatura, x="Settimana", y="Pezzatura", color="Varietà", markers=True)
    st.plotly_chart(fig4, use_container_width=True, key="Pezzatura") 

