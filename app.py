import streamlit as st
import sqlite3
import json
from datetime import datetime, timedelta
import os

# Configuração da página
st.set_page_config(
    page_title="Barbearia Du Cortz",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS para esconder elementos padrão do Streamlit
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

# ==================== BANCO DE DADOS ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('barbearia_du_cortz.db', check_same_thread=False)
        self.criar_tabelas()
        self.inserir_dados_teste()
    
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
    
    def inserir_dados_teste(self):
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM agendamentos')
        if cursor.fetchone()[0] > 0:
            return
        
        # Clientes de teste
        clientes_teste = [
            ("Carlos Silva", "carlos@email.com", "(11) 99999-1111", 150.00, datetime.now() - timedelta(days=2)),
            ("Roberto Santos", "roberto@email.com", "(11) 99999-2222", 85.00, datetime.now() - timedelta(days=5)),
            ("Fernanda Lima", "fernanda@email.com", "(11) 99999-3333", 120.00, datetime.now() - timedelta(days=1)),
            ("Julio Cesar", "julio@email.com", "(11) 99999-4444", 200.00, datetime.now() - timedelta(days=3)),
            ("Mariana Costa", "mariana@email.com", "(11) 99999-5555", 95.00, datetime.now() - timedelta(days=4)),
        ]
        
        for cliente in clientes_teste:
            cursor.execute('''
                INSERT OR IGNORE INTO clientes (nome, email, telefone, total_gasto, ultima_visita)
                VALUES (?, ?, ?, ?, ?)
            ''', cliente)
        
        # Agendamentos de teste
        agora = datetime.now()
        agendamentos_teste = [
            ("Carlos Silva", "carlos@email.com", "(11) 99999-1111", agora + timedelta(hours=2), "Corte Simples", 35, 1,0,0,0,0,0, "confirmado"),
            ("Fernanda Lima", "fernanda@email.com", "(11) 99999-3333", agora + timedelta(days=1, hours=10), "Corte Simples, Luzes", 70, 1,0,0,0,1,0, "pendente"),
            ("Roberto Santos", "roberto@email.com", "(11) 99999-2222", agora + timedelta(days=2, hours=14), "Barba, Sobrancelha", 20, 0,1,1,0,0,0, "confirmado"),
            ("Julio Cesar", "julio@email.com", "(11) 99999-4444", agora + timedelta(days=3, hours=16), "Corte Simples, Barba", 45, 1,1,0,0,0,0, "pendente"),
            ("Mariana Costa", "mariana@email.com", "(11) 99999-5555", agora + timedelta(days=4, hours=11), "Pigmentação", 50, 0,0,0,1,0,0, "confirmado"),
            ("Carlos Silva", "carlos@email.com", "(11) 99999-1111", agora - timedelta(days=1, hours=3), "Corte Simples", 35, 1,0,0,0,0,0, "concluido"),
            ("Fernanda Lima", "fernanda@email.com", "(11) 99999-3333", agora - timedelta(days=3, hours=5), "Corte Simples, Barba", 45, 1,1,0,0,0,0, "concluido"),
        ]
        
        for ag in agendamentos_teste:
            cursor.execute('''
                INSERT INTO agendamentos (nome, email, telefone, data_horario, servicos, valor_total,
                corte_simples, barba, sobrancelha, pigmentacao, luzes, descolorimento, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ag)
        
        # Despesas de teste
        despesas_teste = [
            ("Aluguel da Loja", 2500.00, "Aluguel", datetime.now().replace(day=1).strftime('%Y-%m-%d')),
            ("Compra de Produtos", 850.00, "Produtos", datetime.now().strftime('%Y-%m-%d')),
            ("Salário Barbeiro", 2000.00, "Salários", datetime.now().replace(day=5).strftime('%Y-%m-%d')),
            ("Marketing Digital", 300.00, "Marketing", datetime.now().strftime('%Y-%m-%d')),
            ("Manutenção Cadeiras", 450.00, "Manutenção", (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')),
        ]
        
        for despesa in despesas_teste:
            cursor.execute('''
                INSERT INTO despesas (descricao, valor, categoria, data)
                VALUES (?, ?, ?, ?)
            ''', despesa)
        
        self.conn.commit()
    
    def inserir_agendamento(self, dados):
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT id FROM clientes WHERE nome = ?', (dados['nome'],))
        cliente = cursor.fetchone()
        
        if cliente:
            cliente_id = cliente[0]
            cursor.execute('''
                UPDATE clientes 
                SET email = ?, telefone = ?, total_gasto = total_gasto + ?, ultima_visita = ?
                WHERE id = ?
            ''', (dados.get('email', ''), dados.get('telefone', ''), dados['valor_total'], dados['data_horario'], cliente_id))
        else:
            cursor.execute('''
                INSERT INTO clientes (nome, email, telefone, total_gasto, ultima_visita)
                VALUES (?, ?, ?, ?, ?)
            ''', (dados['nome'], dados.get('email', ''), dados.get('telefone', ''), dados['valor_total'], dados['data_horario']))
        
        cursor.execute('''
            INSERT INTO agendamentos (
                nome, email, telefone, data_horario, servicos, valor_total,
                corte_simples, barba, sobrancelha, pigmentacao, luzes, descolorimento, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados['nome'], dados.get('email', ''), dados.get('telefone', ''),
            dados['data_horario'], dados['servicos'], dados['valor_total'],
            dados.get('corte_simples', 0), dados.get('barba', 0), dados.get('sobrancelha', 0),
            dados.get('pigmentacao', 0), dados.get('luzes', 0), dados.get('descolorimento', 0),
            'pendente'
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def listar_agendamentos(self, status=None):
        cursor = self.conn.cursor()
        if status and status != 'todos':
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
        cursor.execute('SELECT COUNT(*) FROM agendamentos WHERE status = "pendente"')
        pendentes = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM agendamentos WHERE status = "confirmado"')
        confirmados = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM agendamentos WHERE status = "concluido"')
        concluidos = cursor.fetchone()[0]
        
        return {
            'total_clientes': total_clientes,
            'total_agendamentos': total_agendamentos,
            'receita_total': receita_total,
            'pendentes': pendentes,
            'confirmados': confirmados,
            'concluidos': concluidos
        }

db = Database()

# ==================== API ROTAS ====================
def process_api():
    query_params = st.query_params
    
    if 'api_path' in query_params:
        path = query_params.get('api_path', [''])[0]
        
        if path == 'estatisticas':
            st.json(db.get_estatisticas())
            st.stop()
        
        elif path == 'agendamentos':
            status = query_params.get('status', [None])[0]
            agendamentos = db.listar_agendamentos(status if status else None)
            result = []
            for a in agendamentos:
                result.append(list(a))
            st.json(result)
            st.stop()
        
        elif path == 'clientes':
            clientes = db.listar_clientes()
            result = []
            for c in clientes:
                result.append(list(c))
            st.json(result)
            st.stop()
        
        elif path == 'despesas':
            despesas = db.listar_despesas()
            result = []
            for d in despesas:
                result.append(list(d))
            st.json(result)
            st.stop()
        
        elif path == 'agendar':
            data_str = query_params.get('data', ['{}'])[0]
            dados = json.loads(data_str)
            db.inserir_agendamento(dados)
            st.json({'success': True, 'message': 'Agendamento realizado com sucesso!'})
            st.stop()
        
        elif path == 'atualizar_status':
            data_str = query_params.get('data', ['{}'])[0]
            dados = json.loads(data_str)
            db.atualizar_status(dados['id'], dados['status'])
            st.json({'success': True, 'message': 'Status atualizado!'})
            st.stop()
        
        elif path == 'despesa':
            data_str = query_params.get('data', ['{}'])[0]
            dados = json.loads(data_str)
            db.inserir_despesa(dados['descricao'], dados['valor'], dados['categoria'], dados['data'])
            st.json({'success': True, 'message': 'Despesa lançada!'})
            st.stop()

# ==================== HTML COMPLETO COM IMAGEM DE FUNDO ====================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>Barbearia Du Cortz</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            min-height: 100vh;
            position: relative;
            background: #0a0a0a;
        }
        
        /* Imagem de fundo com opacidade */
        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url('barber2.webp'), url('barber1.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            opacity: 0.15;
            z-index: -1;
        }
        
        /* Fallback se as imagens não carregarem */
        @media (max-width: 768px) {
            body::before {
                background-size: cover;
                background-position: center;
            }
        }
        
        /* Top Navigation - Gradiente mais vibrante */
        .top-nav {
            background: linear-gradient(135deg, #D4AF37 0%, #8B0000 50%, #4a0a0a 100%);
            padding: 12px 20px;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            border-bottom: 2px solid #FFD700;
        }
        
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .logo {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .logo-icon { font-size: 2rem; animation: pulse 2s infinite; }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .logo-text { 
            background: linear-gradient(135deg, #FFD700 0%, #FFFFFF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
        .logo span { color: #FFD700; }
        
        .nav-links { display: flex; gap: 10px; flex-wrap: wrap; }
        
        .nav-btn {
            background: rgba(0,0,0,0.6);
            color: #FFD700;
            border: 1px solid #FFD700;
            padding: 8px 16px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s;
            backdrop-filter: blur(5px);
        }
        
        .nav-btn:hover, .nav-btn.active {
            background: linear-gradient(135deg, #D4AF37 0%, #8B0000 100%);
            color: white;
            border-color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(212,175,55,0.3);
        }
        
        @media (max-width: 768px) {
            .nav-container { flex-direction: column; }
            .nav-links { justify-content: center; }
            .nav-btn { padding: 6px 12px; font-size: 12px; }
        }
        
        .main-content { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        /* Cards com vidro fosco (glassmorphism) */
        .card {
            background: rgba(0,0,0,0.75);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(212,175,55,0.3);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(212,175,55,0.2);
            border-color: rgba(212,175,55,0.6);
        }
        
        .card-title {
            color: #FFD700;
            font-size: 1.2rem;
            margin-bottom: 15px;
            font-weight: bold;
            border-left: 4px solid #FFD700;
            padding-left: 12px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        
        .grid-2, .grid-3, .grid-4 { display: grid; gap: 20px; margin-bottom: 20px; }
        .grid-2 { grid-template-columns: repeat(2, 1fr); }
        .grid-3 { grid-template-columns: repeat(3, 1fr); }
        .grid-4 { grid-template-columns: repeat(4, 1fr); }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
        }
        
        /* Metric Cards com efeito brilho */
        .metric-card {
            background: linear-gradient(135deg, rgba(139,0,0,0.9) 0%, rgba(212,175,55,0.9) 100%);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            color: white;
            border: 1px solid #FFD700;
            transition: all 0.3s;
            cursor: pointer;
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        .metric-card:hover { 
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(212,175,55,0.4);
        }
        .metric-value { font-size: 2rem; font-weight: bold; margin-top: 10px; color: #FFD700; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
        
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #FFD700; font-weight: bold; text-shadow: 1px 1px 1px rgba(0,0,0,0.5); }
        
        input, select {
            width: 100%;
            padding: 12px;
            background: rgba(42,42,42,0.9);
            border: 2px solid #FFD700;
            border-radius: 12px;
            color: white;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #D4AF37;
            background: rgba(0,0,0,0.9);
            box-shadow: 0 0 10px rgba(212,175,55,0.5);
        }
        
        button {
            background: linear-gradient(135deg, #D4AF37 0%, #8B0000 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        
        button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 6px 20px rgba(212,175,55,0.4);
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .service-item {
            background: rgba(42,42,42,0.9);
            border: 2px solid #FFD700;
            border-radius: 12px;
            padding: 15px;
            cursor: pointer;
            text-align: center;
            color: white;
            transition: all 0.3s;
            backdrop-filter: blur(5px);
        }
        
        .service-item:hover { 
            transform: translateY(-3px); 
            border-color: #D4AF37;
            box-shadow: 0 4px 15px rgba(212,175,55,0.3);
        }
        .service-item.selected { 
            background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%);
            border-color: #FFD700;
            box-shadow: 0 0 15px rgba(212,175,55,0.5);
        }
        .service-name { font-weight: bold; margin-bottom: 5px; font-size: 1rem; }
        .service-price { color: #FFD700; font-weight: bold; margin-top: 5px; }
        .service-item.selected .service-price { color: white; }
        
        .data-table {
            width: 100%;
            background: rgba(0,0,0,0.7);
            border-radius: 12px;
            overflow-x: auto;
            backdrop-filter: blur(5px);
        }
        
        .data-table table { width: 100%; border-collapse: collapse; }
        .data-table th, .data-table td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(212,175,55,0.3); color: white; }
        .data-table th { color: #FFD700; font-weight: bold; background: rgba(139,0,0,0.4); }
        .data-table tr:hover { background: rgba(212,175,55,0.1); }
        
        .status {
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 12px;
            display: inline-block;
            font-weight: bold;
        }
        .status-pendente { background: #FFC107; color: #000; }
        .status-confirmado { background: #28A745; color: #fff; }
        .status-concluido { background: #17A2B8; color: #fff; }
        .status-cancelado { background: #DC3545; color: #fff; }
        
        .action-btn {
            padding: 4px 8px;
            margin: 0 2px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            width: auto;
        }
        .btn-confirm { background: #28A745; color: white; }
        .btn-cancel { background: #DC3545; color: white; }
        
        .message {
            padding: 12px;
            border-radius: 10px;
            margin-top: 15px;
            display: none;
        }
        .message.success { background: #28A745; color: white; display: block; }
        .message.error { background: #DC3545; color: white; display: block; }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #FFD700;
            font-size: 12px;
            border-top: 1px solid rgba(212,175,55,0.3);
            margin-top: 20px;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }
        
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #1a1a1a; }
        ::-webkit-scrollbar-thumb { background: #D4AF37; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #FFD700; }
        
        /* Animações */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .page {
            animation: fadeInUp 0.5s ease-out;
        }
    </style>
</head>
<body>
    <div class="top-nav">
        <div class="nav-container">
            <div class="logo" onclick="showPage('dashboard')">
                <span class="logo-icon">💈</span>
                <span class="logo-text">Barbearia <span>Du Cortz</span></span>
            </div>
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
        <div id="dashboard-page" class="page">
            <div class="grid-4">
                <div class="metric-card" onclick="showPage('clientes')"><div>👥 Clientes</div><div class="metric-value" id="total-clientes">0</div></div>
                <div class="metric-card" onclick="showPage('lista')"><div>📅 Agendamentos</div><div class="metric-value" id="total-agendamentos">0</div></div>
                <div class="metric-card"><div>💰 Receita Total</div><div class="metric-value" id="receita-total">R$ 0</div></div>
                <div class="metric-card"><div>⭐ Ticket Médio</div><div class="metric-value" id="ticket-medio">R$ 0</div></div>
            </div>
            <div class="grid-3">
                <div class="card"><div class="card-title">🟡 Pendentes</div><div style="font-size: 2rem; text-align: center; color: #FFC107;" id="pendentes">0</div></div>
                <div class="card"><div class="card-title">🟢 Confirmados</div><div style="font-size: 2rem; text-align: center; color: #28A745;" id="confirmados">0</div></div>
                <div class="card"><div class="card-title">🔵 Concluídos</div><div style="font-size: 2rem; text-align: center; color: #17A2B8;" id="concluidos">0</div></div>
            </div>
            <div class="card">
                <div class="card-title">📅 Próximos Agendamentos</div>
                <div class="data-table">\\\\(\\\\(<thead>\\\\
                    <th>Cliente</th><th>Data/Horário</th><th>Serviços</th><th>Valor</th><th>Status</th>\\\\
                </thead><tbody id="proximos-tbody"></tbody>\\\\)\\\\)</div>
            </div>
        </div>
        
        <div id="agendamento-page" class="page" style="display:none;">
            <div class="card">
                <div class="card-title">✂️ Novo Agendamento</div>
                <form id="agendamento-form">
                    <div class="form-group"><label>👤 Nome Completo *</label><input type="text" id="nome" placeholder="Digite seu nome completo" required></div>
                    <div class="form-group"><label>📧 E-mail</label><input type="email" id="email" placeholder="seuemail@exemplo.com"></div>
                    <div class="form-group"><label>📱 WhatsApp</label><input type="tel" id="telefone" placeholder="(11) 99999-9999"></div>
                    <div class="form-group"><label>🕐 Data e Horário *</label><input type="datetime-local" id="horario" required></div>
                    <div class="form-group"><label>✂️ Selecione os Serviços *</label><div class="services-grid" id="services-grid"></div></div>
                    <div class="form-group" style="text-align: center;"><div style="font-size: 1.2rem;">💰 <strong>Total:</strong> <strong id="total-valor" style="color: #FFD700;">R$ 0,00</strong></div></div>
                    <button type="submit">✅ Confirmar Agendamento</button>
                </form>
                <div id="agendamento-message" class="message"></div>
            </div>
        </div>
        
        <div id="lista-page" class="page" style="display:none;">
            <div class="card">
                <div class="card-title">📋 Lista de Agendamentos</div>
                <div style="margin-bottom: 15px;"><select id="status-filtro" style="width: auto; display: inline-block; background: #2a2a2a; color: white; border: 1px solid #FFD700;"><option value="todos">📌 Todos</option><option value="pendente">🟡 Pendentes</option><option value="confirmado">🟢 Confirmados</option><option value="concluido">🔵 Concluídos</option><option value="cancelado">🔴 Cancelados</option></select></div>
                <div class="data-table" id="agendamentos-table"></div>
            </div>
        </div>
        
        <div id="clientes-page" class="page" style="display:none;">
            <div class="card"><div class="card-title">👥 Nossos Clientes</div><div class="data-table" id="clientes-table"></div></div>
        </div>
        
        <div id="financeiro-page" class="page" style="display:none;">
            <div class="grid-2">
                <div class="card"><div class="card-title">📝 Lançar Despesa</div>
                    <form id="despesa-form">
                        <div class="form-group"><label>Descrição</label><input type="text" id="descricao" placeholder="Ex: Compra de produtos" required></div>
                        <div class="form-group"><label>Valor</label><input type="number" id="valor-despesa" step="0.01" placeholder="0,00" required></div>
                        <div class="form-group"><label>Categoria</label><select id="categoria"><option>Aluguel</option><option>Salários</option><option>Produtos</option><option>Marketing</option><option>Manutenção</option><option>Outros</option></select></div>
                        <div class="form-group"><label>Data</label><input type="date" id="data-despesa" required></div>
                        <button type="submit">💰 Lançar Despesa</button>
                    </form>
                    <div id="despesa-message" class="message"></div>
                </div>
                <div class="card"><div class="card-title">📊 Resumo Financeiro</div><div id="resumo-financeiro"></div></div>
            </div>
            <div class="card"><div class="card-title">📋 Últimas Despesas</div><div class="data-table" id="despesas-table"></div></div>
        </div>
    </div>
    
    <div class="footer"><p>💈 Barbearia Du Cortz - Tradição, Estilo e Elegância</p><p>© 2024 - Todos os direitos reservados</p></div>
    
    <script>
        let servicosSelecionados = new Map();
        
        const servicos = [
            { id: 'corte_simples', nome: '✂️ Corte Simples', preco: 35 },
            { id: 'barba', nome: '🧔 Barba', preco: 10 },
            { id: 'sobrancelha', nome: '👁️ Sobrancelha', preco: 10 },
            { id: 'pigmentacao', nome: '🎨 Pigmentação', preco: 50 },
            { id: 'luzes', nome: '✨ Luzes', preco: 35 },
            { id: 'descolorimento', nome: '⚡ Descolorimento', preco: 50 }
        ];
        
        function renderServices() {
            const grid = document.getElementById('services-grid');
            if (!grid) return;
            grid.innerHTML = '';
            servicos.forEach(s => {
                const div = document.createElement('div');
                div.className = 'service-item';
                div.innerHTML = `<div class="service-name">${s.nome}</div><div class="service-price">R$ ${s.preco.toFixed(2)}</div>`;
                div.onclick = () => toggleServico(div, s.id, s.preco);
                grid.appendChild(div);
            });
        }
        
        function toggleServico(element, servico, preco) {
            if (servicosSelecionados.has(servico)) {
                servicosSelecionados.delete(servico);
                element.classList.remove('selected');
            } else {
                servicosSelecionados.set(servico, preco);
                element.classList.add('selected');
            }
            updateTotal();
        }
        
        function updateTotal() {
            let total = 0;
            servicosSelecionados.forEach((preco) => total += preco);
            const totalEl = document.getElementById('total-valor');
            if (totalEl) totalEl.textContent = `R$ ${total.toFixed(2)}`;
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
            servicosSelecionados.forEach((_, servico) => servicosLista.push(servicosMap[servico]));
            return servicosLista.join(', ');
        }
        
        async function apiCall(endpoint, method = 'GET', data = null) {
            let url = `/api/${endpoint}`;
            if (method === 'GET' && data) {
                url += '?' + new URLSearchParams(data).toString();
            }
            const options = { method };
            if (method === 'POST' && data) {
                url += `?data=${encodeURIComponent(JSON.stringify(data))}`;
            }
            const response = await fetch(url, options);
            return await response.json();
        }
        
        function showPage(page) {
            document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
            document.getElementById(`${page}-page`).style.display = 'block';
            if (page === 'dashboard') loadDashboard();
            if (page === 'lista') loadAgendamentos();
            if (page === 'clientes') loadClientes();
            if (page === 'financeiro') loadFinanceiro();
        }
        
        async function loadDashboard() {
            try {
                const stats = await apiCall('estatisticas');
                document.getElementById('total-clientes').textContent = stats.total_clientes;
                document.getElementById('total-agendamentos').textContent = stats.total_agendamentos;
                document.getElementById('receita-total').textContent = `R$ ${stats.receita_total.toFixed(2)}`;
                document.getElementById('pendentes').textContent = stats.pendentes;
                document.getElementById('confirmados').textContent = stats.confirmados;
                document.getElementById('concluidos').textContent = stats.concluidos;
                const ticketMedio = stats.total_agendamentos > 0 ? stats.receita_total / stats.total_agendamentos : 0;
                document.getElementById('ticket-medio').textContent = `R$ ${ticketMedio.toFixed(2)}`;
                
                const agendamentos = await apiCall('agendamentos');
                const tbody = document.getElementById('proximos-tbody');
                tbody.innerHTML = '';
                const agora = new Date();
                const proximos = agendamentos.filter(a => new Date(a[5]) > agora).slice(0, 10);
                proximos.forEach(a => {
                    const row = tbody.insertRow();
                    row.insertCell(0).textContent = a[2];
                    row.insertCell(1).textContent = new Date(a[5]).toLocaleString('pt-BR');
                    row.insertCell(2).textContent = a[6];
                    row.insertCell(3).textContent = `R$ ${a[7].toFixed(2)}`;
                    row.insertCell(4).innerHTML = `<span class="status status-${a[13]}">${a[13]}</span>`;
                });
            } catch(e) { console.error('Erro:', e); }
        }
        
        async function loadAgendamentos() {
            try {
                const filtro = document.getElementById('status-filtro')?.value || 'todos';
                const agendamentos = await apiCall(`agendamentos?status=${filtro === 'todos' ? '' : filtro}`);
                const container = document.getElementById('agendamentos-table');
                if (!container) return;
                
                let html = '<table><thead><tr><th>Cliente</th><th>Data/Horário</th><th>Serviços</th><th>Valor</th><th>Status</th><th>Ações</th></tr></thead><tbody>';
                agendamentos.forEach(a => {
                    html += `<tr>
                        <td><strong>${a[2]}</strong></td>
                        <td>${new Date(a[5]).toLocaleString('pt-BR')}</td>
                        <td>${a[6]}</td>
                        <td>R$ ${a[7].toFixed(2)}</td>
                        <td><span class="status status-${a[13]}">${a[13]}</span></td>
                        <td>`;
                    if (a[13] === 'pendente') {
                        html += `<button class="action-btn btn-confirm" onclick="updateStatus(${a[0]}, 'confirmado')">✅ Confirmar</button>`;
                        html += `<button class="action-btn btn-cancel" onclick="updateStatus(${a[0]}, 'cancelado')">❌ Cancelar</button>`;
                    }
                    html += `</td></tr>`;
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            } catch(e) { console.error('Erro:', e); }
        }
        
        async function updateStatus(id, status) {
            await apiCall('atualizar_status', 'POST', { id, status });
            loadAgendamentos();
            loadDashboard();
        }
        
        async function loadClientes() {
            try {
                const clientes = await apiCall('clientes');
                const container = document.getElementById('clientes-table');
                if (!container) return;
                
                let html = '<table><thead><tr><th>Nome</th><th>Email</th><th>Telefone</th><th>Total Gasto</th><th>Última Visita</th></tr></thead><tbody>';
                clientes.forEach(c => {
                    html += `<tr>
                        <td><strong>${c[1]}</strong></td>
                        <td>${c[2] || '-'}</td>
                        <td>${c[3] || '-'}</td>
                        <td><span style="color: #FFD700;">R$ ${(c[5] || 0).toFixed(2)}</span></td>
                        <td>${c[6] ? new Date(c[6]).toLocaleDateString('pt-BR') : '-'}</td>
                    </tr>`;
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            } catch(e) { console.error('Erro:', e); }
        }
        
        async function loadFinanceiro() {
            try {
                const despesas = await apiCall('despesas');
                const agendamentos = await apiCall('agendamentos');
                const receita = agendamentos.reduce((sum, a) => sum + a[7], 0);
                const despesaTotal = despesas.reduce((sum, d) => sum + d[2], 0);
                const lucro = receita - despesaTotal;
                
                document.getElementById('resumo-financeiro').innerHTML = `
                    <div style="margin-bottom:15px; padding:10px; background: rgba(42,42,42,0.8); border-radius:12px;">
                        <div><strong>💰 Receita Total:</strong> <span style="color: #FFD700;">R$ ${receita.toFixed(2)}</span></div>
                    </div>
                    <div style="margin-bottom:15px; padding:10px; background: rgba(42,42,42,0.8); border-radius:12px;">
                        <div><strong>📉 Despesas Totais:</strong> <span style="color: #FFD700;">R$ ${despesaTotal.toFixed(2)}</span></div>
                    </div>
                    <div style="padding:10px; background: linear-gradient(135deg, #8B0000 0%, #D4AF37 100%); border-radius:12px;">
                        <div><strong>📈 Lucro Líquido:</strong> <span style="color: #FFD700;">R$ ${lucro.toFixed(2)}</span></div>
                    </div>
                `;
                
                let html = '<table><thead><tr><th>Descrição</th><th>Valor</th><th>Categoria</th><th>Data</th></tr></thead><tbody>';
                despesas.forEach(d => {
                    html += `<tr>
                        <td>${d[1]}</td>
                        <td><span style="color: #FFD700;">R$ ${d[2].toFixed(2)}</span></td>
                        <td>${d[3]}</td>
                        <td>${new Date(d[4]).toLocaleDateString('pt-BR')}</td>
                    </tr>`;
                });
                html += '</tbody></table>';
                document.getElementById('despesas-table').innerHTML = html;
            } catch(e) { console.error('Erro:', e); }
        }
        
        document.getElementById('agendamento-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const nome = document.getElementById('nome').value;
            const email = document.getElementById('email').value;
            const telefone = document.getElementById('telefone').value;
            const horario = document.getElementById('horario').value;
            
            if (!nome || !horario || servicosSelecionados.size === 0) {
                const msg = document.getElementById('agendamento-message');
                msg.textContent = '❌ Preencha todos os campos obrigatórios e selecione pelo menos um serviço!';
                msg.className = 'message error';
                setTimeout(() => msg.style.display = 'none', 3000);
                return;
            }
            
            let total = 0;
            servicosSelecionados.forEach((preco) => total += preco);
            
            const dados = {
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
            };
            
            const result = await apiCall('agendar', 'POST', dados);
            const msg = document.getElementById('agendamento-message');
            if (result.success) {
                msg.textContent = '✅ Agendamento realizado com sucesso!';
                msg.className = 'message success';
                document.getElementById('agendamento-form').reset();
                servicosSelecionados.clear();
                document.querySelectorAll('.service-item').forEach(i => i.classList.remove('selected'));
                updateTotal();
                setTimeout(() => showPage('dashboard'), 2000);
            } else {
                msg.textContent = '❌ Erro ao agendar. Tente novamente.';
                msg.className = 'message error';
            }
            setTimeout(() => msg.style.display = 'none', 3000);
        });
        
        document.getElementById('despesa-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const descricao = document.getElementById('descricao').value;
            const valor = parseFloat(document.getElementById('valor-despesa').value);
            const categoria = document.getElementById('categoria').value;
            const data = document.getElementById('data-despesa').value;
            
            const result = await apiCall('despesa', 'POST', { descricao, valor, categoria, data });
            const msg = document.getElementById('despesa-message');
            if (result.success) {
                msg.textContent = '✅ Despesa lançada com sucesso!';
                msg.className = 'message success';
                document.getElementById('despesa-form').reset();
                loadFinanceiro();
            } else {
                msg.textContent = '❌ Erro ao lançar despesa.';
                msg.className = 'message error';
            }
            setTimeout(() => msg.style.display = 'none', 3000);
        });
        
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

# ==================== MAIN ====================
process_api()
st.components.v1.html(HTML_TEMPLATE, height=800, scrolling=True)
