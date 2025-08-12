# Comunidade Data Scienc - ComunidadeDS - https://comunidadeds.com/

# Curso FDS - Formação dem Analista de Dados
# PA - Projeto do Aluno
# Tema: FZ Restaurante
# Professores: 
# - Meigarom Lopes
# - Pedro Ferraresi
# Aluno: Alfredo Junior Albieri
# Ano letivo: 2025
# ====================================
# Bibliotecas
#-------------------------------------
import streamlit as st
from PIL import Image

# ------------------------------------
# Import Daset zomato.csv
# ------------------------------------
df = pd.read_csv('../dataset/new_zomato.csv')

# ------------------
# Ajusta a largura da página de apresentação
# ------------------
st.set_page_config(
    page_title="Home",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar com imagem e textos
image_path = 'PA-Images/logo2_fz.png'
image = Image.open(image_path)
st.sidebar.image(image, width=60)

st.sidebar.markdown('# FZ Restaurantes')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

# Título principal
st.write('# FZ Restaurantes Growth Dashboard')

# Texto de introdução
st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Restaurantes.

    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.

    ### Sugestões e Ajuda
    - Time de Data Science no Discord: @meigarom
    """
)

# Botões de navegação (opcional)
st.markdown("### 🧭 Navegação Rápida")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Visão da Empresa"):
        st.switch_page("pages/1_visao_empresa.py")
with col2:
    if st.button("🛵 Visão dos Entregadores"):
        st.switch_page("pages/2_visao_entregadores.py")
with col3:
    if st.button("🍽️ Visão dos Restaurantes"):
        st.switch_page("pages/3_visao_restaurantes.py")