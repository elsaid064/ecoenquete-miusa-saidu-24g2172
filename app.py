import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3

st.set_page_config(page_title="EcoEnquête - MUSA SAIDU 24G2172", page_icon="🌍", layout="wide")

st.title("🌍 EcoEnquête")
st.subheader("Collecte et Analyse Descriptive des Habitudes Éco-Responsables")
st.caption("TP INF232 EC2 • MUSA SAIDU • Matricule : 24G2172")

# Base de données SQLite (persistante sur la plupart des plateformes)
conn = sqlite3.connect('ecoenquete.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS reponses 
             (date TEXT, age INTEGER, genre TEXT, ville TEXT, transport TEXT, 
              energie INTEGER, eau INTEGER, recyclage TEXT, alimentation TEXT, 
              achats TEXT, eco_index REAL)''')
conn.commit()

# Formulaire
with st.form("form"):
    st.subheader("📋 Participez à l'enquête")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Âge", 15, 80, 25)
        genre = st.selectbox("Genre", ["Homme", "Femme", "Autre"])
        ville = st.text_input("Ville/Région", "Yaoundé")
    with col2:
        transport = st.selectbox("Transport principal", ["Voiture personnelle", "Moto", "Bus/Taxi", "Vélo ou Marche", "Autre"])
        energie = st.slider("Énergie estimée (kWh/mois)", 50, 600, 180)
        eau = st.slider("Eau estimée (litres/mois)", 1000, 30000, 8000)
    
    recyclage = st.selectbox("Recyclage", ["Jamais", "Parfois", "Souvent", "Toujours"])
    alimentation = st.selectbox("Alimentation", ["Viande lourde", "Équilibrée", "Végétarien", "Végan"])
    achats = st.selectbox("Achats éco-responsables", ["Rarement", "Parfois", "Souvent", "Toujours"])
    
    if st.form_submit_button("Soumettre"):
        # Calcul Éco-Index (robuste et explicable)
        score = 0
        if transport in ["Vélo ou Marche", "Bus/Taxi"]: score += 25
        if recyclage in ["Souvent", "Toujours"]: score += 20
        if alimentation in ["Végétarien", "Végan"]: score += 20
        if achats in ["Souvent", "Toujours"]: score += 20
        if energie < 250 and eau < 10000: score += 15
        eco_index = min(100, max(30, score))
        
        c.execute("INSERT INTO reponses VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (datetime.now().strftime("%Y-%m-%d %H:%M"), age, genre, ville, transport,
                   energie, eau, recyclage, alimentation, achats, eco_index))
        conn.commit()
        
        st.success(f"✅ Merci ! Votre **Éco-Index** est de **{eco_index:.1f}/100**")
        if eco_index >= 75:
            st.balloons()

# Dashboard d'analyse descriptive
df = pd.read_sql_query("SELECT * FROM reponses", conn)

if not df.empty:
    st.subheader("📊 Analyse Descriptive")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de réponses", len(df))
    col2.metric("Éco-Index moyen", f"{df['eco_index'].mean():.1f}/100")
    col3.metric("Âge moyen", f"{df['age'].mean():.1f} ans")
    
    tab1, tab2 = st.tabs(["Visualisations", "Données brutes"])
    
    with tab1:
        fig1 = px.histogram(df, x="eco_index", title="Distribution de l'Éco-Index")
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.pie(df, names="transport", title="Modes de transport")
        st.plotly_chart(fig2, use_container_width=True)
        
        fig3 = px.bar(df.groupby("ville")["eco_index"].mean().reset_index(), 
                      x="ville", y="eco_index", title="Éco-Index moyen par ville")
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab2:
        st.dataframe(df)
        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Télécharger CSV", csv, "ecoenquete_data.csv", "text/csv")
else:
    st.info("Remplissez le formulaire plusieurs fois pour générer des données et voir les analyses.")

conn.close()
st.caption("Application robuste, efficace et créative (secteur Environnement) - Python + Streamlit")
