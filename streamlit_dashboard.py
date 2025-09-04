import streamlit as st
import pandas as pd
import plotly.express as px
import gdown

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter password:", type = "password")

    if password == st.secrets["credentials"]["password"]:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.error("Access denied ❌")
        st.stop()

if st.session_state.authenticated:
    st.success("Welcome to your dashboard!")
    
DATA_URLS = st.secrets["google_drive"]

@st.cache_data
def load_data(species):
    url = DATA_URLS[species]
    output = f"{species}.xlsx"
    gdown.download(url, output, quiet=True)
    df = pd.read_excel(output)
    df["Data"] = pd.to_datetime(df["Data"])
    df["Settimana"] = df["Data"].dt.to_period("W").apply(lambda r: r.start_time)
    return df

st.sidebar.header("Filtri")

species = st.sidebar.radio("Seleziona la specie:", ["Raspberry", "Blackberry", "Strawberry"])

if st.sidebar.button("🔄 Ricarica dati per " + species):
    st.cache_data.clear()
    
df = load_data(species)

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
    cumulati_varieta["% Scarto"] = (cumulati_varieta["Scarto"] / cumulati_varieta["Produzione"] * 100).round(2)
    fig3 = px.bar(cumulati_varieta, x="Varietà", y=["Produzione", "Scarto"], barmode="group")

    for i, trace in enumerate(fig3.data):
        if trace.name == "Scarto":
            trace.text = cumulati_varieta["% Scarto"].apply(lambda x: f"{x}%")
            trace.textposition = "outside"
    st.plotly_chart(fig3, use_container_width=True, key = "production_vs_waste")

with tab4:  
    st.header("Pezzatura Media")
    media_pezzatura = df.groupby("Varietà")["Pezzatura"].mean().reset_index()
    fig4 = px.bar(pezzatura, x="Settimana", y="Pezzatura", barmode="group")
    st.plotly_chart(fig4, use_container_width=True, key="Pezzatura") 

