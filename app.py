import streamlit as st
import sqlite3
import json
import pandas as pd
from datetime import datetime
import hashlib
import os

# Configuração da página
st.set_page_config(
    page_title="Barber Club PRO",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS para esconder sidebar e centralizar conteúdo
st.markdown("""
    <style>
        /* Esconder sidebar completamente */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        /* Remover espaçamento da sidebar */
        .main > div {
            padding-left: 0rem;
            padding-right: 0rem;
        }
        
        /* Centralizar conteúdo */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }
        
        /* Esconder elementos padrão do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Estilos gerais */
        .stApp {
            background: linear-gradient(135deg, #1C1C1C 0%, #2C2C2C 100%);
        }
        
        /* Títulos */
        h1, h2, h3 {
            background: linear-gradient(135deg, #D4AF37 0%, #8B0000 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
        
        /* Cards */
        .premium-card {
            background: linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(44,44,44,0.9) 100%);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #D4AF37;
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.5);
        }
        
        /* Botões */
        .stButton > button {
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 25px;
            font-weight: bold;
            width: 100%;
        }
        
        /* Métricas */
        .metric-premium {
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: white;
        }
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {
            background-color: #3C3C3C;
            color: white;
            border: 1px solid #D4AF37;
            border-radius: 10px;
        }
        
        /* Tabelas */
        .dataframe {
            background: rgba(0,0,0,0.7);
            border-radius: 10px;
            color: white;
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .block-container {
                padding: 1rem;
            }
            h1 { font-size: 1.8rem; }
            h2 { font-size: 1.4rem; }
        }
    </style>
""", unsafe_allow_html=True)

# ==================== BANCO DE DADOS ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('barber_club.db', check_same_thread=False)
        self.criar_tabelas()
    
    def criar_tabelas(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                email TEXT,
                telefone TEXT,
                total_gasto REAL DEFAULT 0,
                ultima_visita DATETIME,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                categoria TEXT,
                data DATE NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def inserir_agendamento(self, dados):
        cursor = self.conn.cursor()
        
        # Atualizar cliente
        cursor.execute('SELECT id FROM clientes WHERE nome = ?', (dados['nome'],))
        cliente = cursor.fetchone()
        
        if cliente:
            cursor.execute('''
                UPDATE clientes 
                SET email = ?, telefone = ?, total_gasto = total_gasto + ?, ultima_visita = ?
                WHERE id = ?
            ''', (dados.get('email', ''), dados.get('telefone', ''), dados['valor_total'], dados['data_horario'], cliente[0]))
        else:
            cursor.execute('''
                INSERT INTO clientes (nome, email, telefone, total_gasto, ultima_visita)
                VALUES (?, ?, ?, ?, ?)
            ''', (dados['nome'], dados.get('email', ''), dados.get('telefone', ''), dados['valor_total'], dados['data_horario']))
        
        # Inserir agendamento
        cursor.execute('''
            INSERT INTO agendamentos (
                nome, email, telefone, data_horario, servicos, valor_total,
                corte_simples, barba, sobrancelha, pigmentacao, luzes, descolorimento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados['nome'], dados.get('email', ''), dados.get('telefone', ''),
            dados['data_horario'], dados['servicos'], dados['valor_total'],
            dados.get('corte_simples', 0), dados.get('barba', 0), dados.get('sobrancelha', 0),
            dados.get('pigmentacao', 0), dados.get('luzes', 0), dados.get('descolorimento', 0)
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def listar_agendamentos(self, status=None):
        cursor = self.conn.cursor()
        if status:
            cursor.execute('SELECT * FROM agendamentos WHERE status = ? ORDER BY data_horario DESC', (status,))
        else:
            cursor.execute('SELECT * FROM agendamentos ORDER BY data_horario DESC')
        return cursor.fetchall()
    
    def listar_clientes(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM clientes ORDER BY total_gasto DESC')
        return cursor.fetchall()
    
    def listar_despesas(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM despesas ORDER BY data DESC')
        return cursor.fetchall()
    
    def inserir_despesa(self, descricao, valor, categoria, data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO despesas (descricao, valor, categoria, data)
            VALUES (?, ?, ?, ?)
        ''', (descricao, valor, categoria, data))
        self.conn.commit()
    
    def atualizar_status(self, id_agendamento, status):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE agendamentos SET status = ? WHERE id = ?', (status, id_agendamento))
        self.conn.commit()
    
    def get_estatisticas(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clientes')
        total_clientes = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM agendamentos')
        total_agendamentos = cursor.fetchone()[0]
        cursor.execute('SELECT SUM(valor_total) FROM agendamentos')
        receita_total = cursor.fetchone()[0] or 0
        return {
            'total_clientes': total_clientes,
            'total_agendamentos': total_agendamentos,
            'receita_total': receita_total
        }

db = Database()

# ==================== HTML COMPLETO ====================
def get_html_content(active_page="dashboard"):
    html = f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>Barber Club PRO</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #1C1C1C 0%, #2C2C2C 100%);
            min-height: 100vh;
        }}
        
        /* Top Navigation */
        .top-nav {{
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
            padding: 12px 20px;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .logo {{
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
        }}
        
        .logo span {{
            color: #D4AF37;
        }}
        
        .nav-links {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .nav-btn {{
            background: rgba(0,0,0,0.3);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }}
        
        .nav-btn:hover, .nav-btn.active {{
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .nav-container {{
                flex-direction: column;
            }}
            .nav-links {{
                justify-content: center;
            }}
            .nav-btn {{
                padding: 6px 12px;
                font-size: 12px;
            }}
        }}
        
        /* Main Content */
        .main-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Cards */
        .card {{
            background: rgba(0,0,0,0.8);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #D4AF37;
        }}
        
        .card-title {{
            color: #D4AF37;
            font-size: 1.2rem;
            margin-bottom: 15px;
            font-weight: bold;
        }}
        
        /* Grid */
        .grid-2, .grid-3, .grid-4 {{
            display: grid;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
        .grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
        .grid-4 {{ grid-template-columns: repeat(4, 1fr); }}
        
        @media (max-width: 768px) {{
            .grid-2, .grid-3, .grid-4 {{ grid-template-columns: 1fr; }}
        }}
        
        /* Metric Cards */
        .metric-card {{
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: white;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        /* Form */
        .form-group {{
            margin-bottom: 20px;
        }}
        
        label {{
            display: block;
            margin-bottom: 8px;
            color: #D4AF37;
            font-weight: bold;
        }}
        
        input, select {{
            width: 100%;
            padding: 12px;
            background: #3C3C3C;
            border: 2px solid #D4AF37;
            border-radius: 10px;
            color: white;
            font-size: 16px;
        }}
        
        input:focus, select:focus {{
            outline: none;
            border-color: #8B0000;
        }}
        
        button {{
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
        }}
        
        button:active {{
            transform: scale(0.98);
        }}
        
        /* Services Grid */
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .service-item {{
            background: #2C2C2C;
            border: 2px solid #D4AF37;
            border-radius: 12px;
            padding: 15px;
            cursor: pointer;
            text-align: center;
            color: white;
            transition: all 0.3s;
        }}
        
        .service-item.selected {{
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
        }}
        
        .service-price {{
            color: #D4AF37;
            font-weight: bold;
            margin-top: 5px;
        }}
        
        .service-item.selected .service-price {{
            color: white;
        }}
        
        /* Tables */
        .data-table {{
            width: 100%;
            background: rgba(0,0,0,0.7);
            border-radius: 10px;
            overflow-x: auto;
        }}
        
        .data-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .data-table th, .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #D4AF37;
            color: white;
        }}
        
        .data-table th {{
            color: #D4AF37;
            font-weight: bold;
        }}
        
        /* Messages */
        .message {{
            padding: 12px;
            border-radius: 10px;
            margin-top: 15px;
            display: none;
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
        
        /* Status badges */
        .status {{
            padding: 4px 8px;
            border-radius: 5px;
            font-size: 12px;
            display: inline-block;
        }}
        
        .status-pendente {{ background: #FFC107; color: #000; }}
        .status-confirmado {{ background: #28A745; color: #fff; }}
        .status-concluido {{ background: #17A2B8; color: #fff; }}
        .status-cancelado {{ background: #DC3545; color: #fff; }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 20px;
            color: #D4AF37;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="top-nav">
        <div class="nav-container">
            <a href="#" onclick="showPage('dashboard')" class="logo">💈 Barber <span>Club PRO</span></a>
            <div class="nav-links">
                <button class="nav-btn" onclick="showPage('dashboard')">🏠 Dashboard</button>
                <button class="nav-btn" onclick="showPage('agendamento')">📅 Agendar</button>
                <button class="nav-btn" onclick="showPage('lista')">📋 Agendamentos</button>
                <button class="nav-btn" onclick="showPage('clientes')">👥 Clientes</button>
                <button class="nav-btn" onclick="showPage('financeiro')">💰 Financeiro</button>
            </div>
        </div>
    </div>
    
    <div class="main-content">
        <!-- Dashboard Page -->
        <div id="dashboard-page" class="page">
            <div class="grid-4" id="dashboard-metrics">
                <div class="metric-card">
                    <div>👥 Clientes</div>
                    <div class="metric-value" id="total-clientes">0</div>
                </div>
                <div class="metric-card">
                    <div>📅 Agendamentos</div>
                    <div class="metric-value" id="total-agendamentos">0</div>
                </div>
                <div class="metric-card">
                    <div>💰 Receita Total</div>
                    <div class="metric-value" id="receita-total">R$ 0</div>
                </div>
                <div class="metric-card">
                    <div>⭐ Ticket Médio</div>
                    <div class="metric-value" id="ticket-medio">R$ 0</div>
                </div>
            </div>
            <div class="card">
                <div class="card-title">📅 Últimos Agendamentos</div>
                <div class="data-table" id="ultimos-agendamentos">
                    <table>
                        <thead>
                            <tr><th>Cliente</th><th>Data/Horário</th><th>Serviços</th><th>Valor</th><th>Status</th></tr>
                        </thead>
                        <tbody id="ultimos-tbody"></tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Agendamento Page -->
        <div id="agendamento-page" class="page" style="display:none;">
            <div class="card">
                <div class="card-title">📅 Novo Agendamento</div>
                <form id="agendamento-form">
                    <div class="form-group">
                        <label>👤 Nome Completo *</label>
                        <input type="text" id="nome" required>
                    </div>
                    <div class="form-group">
                        <label>📧 E-mail</label>
                        <input type="email" id="email">
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
                        <label>✂️ Serviços *</label>
                        <div class="services-grid" id="services-grid"></div>
                    </div>
                    <div class="form-group" style="text-align: center;">
                        <div style="font-size: 1.2rem;">💰 Total: <strong id="total-valor">R$ 0,00</strong></div>
                    </div>
                    <button type="submit">✅ Confirmar Agendamento</button>
                </form>
                <div id="agendamento-message" class="message"></div>
            </div>
        </div>
        
        <!-- Lista Page -->
        <div id="lista-page" class="page" style="display:none;">
            <div class="card">
                <div class="card-title">📋 Agendamentos</div>
                <select id="status-filtro" style="margin-bottom: 15px; width: auto; display: inline-block;">
                    <option value="todos">Todos</option>
                    <option value="pendente">Pendentes</option>
                    <option value="confirmado">Confirmados</option>
                    <option value="concluido">Concluídos</option>
                    <option value="cancelado">Cancelados</option>
                </select>
                <div class="data-table" id="agendamentos-table"></div>
            </div>
        </div>
        
        <!-- Clientes Page -->
        <div id="clientes-page" class="page" style="display:none;">
            <div class="card">
                <div class="card-title">👥 Clientes</div>
                <div class="data-table" id="clientes-table"></div>
            </div>
        </div>
        
        <!-- Financeiro Page -->
        <div id="financeiro-page" class="page" style="display:none;">
            <div class="grid-2">
                <div class="card">
                    <div class="card-title">📝 Nova Despesa</div>
                    <form id="despesa-form">
                        <div class="form-group">
                            <label>Descrição</label>
                            <input type="text" id="descricao" required>
                        </div>
                        <div class="form-group">
                            <label>Valor</label>
                            <input type="number" id="valor-despesa" step="0.01" required>
                        </div>
                        <div class="form-group">
                            <label>Categoria</label>
                            <select id="categoria">
                                <option>Aluguel</option>
                                <option>Salários</option>
                                <option>Produtos</option>
                                <option>Marketing</option>
                                <option>Manutenção</option>
                                <option>Outros</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Data</label>
                            <input type="date" id="data-despesa" required>
                        </div>
                        <button type="submit">Lançar Despesa</button>
                    </form>
                    <div id="despesa-message" class="message"></div>
                </div>
                <div class="card">
                    <div class="card-title">📊 Resumo Financeiro</div>
                    <div id="resumo-financeiro"></div>
                </div>
            </div>
            <div class="card">
                <div class="card-title">📋 Últimas Despesas</div>
                <div class="data-table" id="despesas-table"></div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>💈 Barber Club PRO - Sistema de Gestão Profissional</p>
        <p>© 2024 - Todos os direitos reservados</p>
    </div>
    
    <script>
        let servicosSelecionados = new Map();
        
        const servicos = [
            {{ id: 'corte_simples', nome: '✂️ Corte Simples', preco: 35 }},
            {{ id: 'barba', nome: '🧔 Barba', preco: 10 }},
            {{ id: 'sobrancelha', nome: '👁️ Sobrancelha', preco: 10 }},
            {{ id: 'pigmentacao', nome: '🎨 Pigmentação', preco: 50 }},
            {{ id: 'luzes', nome: '✨ Luzes', preco: 35 }},
            {{ id: 'descolorimento', nome: '⚡ Descolorimento', preco: 50 }}
        ];
        
        function renderServices() {{
            const grid = document.getElementById('services-grid');
            if (!grid) return;
            grid.innerHTML = '';
            servicos.forEach(s => {{
                const div = document.createElement('div');
                div.className = 'service-item';
                div.setAttribute('data-servico', s.id);
                div.setAttribute('data-preco', s.preco);
                div.innerHTML = `<div class="service-name">${{s.nome}}</div><div class="service-price">R$ ${{s.preco.toFixed(2)}}</div>`;
                div.onclick = () => toggleServico(div, s.id, s.preco);
                grid.appendChild(div);
            }});
        }}
        
        function toggleServico(element, servico, preco) {{
            if (servicosSelecionados.has(servico)) {{
                servicosSelecionados.delete(servico);
                element.classList.remove('selected');
            }} else {{
                servicosSelecionados.set(servico, preco);
                element.classList.add('selected');
            }}
            updateTotal();
        }}
        
        function updateTotal() {{
            let total = 0;
            servicosSelecionados.forEach((preco) => total += preco);
            const totalEl = document.getElementById('total-valor');
            if (totalEl) totalEl.textContent = `R$ ${{total.toFixed(2)}}`;
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
            servicosSelecionados.forEach((_, servico) => servicosLista.push(servicosMap[servico]));
            return servicosLista.join(', ');
        }}
        
        function showPage(page) {{
            document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
            document.getElementById(`${{page}}-page`).style.display = 'block';
            
            if (page === 'dashboard') loadDashboard();
            if (page === 'lista') loadAgendamentos();
            if (page === 'clientes') loadClientes();
            if (page === 'financeiro') loadFinanceiro();
        }}
        
        async function loadDashboard() {{
            const response = await fetch('/api/estatisticas');
            const data = await response.json();
            document.getElementById('total-clientes').textContent = data.total_clientes;
            document.getElementById('total-agendamentos').textContent = data.total_agendamentos;
            document.getElementById('receita-total').textContent = `R$ ${{data.receita_total.toFixed(2)}}`;
            const ticketMedio = data.total_agendamentos > 0 ? data.receita_total / data.total_agendamentos : 0;
            document.getElementById('ticket-medio').textContent = `R$ ${{ticketMedio.toFixed(2)}}`;
            
            const agendamentos = await fetch('/api/agendamentos').then(r => r.json());
            const tbody = document.getElementById('ultimos-tbody');
            tbody.innerHTML = '';
            agendamentos.slice(0, 10).forEach(a => {{
                const row = tbody.insertRow();
                row.insertCell(0).textContent = a[2];
                row.insertCell(1).textContent = new Date(a[5]).toLocaleString('pt-BR');
                row.insertCell(2).textContent = a[6];
                row.insertCell(3).textContent = `R$ ${{a[7].toFixed(2)}}`;
                row.insertCell(4).innerHTML = `<span class="status status-${{a[13]}}">${{a[13]}}</span>`;
            }});
        }}
        
        async function loadAgendamentos() {{
            const filtro = document.getElementById('status-filtro')?.value || 'todos';
            const response = await fetch(`/api/agendamentos?status=${{filtro === 'todos' ? '' : filtro}}`);
            const agendamentos = await response.json();
            const container = document.getElementById('agendamentos-table');
            if (!container) return;
            
            let html = '<table><thead><tr><th>Cliente</th><th>Data/Horário</th><th>Serviços</th><th>Valor</th><th>Status</th><th>Ações</th></tr></thead><tbody>';
            agendamentos.forEach(a => {{
                html += `<tr>
                    <td>${{a[2]}}</td>
                    <td>${{new Date(a[5]).toLocaleString('pt-BR')}}</td>
                    <td>${{a[6]}}</td>
                    <td>R$ ${{a[7].toFixed(2)}}</td>
                    <td><span class="status status-${{a[13]}}">${{a[13]}}</span></td>
                    <td>`;
                if (a[13] === 'pendente') {{
                    html += `<button onclick="updateStatus(${{a[0]}}, 'confirmado')" style="background:#28A745; padding:4px 8px; margin-right:5px;">Confirmar</button>`;
                    html += `<button onclick="updateStatus(${{a[0]}}, 'cancelado')" style="background:#DC3545; padding:4px 8px;">Cancelar</button>`;
                }}
                html += `</td></tr>`;
            }});
            html += '</tbody></table>';
            container.innerHTML = html;
        }}
        
        async function updateStatus(id, status) {{
            await fetch('/api/atualizar_status', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{id, status}})
            }});
            loadAgendamentos();
        }}
        
        async function loadClientes() {{
            const response = await fetch('/api/clientes');
            const clientes = await response.json();
            const container = document.getElementById('clientes-table');
            if (!container) return;
            
            let html = '<table><thead><tr><th>Nome</th><th>Email</th><th>Telefone</th><th>Total Gasto</th><th>Última Visita</th></tr></thead><tbody>';
            clientes.forEach(c => {{
                html += `<tr>
                    <td>${{c[1]}}</td>
                    <td>${{c[2] || '-'}}</td>
                    <td>${{c[3] || '-'}}</td>
                    <td>R$ ${{(c[5] || 0).toFixed(2)}}</td>
                    <td>${{c[6] ? new Date(c[6]).toLocaleDateString('pt-BR') : '-'}}</td>
                </tr>`;
            }});
            html += '</tbody></table>';
            container.innerHTML = html;
        }}
        
        async function loadFinanceiro() {{
            const despesas = await fetch('/api/despesas').then(r => r.json());
            const agendamentos = await fetch('/api/agendamentos').then(r => r.json());
            
            const receita = agendamentos.reduce((sum, a) => sum + a[7], 0);
            const despesaTotal = despesas.reduce((sum, d) => sum + d[2], 0);
            const lucro = receita - despesaTotal;
            
            document.getElementById('resumo-financeiro').innerHTML = `
                <div style="margin-bottom:15px;"><strong>💰 Receita Total:</strong> R$ ${{receita.toFixed(2)}}</div>
                <div style="margin-bottom:15px;"><strong>📉 Despesas Totais:</strong> R$ ${{despesaTotal.toFixed(2)}}</div>
                <div><strong>📈 Lucro Líquido:</strong> R$ ${{lucro.toFixed(2)}}</div>
            `;
            
            let html = '<table><thead><tr><th>Descrição</th><th>Valor</th><th>Categoria</th><th>Data</th></tr></thead><tbody>';
            despesas.forEach(d => {{
                html += `<tr>
                    <td>${{d[1]}}</td>
                    <td>R$ ${{d[2].toFixed(2)}}</td>
                    <td>${{d[3]}}</td>
                    <td>${{new Date(d[4]).toLocaleDateString('pt-BR')}}</td>
                </tr>`;
            }});
            html += '</tbody></table>';
            document.getElementById('despesas-table').innerHTML = html;
        }}
        
        document.getElementById('agendamento-form')?.addEventListener('submit', async (e) => {{
            e.preventDefault();
            const nome = document.getElementById('nome').value;
            const email = document.getElementById('email').value;
            const telefone = document.getElementById('telefone').value;
            const horario = document.getElementById('horario').value;
            
            if (!nome || !horario || servicosSelecionados.size === 0) {{
                const msg = document.getElementById('agendamento-message');
                msg.textContent = 'Preencha todos os campos obrigatórios e selecione pelo menos um serviço!';
                msg.className = 'message error';
                setTimeout(() => msg.style.display = 'none', 3000);
                return;
            }}
            
            let total = 0;
            servicosSelecionados.forEach((preco) => total += preco);
            
            const dados = {{
                nome, email, telefone,
                data_horario: new Date(horario).toISOString(),
                servicos: getServicosTexto(),
                valor_total: total,
                corte_simples: servicosSelecionados.has('corte_simples') ? 1 : 0,
                barba: servicosSelecionados.has('barba') ? 1 : 0,
                sobrancelha: servicosSelecionados.has('sobrancelha') ? 1 : 0,
                pigmentacao: servicosSelecionados.has('pigmentacao') ? 1 : 0,
                luzes: servicosSelecionados.has('luzes') ? 1 : 0,
                descolorimento: servicosSelecionados.has('descolorimento') ? 1 : 0
            }};
            
            const response = await fetch('/api/agendar', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(dados)
            }});
            
            const result = await response.json();
            const msg = document.getElementById('agendamento-message');
            if (result.success) {{
                msg.textContent = '✅ Agendamento realizado com sucesso!';
                msg.className = 'message success';
                document.getElementById('agendamento-form').reset();
                servicosSelecionados.clear();
                document.querySelectorAll('.service-item').forEach(i => i.classList.remove('selected'));
                updateTotal();
                setTimeout(() => showPage('dashboard'), 2000);
            }} else {{
                msg.textContent = '❌ Erro ao agendar. Tente novamente.';
                msg.className = 'message error';
            }}
            setTimeout(() => msg.style.display = 'none', 3000);
        }});
        
        document.getElementById('despesa-form')?.addEventListener('submit', async (e) => {{
            e.preventDefault();
            const descricao = document.getElementById('descricao').value;
            const valor = parseFloat(document.getElementById('valor-despesa').value);
            const categoria = document.getElementById('categoria').value;
            const data = document.getElementById('data-despesa').value;
            
            const response = await fetch('/api/despesa', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{descricao, valor, categoria, data}})
            }});
            
            const msg = document.getElementById('despesa-message');
            if (response.ok) {{
                msg.textContent = '✅ Despesa lançada com sucesso!';
                msg.className = 'message success';
                document.getElementById('despesa-form').reset();
                loadFinanceiro();
            }} else {{
                msg.textContent = '❌ Erro ao lançar despesa.';
                msg.className = 'message error';
            }}
            setTimeout(() => msg.style.display = 'none', 3000);
        }});
        
        document.getElementById('status-filtro')?.addEventListener('change', () => loadAgendamentos());
        
        renderServices();
        
        const hoje = new Date();
        hoje.setDate(hoje.getDate() + 1);
        hoje.setHours(8, 0, 0);
        const horarioInput = document.getElementById('horario');
        if (horarioInput) horarioInput.min = hoje.toISOString().slice(0, 16);
        
        loadDashboard();
    </script>
</body>
</html>'''
    return html

# ==================== API ROTAS ====================
def handle_api():
    from flask import Flask, request, jsonify
    import sys
    
    if '/api/' in st.query_params:
        path = st.query_params.get('api_path', [''])[0]
        
        if path == 'estatisticas':
            stats = db.get_estatisticas()
            st.json(stats)
            st.stop()
        
        elif path == 'agendamentos':
            status = st.query_params.get('status', [None])[0]
            agendamentos = db.listar_agendamentos(status if status else None)
            st.json(agendamentos)
            st.stop()
        
        elif path == 'clientes':
            clientes = db.listar_clientes()
            st.json(clientes)
            st.stop()
        
        elif path == 'despesas':
            despesas = db.listar_despesas()
            st.json(despesas)
            st.stop()
        
        elif path == 'agendar' and st.query_params.get('data'):
            dados = json.loads(st.query_params.get('data', ['{}'])[0])
            db.inserir_agendamento(dados)
            st.json({'success': True})
            st.stop()
        
        elif path == 'atualizar_status' and st.query_params.get('data'):
            dados = json.loads(st.query_params.get('data', ['{}'])[0])
            db.atualizar_status(dados['id'], dados['status'])
            st.json({'success': True})
            st.stop()
        
        elif path == 'despesa' and st.query_params.get('data'):
            dados = json.loads(st.query_params.get('data', ['{}'])[0])
            db.inserir_despesa(dados['descricao'], dados['valor'], dados['categoria'], dados['data'])
            st.json({'success': True})
            st.stop()

# ==================== MAIN ====================
# Processar requisições API
query_params = st.query_params
if 'api_path' in query_params:
    handle_api()

# Exibir HTML completo
html_content = get_html_content()
st.components.v1.html(html_content, height=1000, scrolling=True)
