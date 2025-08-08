import streamlit as st
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao, set_page_title
aplicar_estilo_padrao()
set_page_title("Arquivo")
st.markdown("""
    <style>
    .topbar {position: fixed;top: 0;left: 0;width: 100vw;height: 64px;background: #263a53;display: flex;align-items: center;z-index: 100;box-shadow: 0 2px 8px #0002;}
    .topbar-logo {height: 40px;margin-left: 32px;margin-right: 24px;}
    .topbar-menu {display: flex;gap: 32px;}
    .topbar-menu a {color: #fff;font-size: 1.1rem;text-decoration: none;font-weight: 500;padding: 8px 0;transition: color 0.2s;}
    .topbar-menu a:hover {color: #42a5f5;}
    .topbar-account {margin-left: auto;margin-right: 32px;background: #42a5f5;color: #fff;border-radius: 8px;padding: 8px 18px;font-weight: 600;font-size: 1rem;box-shadow: 0 2px 8px #0002;}
    .stApp {padding-top: 72px !important;}
    </style>
    <div class="topbar">
        <img src="https://raw.githubusercontent.com/Notalize/brand-assets/main/logo-notalize.png" class="topbar-logo" alt="Logo" />
        <div class="topbar-menu">
            <a href="#">Cadastros</a>
            <a href="#">Administrativo</a>
            <a href="#">Busca de Documentos</a>
            <a href="#">NF-e | NFC-e | CF-e</a>
            <a href="#">CT-e</a>
            <a href="#">NFC-e</a>
            <a href="#">MDF-e</a>
            <a href="#">Relatórios</a>
        </div>
        <div class="topbar-account">Minha Conta</div>
    </div>
""", unsafe_allow_html=True)

import streamlit as st

from pathlib import Path
from datetime import datetime
import mimetypes
import gspread
import re
from funcoes_compartilhadas.drive_utils import upload_para_drive

ID_PASTA_ARQUIVOS = "1V7qAWb8MpoX6fV9LVB0Cq8ovlogEanmt"

# Lista de bancos conhecidos para identificar o nome mesmo que contenha outras palavras
BANCOS_CONHECIDOS = [
    "SICREDI", "SICOOB", "BRADESCO", "BANCO DO BRASIL", "CAIXA", "ITAU",
    "SANTANDER", "INTER", "NUBANK", "BTG", "C6", "XP"
]

def get_cnpjs_planilha():
    import json
    from google.oauth2.service_account import Credentials
    credenciais_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credenciais = Credentials.from_service_account_info(credenciais_dict)
    gc = gspread.authorize(credenciais)
    sh = gc.open_by_key('1bJOkcArR6DZK_7SYwiAiFZEPE9t8HQ1d6ZmDoigCPJw')
    ws = sh.worksheet('Empresas')
    cnpjs = ws.col_values(2)[1:]
    razoes = ws.col_values(3)[1:]
    return {cnpj: razao for cnpj, razao in zip(cnpjs, razoes)}

def extrair_info(nome_arquivo):
    nome_limpo = nome_arquivo.lower()
    cnpj_match = re.search(r"\d{14}", nome_limpo)
    data_match = re.search(r"(\d{2})_(\d{4})", nome_limpo)

    cnpj = cnpj_match.group() if cnpj_match else "geral"
    mes = data_match.group(1) if data_match else "00"
    ano = data_match.group(2) if data_match else "0000"

    banco = "desconhecido"
    for b in BANCOS_CONHECIDOS:
        if b.lower() in nome_limpo:
            banco = b.upper()
            break

    return cnpj, banco, ano, mes

def exibir():
    st.title("📁 Arquivos Contábil")


    st.subheader("📤 Enviar arquivos")

    tipos_aceitos = [
        "pdf", "jpg", "jpeg", "png",
        "xls", "xlsx",
        "doc", "docx",
        "ppt", "pptx",
        "txt"
    ]

    arquivos = st.file_uploader(
        "Envie arquivos (PDF, Excel, Word, Imagem, TXT...)", 
        type=tipos_aceitos, accept_multiple_files=True
    )

    if arquivos:
        usuario = st.session_state.get("usuario", {})
        nome_usuario = usuario.get("Usuario", "Desconhecido").replace(" ", "_")
        nome_empresa = usuario.get("Empresa", "").replace(" ", "_")
        for arq in arquivos:
            nome = arq.name
            cnpj, banco, ano, mes = extrair_info(nome)
            # Monta nome: nome_original_usuario_empresa.ext
            nome_base, ext = nome.rsplit('.', 1)
            nome_final = f"{nome_base}_{nome_usuario}_{nome_empresa}.{ext}"
            # Opcional: pode incluir mais informações no nome_final se desejar
            # Salva temporariamente
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.'+ext) as tmp:
                tmp.write(arq.read())
                temp_path = tmp.name
            # Upload para o Google Drive
            upload_para_drive(temp_path, nome_final, ID_PASTA_ARQUIVOS)
            import os
            os.remove(temp_path)
        st.success(f"{len(arquivos)} arquivo(s) enviado(s) com sucesso!")

    st.subheader("📂 Arquivos Armazenados")
    cnpjs_empresas = get_cnpjs_planilha()
    arquivos_listados = []

    from pathlib import Path
    BASE_DIR = Path("n:/Comum/carlos.santos/2. Operacional/2.2. Em Andamento/Projeto xml/APP_ALENCAR/arquivo")
    for cnpj_dir in BASE_DIR.iterdir():
        if not cnpj_dir.is_dir():
            continue

        if st.session_state.get("usuario", {}).get("Tipo") == "Cliente":
            if cnpj_dir.name != st.session_state["usuario"]["Empresa_ID"]:
                continue

        razao_social = cnpjs_empresas.get(cnpj_dir.name, cnpj_dir.name)

        for banco_dir in cnpj_dir.iterdir():
            for ano_dir in banco_dir.iterdir():
                for mes_dir in ano_dir.iterdir():
                    for arquivo in mes_dir.iterdir():
                        tipo_mime, _ = mimetypes.guess_type(arquivo)
                        arquivos_listados.append({
                            "Empresa": razao_social,
                            "CNPJ": cnpj_dir.name,
                            "Banco": banco_dir.name,
                            "Ano": ano_dir.name,
                            "Mês": mes_dir.name,
                            "Nome": arquivo.name,
                            "Caminho": str(arquivo),
                            "Tipo": tipo_mime or "desconhecido"
                        })

    empresas = sorted(set(a["Empresa"] for a in arquivos_listados))
    filtro = st.selectbox("Filtrar por empresa", ["Todas"] + empresas)

    if filtro != "Todas":
        arquivos_listados = [a for a in arquivos_listados if a["Empresa"] == filtro]

    for arq in arquivos_listados:
        with st.expander(f'{arq["Nome"]} — {arq["Banco"]} {arq["Mês"]}/{arq["Ano"]} — {arq["Empresa"]}'):
            st.write(f"📌 Empresa: {arq["Empresa"]}")
            st.write(f"🏦 Banco: {arq["Banco"]}")
            st.write(f"📅 Data: {arq["Mês"]}/{arq["Ano"]}")
            with open(arq["Caminho"], "rb") as f:
                st.download_button("⬇️ Baixar", f, file_name=arq["Nome"])
