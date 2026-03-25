import streamlit as st
import os

# Configuração da página - TELA CHEIA
st.set_page_config(
    page_title="Du Cortz Barbearia",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS para remover paddings e margens do Streamlit e centralizar conteúdo
st.markdown("""
    <style>
        /* Remove todos os espaços extras do Streamlit */
        .main > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
            margin: 0 !important;
        }
        
        /* Esconde elementos padrão */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Garante que o iframe ocupe toda a tela */
        iframe {
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
        }
        
        /* Remove barras de rolagem do app */
        .stApp {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        
        /* Centraliza o conteúdo se necessário */
        .stApp > header {
            display: none;
        }
        
        /* Remove qualquer padding do elemento root */
        .st-emotion-cache-1v0mbdj {
            padding: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Função para ler o arquivo HTML
def load_html():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

# Carrega e exibe o HTML em tela cheia
try:
    html_content = load_html()
    
    # Renderiza o HTML ocupando 100% da tela
    st.components.v1.html(
        html_content,
        height=1000,
        scrolling=False,
        width=1000
    )
    
except FileNotFoundError:
    st.error("❌ Arquivo 'index.html' não encontrado!")
    st.info("Certifique-se de que o arquivo 'index.html' está no mesmo diretório deste script Python.")
    
    with st.expander("📝 Como usar:"):
        st.markdown("""
        1. Salve o código HTML em um arquivo chamado `index.html`
        2. Coloque este arquivo Python no mesmo diretório
        3. Execute com: `streamlit run app.py`
        """)
        
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {str(e)}")
