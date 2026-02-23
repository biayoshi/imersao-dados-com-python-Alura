# Ao visualizar o dashboard, recomendo usar o modo claro para que o contraste entre as cores fique melhor!
import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

# Configurando a Página
# Definimos o título, o ícone e o layout
st.set_page_config(
    page_title="Dashboard - Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
    <style>
        /* Fundo principal */
        .stApp {
            background-color: #fff0f6;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #f8bbd0;
        }

        /* Títulos */
        h1, h2, h3 {
            color: #000000 !important;
        }

        /* Texto padrão (parágrafos, markdown, labels etc.) */
        .stMarkdown, 
        .stText, 
        p, 
        span, 
        label, 
        div {
            color: #000000 !important;
        }

        /* Botões */
        .stButton>button {
            background-color: #ec407a;
            color: white;
            border-radius: 8px;
            border: none;
        }

        .stButton>button:hover {
            background-color: #d81b60;
            color: white;
        }

        /* Métricas */
        div[data-testid="metric-container"] {
            background-color: #fce4ec;
            border: 1px solid #f48fb1;
            padding: 10px;
            border-radius: 10px;
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Carregamento dos dados já limpos (Aula 2)
df = pd.read_csv('df_limpo.csv')

# Barra Lateral (Filtros)
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['ano_de_trabalho'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['nivel_de_exp'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['tipo_de_emprego'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# Filtrando o DataFrame
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral
df_filtrado = df[
    (df['ano_de_trabalho'].isin(anos_selecionados)) &
    (df['nivel_de_exp'].isin(senioridades_selecionadas)) &
    (df['tipo_de_emprego'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# Conteúdo Principal
st.title("🎲 Dashboard - Analisando Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos! Utilize os filtros à esquerda para refinar a análise!")
st.markdown("Importante: Lembre-se de deixar ao menos um filtro marcado por categoria!")

# Métricas Principais (KPIs)
st.subheader("Métricas gerais/KPIs (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['salario_em_usd'].mean()
    salario_maximo = df_filtrado['salario_em_usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# Análises Visuais usando o Plotly
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['salario_em_usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
        top_cargos,
        x='salario_em_usd',
        y='cargo',
        orientation='h',
        title="Top 10 cargos por salário médio",
        labels={'salario_em_usd': 'Média salarial anual (USD)', 'cargo': ''},
        color_discrete_sequence=["#ec407a"]
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
        df_filtrado,
        x='salario_em_usd',
        nbins=30,
        title="Distribuição de salários anuais",
        labels={'salario_em_usd': 'Faixa salarial (USD)', 'contagem': ''},
        color_discrete_sequence=["#f06292"]
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['taxa_remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_de_emprego', 'contagem']
        grafico_remoto = px.pie(
    remoto_contagem,
    names='tipo_de_emprego',
    values='contagem',
    title='Proporção dos tipos de trabalho',
    hole=0.5,
    color_discrete_sequence=[
        "#880e4f",  # rosa vinho (mais escuro)
        "#d81b60",  # rosa forte
        "#f06292"   # rosa médio vibrante
        ])
        grafico_remoto.update_traces(textposition='inside',textinfo='percent+label',textfont=dict(color='white', size=14),marker=dict(line=dict(color='#ffffff', width=2)))
        grafico_remoto.update_layout(title_x=0.1,paper_bgcolor="#fff0f6")
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

# Função para converter ISO-2 em ISO-3
def iso2_para_iso3(codigo_iso2):
    try:
        pais = pycountry.countries.get(alpha_2=codigo_iso2)
        return pais.alpha_3
    except:
        return None

with col_graf4:
    if not df_filtrado.empty:
        
        # Filtra apenas Data Scientist
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        
        # Calcula média salarial por país (usando ISO-2 da coluna local_empresa)
        salario_medio_data_scientist_por_pais = (
            df_ds.groupby('local_empresa')['salario_em_usd']
            .mean()
            .reset_index()
        )
        
        # Converte ISO-2 para ISO-3
        salario_medio_data_scientist_por_pais['res_iso3_local_empresa'] = (
            salario_medio_data_scientist_por_pais['local_empresa']
            .apply(iso2_para_iso3)
        )
        
        # Remove possíveis valores nulos após conversão
        salario_medio_data_scientist_por_pais = (
            salario_medio_data_scientist_por_pais
            .dropna(subset=['res_iso3_local_empresa'])
        )

        # Gera o mapa
        grafico_paises = px.choropleth(
            salario_medio_data_scientist_por_pais,
            locations='res_iso3_local_empresa',
            color='salario_em_usd',
            color_continuous_scale=[
            "#fce4ec",
            "#f8bbd0",
            "#f48fb1",
            "#ec407a",
            "#ad1457"],
            title='Salário médio de Cientista de Dados por país',
            labels={
                'salario_em_usd': 'Salário médio (USD)',
                'res_iso3_local_empresa': 'País'
            }
        )

        grafico_paises.update_layout(title_x=0.1)

        st.plotly_chart(grafico_paises, use_container_width=True)

    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")

st.dataframe(df_filtrado)



