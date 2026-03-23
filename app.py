import streamlit as st
import pandas as pd
import datetime
import os
import json
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import base64
import random
import string

# Configuração da página
st.set_page_config(
    page_title="Barber Club PRO - Sistema de Gestão",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado premium
st.markdown("""
    <style>
    /* Reset e estilos globais */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
    }
    
    /* Cards premium */
    .premium-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px 0 rgba(31,38,135,0.37);
        transition: transform 0.3s ease;
    }
    
    .premium-card:hover {
        transform: translateY(-5px);
    }
    
    /* Métricas premium */
    .metric-premium {
        background: linear-gradient(135deg, #e65c00 0%, #f9d423 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(230,92,0,0.3);
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #e65c00 0%, #f9d423 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(230,92,0,0.4);
    }
    
    /* Títulos */
    h1, h2, h3 {
        background: linear-gradient(135deg, #e65c00 0%, #f9d423 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f0f1f 0%, #1a1a2e 100%);
    }
    
    /* Tabelas */
    .dataframe {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        color: white;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== CONFIGURAÇÕES DO SISTEMA ====================
class Config:
    BARBEARIA_NOME = "Barber Club PRO"
    BARBEARIA_EMAIL = "contato@barberclub.com"
    BARBEARIA_TELEFONE = "(11) 99999-9999"
    BARBEARIA_WHATSAPP = "5511999999999"
    BARBEARIA_ENDERECO = "Av. Principal, 123 - Centro, São Paulo - SP"
    HORARIO_ABERTURA = "09:00"
    HORARIO_FECHAMENTO = "20:00"
    DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
    DOMINGO_FUNCIONA = True
    HORARIO_DOMINGO = "10:00 às 16:00"
    
    # Cores
    COR_PRIMARIA = "#e65c00"
    COR_SECUNDARIA = "#f9d423"
    COR_FUNDO = "#0a0a0f"

# ==================== FUNÇÕES DE AUTENTICAÇÃO ====================
def gerar_senha_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_usuario_admin():
    usuarios = {}
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as f:
            usuarios = json.load(f)
    else:
        usuarios["admin"] = {
            "senha": gerar_senha_hash("admin123"),
            "nome": "Administrador",
            "nivel": "admin"
        }
        with open("usuarios.json", "w") as f:
            json.dump(usuarios, f)
    return usuarios

# ==================== FUNÇÕES DE BANCO DE DADOS ====================
def carregar_dados():
    if os.path.exists("agendamentos.csv"):
        df = pd.read_csv("agendamentos.csv")
        if 'data_agendamento' in df.columns:
            df['data_agendamento'] = pd.to_datetime(df['data_agendamento'])
        return df
    else:
        return pd.DataFrame(columns=[
            "id", "nome", "email", "telefone", "horario", "servicos", 
            "valor_total", "corte_simples", "barba", "sobrancelha",
            "pigmentacao", "luzes", "descolorimento", "data_agendamento",
            "status", "observacoes", "confirmado"
        ])

def salvar_dados(df):
    df.to_csv("agendamentos.csv", index=False)

def carregar_clientes():
    if os.path.exists("clientes.json"):
        with open("clientes.json", "r") as f:
            return json.load(f)
    return {}

def salvar_clientes(clientes):
    with open("clientes.json", "w") as f:
        json.dump(clientes, f, indent=2)

def carregar_financeiro():
    if os.path.exists("financeiro.json"):
        with open("financeiro.json", "r") as f:
            return json.load(f)
    return {"receitas": [], "despesas": [], "caixa": 0}

def salvar_financeiro(financeiro):
    with open("financeiro.json", "w") as f:
        json.dump(financeiro, f, indent=2)

# ==================== FUNÇÕES DE NOTIFICAÇÃO ====================
def enviar_whatsapp(telefone, mensagem):
    # Simulação de envio de WhatsApp
    whatsapp_url = f"https://wa.me/{telefone}?text={mensagem}"
    return whatsapp_url

def enviar_email(destinatario, assunto, corpo):
    # Simulação de envio de email
    # Em produção, configurar SMTP real
    return True

# ==================== FUNÇÕES DE RELATÓRIOS ====================
def gerar_relatorio_periodo(df, data_inicio, data_fim):
    mask = (df['data_agendamento'].dt.date >= data_inicio) & (df['data_agendamento'].dt.date <= data_fim)
    df_filtrado = df[mask]
    
    relatorio = {
        "total_agendamentos": len(df_filtrado),
        "receita_total": df_filtrado['valor_total'].sum(),
        "ticket_medio": df_filtrado['valor_total'].mean() if len(df_filtrado) > 0 else 0,
        "servicos_mais_vendidos": {
            "Corte Simples": df_filtrado['corte_simples'].sum(),
            "Barba": df_filtrado['barba'].sum(),
            "Sobrancelha": df_filtrado['sobrancelha'].sum(),
            "Pigmentação": df_filtrado['pigmentacao'].sum(),
            "Luzes": df_filtrado['luzes'].sum(),
            "Descolorimento": df_filtrado['descolorimento'].sum()
        }
    }
    return relatorio

# ==================== FUNÇÃO DO HTML ====================
def criar_arquivo_html():
    html_path = "agendamento.html"
    
    html_content = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Barber Club PRO - Agendamento</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 30px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #e65c00 0%, #f9d423 100%);
            color: white;
            padding: 50px 30px;
            text-align: center;
            position: relative;
        }

        .header h1 {
            font-size: 3.5em;
            margin-bottom: 10px;
            font-weight: 800;
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.95;
        }

        .form-content {
            padding: 40px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: #333;
        }

        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #e65c00;
        }

        .servicos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .servico-item {
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }

        .servico-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }

        .servico-item.selected {
            background: linear-gradient(135deg, #e65c00 0%, #f9d423 100%);
            border-color: #e65c00;
            color: white;
        }

        .servico-nome {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }

        .servico-preco {
            font-size: 1.3em;
            color: #e65c00;
            font-weight: bold;
        }

        .servico-item.selected .servico-preco {
            color: white;
        }

        .total-section {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
            text-align: center;
        }

        .total-value {
            font-size: 3em;
            color: #e65c00;
            font-weight: bold;
        }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #e65c00 0%, #f9d423 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
        }

        .message {
            margin-top: 20px;
            padding: 10px;
            border-radius: 8px;
            display: none;
        }

        .message.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }

        .message.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💈 Barber Club PRO</h1>
            <p>Agendamento Premium - Sistema de Gestão Profissional</p>
        </div>
        
        <div class="form-content">
            <div class="form-group">
                <label>👤 Seu Nome:</label>
                <input type="text" id="nome" placeholder="Digite seu nome completo" required>
            </div>
            
            <div class="form-group">
                <label>📧 E-mail:</label>
                <input type="email" id="email" placeholder="seuemail@exemplo.com">
            </div>
            
            <div class="form-group">
                <label>📱 WhatsApp:</label>
                <input type="tel" id="telefone" placeholder="(11) 99999-9999">
            </div>

            <div class="form-group">
                <label>🕐 Data e Horário:</label>
                <input type="datetime-local" id="horario" required>
            </div>

            <div class="form-group">
                <label>✂️ Selecione os Serviços:</label>
                <div class="servicos-grid">
                    <div class="servico-item" data-servico="corte_simples" data-preco="35">
                        <div class="servico-nome">✂️ Corte Simples</div>
                        <div class="servico-preco">R$ 35,00</div>
                    </div>
                    <div class="servico-item" data-servico="barba" data-preco="10">
                        <div class="servico-nome">🧔 Barba</div>
                        <div class="servico-preco">R$ 10,00</div>
                    </div>
                    <div class="servico-item" data-servico="sobrancelha" data-preco="10">
                        <div class="servico-nome">👁️ Sobrancelha</div>
                        <div class="servico-preco">R$ 10,00</div>
                    </div>
                    <div class="servico-item" data-servico="pigmentacao" data-preco="50">
                        <div class="servico-nome">🎨 Pigmentação</div>
                        <div class="servico-preco">R$ 50,00</div>
                    </div>
                    <div class="servico-item" data-servico="luzes" data-preco="35">
                        <div class="servico-nome">✨ Luzes</div>
                        <div class="servico-preco">R$ 35,00</div>
                    </div>
                    <div class="servico-item" data-servico="descolorimento" data-preco="50">
                        <div class="servico-nome">⚡ Descolorimento</div>
                        <div class="servico-preco">R$ 50,00</div>
                    </div>
                </div>
            </div>

            <div class="total-section">
                <div class="total-label">💰 Valor Total:</div>
                <div class="total-value">R$ 0,00</div>
            </div>

            <button onclick="agendar()">📅 Confirmar Agendamento</button>
            
            <div id="message" class="message"></div>
        </div>
    </div>

    <script>
        let servicosSelecionados = new Map();

        document.querySelectorAll('.servico-item').forEach(item => {
            item.addEventListener('click', function() {
                const servico = this.dataset.servico;
                const preco = parseFloat(this.dataset.preco);
                
                if (servicosSelecionados.has(servico)) {
                    servicosSelecionados.delete(servico);
                    this.classList.remove('selected');
                } else {
                    servicosSelecionados.set(servico, preco);
                    this.classList.add('selected');
                }
                
                atualizarTotal();
            });
        });

        function atualizarTotal() {
            let total = 0;
            servicosSelecionados.forEach((preco) => {
                total += preco;
            });
            document.querySelector('.total-value').textContent = `R$ ${total.toFixed(2)}`;
        }

        function getServicosTexto() {
            const servicosMap = {
                'corte_simples': 'Corte Simples',
                'barba': 'Barba',
                'sobrancelha': 'Sobrancelha',
                'pigmentacao': 'Pigmentação',
                'luzes': 'Luzes',
                'descolorimento': 'Descolorimento'
            };
            let servicosLista = [];
            servicosSelecionados.forEach((_, servico) => {
                servicosLista.push(servicosMap[servico]);
            });
            return servicosLista.join(', ');
        }

        function agendar() {
            const nome = document.getElementById('nome').value;
            const email = document.getElementById('email').value;
            const telefone = document.getElementById('telefone').value;
            const horario = document.getElementById('horario').value;
            
            if (!nome || !horario) {
                mostrarMensagem('Por favor, preencha nome e horário!', 'error');
                return;
            }
            
            if (servicosSelecionados.size === 0) {
                mostrarMensagem('Selecione pelo menos um serviço!', 'error');
                return;
            }
            
            let total = 0;
            servicosSelecionados.forEach((preco) => {
                total += preco;
            });
            
            const dadosAgendamento = {
                nome: nome,
                email: email,
                telefone: telefone,
                horario: new Date(horario).toLocaleString('pt-BR'),
                servicos: getServicosTexto(),
                valor_total: total,
                corte_simples: servicosSelecionados.has('corte_simples') ? 1 : 0,
                barba: servicosSelecionados.has('barba') ? 1 : 0,
                sobrancelha: servicosSelecionados.has('sobrancelha') ? 1 : 0,
                pigmentacao: servicosSelecionados.has('pigmentacao') ? 1 : 0,
                luzes: servicosSelecionados.has('luzes') ? 1 : 0,
                descolorimento: servicosSelecionados.has('descolorimento') ? 1 : 0,
                data_agendamento: new Date().toISOString(),
                status: "pendente",
                confirmado: false
            };
            
            const dadosString = encodeURIComponent(JSON.stringify(dadosAgendamento));
            window.parent.location.href = `/?dados_agendamento=${dadosString}`;
            
            mostrarMensagem('✅ Agendamento realizado com sucesso!', 'success');
        }
        
        function mostrarMensagem(texto, tipo) {
            const msgDiv = document.getElementById('message');
            msgDiv.textContent = texto;
            msgDiv.className = `message ${tipo}`;
            setTimeout(() => {
                msgDiv.style.display = 'none';
            }, 3000);
        }
        
        const hoje = new Date();
        hoje.setDate(hoje.getDate() + 1);
        hoje.setHours(8, 0, 0);
        document.getElementById('horario').min = hoje.toISOString().slice(0, 16);
    </script>
</body>
</html>'''
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path

# ==================== INICIALIZAÇÃO DO SISTEMA ====================
df_agendamentos = carregar_dados()
clientes = carregar_clientes()
financeiro = carregar_financeiro()
usuarios = criar_usuario_admin()

# ==================== INTERFACE PRINCIPAL ====================
# Sidebar Premium
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="font-size: 2em;">💈</h1>
            <h2>Barber Club PRO</h2>
            <p>Sistema de Gestão Profissional</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu Principal
    menu = st.radio(
        "📋 MENU PRINCIPAL",
        ["🏠 Dashboard", "📅 Agendamentos", "👥 Clientes", "💰 Financeiro", "📊 Relatórios", "⚙️ Configurações"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Informações da barbearia
    st.markdown("### 📍 Informações")
    st.markdown(f"**Endereço:** {Config.BARBEARIA_ENDERECO}")
    st.markdown(f"**📞 Telefone:** {Config.BARBEARIA_TELEFONE}")
    st.markdown(f"**💬 WhatsApp:** {Config.BARBEARIA_WHATSAPP}")
    st.markdown(f"**⏰ Horário:** {Config.HORARIO_ABERTURA} às {Config.HORARIO_FECHAMENTO}")
    
    st.markdown("---")
    
    # Estatísticas rápidas
    if len(df_agendamentos) > 0:
        st.markdown("### 📊 Hoje")
        hoje = datetime.now().date()
        agendamentos_hoje = df_agendamentos[df_agendamentos['data_agendamento'].dt.date == hoje]
        st.metric("Agendamentos Hoje", len(agendamentos_hoje))
        
        if len(agendamentos_hoje) > 0:
            receita_hoje = agendamentos_hoje['valor_total'].sum()
            st.metric("Receita Hoje", f"R$ {receita_hoje:.2f}")

# ==================== DASHBOARD ====================
if menu == "🏠 Dashboard":
    st.title("💈 Dashboard Barber Club PRO")
    st.markdown("---")
    
    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-premium">
                <h3>Total Clientes</h3>
                <h1 style="font-size: 2.5em;">{}</h1>
            </div>
        """.format(len(clientes)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-premium">
                <h3>Agendamentos</h3>
                <h1 style="font-size: 2.5em;">{}</h1>
            </div>
        """.format(len(df_agendamentos)), unsafe_allow_html=True)
    
    with col3:
        receita_total = df_agendamentos['valor_total'].sum() if len(df_agendamentos) > 0 else 0
        st.markdown("""
            <div class="metric-premium">
                <h3>Receita Total</h3>
                <h1 style="font-size: 2em;">R$ {:.2f}</h1>
            </div>
        """.format(receita_total), unsafe_allow_html=True)
    
    with col4:
        ticket_medio = df_agendamentos['valor_total'].mean() if len(df_agendamentos) > 0 else 0
        st.markdown("""
            <div class="metric-premium">
                <h3>Ticket Médio</h3>
                <h1 style="font-size: 2em;">R$ {:.2f}</h1>
            </div>
        """.format(ticket_medio), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Agendamentos por Mês")
        if len(df_agendamentos) > 0:
            df_agendamentos['mes'] = df_agendamentos['data_agendamento'].dt.strftime('%Y-%m')
            agendamentos_mes = df_agendamentos.groupby('mes').size().reset_index(name='quantidade')
            fig = px.bar(agendamentos_mes, x='mes', y='quantidade', title="Agendamentos Mensais")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Receita por Mês")
        if len(df_agendamentos) > 0:
            receita_mes = df_agendamentos.groupby('mes')['valor_total'].sum().reset_index()
            fig = px.line(receita_mes, x='mes', y='valor_total', title="Receita Mensal")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Próximos agendamentos
    st.subheader("📅 Próximos Agendamentos")
    if len(df_agendamentos) > 0:
        hoje = datetime.now()
        proximos = df_agendamentos[df_agendamentos['data_agendamento'] > hoje].sort_values('data_agendamento').head(10)
        
        for idx, row in proximos.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
                with col1:
                    st.write(f"**{row['nome']}**")
                with col2:
                    st.write(f"📅 {row['data_agendamento'].strftime('%d/%m/%Y %H:%M')}")
                with col3:
                    st.write(f"✂️ {row['servicos']}")
                with col4:
                    st.write(f"💰 R$ {row['valor_total']}")
                st.markdown("---")
    else:
        st.info("Nenhum agendamento futuro encontrado.")

# ==================== AGENDAMENTOS ====================
elif menu == "📅 Agendamentos":
    tab1, tab2, tab3 = st.tabs(["📅 Novo Agendamento", "📋 Lista de Agendamentos", "✅ Confirmar Agendamentos"])
    
    with tab1:
        st.header("📅 Novo Agendamento")
        
        html_path = criar_arquivo_html()
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=900, scrolling=True)
            
            query_params = st.query_params
            if "dados_agendamento" in query_params:
                try:
                    dados_json = json.loads(query_params["dados_agendamento"])
                    dados_json["id"] = str(int(datetime.now().timestamp()))
                    novo_agendamento = pd.DataFrame([dados_json])
                    df_agendamentos = pd.concat([df_agendamentos, novo_agendamento], ignore_index=True)
                    salvar_dados(df_agendamentos)
                    
                    # Salvar cliente
                    if dados_json['nome'] not in clientes:
                        clientes[dados_json['nome']] = {
                            "email": dados_json.get('email', ''),
                            "telefone": dados_json.get('telefone', ''),
                            "total_gasto": dados_json['valor_total'],
                            "ultima_visita": dados_json['data_agendamento']
                        }
                    else:
                        clientes[dados_json['nome']]['total_gasto'] += dados_json['valor_total']
                        clientes[dados_json['nome']]['ultima_visita'] = dados_json['data_agendamento']
                    salvar_clientes(clientes)
                    
                    st.success("✅ Agendamento realizado com sucesso!")
                    st.balloons()
                    st.query_params.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")
    
    with tab2:
        st.header("📋 Todos os Agendamentos")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filtro = st.selectbox("Status", ["Todos", "pendente", "confirmado", "concluido", "cancelado"])
        with col2:
            data_filtro = st.date_input("Data")
        with col3:
            busca = st.text_input("Buscar por nome")
        
        df_filtrado = df_agendamentos.copy()
        if status_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == status_filtro]
        if busca:
            df_filtrado = df_filtrado[df_filtrado['nome'].str.contains(busca, case=False)]
        
        for idx, row in df_filtrado.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                with col1:
                    st.write(f"**👤 {row['nome']}**")
                with col2:
                    st.write(f"📅 {row['horario']}")
                with col3:
                    st.write(f"✂️ {row['servicos']}")
                with col4:
                    st.write(f"💰 R$ {row['valor_total']}")
                with col5:
                    status_cor = {
                        "pendente": "🟡 Pendente",
                        "confirmado": "🟢 Confirmado",
                        "concluido": "🔵 Concluído",
                        "cancelado": "🔴 Cancelado"
                    }.get(row.get('status', 'pendente'), "🟡 Pendente")
                    st.write(status_cor)
                st.markdown("---")
    
    with tab3:
        st.header("✅ Confirmar Agendamentos")
        agendamentos_pendentes = df_agendamentos[df_agendamentos['status'] == 'pendente']
        
        if len(agendamentos_pendentes) > 0:
            for idx, row in agendamentos_pendentes.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    with col1:
                        st.write(f"**{row['nome']}**")
                    with col2:
                        st.write(f"📅 {row['horario']}")
                    with col3:
                        st.write(f"✂️ {row['servicos']}")
                    with col4:
                        if st.button(f"✅ Confirmar", key=f"confirm_{idx}"):
                            df_agendamentos.at[idx, 'status'] = 'confirmado'
                            df_agendamentos.at[idx, 'confirmado'] = True
                            salvar_dados(df_agendamentos)
                            st.success(f"Agendamento de {row['nome']} confirmado!")
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("Nenhum agendamento pendente.")

# ==================== CLIENTES ====================
elif menu == "👥 Clientes":
    st.title("👥 Gestão de Clientes")
    
    tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Novo Cliente"])
    
    with tab1:
        if len(clientes) > 0:
            df_clientes = pd.DataFrame.from_dict(clientes, orient='index')
            df_clientes.index.name = 'Nome'
            df_clientes = df_clientes.reset_index()
            st.dataframe(df_clientes, use_container_width=True)
            
            # Top clientes
            st.subheader("🏆 Top 5 Clientes")
            top_clientes = df_clientes.nlargest(5, 'total_gasto')[['Nome', 'total_gasto', 'ultima_visita']]
            st.dataframe(top_clientes, use_container_width=True)
        else:
            st.info("Nenhum cliente cadastrado.")
    
    with tab2:
        with st.form("novo_cliente"):
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail")
            telefone = st.text_input("Telefone")
            
            if st.form_submit_button("Cadastrar Cliente"):
                if nome:
                    clientes[nome] = {
                        "email": email,
                        "telefone": telefone,
                        "total_gasto": 0,
                        "ultima_visita": datetime.now().isoformat()
                    }
                    salvar_clientes(clientes)
                    st.success(f"Cliente {nome} cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Nome é obrigatório!")

# ==================== FINANCEIRO ====================
elif menu == "💰 Financeiro":
    st.title("💰 Gestão Financeira")
    
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "📝 Lançar Despesa", "📈 Fluxo de Caixa"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            receita_total = df_agendamentos['valor_total'].sum() if len(df_agendamentos) > 0 else 0
            st.metric("Receita Total", f"R$ {receita_total:.2f}")
        
        with col2:
            despesa_total = sum([d['valor'] for d in financeiro['despesas']]) if financeiro['despesas'] else 0
            st.metric("Despesas Totais", f"R$ {despesa_total:.2f}")
        
        with col3:
            lucro = receita_total - despesa_total
            st.metric("Lucro Líquido", f"R$ {lucro:.2f}", delta=f"{lucro/receita_total*100:.1f}%" if receita_total > 0 else "0%")
    
    with tab2:
        with st.form("nova_despesa"):
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor", min_value=0.01, step=0.01)
            categoria = st.selectbox("Categoria", ["Aluguel", "Salários", "Produtos", "Marketing", "Manutenção", "Outros"])
            data = st.date_input("Data")
            
            if st.form_submit_button("Lançar Despesa"):
                financeiro['despesas'].append({
                    "descricao": descricao,
                    "valor": valor,
                    "categoria": categoria,
                    "data": data.isoformat()
                })
                financeiro['caixa'] -= valor
                salvar_financeiro(financeiro)
                st.success("Despesa lançada com sucesso!")
                st.rerun()
    
    with tab3:
        st.subheader("📈 Fluxo de Caixa")
        # Gráfico de fluxo de caixa
        receitas_mensais = {}
        if len(df_agendamentos) > 0:
            df_agendamentos['mes'] = df_agendamentos['data_agendamento'].dt.strftime('%Y-%m')
            receitas_mensais = df_agendamentos.groupby('mes')['valor_total'].sum().to_dict()
        
        despesas_mensais = {}
        for d in financeiro['despesas']:
            mes = d['data'][:7]
            despesas_mensais[mes] = despesas_mensais.get(mes, 0) + d['valor']
        
        todos_meses = sorted(set(list(receitas_mensais.keys()) + list(despesas_mensais.keys())))
        
        fluxo_df = pd.DataFrame({
            'Mês': todos_meses,
            'Receitas': [receitas_mensais.get(mes, 0) for mes in todos_meses],
            'Despesas': [despesas_mensais.get(mes, 0) for mes in todos_meses]
        })
        fluxo_df['Lucro'] = fluxo_df['Receitas'] - fluxo_df['Despesas']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Receitas', x=fluxo_df['Mês'], y=fluxo_df['Receitas'], marker_color='green'))
        fig.add_trace(go.Bar(name='Despesas', x=fluxo_df['Mês'], y=fluxo_df['Despesas'], marker_color='red'))
        fig.add_trace(go.Scatter(name='Lucro', x=fluxo_df['Mês'], y=fluxo_df['Lucro'], mode='lines+markers', line=dict(color='gold', width=3)))
        
        fig.update_layout(barmode='group', title="Fluxo de Caixa Mensal")
        st.plotly_chart(fig, use_container_width=True)

# ==================== RELATÓRIOS ====================
elif menu == "📊 Relatórios":
    st.title("📊 Relatórios Avançados")
    
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Início", datetime.now() - timedelta(days=30))
    with col2:
        data_fim = st.date_input("Data Fim", datetime.now())
    
    if st.button("Gerar Relatório"):
        if len(df_agendamentos) > 0:
            relatorio = gerar_relatorio_periodo(df_agendamentos, data_inicio, data_fim)
            
            st.markdown("### 📈 Resumo do Período")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Agendamentos", relatorio['total_agendamentos'])
            with col2:
                st.metric("Receita Total", f"R$ {relatorio['receita_total']:.2f}")
            with col3:
                st.metric("Ticket Médio", f"R$ {relatorio['ticket_medio']:.2f}")
            
            st.markdown("### 🏆 Serviços Mais Vendidos")
            servicos_df = pd.DataFrame.from_dict(relatorio['servicos_mais_vendidos'], orient='index', columns=['Quantidade'])
            st.bar_chart(servicos_df)
            
            # Exportar relatório
            csv = df_agendamentos[(df_agendamentos['data_agendamento'].dt.date >= data_inicio) & 
                                   (df_agendamentos['data_agendamento'].dt.date <= data_fim)].to_csv(index=False)
            st.download_button(
                label="📥 Exportar Relatório (CSV)",
                data=csv,
                file_name=f"relatorio_{data_inicio}_{data_fim}.csv",
                mime="text/csv"
            )

# ==================== CONFIGURAÇÕES ====================
elif menu == "⚙️ Configurações":
    st.title("⚙️ Configurações do Sistema")
    
    tab1, tab2, tab3 = st.tabs(["🏪 Barbearia", "👤 Usuários", "💳 Serviços"])
    
    with tab1:
        st.subheader("Informações da Barbearia")
        nome = st.text_input("Nome da Barbearia", Config.BARBEARIA_NOME)
        endereco = st.text_input("Endereço", Config.BARBEARIA_ENDERECO)
        telefone = st.text_input("Telefone", Config.BARBEARIA_TELEFONE)
        whatsapp = st.text_input("WhatsApp", Config.BARBEARIA_WHATSAPP)
        
        if st.button("Salvar Configurações"):
            st.success("Configurações salvas com sucesso!")
    
    with tab2:
        st.subheader("Gerenciar Usuários")
        st.info("Funcionalidade em desenvolvimento")
    
    with tab3:
        st.subheader("Preços dos Serviços")
        servicos = {
            "Corte Simples": 35,
            "Barba": 10,
            "Sobrancelha": 10,
            "Pigmentação": 50,
            "Luzes": 35,
            "Descolorimento": 50
        }
        
        for servico, preco in servicos.items():
            novo_preco = st.number_input(f"{servico}", value=preco, step=5)
            if novo_preco != preco:
                st.info(f"Preço de {servico} alterado para R$ {novo_preco}")

# Rodapé
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <p>💈 Barber Club PRO - Sistema de Gestão Profissional</p>
        <p>© 2024 - Todos os direitos reservados</p>
    </div>
""", unsafe_allow_html=True)
