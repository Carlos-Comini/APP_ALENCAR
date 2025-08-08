import streamlit as st
import requests
from funcoes_compartilhadas.conversa_banco import salvar_empresa
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao, set_page_title

def buscar_razao_social(cnpj):
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("razao_social", "")
    return ""

def exibir():
    aplicar_estilo_padrao()
    set_page_title("Cadastro de Empresas")
    st.header("Cadastro de Empresas Clientes")

    with st.form("form_empresa"):
        cnpj = st.text_input("CNPJ")
        buscar = st.form_submit_button("Buscar Razão Social")

        if buscar:
            if cnpj:
                razao = buscar_razao_social(cnpj)
                if razao:
                    st.success(f"Razão Social encontrada: {razao}")
                    st.session_state["razao_social"] = razao
                else:
                    st.error("Razão Social não encontrada.")

        razao_social = st.text_input("Razão Social", value=st.session_state.get("razao_social", ""))
        salvar = st.form_submit_button("Salvar Empresa")

        if salvar:
            if cnpj and razao_social:
                salvar_empresa("Empresa", cnpj, razao_social)
                st.success("Empresa cadastrada com sucesso.")
                st.session_state["razao_social"] = ""
            else:
                st.error("Preencha todos os campos.")
