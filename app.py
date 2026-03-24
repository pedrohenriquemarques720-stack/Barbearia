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
        agendamentos_teste = [
            ("Carlos Silva", "carlos@email.com", "(11) 99999-1111", datetime.now() + timedelta(hours=2), "Corte Simples", 35, 1,0,0,0,0,0, "confirmado"),
            ("Fernanda Lima", "fernanda@email.com", "(11) 99999-3333", datetime.now() + timedelta(days=1, hours=10), "Corte Simples, Luzes", 70, 1,0,0,0,1,0, "pendente"),
            ("Roberto Santos", "roberto@email.com", "(11) 99999-2222", datetime.now() + timedelta(days=2, hours=14), "Barba, Sobrancelha", 20, 0,1,1,0,0,0, "confirmado"),
            ("Julio Cesar", "julio@email.com", "(11) 99999-4444", datetime.now() + timedelta(days=3, hours=16), "Corte Simples, Barba", 45, 1,1,0,0,0,0, "pendente"),
            ("Mariana Costa", "mariana@email.com", "(11) 99999-5555", datetime.now() + timedelta(days=4, hours=11), "Pigmentação", 50, 0,0,0,1,0,0, "confirmado"),
            ("Carlos Silva", "carlos@email.com", "(11) 99999-1111", datetime.now() - timedelta(days=1, hours=3), "Corte Simples", 35, 1,0,0,0,0,0, "concluido"),
            ("Fernanda Lima", "fernanda@email.com", "(11) 99999-3333", datetime.now() - timedelta(days=3, hours=5), "Corte Simples, Barba", 45, 1,1,0,0,0,0, "concluido"),
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

# Inicializar banco de dados
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
            st.json(agendamentos)
            st.stop()
        
        elif path == 'clientes':
            st.json(db.listar_clientes())
            st.stop()
        
        elif path == 'despesas':
            st.json(db.listar_despesas())
            st.stop()
        
        elif path == 'agendar' and query_params.get('data'):
            dados = json.loads(query_params.get('data', ['{}'])[0])
            db.inserir_agendamento(dados)
            st.json({'success': True})
            st.stop()
        
        elif path == 'atualizar_status' and query_params.get('data'):
            dados = json.loads(query_params.get('data', ['{}'])[0])
            db.atualizar_status(dados['id'], dados['status'])
            st.json({'success': True})
            st.stop()
        
        elif path == 'despesa' and query_params.get('data'):
            dados = json.loads(query_params.get('data', ['{}'])[0])
            db.inserir_despesa(dados['descricao'], dados['valor'], dados['categoria'], dados['data'])
            st.json({'success': True})
            st.stop()

# ==================== LER E SERVIR O HTML ====================
def ler_html():
    """Lê o arquivo index.html da mesma pasta"""
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Se o arquivo não existir, retorna uma mensagem de erro
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Erro</title></head>
        <body style="background:#1a1a1a; color:white; text-align:center; padding:50px;">
            <h1>❌ Arquivo index.html não encontrado!</h1>
            <p>Certifique-se de que o arquivo <strong>index.html</strong> está na mesma pasta do app.py</p>
            <p>📁 Estrutura esperada:</p>
            <pre>
            barbearia_du_cortz/
            ├── app.py
            ├── index.html
            └── requirements.txt
            </pre>
        </body>
        </html>
        """

# Processar requisições API
process_api()

# Servir o HTML
html_content = ler_html()
st.components.v1.html(html_content, height=800, scrolling=True)
