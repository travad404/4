import pandas as pd
import streamlit as st
import plotly.express as px

# Função para carregar e validar os dados
@st.cache_data
def carregar_tabelas(tabela1_path, tabela2_path):
    gravimetria_data = pd.read_excel(tabela1_path)
    resumo_fluxo_data = pd.read_excel(tabela2_path)

    # Limpando espaços nos nomes das colunas
    gravimetria_data.columns = gravimetria_data.columns.str.strip()
    resumo_fluxo_data.columns = resumo_fluxo_data.columns.str.strip()

    return gravimetria_data, resumo_fluxo_data


# Percentuais para entulhos
PERCENTUAIS_ENTULHO = {
    "Concreto": 0.0677, "Argamassa": 0.1065, "Tijolo": 0.078, "Madeira": 0.0067,
    "Papel": 0.0023, "Plástico": 0.0034, "Metal": 0.0029, "Material agregado": 0.0484,
    "Terra bruta": 0.0931, "Pedra": 0.00192, "Caliça Retida": 0.3492,
    "Caliça Peneirada": 0.2, "Cerâmica": 0.0161, "Material orgânico e galhos": 0.0087,
    "Outros": 0
}


# Função para calcular o fluxo ajustado
def calcular_fluxo_ajustado(gravimetria_data, resumo_fluxo_data):
    fluxo_ajustado = []

    for _, row in resumo_fluxo_data.iterrows():
        unidade = row["Tipo de unidade, segundo o município informante"]
        gravimetricos = gravimetria_data[gravimetria_data["Tipo de unidade, segundo o município informante"] == unidade]

        if gravimetricos.empty:
            continue

        gravimetricos = gravimetricos.iloc[0]
        ajuste_residuos = {"UF": row["UF"], "Unidade": unidade}

        # Calcular resíduos
        if "Dom+Pub" in row:
            ajuste_residuos.update({
                "Papel/Papelão": row["Dom+Pub"] * gravimetricos.get("Papel/Papelão", 0),
                "Plásticos": row["Dom+Pub"] * gravimetricos.get("Plásticos", 0),
                "Vidros": row["Dom+Pub"] * gravimetricos.get("Vidros", 0),
                "Metais": row["Dom+Pub"] * gravimetricos.get("Metais", 0),
                "Orgânicos": row["Dom+Pub"] * gravimetricos.get("Orgânicos", 0),
            })

        if "Entulho" in row:
            for material, percentual in PERCENTUAIS_ENTULHO.items():
                ajuste_residuos[material] = row["Entulho"] * percentual

        fluxo_ajustado.append(ajuste_residuos)

    return pd.DataFrame(fluxo_ajustado)


# Aplicação Streamlit
st.set_page_config(page_title="Gestão de Resíduos", layout="wide")
st.title("📊 Gestão de Resíduos Sólidos Urbanos")
st.sidebar.header("Configurações de Entrada")

# Upload de arquivos
tabela1_path = st.sidebar.file_uploader("Carregue a Tabela 1 (Gravimetria por Tipo de Unidade)", type=["xlsx"])
tabela2_path = st.sidebar.file_uploader("Carregue a Tabela 2 (Resumo por Unidade e UF)", type=["xlsx"])

if tabela1_path and tabela2_path:
    try:
        gravimetria_data, resumo_fluxo_data = carregar_tabelas(tabela1_path, tabela2_path)
        st.success("✅ Tabelas carregadas com sucesso!")

        fluxo_ajustado = calcular_fluxo_ajustado(gravimetria_data, resumo_fluxo_data)

        # Exibição de métricas
        st.header("Resumo dos Indicadores")
        total_residuos = fluxo_ajustado.filter(regex="Papel|Plásticos|Vidros|Metais|Orgânicos|Concreto|Argamassa").sum().sum()
        st.metric("Total de Resíduos Processados (ton)", f"{total_residuos:,.2f}")

        # Exibição de tabela
        st.header("📈 Resultados Detalhados")
        st.dataframe(fluxo_ajustado)

        # Gráficos
        st.header("📊 Gráficos")
        if "Concreto" in fluxo_ajustado:
            grafico = fluxo_ajustado.groupby("UF")[["Concreto", "Argamassa", "Tijolo"]].sum().reset_index()
            fig = px.bar(grafico, x="UF", y=["Concreto", "Argamassa", "Tijolo"], title="Entulho por UF")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar os dados: {str(e)}")
