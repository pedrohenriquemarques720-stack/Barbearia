import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os
import json
import hashlib
from datetime import datetime, timedelta
import base64

# Configuração da página MUST BE FIRST
st.set_page_config(
    page_title="Barber Club PRO - Sistema de Gestão",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CORES PROFISSIONAL BARBEARIA ====================
CORES = {
    "primary": "#8B0000",      # Vermelho sangue
    "secondary": "#D4AF37",    # Dourado
    "dark": "#1C1C1C",         # Preto carvão
    "medium": "#2C2C2C",       # Cinza escuro
    "light": "#3C3C3C",        # Cinza médio
    "text": "#FFFFFF",          # Branco
    "text_dark": "#E0E0E0",     # Cinza claro
    "success": "#28A745",       # Verde
    "warning": "#FFC107",       # Amarelo
    "danger": "#DC3545"         # Vermelho
}

# CSS Responsivo para Celular e Desktop
st.markdown(f"""
    <style>
    /* Reset e estilos globais */
    .stApp {{
        background: linear-gradient(135deg, {CORES['dark']} 0%, {CORES['medium']} 100%);
    }}
    
    /* Responsividade para celular */
    @media (max-width: 768px) {{
        .stApp {{
            padding: 0px;
        }}
        .main .block-container {{
            padding: 1rem;
        }}
        h1 {{
            font-size: 1.8rem !important;
        }}
        h2 {{
            font-size: 1.4rem !important;
        }}
        .stMetric {{
            margin-bottom: 0.5rem;
        }}
    }}
    
    /* Cards premium */
    .premium-card {{
        background: linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(44,44,44,0.9) 100%);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid {CORES['secondary']};
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.5);
        transition: transform 0.3s ease;
    }}
    
    .premium-card:hover {{
        transform: translateY(-5px);
        border: 1px solid {CORES['primary']};
    }}
    
    /* Métricas premium */
    .metric-premium {{
        background: linear-gradient(135deg, {CORES['primary']} 0%, {CORES['secondary']} 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(139,0,0,0.3);
    }}
    
    /* Botões */
    .stButton > button {{
        background: linear-gradient(135deg, {CORES['primary']} 0%, {CORES['secondary']} 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(139,0,0,0.4);
    }}
    
    /* Títulos */
    h1, h2, h3 {{
        background: linear-gradient(135deg, {CORES['secondary']} 0%, {CORES['primary']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }}
    
    /* Sidebar responsiva */
    .css-1d391kg {{
        background: linear-gradient(180deg, {CORES['dark']} 0%, {CORES['medium']} 100%);
    }}
    
    @media (max-width: 768px) {{
        .css-1d391kg {{
            width: 250px;
        }}
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {{
        background-color: {CORES['light']};
        color: white;
        border: 1px solid {CORES['secondary']};
        border-radius: 10px;
    }}
    
    /* Tabelas responsivas */
    .dataframe {{
        background: rgba(0,0,0,0.7);
        border-radius: 10px;
        color: white;
        overflow-x: auto;
        font-size: 14px;
    }}
    
    @media (max-width: 768px) {{
        .dataframe {{
            font-size: 12px;
        }}
        .dataframe td, .dataframe th {{
            padding: 8px 4px;
        }}
    }}
    
    /* Tabs responsivas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        flex-wrap: wrap;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 8px 16px;
        font-size: 14px;
    }}
    
    @media (max-width: 768px) {{
        .stTabs [data-baseweb="tab"] {{
            padding: 6px 12px;
            font-size: 12px;
        }}
    }}
    
    /* Mensagens */
    .stAlert {{
        border-radius: 10px;
    }}
    
    /* Animações */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.5s ease;
    }}
    </style>
""", unsafe_allow_html=True)

# ==================== BANCO DE DADOS SQLITE ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('barber_club.db', check_same_thread=False)
        self.criar_tabelas()
    
    def criar_tabelas(self):
        cursor = self.conn.cursor()
        
        # Tabela de agendamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                nome TEXT NOT NULL,
                email TEXT,
                telefone TEXT,
                data_horario DATETIME NOT NULL,
                servicos TEXT NOT NULL,
                valor_total REAL NOT NULL,
                corte_simples INTEGER DEFAULT 0,
                barba INTEGER DEFAULT 0,
                sobrancelha INTEGER DEFAULT 0,
                pigmentacao INTEGER DEFAULT 0,
                luzes INTEGER DEFAULT 0,
                descolorimento INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pendente',
                observacoes TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                confirmado INTEGER DEFAULT 0
            )
        ''')
        
        # Tabela de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                email TEXT,
                telefone TEXT,
                data_nascimento DATE,
                total_gasto REAL DEFAULT 0,
                ultima_visita DATETIME,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                pontos INTEGER DEFAULT 0,
                observacoes TEXT
            )
        ''')
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nome TEXT NOT NULL,
                nivel TEXT DEFAULT 'user',
                ativo INTEGER DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de serviços
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                preco REAL NOT NULL,
                duracao INTEGER DEFAULT 30,
                ativo INTEGER DEFAULT 1
            )
        ''')
        
        # Tabela de despesas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                categoria TEXT,
                data DATE NOT NULL,
                observacoes TEXT
            )
        ''')
        
        # Inserir serviços padrão se não existirem
        servicos_padrao = [
            ("Corte Simples", 35, 30),
            ("Barba", 10, 20),
            ("Sobrancelha", 10, 15),
            ("Pigmentação", 50, 60),
            ("Luzes", 35, 45),
            ("Descolorimento", 50, 60)
        ]
        
        for servico in servicos_padrao:
            cursor.execute('''
                INSERT OR IGNORE INTO servicos (nome, preco, duracao)
                VALUES (?, ?, ?)
            ''', servico)
        
        # Inserir usuário admin padrão
        cursor.execute('''
            INSERT OR IGNORE INTO usuarios (username, senha, nome, nivel)
            VALUES (?, ?, ?, ?)
        ''', ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'Administrador', 'admin'))
        
        self.conn.commit()
    
    def inserir_agendamento(self, dados):
        cursor = self.conn.cursor()
        
        # Verificar se cliente existe
        cursor.execute('SELECT id FROM clientes WHERE nome = ?', (dados['nome'],))
        cliente = cursor.fetchone()
        
        if cliente:
            cliente_id = cliente[0]
            # Atualizar dados do cliente
            cursor.execute('''
                UPDATE clientes 
                SET email = ?, telefone = ?, total_gasto = total_gasto + ?, ultima_visita = ?
                WHERE id = ?
            ''', (dados.get('email', ''), dados.get('telefone', ''), dados['valor_total'], dados['data_horario'], cliente_id))
        else:
            # Criar novo cliente
            cursor.execute('''
                INSERT INTO clientes (nome, email, telefone, total_gasto, ultima_visita)
                VALUES (?, ?, ?, ?, ?)
            ''', (dados['nome'], dados.get('email', ''), dados.get('telefone', ''), dados['valor_total'], dados['data_horario']))
            cliente_id = cursor.lastrowid
        
        # Inserir agendamento
        cursor.execute('''
            INSERT INTO agendamentos (
                cliente_id, nome, email, telefone, data_horario, servicos, valor_total,
                corte_simples, barba, sobrancelha, pigmentacao, luzes, descolorimento, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cliente_id, dados['nome'], dados.get('email', ''), dados.get('telefone', ''),
            dados['data_horario'], dados['servicos'], dados['valor_total'],
            dados.get('corte_simples', 0), dados.get('barba', 0), dados.get('sobrancelha', 0),
            dados.get('pigmentacao', 0), dados.get('luzes', 0), dados.get('descolorimento', 0),
            dados.get('status', 'pendente')
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def listar_agendamentos(self, status=None, data_inicio=None, data_fim=None):
        cursor = self.conn.cursor()
        query = 'SELECT * FROM agendamentos WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        if data_inicio:
            query += ' AND date(data_horario) >= ?'
            params.append(data_inicio)
        if data_fim:
            query += ' AND date(data_horario) <= ?'
            params.append(data_fim)
        
        query += ' ORDER BY data_horario DESC'
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def listar_clientes(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM clientes ORDER BY total_gasto DESC')
        return cursor.fetchall()
    
    def listar_servicos(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM servicos WHERE ativo = 1')
        return cursor.fetchall()
    
    def inserir_despesa(self, descricao, valor, categoria, data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO despesas (descricao, valor, categoria, data)
            VALUES (?, ?, ?, ?)
        ''', (descricao, valor, categoria, data))
        self.conn.commit()
    
    def listar_despesas(self, data_inicio=None, data_fim=None):
        cursor = self.conn.cursor()
        query = 'SELECT * FROM despesas WHERE 1=1'
        params = []
        
        if data_inicio:
            query += ' AND data >= ?'
            params.append(data_inicio)
        if data_fim:
            query += ' AND data <= ?'
            params.append(data_fim)
        
        query += ' ORDER BY data DESC'
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def atualizar_status_agendamento(self, id_agendamento, status):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE agendamentos SET status = ? WHERE id = ?', (status, id_agendamento))
        self.conn.commit()
    
    def get_estatisticas(self):
        cursor = self.conn.cursor()
        
        # Total de clientes
        cursor.execute('SELECT COUNT(*) FROM clientes')
        total_clientes = cursor.fetchone()[0]
        
        # Total de agendamentos
        cursor.execute('SELECT COUNT(*) FROM agendamentos')
        total_agendamentos = cursor.fetchone()[0]
        
        # Receita total
        cursor.execute('SELECT SUM(valor_total) FROM agendamentos')
        receita_total = cursor.fetchone()[0] or 0
        
        # Agendamentos hoje
        hoje = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*), SUM(valor_total) FROM agendamentos WHERE date(data_horario) = ?', (hoje,))
        hoje_result = cursor.fetchone()
        agendamentos_hoje = hoje_result[0] or 0
        receita_hoje = hoje_result[1] or 0
        
        return {
            'total_clientes': total_clientes,
            'total_agendamentos': total_agendamentos,
            'receita_total': receita_total,
            'agendamentos_hoje': agendamentos_hoje,
            'receita_hoje': receita_hoje
        }

