import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import json
import hashlib
import os

# ID da planilha compartilhada
PLANILHA_ID = "1bJOkcArR6DZK_7SYwiAiFZEPE9t8HQ1d6ZmDoigCPJw"
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

XML_BASE = os.path.join(os.getcwd(), "xmls")


def conectar_google_sheets():
    credenciais_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credenciais = Credentials.from_service_account_info(credenciais_dict, scopes=SCOPES)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(PLANILHA_ID)
    return planilha


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def autenticar_usuario(email, senha):
    planilha = conectar_google_sheets()
    aba = planilha.worksheet("Usuarios")
    dados = aba.get_all_records()
    senha_hash = hash_senha(senha)
    for usuario in dados:
        if usuario["Email"].lower() == email.lower() and usuario["Senha"] == senha_hash:
            return True, usuario.get("Tipo", ""), usuario
    return False, None, None


def salvar_empresa(nome_empresa, cnpj, razao_social):
    planilha = conectar_google_sheets()
    aba = planilha.worksheet("Empresas")
    nova_linha = [nome_empresa, cnpj, razao_social]
    aba.append_row(nova_linha)


def salvar_usuario(nome, email, senha, tipo, empresa=None, permissoes=None):
    planilha = conectar_google_sheets()
    aba = planilha.worksheet("Usuarios")
    senha_hash = hash_senha(senha)

    # Ordem da planilha: ID | Nome | Email | Senha | Tipo | Empresa_ID | Ver_Arquivos | Ver_XML | Permitir_Cadastros
    linha = ["", nome, email, senha_hash, tipo]

    if tipo == "Cliente":
        linha.append(empresa if empresa else "")
        linha.extend([
            "Sim" if permissoes and permissoes.get("ver_arquivo") else "Não",
            "Sim" if permissoes and permissoes.get("ver_xml") else "Não",
            "Não"  # 'Permitir_Cadastros' sempre presente mesmo para Cliente
        ])

    elif tipo == "Escritorio":
        linha.append("")  # Empresa_ID vazio para Escritório
        linha.extend([
            "Sim" if permissoes and permissoes.get("ver_arquivo") else "Não",
            "Sim" if permissoes and permissoes.get("ver_xml") else "Não",
            "Sim" if permissoes and permissoes.get("cadastrar") else "Não"
        ])

    else:
        linha.extend(["", "Não", "Não", "Não"])  # fallback de segurança

    aba.append_row(linha)


def listar_empresas():
    planilha = conectar_google_sheets()
    aba = planilha.worksheet("Empresas")
    return aba.get_all_records()


def listar_usuarios():
    planilha = conectar_google_sheets()
    aba = planilha.worksheet("Usuarios")
    return aba.get_all_records()


def listar_cnpjs_xml():
    if not os.path.exists(XML_BASE):
        return []
    return sorted([d for d in os.listdir(XML_BASE) if os.path.isdir(os.path.join(XML_BASE, d))])
