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

    # Validação básica das colunas esperadas
    colunas_esperadas_gravimetria = [
        "Tipo de unidade, segundo o município informante", "Papel/Papelão", "Plásticos", 
        "Vidros", "Metais", "Orgânicos", "Valor energético p/Incineração", 
        "Redução de peso seco com Podas", "Redução de peso Líquido com Podas"
    ]
    validar_tabelas(gravimetria_data, colunas_esperadas_gravimetria)

    colunas_esperadas_resumo = ["UF", "Tipo de unidade, segundo o município informante", "Dom+Pub", "Entulho", "Podas", "Saúde", "Outros"]
    validar_tabelas(resumo_fluxo_data, colunas_esperadas_resumo)

    return gravimetria_data, resumo_fluxo_data


def validar_tabelas(df, colunas_esperadas):
    colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
    if colunas_faltantes:
        raise ValueError(f"Colunas faltantes: {', '.join(colunas_faltantes)}")


# Percentuais para entulhos
PERCENTUAIS_ENTULHO = {
    "Concreto": 0.0677, "Argamassa": 0.1065, "Tijolo": 0.078, "Madeira": 0.0067,
    "Papel": 0.0023, "Plástico": 0.0034, "Metal": 0.0029, "Material agregado": 0.0484,
    "Terra bruta": 0.0931, "Pedra": 0.00192, "Caliça Retida": 0.3492,
    "Caliça Peneirada": 0.2, "Cerâmica": 0.0161, "Material orgânico e galhos": 0.0087,
    "Outros": 0
}


# Funções auxiliares para cálculos
def calcular_dom_pub(row, gravimetricos):
    return {
        "Papel/Papelão": row * gravimetricos.get("Papel/Papelão", 0),
        "Plásticos": row * gravimetricos.get("Plásticos", 0),
        "Vidros": row * gravimetricos.get("Vidros", 0),
        "Metais": row * gravimetricos.get("Metais", 0),
        "Orgânicos": row * gravimetricos.get("Orgânicos", 0),
    }


def calcular_entulho(row):
    return {material: row * percentual for material, percentual in PERCENTUAIS_ENTULHO.items()}


def calcular_fluxo_ajustado(gravimetria_data, resumo_fluxo_data):
    fluxo_ajustado = []

    for _, row in resumo_fluxo_data.iterrows():
        unidade = row["Tipo de unidade, segundo o município informante"]
        gravimetricos = gravimetria_data[gravimetria_data["Tipo de unidade, segundo o município informante"] == unidade]

        if gravimetricos.empty:
            continue

        gravimetricos = gravimetricos.iloc[0]
        ajuste_residuos = {"UF": row["UF"], "Unidade": unidade}

        # Calcular resíduos por tipo
        if "Dom+Pub" in row:
            ajuste_residuos.update(calcular_dom_pub(row["Dom+Pub"], gravimetricos))

        if "Entulho" in row:
            ajuste_residuos.update(calcular_entulho(row["Entulho"]))

        if "Saúde" in row and "Valor energético p/Incineração" in gravimetricos:
            ajuste_residuos["Valor energético (MJ/ton)"] = row["Saúde"] * gravimetricos.get("Valor energético p/Incineração", 0)

        if "Podas" in row:
            ajuste_residuos["Redução Peso Seco"] = row["Podas"] * gravimetricos.get("Redução de peso seco com Podas", 0)
            ajuste_residuos["Redução Peso Líquido"] = row["Podas"] * gravimetricos.get("Redução de peso Líquido com Podas", 0)

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

        # Métricas resumidas
        st.header("Resumo dos Indicadores")
        total_residuos = fluxo_ajustado.filter(regex="Papel|Plásticos|Vidros|Metais|Orgânicos|Concreto|Argamassa").sum().sum()
        total_entulho = fluxo_ajustado.filter(regex="Concreto|Argamassa|Tijolo").sum().sum()

        col1, col2 = st.columns(2)
        col1.metric("Total de Resíduos Processados (ton)", f"{total_residuos:,.2f}")
        col2.metric("Total de Entulho Processado (ton)", f"{total_entulho:,.2f}")

        # Resultados detalhados
        st.header("📈 Resultados Detalhados")
        st.dataframe(fluxo_ajustado)

        # Gráficos interativos
        if "Redução Peso Seco" in fluxo_ajustado and "Redução Peso Líquido" in fluxo_ajustado:
            st.subheader("📍 Redução de Peso")
            reducao_peso = fluxo_ajustado.groupby("UF")[["Redução Peso Seco", "Redução Peso Líquido"]].sum().reset_index()
            fig_peso = px.bar(reducao_peso, x="UF", y=["Redução Peso Seco", "Redução Peso Líquido"], barmode="stack")
            st.plotly_chart(fig_peso, use_container_width=True)

    except Exception as e:
        st.error(f"Erro: {str(e)}")