# Inicializar banco de dados
db = Database()

# ==================== FUNÇÃO DO HTML RESPONSIVO ====================
def criar_arquivo_html():
    html_path = "agendamento.html"
    
    html_content = f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>Barber Club PRO - Agendamento</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #1C1C1C 0%, #2C2C2C 100%);
            padding: 16px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 500px;
            margin: 0 auto;
            background: rgba(0,0,0,0.9);
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
            overflow: hidden;
            border: 1px solid #D4AF37;
        }}

        @media (min-width: 768px) {{
            .container {{
                max-width: 800px;
            }}
            body {{
                padding: 40px;
            }}
        }}

        .header {{
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 1.8rem;
            margin-bottom: 8px;
            font-weight: 800;
        }}

        .header p {{
            font-size: 0.9rem;
            opacity: 0.95;
        }}

        @media (min-width: 768px) {{
            .header h1 {{
                font-size: 2.5rem;
            }}
            .header p {{
                font-size: 1rem;
            }}
        }}

        .form-content {{
            padding: 20px;
        }}

        @media (min-width: 768px) {{
            .form-content {{
                padding: 30px;
            }}
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #D4AF37;
            font-size: 0.9rem;
        }}

        input, select {{
            width: 100%;
            padding: 12px;
            background: #3C3C3C;
            border: 2px solid #D4AF37;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
            color: white;
            -webkit-appearance: none;
        }}

        input:focus, select:focus {{
            outline: none;
            border-color: #8B0000;
            background: #2C2C2C;
        }}

        .servicos-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
            margin-top: 10px;
        }}

        @media (min-width: 768px) {{
            .servicos-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        .servico-item {{
            background: #2C2C2C;
            border: 2px solid #D4AF37;
            border-radius: 12px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
            color: white;
        }}

        .servico-item:active {{
            transform: scale(0.98);
        }}

        .servico-item.selected {{
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
            border-color: #D4AF37;
            color: white;
        }}

        .servico-nome {{
            font-weight: bold;
            font-size: 1rem;
            margin-bottom: 5px;
        }}

        .servico-preco {{
            font-size: 1.2rem;
            color: #D4AF37;
            font-weight: bold;
        }}

        .servico-item.selected .servico-preco {{
            color: white;
        }}

        .total-section {{
            background: linear-gradient(135deg, #2C2C2C 0%, #1C1C1C 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
            border: 1px solid #D4AF37;
        }}

        .total-value {{
            font-size: 2rem;
            color: #D4AF37;
            font-weight: bold;
        }}

        @media (min-width: 768px) {{
            .total-value {{
                font-size: 2.5rem;
            }}
        }}

        button {{
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            -webkit-tap-highlight-color: transparent;
        }}

        button:active {{
            transform: scale(0.98);
        }}

        .message {{
            margin-top: 20px;
            padding: 12px;
            border-radius: 10px;
            display: none;
            text-align: center;
            font-size: 14px;
        }}

        .message.success {{
            background: #28A745;
            color: white;
            display: block;
        }}

        .message.error {{
            background: #DC3545;
            color: white;
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💈 Barber Club PRO</h1>
            <p>Agendamento Premium</p>
        </div>
        
        <div class="form-content">
            <div class="form-group">
                <label>👤 Seu Nome *</label>
                <input type="text" id="nome" placeholder="Digite seu nome completo" required>
            </div>
            
            <div class="form-group">
                <label>📧 E-mail</label>
                <input type="email" id="email" placeholder="seuemail@exemplo.com">
            </div>
            
            <div class="form-group">
                <label>📱 WhatsApp</label>
                <input type="tel" id="telefone" placeholder="(11) 99999-9999">
            </div>

            <div class="form-group">
                <label>🕐 Data e Horário *</label>
                <input type="datetime-local" id="horario" required>
            </div>

            <div class="form-group">
                <label>✂️ Selecione os Serviços *</label>
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

        document.querySelectorAll('.servico-item').forEach(item => {{
            item.addEventListener('click', function(e) {{
                e.preventDefault();
                const servico = this.dataset.servico;
                const preco = parseFloat(this.dataset.preco);
                
                if (servicosSelecionados.has(servico)) {{
                    servicosSelecionados.delete(servico);
                    this.classList.remove('selected');
                }} else {{
                    servicosSelecionados.set(servico, preco);
                    this.classList.add('selected');
                }}
                
                atualizarTotal();
            }});
        }});

        function atualizarTotal() {{
            let total = 0;
            servicosSelecionados.forEach((preco) => {{
                total += preco;
            }});
            document.querySelector('.total-value').textContent = `R$ ${{total.toFixed(2)}}`;
        }}

        function getServicosTexto() {{
            const servicosMap = {{
                'corte_simples': 'Corte Simples',
                'barba': 'Barba',
                'sobrancelha': 'Sobrancelha',
                'pigmentacao': 'Pigmentação',
                'luzes': 'Luzes',
                'descolorimento': 'Descolorimento'
            }};
            let servicosLista = [];
            servicosSelecionados.forEach((_, servico) => {{
                servicosLista.push(servicosMap[servico]);
            }});
            return servicosLista.join(', ');
        }}

        function agendar() {{
            const nome = document.getElementById('nome').value;
            const email = document.getElementById('email').value;
            const telefone = document.getElementById('telefone').value;
            const horario = document.getElementById('horario').value;
            
            if (!nome || !horario) {{
                mostrarMensagem('Por favor, preencha nome e horário!', 'error');
                return;
            }}
            
            if (servicosSelecionados.size === 0) {{
                mostrarMensagem('Selecione pelo menos um serviço!', 'error');
                return;
            }}
            
            let total = 0;
            servicosSelecionados.forEach((preco) => {{
                total += preco;
            }});
            
            const dadosAgendamento = {{
                nome: nome,
                email: email,
                telefone: telefone,
                data_horario: new Date(horario).toISOString(),
                servicos: getServicosTexto(),
                valor_total: total,
                corte_simples: servicosSelecionados.has('corte_simples') ? 1 : 0,
                barba: servicosSelecionados.has('barba') ? 1 : 0,
                sobrancelha: servicosSelecionados.has('sobrancelha') ? 1 : 0,
                pigmentacao: servicosSelecionados.has('pigmentacao') ? 1 : 0,
                luzes: servicosSelecionados.has('luzes') ? 1 : 0,
                descolorimento: servicosSelecionados.has('descolorimento') ? 1 : 0,
                status: "pendente"
            }};
            
            const dadosString = encodeURIComponent(JSON.stringify(dadosAgendamento));
            window.parent.location.href = `/?dados_agendamento=${{dadosString}}`;
            
            mostrarMensagem('✅ Agendamento realizado com sucesso!', 'success');
        }}
        
        function mostrarMensagem(texto, tipo) {{
            const msgDiv = document.getElementById('message');
            msgDiv.textContent = texto;
            msgDiv.className = `message ${{tipo}}`;
            setTimeout(() => {{
                msgDiv.style.display = 'none';
            }}, 3000);
        }}
        
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

# ==================== INTERFACE PRINCIPAL ====================
# Sidebar Premium
with st.sidebar:
    st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <h1 style="font-size: 3em; color: {CORES['secondary']};">💈</h1>
            <h2 style="color: {CORES['secondary']};">Barber Club PRO</h2>
            <p style="color: white;">Sistema de Gestão</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu Principal
    menu = st.radio(
        "📋 MENU",
        ["🏠 Dashboard", "📅 Agendamentos", "👥 Clientes", "💰 Financeiro", "📊 Relatórios", "⚙️ Configurações"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Informações
    st.markdown(f"<h3 style='color: {CORES['secondary']}; font-size: 1rem;'>📍 Info</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: white; font-size: 0.8rem;'>Av. Principal, 123<br>SP - Brasil</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: white; font-size: 0.8rem;'>📞 (11) 99999-9999</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Estatísticas rápidas
    stats = db.get_estatisticas()
    st.markdown(f"<h3 style='color: {CORES['secondary']}; font-size: 1rem;'>📊 Hoje</h3>", unsafe_allow_html=True)
    st.metric("Agendamentos", stats['agendamentos_hoje'])
    st.metric("Receita", f"R$ {stats['receita_hoje']:.2f}")

# ==================== DASHBOARD ====================
if menu == "🏠 Dashboard":
    st.title("💈 Dashboard")
    st.markdown("---")
    
    stats = db.get_estatisticas()
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class="metric-premium">
                <h3>Clientes</h3>
                <h1 style="font-size: 2rem;">{stats['total_clientes']}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-premium">
                <h3>Agendamentos</h3>
                <h1 style="font-size: 2rem;">{stats['total_agendamentos']}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-premium">
                <h3>Receita Total</h3>
                <h1 style="font-size: 1.5rem;">R$ {stats['receita_total']:.2f}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        ticket_medio = stats['receita_total'] / stats['total_agendamentos'] if stats['total_agendamentos'] > 0 else 0
        st.markdown(f"""
            <div class="metric-premium">
                <h3>Ticket Médio</h3>
                <h1 style="font-size: 1.5rem;">R$ {ticket_medio:.2f}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Próximos agendamentos
    st.subheader("📅 Próximos Agendamentos")
    agendamentos = db.listar_agendamentos()
    hoje = datetime.now()
    proximos = [a for a in agendamentos if datetime.fromisoformat(a[5]) > hoje][:10]
    
    if proximos:
        for agendamento in proximos:
            with st.container():
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write(f"**👤 {agendamento[2]}**")
                    st.write(f"✂️ {agendamento[6]}")
                with col2:
                    st.write(f"📅 {datetime.fromisoformat(agendamento[5]).strftime('%d/%m/%Y %H:%M')}")
                    st.write(f"💰 R$ {agendamento[7]:.2f}")
                st.markdown("---")
    else:
        st.info("Nenhum agendamento futuro encontrado.")

# ==================== AGENDAMENTOS ====================
elif menu == "📅 Agendamentos":
    tab1, tab2 = st.tabs(["📅 Novo Agendamento", "📋 Lista"])
    
    with tab1:
        st.header("Novo Agendamento")
        
        html_path = criar_arquivo_html()
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=700, scrolling=True)
            
            query_params = st.query_params
            if "dados_agendamento" in query_params:
                try:
                    dados_json = json.loads(query_params["dados_agendamento"])
                    db.inserir_agendamento(dados_json)
                    st.success("✅ Agendamento realizado com sucesso!")
                    st.balloons()
                    st.query_params.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    with tab2:
        st.header("Lista de Agendamentos")
        
        status_filtro = st.selectbox("Filtrar por Status", ["Todos", "pendente", "confirmado", "concluido", "cancelado"])
        
        agendamentos = db.listar_agendamentos(status_filtro if status_filtro != "Todos" else None)
        
        if agendamentos:
            for agendamento in agendamentos:
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**👤 {agendamento[2]}**")
                        st.write(f"✂️ {agendamento[6]}")
                    with col2:
                        st.write(f"📅 {datetime.fromisoformat(agendamento[5]).strftime('%d/%m/%Y %H:%M')}")
                        st.write(f"💰 R$ {agendamento[7]:.2f}")
                        status_cor = {
                            "pendente": "🟡 Pendente",
                            "confirmado": "🟢 Confirmado",
                            "concluido": "🔵 Concluído",
                            "cancelado": "🔴 Cancelado"
                        }.get(agendamento[13], "🟡 Pendente")
                        st.write(status_cor)
                        
                        if agendamento[13] == "pendente":
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ Confirmar", key=f"conf_{agendamento[0]}"):
                                    db.atualizar_status_agendamento(agendamento[0], "confirmado")
                                    st.rerun()
                            with col2:
                                if st.button("❌ Cancelar", key=f"cancel_{agendamento[0]}"):
                                    db.atualizar_status_agendamento(agendamento[0], "cancelado")
                                    st.rerun()
                    st.markdown("---")
        else:
            st.info("Nenhum agendamento encontrado.")

# ==================== CLIENTES ====================
elif menu == "👥 Clientes":
    st.title("👥 Clientes")
    
    clientes = db.listar_clientes()
    
    if clientes:
        for cliente in clientes:
            with st.container():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**👤 {cliente[1]}**")
                    st.write(f"📧 {cliente[2] if cliente[2] else 'Não informado'}")
                    st.write(f"📞 {cliente[3] if cliente[3] else 'Não informado'}")
                with col2:
                    st.write(f"💰 Total: R$ {cliente[5]:.2f}")
                    if cliente[6]:
                        st.write(f"📅 Última visita: {datetime.fromisoformat(cliente[6]).strftime('%d/%m/%Y')}")
                st.markdown("---")
    else:
        st.info("Nenhum cliente cadastrado.")

# ==================== FINANCEIRO ====================
elif menu == "💰 Financeiro":
    st.title("💰 Financeiro")
    
    tab1, tab2 = st.tabs(["📊 Visão Geral", "📝 Despesas"])
    
    with tab1:
        stats = db.get_estatisticas()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Receita Total", f"R$ {stats['receita_total']:.2f}")
        with col2:
            despesas = db.listar_despesas()
            despesa_total = sum(d[2] for d in despesas) if despesas else 0
            st.metric("Despesas Totais", f"R$ {despesa_total:.2f}")
        
        lucro = stats['receita_total'] - despesa_total
        st.metric("Lucro Líquido", f"R$ {lucro:.2f}")
    
    with tab2:
        with st.form("nova_despesa"):
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor", min_value=0.01, step=0.01)
            categoria = st.selectbox("Categoria", ["Aluguel", "Salários", "Produtos", "Marketing", "Manutenção", "Outros"])
            data = st.date_input("Data")
            
            if st.form_submit_button("Lançar Despesa"):
                if descricao and valor > 0:
                    db.inserir_despesa(descricao, valor, categoria, data)
                    st.success("Despesa lançada!")
                    st.rerun()

# ==================== RELATÓRIOS ====================
elif menu == "📊 Relatórios":
    st.title("📊 Relatórios")
    
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Início", datetime.now() - timedelta(days=30))
    with col2:
        data_fim = st.date_input("Data Fim", datetime.now())
    
    if st.button("Gerar Relatório"):
        agendamentos = db.listar_agendamentos(data_inicio=data_inicio, data_fim=data_fim)
        
        if agendamentos:
            total = len(agendamentos)
            receita = sum(a[7] for a in agendamentos)
            ticket = receita / total if total > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", total)
            with col2:
                st.metric("Receita", f"R$ {receita:.2f}")
            with col3:
                st.metric("Ticket Médio", f"R$ {ticket:.2f}")
            
            # Exportar
            df = pd.DataFrame(agendamentos, columns=['id', 'cliente_id', 'nome', 'email', 'telefone', 
                                                       'data_horario', 'servicos', 'valor_total',
                                                       'corte_simples', 'barba', 'sobrancelha', 
                                                       'pigmentacao', 'luzes', 'descolorimento', 
                                                       'status', 'observacoes', 'data_criacao', 'confirmado'])
            csv = df.to_csv(index=False)
            st.download_button("📥 Exportar CSV", csv, f"relatorio_{data_inicio}_{data_fim}.csv", "text/csv")
        else:
            st.info("Nenhum dado no período")

# ==================== CONFIGURAÇÕES ====================
elif menu == "⚙️ Configurações":
    st.title("⚙️ Configurações")
    
    tab1, tab2 = st.tabs(["💳 Serviços", "ℹ️ Sobre"])
    
    with tab1:
        servicos = db.listar_servicos()
        for servico in servicos:
            novo_preco = st.number_input(f"{servico[1]}", value=servico[2], step=5, key=f"serv_{servico[0]}")
            if novo_preco != servico[2]:
                cursor = db.conn.cursor()
                cursor.execute('UPDATE servicos SET preco = ? WHERE id = ?', (novo_preco, servico[0]))
                db.conn.commit()
                st.success(f"Preço atualizado!")
    
    with tab2:
        st.info("""
            **Barber Club PRO v1.0**
            
            Sistema de Gestão Profissional para Barbearias
            
            Funcionalidades:
            - Agendamento Online
            - Gestão de Clientes
            - Controle Financeiro
            - Relatórios Completos
            - Banco de Dados SQLite
            
            Desenvolvido para barbearias profissionais
        """)

# Rodapé
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <p style="color: {CORES['secondary']};">💈 Barber Club PRO</p>
        <p style="color: white; font-size: 0.8rem;">© 2024 - Sistema de Gestão Profissional</p>
    </div>
""", unsafe_allow_html=True)
