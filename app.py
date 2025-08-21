# Comunidade Data Scienc - ComunidadeDS - https://comunidadeds.com/

# Curso FDS - Formação dem Analista de Dados
# PA - Projeto do Aluno
# Tema: FZ Restaurante
# Professores: 
# - Meigarom Lopes
# - Pedro Ferraresi
# Aluno: Alfredo Junior Albieri
# Ano letivo: 2025

# ZF Restaurantes – Dashboard (v1) – Streamlit
# -------------------------------------------------------------
# Como usar:
# 1) Salve este arquivo como: app.py
# 2) Rode: streamlit run app.py
# 3) Faça upload do seu CSV (padrão: zf_restaurantes.csv)
# -------------------------------------------------------------

import io
import sys
import math
import numpy as np
import pandas as pd
import streamlit as st

# -------------------------------------------------------------
# Configurações da página
# -------------------------------------------------------------
st.set_page_config(
    page_title="ZF Restaurantes – Dashboard",
    layout="wide",
    page_icon="🍽️",
)

st.title("🍽️ ZF Restaurantes – Dashboard (v1)")
st.caption("Primeira versão funcional com cálculos automáticos para responder às questões de negócio.")

# -------------------------------------------------------------
# Upload/Leitura de dados
# -------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuração de Dados")
    uploaded = st.file_uploader("CDS_Analista/FTC_Analisando_Dados_com_Python/Projeto_Aluno/PA-Final_Project/dataset/new_zomato.csv")    
    sample_cols = [
        "restaurant_id","restaurant_name","country","city","cuisines",
        "average_cost_for_two","currency","aggregate_rating","rating_text",
        "votes","price_range","has_online_delivery","is_delivering_now",
        "has_table_booking"
    ]
    st.markdown("**Colunas esperadas:** ")
    st.code(", ".join(sample_cols), language="text")

    currency_note = st.checkbox("Meus preços estão em moedas diferentes (ver nota)")
    st.markdown("""
    *Nota:* A métrica **preço médio para duas pessoas por país** presume que os preços
    estejam **na mesma moeda** por país. Se seu dataset tiver múltiplas moedas por país,
    normalize antes (ex.: converter para USD). Esta versão não converte câmbio.
    """)

# Funções utilitárias ----------------------------------------------------------

def _coerce_bool(x):
    """Normaliza valores booleanos/flags que podem vir como 0/1, True/False, Yes/No, 'Y'/'N', etc."""
    if pd.isna(x):
        return False
    if isinstance(x, (int, float)):
        return bool(int(x))
    s = str(x).strip().lower()
    return s in {"1", "true", "yes", "y", "sim"}


