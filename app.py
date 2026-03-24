import streamlit as st
import os

# Configuração da página
st.set_page_config(
    page_title="Barbearia Du Cortz",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Esconder elementos padrão do Streamlit
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .main > div { padding-left: 0rem; padding-right: 0rem; }
        .block-container { padding-top: 0rem; padding-bottom: 0rem; max-width: 100%; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background: transparent; }
    </style>
""", unsafe_allow_html=True)

# Ler o arquivo index.html
def carregar_html():
    # Caminho do arquivo HTML
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    
    # Verificar se o arquivo existe
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Mensagem de erro se o arquivo não for encontrado
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Erro - Arquivo não encontrado</title>
            <style>
                body {{
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    color: white;
                }}
                .error-box {{
                    text-align: center;
                    padding: 40px;
                    background: rgba(0,0,0,0.8);
                    border-radius: 20px;
                    border: 1px solid #D4AF37;
                }}
                h1 {{ color: #D4AF37; }}
                p {{ margin: 20px 0; }}
                .emoji {{ font-size: 3rem; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <div class="emoji">📁</div>
                <h1>Arquivo index.html não encontrado!</h1>
                <p>Certifique-se de que o arquivo <strong style="color:#D4AF37">index.html</strong> está na mesma pasta do app.py</p>
                <p>📂 Estrutura esperada:</p>
                <pre style="background:#2a2a2a; padding:15px; border-radius:10px; text-align:left;">
barbearia_du_cortz/
├── app.py
├── index.html
└── requirements.txt
                </pre>
            </div>
        </body>
        </html>
        """

# Carregar e exibir o HTML
html_content = carregar_html()
st.components.v1.html(html_content, height=800, scrolling=True)
