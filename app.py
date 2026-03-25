import streamlit as st
import os

# Configuração da página
st.set_page_config(
    page_title="Du Cortz Barbearia",
    page_icon="✂️",
    layout="wide"
)

# Função para ler o arquivo HTML
def load_html():
    # Obtém o diretório do arquivo atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "index.html")
    
    # Lê o conteúdo do arquivo HTML
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return html_content

# Carrega e exibe o HTML
try:
    html_content = load_html()
    
    # Remove qualquer estilo padrão do Streamlit que possa interferir
    st.markdown("""
        <style>
            /* Remove padding e margens padrão do Streamlit */
            .main .block-container {
                padding: 0 !important;
                max-width: 100% !important;
            }
            /* Esconde elementos padrão do Streamlit */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Renderiza o HTML completo
    st.components.v1.html(html_content, height=800, scrolling=True)
    
except FileNotFoundError:
    st.error("❌ Arquivo 'index.html' não encontrado!")
    st.info("Certifique-se de que o arquivo 'index.html' está no mesmo diretório deste script Python.")
    
    # Mostra instruções
    with st.expander("📝 Como usar:"):
        st.markdown("""
        1. Salve o código HTML fornecido anteriormente em um arquivo chamado `index.html`
        2. Coloque este arquivo Python no mesmo diretório do `index.html`
        3. Execute com: `streamlit run seu_arquivo.py`
        """)
        
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {str(e)}")
