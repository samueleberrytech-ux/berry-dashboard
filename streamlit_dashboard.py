import streamlit as st
import pandas as pd
import plotly.express as px
import gdown

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter password:", type = "password")

    if password == "berry":
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.error("Access denied ❌")
        st.stop()

if st.session_state.authenticated:
    st.success("Welcome to your dashboard!")
    
DATA_URLS = {
    "Raspberry": "https://drive.google.com/uc?id=1Wmzya0x9D45bUpDU9KjA8sUL1zDJM5d9",
    "Blackberry": "https://drive.google.com/uc?id=1bv1Dca6kXH28-klpqPvLshBs32efQlBw"
}

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
species = st.sidebar.radio("Seleziona la specie:", ["Raspberry", "Blackberry"])

if st.sidebar.button("🔄 Reload Data"):
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
    fig3 = px.bar(cumulati_varieta, x="Varietà", y=["Produzione", "Scarto"], barmode="group")
    st.plotly_chart(fig3, use_container_width=True, key = "production_vs_waste")

with tab4:  
    st.header("Pezzatura Media")
    pezzatura = df_filtered.groupby(["Settimana", "Varietà"])["Pezzatura"].mean().reset_index()
    fig4 = px.line(pezzatura, x="Settimana", y="Pezzatura", color="Varietà", markers=True)
    st.plotly_chart(fig4, use_container_width=True, key="Pezzatura") 