def _clean_cuisines(s):
    if pd.isna(s):
        return []
    # Divide por vírgula e limpa espaços
    return [c.strip() for c in str(s).split(',') if c.strip()]


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Renomeia colunas essenciais se houver variações comuns
    rename_map = {
        'Restaurant ID': 'restaurant_id',
        'Restaurant Name': 'restaurant_name',
        'Country Code': 'country',
        'City': 'city',
        'Cuisines': 'cuisines',
        'Average Cost for two': 'average_cost_for_two',
        'Currency': 'currency',
        'Aggregate rating': 'aggregate_rating',
        'Rating text': 'rating_text',
        'Votes': 'votes',
        'Price range': 'price_range',
        'Has Online delivery': 'has_online_delivery',
        'Is delivering now': 'is_delivering_now',
        'Has Table booking': 'has_table_booking',
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Garante colunas mínimas
    required = {
        "restaurant_id","restaurant_name","country","city","cuisines",
        "average_cost_for_two","currency","aggregate_rating","votes","price_range",
        "has_online_delivery","is_delivering_now","has_table_booking"
    }
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Faltam colunas no CSV: {missing}")
        st.stop()

    # Tipagens básicas
    df['restaurant_id'] = pd.to_numeric(df['restaurant_id'], errors='coerce')
    df['average_cost_for_two'] = pd.to_numeric(df['average_cost_for_two'], errors='coerce')
    df['aggregate_rating'] = pd.to_numeric(df['aggregate_rating'], errors='coerce')
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce')
    df['price_range'] = pd.to_numeric(df['price_range'], errors='coerce')

    # Normaliza flags
    for col in ['has_online_delivery','is_delivering_now','has_table_booking']:
        df[col] = df[col].apply(_coerce_bool)

    # Limpa strings
    for col in ['restaurant_name','country','city','currency']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Cuisines em lista + coluna auxiliar lower
    df['cuisines_list'] = df['cuisines'].apply(_clean_cuisines)
    df['cuisines_lower'] = df['cuisines'].fillna('').str.lower()

    return df


def cuisine_mask(df, cuisine_name: str):
    return df['cuisines_lower'].str.contains(fr"\b{cuisine_name.strip().lower()}\b", regex=True)


# Carrega/Prepara dados --------------------------------------------------------
if uploaded is not None:
    try:
        df_raw = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Erro ao ler CSV: {e}")
        st.stop()
else:
    st.info("Faça upload de um CSV para iniciar.")
    st.stop()

# Prepara
df = prepare_dataframe(df_raw).copy()

# Filtros globais --------------------------------------------------------------
with st.sidebar:
    st.header("🔍 Filtros")
    countries = sorted(df['country'].dropna().unique().tolist())
    cities = sorted(df['city'].dropna().unique().tolist())
    cuisines_all = sorted(sorted({c for lst in df['cuisines_list'] for c in lst}))

    sel_countries = st.multiselect("País", options=countries, default=countries)
    sel_cities = st.multiselect("Cidade", options=cities, default=cities)
    sel_cuisines = st.multiselect("Tipo de culinária", options=cuisines_all)

# Aplica filtros
mask = df['country'].isin(sel_countries) & df['city'].isin(sel_cities)
if sel_cuisines:
    mask = mask & df['cuisines_list'].apply(lambda lst: any(c in lst for c in sel_cuisines))

df_f = df.loc[mask].copy()

# Tabs principais --------------------------------------------------------------
tab_geral, tab_pais, tab_cidade, tab_rest, tab_cuisine = st.tabs([
    "Geral", "País", "Cidade", "Restaurantes", "Tipos de Culinária"
])

# ============================= GERAl ==========================================
with tab_geral:
    st.subheader("📊 Visão Geral")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Restaurantes únicos", int(df_f['restaurant_id'].nunique()))
    c2.metric("Países únicos", int(df_f['country'].nunique()))
    c3.metric("Cidades únicas", int(df_f['city'].nunique()))
    c4.metric("Total de avaliações (votes)", int(df_f['votes'].fillna(0).sum()))
    # Quantidade de tipos de culinária distintos considerando explode
    cuisines_distintos = sorted({c for lst in df_f['cuisines_list'] for c in lst})
    c5.metric("Tipos de culinária distintos", len(cuisines_distintos))

    st.divider()
    st.caption("Os números refletem os filtros aplicados na barra lateral.")

# ============================= PAÍS ===========================================
with tab_pais:
    st.subheader("🌍 Análises por País")
    g = df_f.copy()

    # 1) País com mais cidades registradas (contagem de cidades únicas por país)
    pais_cidades = g.groupby('country')['city'].nunique().sort_values(ascending=False)

    # 2) País com mais restaurantes registrados
    pais_restaurantes = g.groupby('country')['restaurant_id'].nunique().sort_values(ascending=False)

    # 3) País com mais restaurantes com price_range == 4
    pais_preco4 = g.loc[g['price_range'] == 4].groupby('country')['restaurant_id'].nunique().sort_values(ascending=False)

    # 4) País com maior quantidade de tipos de culinária distintos
    # Explode cuisines
    df_c = g[['country','cuisines_list']].explode('cuisines_list')
    pais_cuisines = df_c.dropna().groupby('country')['cuisines_list'].nunique().sort_values(ascending=False)

    # 5) País com maior quantidade de avaliações feitas (soma de votes)
    pais_votes = g.groupby('country')['votes'].sum().sort_values(ascending=False)

    # 6) País com maior quantidade de restaurantes que fazem entrega (is_delivering_now True)
    pais_entregas = g.loc[g['is_delivering_now']].groupby('country')['restaurant_id'].nunique().sort_values(ascending=False)

    # 7) País com maior quantidade de restaurantes que aceitam reservas
    pais_reservas = g.loc[g['has_table_booking']].groupby('country')['restaurant_id'].nunique().sort_values(ascending=False)

    # 8) País com maior média de avaliações registradas (média de votes por restaurante)
    pais_media_votes = g.groupby('country').apply(lambda x: x['votes'].mean()).sort_values(ascending=False)

    # 9) País com maior nota média registrada (média de aggregate_rating)
    pais_media_nota = g.groupby('country')['aggregate_rating'].mean().sort_values(ascending=False)

    # 10) País com menor nota média registrada
    pais_menor_nota = pais_media_nota.sort_values(ascending=True)

    # 11) Média de preço de um prato para dois por país (média simples)
    pais_preco_medio = g.groupby('country')['average_cost_for_two'].mean().sort_values(ascending=False)

    def top_label(s):
        return s.index[0] if len(s) else "—"

    c1,c2,c3 = st.columns(3)
    c1.metric("Mais cidades", top_label(pais_cidades))
    c2.metric("Mais restaurantes", top_label(pais_restaurantes))
    c3.metric("Mais restaurantes preço=4", top_label(pais_preco4))

    c4,c5,c6 = st.columns(3)
    c4.metric("Mais tipos de culinária distintos", top_label(pais_cuisines))
    c5.metric("Mais avaliações (soma de votes)", top_label(pais_votes))
    c6.metric("Mais restaurantes que entregam", top_label(pais_entregas))

    c7,c8,c9 = st.columns(3)
    c7.metric("Mais restaurantes com reservas", top_label(pais_reservas))
    c8.metric("Maior média de avaliações (votes)", top_label(pais_media_votes))
    c9.metric("Maior nota média", top_label(pais_media_nota))

    c10, c11 = st.columns(2)
    c10.metric("Menor nota média", top_label(pais_menor_nota))
    # Mostra tabela de preço médio por país
    c11.dataframe(pais_preco_medio.reset_index().rename(columns={'average_cost_for_two':'preco_medio_para_dois'}))

    st.divider()
    st.markdown("**Rankings por País (top 10)**")
    colA, colB = st.columns(2)
    with colA:
        st.bar_chart(pais_restaurantes.head(10))
        st.bar_chart(pais_cidades.head(10))
        st.bar_chart(pais_votes.head(10))
    with colB:
        st.bar_chart(pais_cuisines.head(10))
        st.bar_chart(pais_preco4.head(10))
        st.bar_chart(pais_preco_medio.head(10))

# ============================= CIDADE =========================================
with tab_cidade:
    st.subheader("🏙️ Análises por Cidade")
    g = df_f.copy()

    # Metricas
    cidade_restaurantes = g.groupby('city')['restaurant_id'].nunique().sort_values(ascending=False)
    cidade_nota_maior4 = g.loc[g['aggregate_rating'] > 4].groupby('city')['restaurant_id'].nunique().sort_values(ascending=False)
    cidade_nota_menor25 = g.loc[g['aggregate_rating'] < 2.5].groupby('city')['restaurant_id'].nunique().sort_values(ascending=False)
    cidade_preco_medio = g.groupby('city')['average_cost_for_two'].mean().sort_values(ascending=False)

    df_c = g[['city','cuisines_list']].explode('cuisines_list')
    cidade_cuisines = df_c.dropna().groupby('city')['cuisines_list'].nunique().sort_values(ascending=False)

    cidade_reservas = g.loc[g['has_table_booking']].groupby('city')['restaurant_id'].nunique().sort_values(ascending=False)
    cidade_entregas = g.loc[g['is_delivering_now']].groupby('city')['restaurant_id'].nunique().sort_values(ascending=False)
    cidade_online = g.loc[g['has_online_delivery']].groupby('city')['restaurant_id'].nunique().sort_values(ascending=False)

    def top_label(s):
        return s.index[0] if len(s) else "—"

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Mais restaurantes", top_label(cidade_restaurantes))
    c2.metric("Mais nota > 4", top_label(cidade_nota_maior4))
    c3.metric("Mais nota < 2.5", top_label(cidade_nota_menor25))
    c4.metric("Maior preço médio p/ dois", top_label(cidade_preco_medio))

    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Mais tipos de culinária distintos", top_label(cidade_cuisines))
    c6.metric("Mais reservas", top_label(cidade_reservas))
    c7.metric("Mais entregas", top_label(cidade_entregas))
    c8.metric("Mais pedidos online", top_label(cidade_online))

    st.divider()
    st.markdown("**Rankings por Cidade (top 10)**")
    colA, colB = st.columns(2)
    with colA:
        st.bar_chart(cidade_restaurantes.head(10))
        st.bar_chart(cidade_nota_maior4.head(10))
        st.bar_chart(cidade_nota_menor25.head(10))
    with colB:
        st.bar_chart(cidade_preco_medio.head(10))
        st.bar_chart(cidade_cuisines.head(10))
        st.bar_chart(cidade_online.head(10))

# ============================= RESTAURANTES ===================================
with tab_rest:
    st.subheader("🍽️ Análises por Restaurante")
    g = df_f.copy()

    # 1) Restaurante com mais avaliações (votes)
    top_votes = g.loc[g['votes'].notna()].sort_values('votes', ascending=False).head(1)

    # 2) Restaurante com maior nota média (aggregate_rating)
    top_rating = g.loc[g['aggregate_rating'].notna()].sort_values('aggregate_rating', ascending=False).head(1)

    # 3) Restaurante com maior valor de prato p/ dois
    top_price = g.loc[g['average_cost_for_two'].notna()].sort_values('average_cost_for_two', ascending=False).head(1)

    # 4) Restaurante de culinária brasileira com menor média
    mask_br_cuisine = cuisine_mask(g, 'Brazilian') | cuisine_mask(g, 'Brasileira')
    br_cuisine = g.loc[mask_br_cuisine]
    worst_br = br_cuisine.loc[br_cuisine['aggregate_rating'].notna()].sort_values('aggregate_rating').head(1)

    # 5) Restaurante de culinária brasileira, do Brasil, com maior média
    br_in_brazil = br_cuisine.loc[br_cuisine['country'].str.lower().isin(['brazil','brasil'])]
    best_br_in_brazil = br_in_brazil.loc[br_in_brazil['aggregate_rating'].notna()].sort_values('aggregate_rating', ascending=False).head(1)

    # 6) Aceitam pedido online têm, na média, mais avaliações?
    online_mean_votes = g.groupby('has_online_delivery')['votes'].mean().rename({True:'Com online',False:'Sem online'})

    # 7) Fazem reservas têm, na média, maior preço médio p/ dois?
    booking_mean_price = g.groupby('has_table_booking')['average_cost_for_two'].mean().rename({True:'Com reserva',False:'Sem reserva'})

    # 8) Japonesa (EUA) vs BBQ (EUA) – preço médio p/ dois
    usa = g.loc[g['country'].str.lower().isin(['united states of america','united states','usa','eua'])]
    japanese_usa = usa.loc[cuisine_mask(usa, 'Japanese') | cuisine_mask(usa, 'Japonesa')]
    bbq_usa = usa.loc[cuisine_mask(usa, 'BBQ') | cuisine_mask(usa, 'Barbecue') | cuisine_mask(usa, 'Churrasco')]
    japanese_mean_price = japanese_usa['average_cost_for_two'].mean()
    bbq_mean_price = bbq_usa['average_cost_for_two'].mean()

    c1,c2,c3 = st.columns(3)
    c1.metric("Mais avaliações", top_votes['restaurant_name'].iloc[0] if len(top_votes) else "—")
    c2.metric("Maior nota média", top_rating['restaurant_name'].iloc[0] if len(top_rating) else "—")
    c3.metric("Maior preço p/ dois", top_price['restaurant_name'].iloc[0] if len(top_price) else "—")

    c4,c5 = st.columns(2)
    c4.metric("Pior média – culinária brasileira", worst_br['restaurant_name'].iloc[0] if len(worst_br) else "—")
    c5.metric("Melhor média – culinária brasileira no Brasil", best_br_in_brazil['restaurant_name'].iloc[0] if len(best_br_in_brazil) else "—")

    st.divider()
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Média de avaliações (votes)** – Online vs. Não Online")
        st.bar_chart(online_mean_votes)
        st.caption("Pergunta 6: comparação direta das médias.")
    with colB:
        st.markdown("**Preço médio p/ dois** – Com reserva vs. Sem reserva")
        st.bar_chart(booking_mean_price)
        st.caption("Pergunta 7: comparação direta das médias.")

    st.divider()
    colC, colD = st.columns(2)
    with colC:
        st.markdown("**Preço médio p/ dois (EUA)** – Japonesa vs. BBQ")
        cmp_df = pd.DataFrame({
            'Categoria': ['Japonesa (EUA)','BBQ (EUA)'],
            'Preço médio p/ dois': [japanese_mean_price, bbq_mean_price]
        }).set_index('Categoria')
        st.bar_chart(cmp_df)
        if not math.isnan(japanese_mean_price) and not math.isnan(bbq_mean_price):
            st.info("Pergunta 8: **{}**".format(
                "Japonesa > BBQ" if japanese_mean_price > bbq_mean_price else "BBQ ≥ Japonesa"
            ))
        else:
            st.info("Pergunta 8: dados insuficientes em uma das categorias.")

    with colD:
        st.markdown("**Top 10 – Restaurantes com mais avaliações**")
        st.dataframe(g[['restaurant_name','country','city','votes']].sort_values('votes', ascending=False).head(10), use_container_width=True)

# ============================= TIPOS DE CULINÁRIA ============================
with tab_cuisine:
    st.subheader("🍜 Análises por Tipo de Culinária")
    g = df_f.copy()

    # Explode para trabalhar por restaurante x culinária
    exp = g[['restaurant_id','restaurant_name','country','city','aggregate_rating','average_cost_for_two','has_online_delivery','is_delivering_now','cuisines_list']].explode('cuisines_list').dropna(subset=['cuisines_list'])
    exp['cuisine'] = exp['cuisines_list'].astype(str)

    def top_bottom_by_cuisine(cname):
        sub = exp.loc[exp['cuisine'].str.lower()==cname.strip().lower()].copy()
        top_row = sub.sort_values('aggregate_rating', ascending=False).head(1)
        bottom_row = sub.sort_values('aggregate_rating', ascending=True).head(1)
        return top_row, bottom_row

    # 1-10) Top/Bottom por culinárias específicas
    targets = [
        ("Italiana","italian"), ("Americana","american"), ("Árabe","arabian"),
        ("Japonesa","japanese"), ("Caseira","home food")
    ]

    cols = st.columns(2)
    for i,(label, key) in enumerate(targets, start=1):
        top_row, bottom_row = top_bottom_by_cuisine(label)
        with cols[i%2]:
            st.markdown(f"**{label}**")
            st.write("Maior média:", top_row['restaurant_name'].iloc[0] if len(top_row) else "—")
            st.write("Menor média:", bottom_row['restaurant_name'].iloc[0] if len(bottom_row) else "—")

    st.divider()

    # 11) Tipo de culinária com maior valor médio de prato p/ dois
    cuisine_price_mean = exp.groupby('cuisine')['average_cost_for_two'].mean().sort_values(ascending=False)

    # 12) Tipo de culinária com maior nota média
    cuisine_rating_mean = exp.groupby('cuisine')['aggregate_rating'].mean().sort_values(ascending=False)

    # 13) Tipo de culinária com mais restaurantes que aceitam pedidos online e fazem entregas
    online_delivery_and_now = exp.loc[exp['has_online_delivery'] & g.loc[exp.index, 'is_delivering_now']]
    cuisine_online_delivery = online_delivery_and_now.groupby('cuisine')['restaurant_id'].nunique().sort_values(ascending=False)

    c1,c2,c3 = st.columns(3)
    c1.metric("Culinária mais cara (média p/ dois)", cuisine_price_mean.index[0] if len(cuisine_price_mean) else "—")
    c2.metric("Culinária com maior nota média", cuisine_rating_mean.index[0] if len(cuisine_rating_mean) else "—")
    c3.metric("Mais restaurantes online+entrega", cuisine_online_delivery.index[0] if len(cuisine_online_delivery) else "—")

    st.divider()
    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown("**Preço médio p/ dois por culinária (top 15)**")
        st.bar_chart(cuisine_price_mean.head(15))
    with colB:
        st.markdown("**Nota média por culinária (top 15)**")
        st.bar_chart(cuisine_rating_mean.head(15))
    with colC:
        st.markdown("**Online + Entregas por culinária (top 15)**")
        st.bar_chart(cuisine_online_delivery.head(15))

st.divider()
st.caption("© ZF Restaurantes – Dashboard v1 | Esta versão responde diretamente às questões listadas, respeitando filtros aplicados.")
