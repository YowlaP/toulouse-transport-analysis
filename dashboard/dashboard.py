"""
Dashboard Streamlit — Réseau de Transport Toulouse Métropole
Lancer avec : streamlit run dashboard/app.py
Les fichiers CSV doivent être dans data/ (ou adapter DATA_DIR)
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── Configuration ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Transport Toulouse — Dashboard",
    page_icon="🚌",
    layout="wide",
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ── Chargement des données ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df1 = pd.read_csv(os.path.join(DATA_DIR, "fichier1.csv"), sep=";")
    df2 = pd.read_csv(os.path.join(DATA_DIR, "fichier2.csv"), sep=";")
    df3 = pd.read_csv(os.path.join(DATA_DIR, "fichier3.csv"), sep=";")

    df3["code_commune"] = df3["code_commune"].astype("Int64")
    df3["code_type"]    = df3["code_type"].astype("Int64")

    df = (
        df3
        .merge(df1, left_on="code_commune", right_on="Code commune", how="left")
        .merge(df2, left_on="code_type",    right_on="Code type",    how="left")
    )
    return df1, df2, df3, df

df1, df2, df3, df = load_data()

# ── Sidebar — Filtres ──────────────────────────────────────────────────────────
st.sidebar.title("🔧 Filtres")

all_types = sorted(df["type"].dropna().unique().tolist())
selected_types = st.sidebar.multiselect(
    "Types de transport", all_types, default=all_types
)

all_communes = sorted(df["commune"].dropna().unique().tolist())
selected_communes = st.sidebar.multiselect(
    "Communes", all_communes, default=all_communes
)

df_filtered = df[
    df["type"].isin(selected_types) &
    df["commune"].isin(selected_communes)
] if selected_types and selected_communes else df

st.sidebar.markdown("---")
st.sidebar.caption(f"**{len(df_filtered):,}** arrêts sélectionnés sur {len(df):,}")

# ── Titre ──────────────────────────────────────────────────────────────────────
st.title("🚌 Réseau de Transport — Toulouse Métropole")
st.caption("Analyse exploratoire des arrêts et stations Tisséo | Open Data Toulouse Métropole")

# ── KPIs ───────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total arrêts", f"{len(df3):,}")
with col2:
    st.metric("Types de transport", df2.shape[0])
with col3:
    velo_count = df[df["type"] == "VeloToulouse"].shape[0]
    st.metric("Stations VéloToulouse", velo_count)
with col4:
    avg_born = df["nb_bornettes"].mean()
    st.metric("Moy. bornettes / station vélo", f"{avg_born:.1f}")

st.markdown("---")

# ── Ligne 1 : Répartition par type + par commune ───────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("📊 Répartition par type de transport")
    type_counts = df_filtered["type"].value_counts().head(12)
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = sns.color_palette("Blues_r", len(type_counts))
    bars = ax.barh(type_counts.index, type_counts.values, color=colors)
    ax.set_xlabel("Nombre d'arrêts")
    ax.invert_yaxis()
    for bar, val in zip(bars, type_counts.values):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_r:
    st.subheader("🏙️ Arrêts par commune (renseignée)")
    commune_counts = df_filtered["commune"].value_counts()
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    colors = sns.color_palette("Set2", len(commune_counts))
    bars = ax2.barh(commune_counts.index, commune_counts.values, color=colors)
    ax2.set_xlabel("Nombre d'arrêts")
    ax2.invert_yaxis()
    for bar, val in zip(bars, commune_counts.values):
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=8)
    ax2.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

# ── Ligne 2 : VéloToulouse ────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🚲 Analyse des stations VéloToulouse")

velo_df = df[df["type"] == "VeloToulouse"][["nom", "nb_bornettes", "commune"]].dropna(subset=["nb_bornettes"])

col_v1, col_v2 = st.columns([2, 1])

with col_v1:
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.hist(velo_df["nb_bornettes"], bins=15, color="#4C9BE8", edgecolor="white")
    ax3.axvline(velo_df["nb_bornettes"].mean(), color="tomato", linestyle="--",
                label=f"Moyenne : {velo_df['nb_bornettes'].mean():.1f}")
    ax3.axvline(velo_df["nb_bornettes"].median(), color="orange", linestyle="--",
                label=f"Médiane : {velo_df['nb_bornettes'].median():.0f}")
    ax3.set_xlabel("Nombre de bornettes")
    ax3.set_ylabel("Nombre de stations")
    ax3.set_title("Distribution du nombre de bornettes par station")
    ax3.legend()
    ax3.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

with col_v2:
    st.markdown("**Statistiques descriptives**")
    stats = velo_df["nb_bornettes"].describe().round(2)
    stats_df = pd.DataFrame({"Indicateur": stats.index, "Valeur": stats.values})
    st.dataframe(stats_df, hide_index=True, use_container_width=True)

# ── Ligne 3 : Qualité des données ────────────────────────────────────────────
st.markdown("---")
st.subheader("🔍 Qualité des données — Valeurs manquantes")

missing = df3.isnull().sum().sort_values(ascending=False)
missing_pct = (missing / len(df3) * 100).round(1)
missing_df = pd.DataFrame({
    "Colonne": missing.index,
    "Valeurs manquantes": missing.values,
    "% manquant": missing_pct.values,
}).query("`Valeurs manquantes` > 0")

col_q1, col_q2 = st.columns([3, 2])

with col_q1:
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    palette = ["#E74C3C" if p > 50 else "#F39C12" if p > 20 else "#2ECC71"
               for p in missing_df["% manquant"]]
    ax4.barh(missing_df["Colonne"], missing_df["% manquant"], color=palette)
    ax4.set_xlabel("% de valeurs manquantes")
    ax4.axvline(50, color="red", linestyle="--", alpha=0.5, label="Seuil 50%")
    ax4.legend(fontsize=8)
    ax4.invert_yaxis()
    ax4.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

with col_q2:
    st.dataframe(missing_df, hide_index=True, use_container_width=True)

# ── Ligne 4 : Top lignes ──────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🗺️ Top 15 des lignes les plus représentées")

top_lignes = df3["ligne"].value_counts().head(15)
fig5, ax5 = plt.subplots(figsize=(10, 4))
ax5.bar(top_lignes.index.astype(str), top_lignes.values,
        color=sns.color_palette("viridis", len(top_lignes)))
ax5.set_xlabel("Ligne")
ax5.set_ylabel("Nombre d'arrêts")
ax5.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
st.pyplot(fig5)
plt.close()

# ── Tableau de données filtrées ───────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Voir les données filtrées"):
    cols_show = ["nom", "ligne", "type", "commune", "nb_bornettes", "nb_places", "en_service"]
    st.dataframe(
        df_filtered[[c for c in cols_show if c in df_filtered.columns]].reset_index(drop=True),
        use_container_width=True,
        height=300,
    )

st.caption("Dashboard réalisé avec Streamlit — Projet Data Analyst étudiant")
