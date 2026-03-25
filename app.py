import streamlit as st
import os

# Configuração da página - TELA CHEIA
st.set_page_config(
    page_title="Du Cortz Barbearia",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS para remover paddings e margens do Streamlit - garantir tela cheia
st.markdown("""
    <style>
        /* Remove padding e margens padrão do Streamlit */
        .main .block-container {
            padding: 0 !important;
            max-width: 100% !important;
            margin: 0 !important;
        }
        
        /* Esconde elementos padrão do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Remove qualquer espaço extra */
        .stApp {
            margin: 0;
            padding: 0;
        }
        
        /* Garante que o iframe ocupe toda a tela */
        iframe {
            width: 100% !important;
            height: 100vh !important;
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Remove barras de rolagem desnecessárias */
        body {
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# Função para ler o arquivo HTML
def load_html():
    # Obtém o diretório do arquivo atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "index.html")
    
    # Lê o conteúdo do arquivo HTML
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return html_content

# Carrega e exibe o HTML em tela cheia
try:
    html_content = load_html()
    
    # Renderiza o HTML completo ocupando toda a tela
    st.components.v1.html(
        html_content, 
        height=1000,  # Altura grande para ocupar
        scrolling=False,  # Desativa scroll do componente, deixa o HTML cuidar
        width=1000
    )
    
except FileNotFoundError:
    st.error("❌ Arquivo 'index.html' não encontrado!")
    st.info("Certifique-se de que o arquivo 'index.html' está no mesmo diretório deste script Python.")
    
    # Mostra instruções
    with st.expander("📝 Como usar:"):
        st.markdown("""
        1. Salve o código HTML fornecido em um arquivo chamado `index.html`
        2. Coloque este arquivo Python no mesmo diretório do `index.html`
        3. Execute com: `streamlit run app.py`
        """)
        
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {str(e)}")
