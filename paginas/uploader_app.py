import streamlit as st
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao, set_page_title
aplicar_estilo_padrao()
set_page_title("Uploader de XMLs")
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
# uploader_app.py
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import sys
from datetime import datetime

XML_BASE = Path(r"C:\Users\carlos.santos\Desktop\PROJETO_XML\xmls")

if getattr(sys, 'frozen', False):
    # Executando como .exe
    PASTA_CLIENTE = Path(sys.executable).parent
else:
    # Executando como script Python
    PASTA_CLIENTE = Path(__file__).parent

def extrair_cnpj(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        dest = root.find(".//nfe:dest", ns)
        emit = root.find(".//nfe:emit", ns)
        cnpj_dest = dest.find("nfe:CNPJ", ns).text if dest is not None else None
        cnpj_emit = emit.find("nfe:CNPJ", ns).text if emit is not None else None
        return cnpj_dest or cnpj_emit or "geral"
    except:
        return "geral"

def enviar_xml():
    arquivos = list(PASTA_CLIENTE.glob("*.xml"))
    if not arquivos:
        messagebox.showinfo("Aviso", "Nenhum arquivo XML encontrado na pasta do cliente.")
        return 0
    hoje = datetime.now().strftime("%Y_%m_%d")
    for arquivo in arquivos:
        cnpj = extrair_cnpj(arquivo)
        pasta_destino = XML_BASE / cnpj / hoje
        pasta_destino.mkdir(parents=True, exist_ok=True)
        novo_nome = f"exe_{arquivo.name}"
        destino = pasta_destino / novo_nome
        shutil.copy2(arquivo, destino)
    messagebox.showinfo("Sucesso", f"{len(arquivos)} arquivo(s) enviado(s) para a contabilidade!")
    return len(arquivos)

if __name__ == "__main__":
    enviar_xml()

xml_files = list(XML_BASE.glob("**/*.xml"))

root = tk.Tk()
root.title("Uploader de XML")
root.geometry("300x150")

btn = tk.Button(root, text="Enviar XMLs da pasta do cliente", command=enviar_xml, height=2, width=30)
btn.pack(pady=40)

root.mainloop()