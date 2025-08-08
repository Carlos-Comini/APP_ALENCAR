

import streamlit as st
import pandas as pd
import gspread
from pathlib import Path
import plotly.express as px

XML_BASE = Path(r"C:\Users\carlos.santos\Desktop\PROJETO_XML\xmls")
PLANILHA_CRED = r"C:\Users\carlos.santos\Desktop\PROJETO_XML\credenciais.json"
PLANILHA_KEY = "1bJOkcArR6DZK_7SYwiAiFZEPE9t8HQ1d6ZmDoigCPJw"

def carregar_empresas_e_usuarios():
	gc = gspread.service_account(filename=PLANILHA_CRED)
	sh = gc.open_by_key(PLANILHA_KEY)
	ws_emp = sh.worksheet('Empresas')
	ws_usu = sh.worksheet('Usuarios')

	# Empresas
	razoes = ws_emp.col_values(3)[1:]  # Razão Social na coluna 3
	cnpjs = ws_emp.col_values(2)[1:]   # CNPJ na coluna 2
	empresas = pd.DataFrame({"Empresa": cnpjs, "Razao_Social": razoes})

	# Usuários
	nomes = ws_usu.col_values(2)[1:]   # Nome na coluna 2
	tipos = ws_usu.col_values(4)[1:]   # Tipo na coluna 4
	empresas_usuarios = ws_usu.col_values(5)[1:]  # CNPJ da empresa na coluna 5
	usuarios = pd.DataFrame({"Usuario": nomes, "Tipo": tipos, "Empresa": empresas_usuarios})

	return empresas, usuarios

def contar_xmls_por_empresa(empresas):
	dados = []
	for _, row in empresas.iterrows():
		cnpj = row["Empresa"]
		razao = row["Razao_Social"]
		total_xml = 0
		empresa_path = XML_BASE / cnpj
		if empresa_path.exists():
			for data_dir in empresa_path.iterdir():
				if data_dir.is_dir():
					total_xml += len(list(data_dir.glob("*.xml")))
		dados.append({"Empresa": cnpj, "Razao_Social": razao, "Quantidade_XML": total_xml})
	return pd.DataFrame(dados)

def exibir():
	st.title("📊 Dashboard")

	# Carregar dados reais
	empresas, usuarios = carregar_empresas_e_usuarios()
	df_xml = contar_xmls_por_empresa(empresas)

	# Filtro de empresa
	empresas_opcoes = empresas["Razao_Social"].tolist()
	empresa_selecionada = st.selectbox("Selecionar empresa para visualizar informações", ["Todas"] + empresas_opcoes)

	if empresa_selecionada != "Todas":
		cnpj_selecionado = empresas[empresas["Razao_Social"] == empresa_selecionada]["Empresa"].values[0]
		df_xml_filtrado = df_xml[df_xml["Empresa"] == cnpj_selecionado]
		usuarios_filtrados = usuarios[usuarios["Empresa"] == cnpj_selecionado]
	else:
		df_xml_filtrado = df_xml
		usuarios_filtrados = usuarios

	# Métricas
	st.subheader("Métricas Gerais")
	st.metric("Total de XMLs processados", int(df_xml_filtrado["Quantidade_XML"].sum()))
	st.metric("Empresas cadastradas", len(empresas))
	st.metric("Usuários Cliente", len(usuarios_filtrados[usuarios_filtrados["Tipo"].str.lower() == "cliente"]))
	st.metric("Usuários Escritório", len(usuarios_filtrados[usuarios_filtrados["Tipo"].str.lower() == "escritorio"]))

	# Gráfico: Empresas com mais XMLs
	st.subheader("Empresas com mais XMLs")
	if not df_xml_filtrado.empty and df_xml_filtrado["Quantidade_XML"].sum() > 0:
		fig = px.pie(
			df_xml_filtrado,
			names="Razao_Social",
			values="Quantidade_XML",
			title="Distribuição de XMLs por Empresa"
		)
		st.plotly_chart(fig, use_container_width=True)
	else:
		st.info("Nenhum XML encontrado para o filtro selecionado.")

	# Tabela de usuários
	st.subheader("Usuários cadastrados")
	st.dataframe(usuarios_filtrados[["Usuario", "Tipo", "Empresa"]])

