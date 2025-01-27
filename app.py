import streamlit as st

# Dicionário com os limites diários por estado
limites_por_estado = {
    "Acre": 300, "Alagoas": 100, "Amapá": 200, "Amazonas": 200,
    "Bahia": 300, "Ceará": 100, "Distrito Federal": 120, "Espírito Santo": 200,
    "Goiás": 120, "Maranhão": 200, "Mato Grosso": 200, "Mato Grosso do Sul": 200,
    "Minas Gerais": 200, "Pará": 200, "Paraíba": 200, "Paraná": 100,
    "Pernambuco": 100, "Piauí": 120, "Rio de Janeiro": 120, "Rio Grande do Norte": 200,
    "Rio Grande do Sul": 300, "Rondônia": 200, "Roraima": 200, "Santa Catarina": 120,
    "São Paulo": 200, "Sergipe": 200, "Tocantins": 120
}

# Título do aplicativo
st.title("Classificação de Gerador de Resíduos e Resíduos - ABNT NBR 10004:2004")

# Criar abas
abas = st.tabs(["Classificação de Resíduos", "Anexo A", "Anexo B", "Anexo G"])

# Aba 1: Classificação de Resíduos
with abas[0]:
    # Perguntar o estado
    estado = st.selectbox("Selecione o estado:", list(limites_por_estado.keys()))

    # Perguntar quantidade de resíduos gerados
    quantidade = st.number_input("Informe a quantidade de resíduos gerados por dia (em litros):", min_value=0)

    # Verificar se é um grande gerador
    limite = limites_por_estado[estado]
    grande_gerador = quantidade > limite

    if grande_gerador:
        st.warning(f"Você é considerado um GRANDE GERADOR de resíduos no estado de {estado}.")
    else:
        st.success(f"Você NÃO é considerado um grande gerador de resíduos no estado de {estado}.")

    # Pergunta 1: Origem do resíduo
    origem_conhecida = st.radio(
        "O resíduo tem origem conhecida?",
        ("Sim", "Não")
    )

    if origem_conhecida == "Sim":
        # Pergunta 2: Consta nos anexos A ou B?
        consta_anexos = st.radio(
            "O resíduo consta nos anexos A ou B?",
            ("Sim", "Não")
        )

        if consta_anexos == "Sim":
            st.error("O resíduo é classificado como PERIGOSO (Classe I).")
        else:
            # Pergunta 3: Tem características de periculosidade?
            perigoso = st.radio(
                "O resíduo tem características de: inflamabilidade, corrosividade, reatividade, toxicidade ou patogenicidade?",
                ("Sim", "Não")
            )

            if perigoso == "Sim":
                st.error("O resíduo é classificado como PERIGOSO (Classe I).")
            else:
                # Pergunta 4: Possui constituintes solubilizados em concentrações superiores ao anexo G?
                solubilidade = st.radio(
                    "O resíduo possui constituintes que são solubilizados em concentrações superiores ao anexo G?",
                    ("Sim", "Não")
                )

                if solubilidade == "Sim":
                    st.warning("O resíduo é classificado como NÃO PERIGOSO - NÃO INERTE (Classe II A).")
                else:
                    st.success("O resíduo é classificado como NÃO PERIGOSO - INERTE (Classe II B).")
    else:
        # Pergunta 3 (para origem desconhecida): Tem características de periculosidade?
        perigoso = st.radio(
            "O resíduo tem características de: inflamabilidade, corrosividade, reatividade, toxicidade ou patogenicidade?",
            ("Sim", "Não")
        )

        if perigoso == "Sim":
            st.error("O resíduo é classificado como PERIGOSO (Classe I).")
        else:
            # Pergunta 4: Possui constituintes solubilizados em concentrações superiores ao anexo G?
            solubilidade = st.radio(
                "O resíduo possui constituintes que são solubilizados em concentrações superiores ao anexo G?",
                ("Sim", "Não")
            )

            if solubilidade == "Sim":
                st.warning("O resíduo é classificado como NÃO PERIGOSO - NÃO INERTE (Classe II A).")
            else:
                st.success("O resíduo é classificado como NÃO PERIGOSO - INERTE (Classe II B).")

# Aba 2: Anexo A
with abas[1]:
    st.header("Anexo A")
    st.image("1a.png", caption="Exemplo: Anexo A", use_column_width=True)

# Aba 3: Anexo B
with abas[2]:
    st.header("Anexo B")
    st.image("1b.png", caption="Exemplo: Anexo B", use_column_width=True)

# Aba 4: Anexo G
with abas[3]:
    st.header("Anexo G")
    st.image("1g.png", caption="Exemplo: Anexo G", use_column_width=True)
