import streamlit as st
import json
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Barcas de Maionese",
    page_icon="🍽️",
    layout="wide"
)

# ==================== BANCO DE DADOS ====================
# Usando arquivo JSON local para persistência
ARQUIVO_DADOS = "pedidos.json"

def carregar_pedidos():
    """Carrega pedidos do arquivo JSON"""
    if not os.path.exists(ARQUIVO_DADOS):
        return []
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def salvar_pedidos(pedidos):
    """Salva pedidos no arquivo JSON"""
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(pedidos, f, ensure_ascii=False, indent=2)

# ==================== DADOS INICIAIS ====================
PRODUTOS = [
    {"id": 1, "nome": "Barca P", "preco": 25.00, "descricao": "Serve 2-3 pessoas", "emoji": "🍽️"},
    {"id": 2, "nome": "Barca M", "preco": 35.00, "descricao": "Serve 4-5 pessoas", "emoji": "🍽️🍽️"},
    {"id": 3, "nome": "Barca G", "preco": 45.00, "descricao": "Serve 6-8 pessoas", "emoji": "🍽️🍽️🍽️"},
]

# ==================== CSS PERSONALIZADO ====================
st.markdown("""
<style>
    /* Cabeçalho principal */
    .main-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Cards de produtos */
    .product-card {
        background: white;
        border: 2px solid #FF6B6B;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        transition: transform 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Botões */
    .stButton > button {
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #FF5252;
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Cards de estatísticas */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    /* Status colors */
    .status-pendente {
        background-color: #ffc107;
        color: #000;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .status-preparando {
        background-color: #17a2b8;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .status-entregue {
        background-color: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    
    /* Container de pedido */
    .order-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #FF6B6B;
    }
    
    hr {
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES AUXILIARES ====================
def obter_proximo_id(pedidos):
    """Obtém o próximo ID disponível"""
    if not pedidos:
        return 1
    return max(p["id"] for p in pedidos) + 1

# ==================== PÁGINA DO CLIENTE ====================
def pagina_cliente():
    st.markdown("""
    <div class="main-header">
        <h1>🍽️ Barcas de Maionese</h1>
        <p>O melhor sabor da região! Peça agora mesmo.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Exibir produtos
    st.header("📋 Cardápio")
    cols = st.columns(len(PRODUTOS))
    
    for idx, produto in enumerate(PRODUTOS):
        with cols[idx]:
            st.markdown(f"""
            <div class="product-card">
                <h2 style="font-size: 2rem;">{produto['emoji']}</h2>
                <h3>{produto['nome']}</h3>
                <p style="color: gray;">{produto['descricao']}</p>
                <h2 style="color: #FF6B6B;">R$ {produto['preco']:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Formulário de pedido
    st.header("📝 Faça seu Pedido")
    
    with st.form("form_pedido"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_cliente = st.text_input("👤 Nome completo *", placeholder="Digite seu nome completo")
            
            tipo_cliente = st.radio("📄 Tipo de Cliente *", ["Pessoa Física (PF)", "Pessoa Jurídica (PJ)"], horizontal=True)
            
            if "PF" in tipo_cliente:
                documento = st.text_input("CPF *", placeholder="000.000.000-00")
                tipo_sigla = "PF"
            else:
                documento = st.text_input("CNPJ *", placeholder="00.000.000/0000-00")
                ie = st.text_input("Inscrição Estadual", placeholder="Opcional")
                tipo_sigla = "PJ"
        
        with col2:
            categoria = st.selectbox("🏷️ Categoria do Cliente *", ["Cliente Fixo", "Cliente Variável"])
            categoria_valor = "Fixo" if categoria == "Cliente Fixo" else "Variável"
            
            st.markdown("---")
            st.markdown("### 🛒 Selecione os itens")
            
            itens_selecionados = []
            total_pedido = 0
            
            for produto in PRODUTOS:
                quantidade = st.number_input(
                    f"{produto['nome']} - R$ {produto['preco']:.2f}",
                    min_value=0,
                    max_value=10,
                    value=0,
                    key=f"prod_{produto['id']}"
                )
                
                if quantidade > 0:
                    subtotal = quantidade * produto['preco']
                    total_pedido += subtotal
                    itens_selecionados.append({
                        "nome": produto['nome'],
                        "quantidade": quantidade,
                        "preco": produto['preco'],
                        "subtotal": subtotal
                    })
        
        observacoes = st.text_area("📝 Observações", placeholder="Ex: sem cebola, extra picles, ponto de referência...")
        
        # Exibir total
        if itens_selecionados:
            st.info(f"💰 **Total do Pedido: R$ {total_pedido:.2f}**")
        else:
            st.warning("⚠️ Selecione pelo menos um item")
        
        # Botão finalizar
        submitted = st.form_submit_button("✅ Finalizar Pedido", use_container_width=True)
        
        if submitted:
            # Validações
            erros = []
            if not nome_cliente:
                erros.append("Nome do cliente é obrigatório")
            if not documento:
                erros.append("Documento é obrigatório")
            if not itens_selecionados:
                erros.append("Selecione pelo menos um item")
            
            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                # Criar pedido
                pedidos = carregar_pedidos()
                
                novo_pedido = {
                    "id": obter_proximo_id(pedidos),
                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "nome_cliente": nome_cliente,
                    "tipo_cliente": tipo_sigla,
                    "documento": documento,
                    "itens": itens_selecionados,
                    "valor_total": total_pedido,
                    "status": "Pendente",
                    "categoria": categoria_valor,
                    "observacoes": observacoes
                }
                
                if tipo_sigla == "PJ" and 'ie' in locals() and ie:
                    novo_pedido["inscricao_estadual"] = ie
                
                pedidos.append(novo_pedido)
                salvar_pedidos(pedidos)
                
                # Mensagem de sucesso
                st.success(f"✅ **Pedido #{novo_pedido['id']} recebido com sucesso!**")
                st.balloons()
                
                # Mostrar resumo
                with st.expander("📋 Ver detalhes do pedido", expanded=True):
                    st.markdown(f"**Número do Pedido:** #{novo_pedido['id']}")
                    st.markdown(f"**Cliente:** {novo_pedido['nome_cliente']}")
                    st.markdown(f"**Tipo:** {novo_pedido['tipo_cliente']}")
                    st.markdown(f"**Documento:** {novo_pedido['documento']}")
                    st.markdown(f"**Total:** R$ {novo_pedido['valor_total']:.2f}")
                    st.markdown("**Itens:**")
                    for item in novo_pedido['itens']:
                        st.markdown(f"- {item['quantidade']}x {item['nome']} = R$ {item['subtotal']:.2f}")
                    if observacoes:
                        st.markdown(f"**Observações:** {observacoes}")
                    st.markdown(f"**Status:** 🟡 {novo_pedido['status']}")

# ==================== PÁGINA ADMIN ====================
def pagina_admin():
    # Autenticação
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        st.markdown("""
        <div class="main-header">
            <h1>🔐 Área Administrativa</h1>
            <p>Acesso restrito</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            senha = st.text_input("Senha do Administrador", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                if senha == "admin123":
                    st.session_state.autenticado = True
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
        return
    
    # Dashboard
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard Administrativo</h1>
        <p>Gerencie seus pedidos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão sair
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()
    
    # Carregar dados
    pedidos = carregar_pedidos()
    
    if not pedidos:
        st.info("📭 Nenhum pedido cadastrado ainda.")
        return
    
    # ========== ESTATÍSTICAS ==========
    total_faturamento = sum(p["valor_total"] for p in pedidos)
    total_pedidos = len(pedidos)
    pedidos_pf = len([p for p in pedidos if p["tipo_cliente"] == "PF"])
    pedidos_pj = len([p for p in pedidos if p["tipo_cliente"] == "PJ"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Faturamento Total", f"R$ {total_faturamento:,.2f}")
    with col2:
        st.metric("📦 Total de Pedidos", total_pedidos)
    with col3:
        st.metric("👤 Pedidos PF", pedidos_pf)
    with col4:
        st.metric("🏢 Pedidos PJ", pedidos_pj)
    
    # Status
    pendentes = len([p for p in pedidos if p["status"] == "Pendente"])
    preparando = len([p for p in pedidos if p["status"] == "Preparando"])
    entregues = len([p for p in pedidos if p["status"] == "Entregue"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟡 Pendentes", pendentes)
    with col2:
        st.metric("🔵 Preparando", preparando)
    with col3:
        st.metric("🟢 Entregues", entregues)
    
    st.divider()
    
    # ========== GESTÃO DE PEDIDOS ==========
    st.header("📋 Gestão de Pedidos")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_status = st.selectbox("Filtrar por status", ["Todos", "Pendente", "Preparando", "Entregue"])
    with col2:
        filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos", "PF", "PJ"])
    
    # Filtrar pedidos
    pedidos_filtrados = pedidos.copy()
    
    if filtro_status != "Todos":
        pedidos_filtrados = [p for p in pedidos_filtrados if p["status"] == filtro_status]
    
    if filtro_tipo != "Todos":
        pedidos_filtrados = [p for p in pedidos_filtrados if p["tipo_cliente"] == filtro_tipo]
    
    # Ordenar por ID decrescente (mais recentes primeiro)
    pedidos_filtrados.sort(key=lambda x: x["id"], reverse=True)
    
    if not pedidos_filtrados:
        st.info("Nenhum pedido encontrado com os filtros selecionados.")
    else:
        for pedido in pedidos_filtrados:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1.5])
                
                with col1:
                    st.markdown(f"**Pedido #{pedido['id']}**")
                    st.caption(pedido['data_hora'])
                
                with col2:
                    st.markdown(f"**{pedido['nome_cliente']}**")
                    st.markdown(f"{pedido['tipo_cliente']}: {pedido['documento']}")
                    if pedido.get('inscricao_estadual'):
                        st.caption(f"IE: {pedido['inscricao_estadual']}")
                
                with col3:
                    st.markdown(f"💰 **R$ {pedido['valor_total']:.2f}**")
                    st.markdown(f"🏷️ {pedido['categoria']}")
                    # Mostrar itens resumidos
                    itens_texto = ", ".join([f"{i['quantidade']}x {i['nome']}" for i in pedido['itens']])
                    st.caption(f"📦 {itens_texto}")
                    if pedido.get('observacoes'):
                        st.caption(f"📝 {pedido['observacoes'][:50]}")
                
                with col4:
                    # Status com cor
                    if pedido['status'] == "Pendente":
                        st.markdown('<span class="status-pendente">🟡 Pendente</span>', unsafe_allow_html=True)
                    elif pedido['status'] == "Preparando":
                        st.markdown('<span class="status-preparando">🔵 Preparando</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="status-entregue">🟢 Entregue</span>', unsafe_allow_html=True)
                    
                    # Botões de ação
                    if pedido['status'] != "Entregue":
                        if pedido['status'] == "Pendente":
                            if st.button("🔵 Preparar", key=f"preparar_{pedido['id']}", use_container_width=True):
                                pedido['status'] = "Preparando"
                                salvar_pedidos(pedidos)
                                st.success(f"Pedido #{pedido['id']} movido para Preparando!")
                                st.rerun()
                        elif pedido['status'] == "Preparando":
                            if st.button("🟢 Entregar", key=f"entregar_{pedido['id']}", use_container_width=True):
                                pedido['status'] = "Entregue"
                                salvar_pedidos(pedidos)
                                st.success(f"Pedido #{pedido['id']} marcado como Entregue!")
                                st.rerun()
                
                st.divider()
    
    # ========== HISTÓRICO ==========
    with st.expander("📜 Histórico de Pedidos Entregues"):
        entregues_lista = [p for p in pedidos if p["status"] == "Entregue"]
        if entregues_lista:
            for p in entregues_lista[-10:]:  # Mostrar últimos 10
                st.write(f"**#{p['id']}** - {p['nome_cliente']} - R$ {p['valor_total']:.2f} - {p['data_hora']}")
        else:
            st.info("Nenhum pedido entregue ainda.")

# ==================== MAIN ====================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("## 🍽️ Barcas de Maionese")
        st.markdown("---")
        
        # Navegação
        pagina = st.radio(
            "📌 Menu Principal",
            ["🛍️ Fazer Pedido", "📊 Área Administrativa"],
            index=0
        )
        
        st.markdown("---")
        
        # Informações
        pedidos = carregar_pedidos()
        st.metric("📦 Total de Pedidos", len(pedidos))
        
        st.markdown("---")
        st.caption("Sistema de Gestão de Pedidos")
        st.caption("Versão 1.0.0")
    
    # Conteúdo principal
    if pagina == "🛍️ Fazer Pedido":
        pagina_cliente()
    else:
        pagina_admin()

# Executar
if __name__ == "__main__":
    main()
