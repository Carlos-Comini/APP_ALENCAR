
import gspread
import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from funcoes_compartilhadas.drive_utils import upload_para_drive

# IDs das pastas no Google Drive
ID_PASTA_XML = "1QrgORE3rm2d_CusD7cqT12wN5wQoeurj"

def get_cnpjs_planilha():
    import json
    from google.oauth2.service_account import Credentials
    credenciais_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credenciais = Credentials.from_service_account_info(credenciais_dict)
    gc = gspread.authorize(credenciais)
    sh = gc.open_by_key('1bJOkcArR6DZK_7SYwiAiFZEPE9t8HQ1d6ZmDoigCPJw')
    ws = sh.worksheet('Empresas')
    cnpjs = ws.col_values(2)[1:]      # Segunda coluna: CNPJ
    razoes = ws.col_values(3)[1:]     # Terceira coluna: Razão Social
    return {cnpj: razao for cnpj, razao in zip(cnpjs, razoes)}

def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

        ide = root.find(".//nfe:ide", ns)
        emit = root.find(".//nfe:emit", ns)
        dest = root.find(".//nfe:dest", ns)
        total = root.find(".//nfe:ICMSTot", ns)

        numero = ide.find("nfe:nNF", ns).text if ide is not None else "—"
        data_emissao = ide.find("nfe:dhEmi", ns).text[:10] if ide is not None else "—"
        cnpj_emit = emit.find("nfe:CNPJ", ns).text if emit is not None else "—"
        cnpj_dest = dest.find("nfe:CNPJ", ns).text if dest is not None else "—"
        valor = total.find("nfe:vNF", ns).text if total is not None else "—"

        return {
            "Número": numero,
            "Data": data_emissao,
            "CNPJ_Emitente": cnpj_emit,
            "CNPJ_Destinatario": cnpj_dest,
            "Valor": valor
        }
    except:
        return {"Número": "Erro", "Data": "Erro", "CNPJ_Emitente": "Erro", "CNPJ_Destinatario": "Erro", "Valor": "Erro"}

def exibir():
    st.title("📂 Gestão de Arquivos XML")
    st.subheader("📤 Enviar XML manualmente")
    uploaded = st.file_uploader("Escolha um ou mais arquivos XML", type=["xml"], accept_multiple_files=True)

    if uploaded:
        cnpjs_empresas = get_cnpjs_planilha()
        for file in uploaded:
            # Salva temporariamente o arquivo recebido
            temp_path = f"temp_{file.name}"
            with open(temp_path, "wb") as f:
                f.write(file.read())
            info = parse_xml(temp_path)
            if info["CNPJ_Destinatario"] in cnpjs_empresas:
                cnpj = info["CNPJ_Destinatario"]
            elif info["CNPJ_Emitente"] in cnpjs_empresas:
                cnpj = info["CNPJ_Emitente"]
            else:
                cnpj = "geral"
            hoje = datetime.today().strftime("%Y_%m_%d")
            # Nome do arquivo no Drive: cnpj/hoje/nome.xml
            nome_arquivo_drive = f"{cnpj}/{hoje}/{file.name}"
            upload_para_drive(temp_path, nome_arquivo_drive, ID_PASTA_XML)
            # Remove arquivo temporário
            import os
            os.remove(temp_path)
        st.success(f"{len(uploaded)} arquivo(s) salvo(s) com sucesso!")

    st.subheader("📁 Arquivos Recebidos")
    cnpjs_empresas = get_cnpjs_planilha()
    from funcoes_compartilhadas.drive_utils import listar_arquivos_drive, baixar_arquivo_drive, ID_PASTA_XML
    dados = []
    arquivos_drive = listar_arquivos_drive(ID_PASTA_XML)
    for file in arquivos_drive:
        nome = file['title']
        if not nome.endswith('.xml'):
            continue
        # Extrair CNPJ e data do caminho (ex: cnpj/data/arquivo.xml)
        partes = nome.split('/')
        if len(partes) >= 3:
            cnpj, data, nome_arquivo = partes[-3], partes[-2], partes[-1]
        else:
            cnpj, data, nome_arquivo = 'geral', '', nome
        if st.session_state.get("usuario", {}).get("Tipo") == "Cliente":
            if cnpj != st.session_state["usuario"].get("Empresa_ID", ""):
                continue
        razao_social = cnpjs_empresas.get(cnpj, cnpj)
        # Baixar conteúdo do XML para parsear informações
        conteudo_xml = baixar_arquivo_drive(file['id'])
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
            tmp.write(conteudo_xml.encode('utf-8'))
            tmp_path = tmp.name
        info = parse_xml(tmp_path)
        info["Empresa"] = razao_social
        info["Arquivo"] = nome_arquivo
        info["Caminho"] = file['id']
        if info["CNPJ_Destinatario"] in cnpjs_empresas:
            info["Tipo"] = "ENTRADA"
            info["CNPJ"] = info["CNPJ_Destinatario"]
            info["Razao_Social"] = cnpjs_empresas.get(info["CNPJ_Destinatario"], "—")
        elif info["CNPJ_Emitente"] in cnpjs_empresas:
            info["Tipo"] = "SAÍDA"
            info["CNPJ"] = info["CNPJ_Emitente"]
            info["Razao_Social"] = cnpjs_empresas.get(info["CNPJ_Emitente"], "—")
        else:
            info["Tipo"] = "OUTRO"
            info["CNPJ"] = "-"
            info["Razao_Social"] = "—"
        dados.append(info)
    empresas = sorted(set(d["Empresa"] for d in dados))
    filtro_empresa = st.selectbox("Empresa", ["Todas"] + empresas)
    if filtro_empresa != "Todas":
        dados = [d for d in dados if d["Empresa"] == filtro_empresa]
    for d in dados:
        with st.expander(f'📄 {d["Arquivo"]} — {d["Data"]} — R$ {d["Valor"]} — {d["Tipo"]}'):
            st.write(f"**Número:** {d['Número']}")
            st.write(f"**CNPJ ({d['Tipo']}):** {d['CNPJ']}")
            st.write(f"**Razão Social:** {d['Razao_Social']}")
            st.write(f"**Empresa:** {d['Empresa']}")
            conteudo_xml = baixar_arquivo_drive(d["Caminho"])
            st.download_button("⬇️ Baixar XML", data=conteudo_xml, file_name=d["Arquivo"])