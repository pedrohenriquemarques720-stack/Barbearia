import streamlit as st
import pandas as pd
import datetime
import os
import json
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Barber Club - Sistema de Agendamento",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .css-1d391kg {
        background-color: #0f0f1f;
    }
    </style>
""", unsafe_allow_html=True)

# Função para criar o arquivo HTML na raiz
def criar_arquivo_html():
    """Cria o arquivo HTML na mesma pasta do app.py"""
    
    html_path = "agendamento.html"
    
    # Conteúdo completo do HTML com nome Barber Club
    html_content = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Barber Club - Agendamento Premium</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 30px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .header {
            background: linear-gradient(135deg, #e65c00 0%, #f9d423 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }

        .header::before {
            content: '💈';
            position: absolute;
            font-size: 80px;
            opacity: 0.1;
            bottom: 10px;
            right: 20px;
        }

        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: 800;
            letter-spacing: -1px;
        }

        .header h1 span {
            font-style: italic;
            background: linear-gradient(135deg, #fff 0%, #ffe6cc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.95;
        }

        .form-content {
            padding: 40px;
        }

        .form-group {
            margin-bottom: 30px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
        }

        input[type="text"],
        input[type="datetime-local"] {
            width: 100%;
            padding: 14px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s;
            font-family: inherit;
        }

        input:focus {
            outline: none;
            border-color: #e65c00;
            box-shadow: 0 0 0 3px rgba(230, 92, 0, 0.1);
        }

        .servicos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }

        .servico-item {
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 18px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .servico-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }

        .servico-item:hover::before {
            left: 100%;
        }

        .servico-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        }

        .servico-item.selected {
            background: linear-gradient(135deg, #e65c00 0%, #f9d423 100%);
            border-color: #e65c00;
            color: white;
            transform: scale(1.02);
        }

        .servico-nome {
            font-weight: 700;
            font-size: 1.1em;
            margin-bottom: 8px;
        }

        .servico-preco {
            font-size: 1.3em;
            color: #e65c00;
            font-weight: 800;
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
            border: 2px solid #e65c00;
        }

        .total-label {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }

        .total-value {
            font-size: 3em;
            color: #e65c00;
            font-weight: 800;
        }

        button {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #e65c00 0%, #f9d423 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(230, 92, 0, 0.4);
        }

        .message {
            margin-top: 20px;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            display: none;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                transform: translateY(-10px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        @media (max-width: 768px) {
            .form-content {
                padding: 20px;
            }
            .header h1 {
                font-size: 2em;
            }
            .servicos-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💈 Barber <span>Club</span></h1>
            <p>Agendamento Premium - Estilo e Tradição</p>
        </div>
        
        <div class="form-content">
            <div class="form-group">
                <label for="nome">👤 Seu Nome:</label>
                <input type="text" id="nome" placeholder="Digite seu nome completo" required>
            </div>

            <div class="form-group">
                <label for="horario">🕐 Escolha o Horário:</label>
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
                <div class="total-label">💰 Valor Total do Serviço:</div>
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
            const horario = document.getElementById('horario').value;
            
            if (!nome || !horario) {
                mostrarMensagem('Por favor, preencha todos os campos!', 'error');
                return;
            }
            
            if (servicosSelecionados.size === 0) {
                mostrarMensagem('Por favor, selecione pelo menos um serviço!', 'error');
                return;
            }
            
            let total = 0;
            servicosSelecionados.forEach((preco) => {
                total += preco;
            });
            
            const dadosAgendamento = {
                nome: nome,
                horario: new Date(horario).toLocaleString('pt-BR'),
                servicos: getServicosTexto(),
                valor_total: total,
                corte_simples: servicosSelecionados.has('corte_simples') ? 1 : 0,
                barba: servicosSelecionados.has('barba') ? 1 : 0,
                sobrancelha: servicosSelecionados.has('sobrancelha') ? 1 : 0,
                pigmentacao: servicosSelecionados.has('pigmentacao') ? 1 : 0,
                luzes: servicosSelecionados.has('luzes') ? 1 : 0,
                descolorimento: servicosSelecionados.has('descolorimento') ? 1 : 0,
                data_agendamento: new Date().toISOString()
            };
            
            const dadosString = encodeURIComponent(JSON.stringify(dadosAgendamento));
            window.parent.location.href = `/?dados_agendamento=${dadosString}`;
            
            mostrarMensagem('✅ Agendamento realizado com sucesso! Redirecionando...', 'success');
            
            setTimeout(() => {
                document.getElementById('nome').value = '';
                document.getElementById('horario').value = '';
                servicosSelecionados.clear();
                document.querySelectorAll('.servico-item').forEach(item => {
                    item.classList.remove('selected');
                });
                atualizarTotal();
            }, 2000);
        }
        
        function mostrarMensagem(texto, tipo) {
            const msgDiv = document.getElementById('message');
            msgDiv.textContent = texto;
            msgDiv.className = `message ${tipo}`;
            msgDiv.style.display = 'block';
            
            setTimeout(() => {
                msgDiv.style.display = 'none';
            }, 3000);
        }
        
        const hoje = new Date();
        hoje.setDate(hoje.getDate() + 1);
        hoje.setHours(8, 0, 0);
        const dataMinima = hoje.toISOString().slice(0, 16);
        document.getElementById('horario').min = dataMinima;
    </script>
</body>
</html>'''
    
    # Criar o arquivo HTML na raiz
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path

# Arquivo para armazenar agendamentos
ARQUIVO_DADOS = "agendamentos.csv"

# Função para carregar dados
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        return pd.DataFrame(columns=[
            "nome", "horario", "servicos", "valor_total",
            "corte_simples", "barba", "sobrancelha",
            "pigmentacao", "luzes", "descolorimento", "data_agendamento"
        ])

# Função para salvar dados
def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

# Carregar dados existentes
df_agendamentos = carregar_dados()

# Sidebar com informações
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/e65c00/ffffff?text=BARBER+CLUB", use_container_width=True)
    st.markdown("## 💈 Barber Club")
    st.markdown("---")
    st.markdown("### 📍 Localização")
    st.markdown("Av. Principal, 123 - Centro")
    st.markdown("### 📞 Contato")
    st.markdown("(11) 99999-9999")
    st.markdown("### ⏰ Horário de Funcionamento")
    st.markdown("Segunda a Sábado: 09h às 20h")
    st.markdown("Domingo: 10h às 16h")
    st.markdown("---")
    
    # Estatísticas rápidas
    if len(df_agendamentos) > 0:
        st.markdown("### 📊 Estatísticas")
        st.metric("Total de Clientes", len(df_agendamentos))
        st.metric("Receita Total", f"R$ {df_agendamentos['valor_total'].sum():.2f}")

# Título principal
st.title("💈 Barber Club - Sistema de Agendamento Premium")
st.markdown("---")

# Verificar e criar arquivo HTML se necessário
html_path = criar_arquivo_html()

# Abas principais
tab1, tab2, tab3 = st.tabs(["📅 Agendamento Online", "📊 Contabilidade & Relatórios", "📋 Lista de Agendamentos"])

# ==================== ABA 1 - AGENDAMENTO ONLINE ====================
with tab1:
    st.header("📅 Faça seu Agendamento")
    
    # Carregar e exibir o HTML
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        st.components.v1.html(html_content, height=900, scrolling=True)
        
        st.markdown("---")
        st.info("💡 **Dica:** Após preencher o formulário acima, o agendamento será registrado automaticamente.")
        
        query_params = st.query_params
        
        if "dados_agendamento" in query_params:
            try:
                dados_json = json.loads(query_params["dados_agendamento"])
                
                novo_agendamento = pd.DataFrame([dados_json])
                df_agendamentos = pd.concat([df_agendamentos, novo_agendamento], ignore_index=True)
                salvar_dados(df_agendamentos)
                
                st.success("✅ Agendamento realizado com sucesso!")
                st.balloons()
                
                st.query_params.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao processar agendamento: {e}")
    else:
        st.error(f"❌ Não foi possível criar o arquivo HTML")

# ==================== ABA 2 - CONTABILIDADE ====================
with tab2:
    st.header("💰 Contabilidade e Relatórios")
    
    if len(df_agendamentos) > 0:
        df_agendamentos["data_agendamento"] = pd.to_datetime(df_agendamentos["data_agendamento"])
        
        # Filtros avançados
        col1, col2, col3 = st.columns(3)
        with col1:
            data_inicio = st.date_input("📅 Data Início", df_agendamentos["data_agendamento"].min().date())
        with col2:
            data_fim = st.date_input("📅 Data Fim", df_agendamentos["data_agendamento"].max().date())
        with col3:
            servico_filtro = st.selectbox("🔍 Filtrar por Serviço", ["Todos", "Corte Simples", "Barba", "Sobrancelha", "Pigmentação", "Luzes", "Descolorimento"])
        
        # Filtrar por período
        mask = (df_agendamentos["data_agendamento"].dt.date >= data_inicio) & \
               (df_agendamentos["data_agendamento"].dt.date <= data_fim)
        df_filtrado = df_agendamentos[mask]
        
        # Filtrar por serviço
        if servico_filtro != "Todos":
            coluna_servico = {
                "Corte Simples": "corte_simples",
                "Barba": "barba",
                "Sobrancelha": "sobrancelha",
                "Pigmentação": "pigmentacao",
                "Luzes": "luzes",
                "Descolorimento": "descolorimento"
            }[servico_filtro]
            df_filtrado = df_filtrado[df_filtrado[coluna_servico] == 1]
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Agendamentos", len(df_filtrado), delta=None)
        with col2:
            st.metric("Receita Total", f"R$ {df_filtrado['valor_total'].sum():.2f}", delta=None)
        with col3:
            media = df_filtrado['valor_total'].mean() if len(df_filtrado) > 0 else 0
            st.metric("Ticket Médio", f"R$ {media:.2f}", delta=None)
        with col4:
            st.metric("Serviços Realizados", df_filtrado[['corte_simples', 'barba', 'sobrancelha', 'pigmentacao', 'luzes', 'descolorimento']].sum().sum())
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Receita por Dia")
            receita_diaria = df_filtrado.groupby(df_filtrado["data_agendamento"].dt.date)["valor_total"].sum().reset_index()
            st.line_chart(receita_diaria.set_index("data_agendamento"), use_container_width=True)
        
        with col2:
            st.subheader("📈 Serviços Mais Solicitados")
            servicos_colunas = ["corte_simples", "barba", "sobrancelha", "pigmentacao", "luzes", "descolorimento"]
            servicos_totais = df_filtrado[servicos_colunas].sum()
            servicos_nomes = ["Corte", "Barba", "Sobrancelha", "Pigmentação", "Luzes", "Descolorimento"]
            servicos_df = pd.DataFrame({"Serviço": servicos_nomes, "Quantidade": servicos_totais.values})
            st.bar_chart(servicos_df.set_index("Serviço"), use_container_width=True)
        
        st.markdown("---")
        
        # Tabela detalhada
        st.subheader("📋 Detalhamento Financeiro Completo")
        detalhes = df_filtrado[["nome", "horario", "servicos", "valor_total", "data_agendamento"]].sort_values("data_agendamento", ascending=False)
        st.dataframe(detalhes, use_container_width=True, height=400)
        
        # Botões de exportação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Exportar Relatório (CSV)", use_container_width=True):
                csv = df_filtrado.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"relatorio_barber_club_{data_inicio}_{data_fim}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📊 Exportar Relatório (Excel)", use_container_width=True):
                try:
                    import io
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_filtrado.to_excel(writer, sheet_name='Agendamentos', index=False)
                    excel_data = output.getvalue()
                    st.download_button(
                        label="Download Excel",
                        data=excel_data,
                        file_name=f"relatorio_barber_club_{data_inicio}_{data_fim}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except:
                    st.warning("Para exportar para Excel, instale: pip install openpyxl")
    else:
        st.info("📭 Nenhum agendamento realizado ainda. Aguardando primeiro cliente!")

# ==================== ABA 3 - LISTA DE AGENDAMENTOS ====================
with tab3:
    st.header("📋 Todos os Agendamentos")
    
    if len(df_agendamentos) > 0:
        df_agendamentos = df_agendamentos.sort_values("data_agendamento", ascending=False)
        
        # Buscador
        busca = st.text_input("🔍 Buscar por nome:", placeholder="Digite o nome do cliente...")
        if busca:
            df_agendamentos = df_agendamentos[df_agendamentos["nome"].str.contains(busca, case=False, na=False)]
        
        # Mostrar cards de agendamentos
        for idx, row in df_agendamentos.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
                with col1:
                    st.markdown(f"**👤 {row['nome']}**")
                with col2:
                    st.markdown(f"**🕐 {row['horario']}**")
                with col3:
                    st.markdown(f"**✂️ {row['servicos']}**")
                with col4:
                    st.markdown(f"**💰 R$ {row['valor_total']}**")
                st.markdown("---")
        
        # Gerenciar agendamentos
        st.markdown("### 🗑️ Gerenciar Agendamentos")
        agendamentos_para_deletar = st.multiselect(
            "Selecione agendamentos para remover:",
            df_agendamentos.index.tolist(),
            format_func=lambda x: f"{df_agendamentos.loc[x, 'nome']} - {df_agendamentos.loc[x, 'horario']} - R$ {df_agendamentos.loc[x, 'valor_total']}"
        )
        
        if st.button("🗑️ Remover Selecionados", use_container_width=True):
            df_agendamentos = df_agendamentos.drop(agendamentos_para_deletar)
            salvar_dados(df_agendamentos)
            st.success("✅ Agendamentos removidos com sucesso!")
            st.rerun()
    else:
        st.info("📭 Nenhum agendamento cadastrado. Comece a receber clientes!")
