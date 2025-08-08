# funcoes_compartilhadas/estilos.py

import streamlit as st
from math import ceil
import os

# Tamanho base das fontes
FONTE_BASE = 22
PHI = 1.618

# Dicionário de tamanhos derivados
FONTES = {
    "poppins":        "'Poppins', sans-serif",
    "material_icons": "'Material Icons'",
    "h1":             f"{FONTE_BASE}px",
    "h2_h3":          f"{FONTE_BASE/PHI:.0f}px",
    "p":              f"{FONTE_BASE/PHI:.0f}px",
    "li":             f"{ceil(FONTE_BASE/PHI*0.8):.0f}px",
    "menu":           f"{ceil(FONTE_BASE/PHI*0.9):.0f}px",
}

# ──────────────────────────────────────────────────────────────────────────────
def aplicar_estilo_padrao() -> None:
    """Aplica estilo visual global ao app."""
    # Tipografia + layout base
    st.markdown(
f"""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

<style>
html, body, .stApp {{
    font-family: {FONTES['poppins']} !important;
    background-color: #1f2c3e !important;
}}

.material-icons {{
    font-family: {FONTES['material_icons']} !important;
}}

h1 {{
    font-size: {FONTES['h1']} !important;
    line-height: 1.2;
    color: white;
    margin-top: 0;
}}
h2, h3 {{
    font-size: {FONTES['h2_h3']} !important;
    line-height: 1.3;
    color: white;
}}
p, li {{
    font-size: {FONTES['p']} !important;
    color: white;
}}

[data-testid="stSidebar"] * {{
    font-size: {FONTES['menu']} !important;
}}

.block-container {{
    padding-top: 0;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}}

footer {{ display: none !important; }}

.stButton > button {{
    background-color: #428eff !important;
    color: white !important;
    padding: 10px 20px;
    font-size: 16px;
    border: none;
    border-radius: 5px;
    font-weight: bold;
    cursor: pointer;
}}
</style>
""",
        unsafe_allow_html=True,
    )

    # Carrega CSS externo, se existir
    caminho_css = "streamlit/styles.css"
    if os.path.exists(caminho_css):
        with open(caminho_css, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
def set_page_title(texto: str) -> None:
    st.markdown(
        f"<div id='page-title-wrapper'><h1>{texto}</h1></div>",
        unsafe_allow_html=True,
    )

def clear_caches() -> None:
    st.cache_data.clear()
    st.cache_resource.clear()
