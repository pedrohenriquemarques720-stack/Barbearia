import streamlit as st
import pandas as pd
import datetime
import os
import json

# Configuração da página
st.set_page_config(
    page_title="Barbearia Du Cortz",
    page_icon="✂️",
    layout="wide"
)

# Função para criar o arquivo HTML na raiz
def criar_arquivo_html():
    """Cria o arquivo HTML na mesma pasta do app.py"""
    
    html_path = "agendamento.html"
    
    # Conteúdo completo do HTML com nome Barbearia Du Cortz
    html_content = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Barbearia Du Cortz - Agendamento</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header h1 span {
            font-style: italic;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .form-content {
            padding: 30px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }

        input[type="text"],
        input[type="datetime-local"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        input:focus {
            outline: none;
            border-color: #2a5298;
        }

        .servicos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }

        .servico-item {
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }

        .servico-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .servico-item.selected {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-color: #2a5298;
            color: white;
        }

        .servico-nome {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }

        .servico-preco {
            font-size: 1.2em;
            color: #27ae60;
            font-weight: bold;
        }

        .servico-item.selected .servico-preco {
            color: white;
        }

        .total-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }

        .total-label {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .total-value {
            font-size: 2.5em;
            color: #27ae60;
            font-weight: bold;
        }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .message {
            margin-top: 20px;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            display: none;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✂️ Barbearia <span>Du Cortz</span></h1>
            <p>Agende seu horário de forma rápida e fácil!</p>
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
                        <div class="servico-nome">Corte Simples</div>
                        <div class="servico-preco">R$ 35,00</div>
                    </div>
                    <div class="servico-item" data-servico="barba" data-preco="10">
                        <div class="servico-nome">Barba</div>
                        <div class="servico-preco">R$ 10,00</div>
                    </div>
                    <div class="servico-item" data-servico="sobrancelha" data-preco="10">
                        <div class="servico-nome">Sobrancelha</div>
                        <div class="servico-preco">R$ 10,00</div>
                    </div>
                    <div class="servico-item" data-servico="pigmentacao" data-preco="50">
                        <div class="servico-nome">Pigmentação</div>
                        <div class="servico-preco">R$ 50,00</div>
                    </div>
                    <div class="servico-item" data-servico="luzes" data-preco="35">
                        <div class="servico-nome">Luzes</div>
                        <div class="servico-preco">R$ 35,00</div>
                    </div>
                    <div class="servico-item" data-servico="descolorimento" data-preco="50">
                        <div class="servico-nome">Descolorimento</div>
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

# Título principal
st.title("✂️ Barbearia Du Cortz - Sistema de Agendamento")
st.markdown("---")

# Verificar e criar arquivo HTML se necessário
html_path = criar_arquivo_html()

# Abas principais
tab1, tab2, tab3 = st.tabs(["📅 Agendamento Online", "📊 Contabilidade", "📋 Lista de Agendamentos"])

# ==================== ABA 1 - AGENDAMENTO ONLINE ====================
with tab1:
    st.header("📅 Faça seu Agendamento")
    
    # Carregar e exibir o HTML
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        st.components.v1.html(html_content, height=800, scrolling=True)
        
        st.markdown("---")
        st.info("💡 Após preencher o formulário acima, o agendamento será registrado automaticamente.")
        
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
    st.header("💰 Contabilidade da Barbearia")
    
    if len(df_agendamentos) > 0:
        df_agendamentos["data_agendamento"] = pd.to_datetime(df_agendamentos["data_agendamento"])
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data Início", df_agendamentos["data_agendamento"].min().date())
        with col2:
            data_fim = st.date_input("Data Fim", df_agendamentos["data_agendamento"].max().date())
        
        mask = (df_agendamentos["data_agendamento"].dt.date >= data_inicio) & \
               (df_agendamentos["data_agendamento"].dt.date <= data_fim)
        df_filtrado = df_agendamentos[mask]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Agendamentos", len(df_filtrado))
        with col2:
            st.metric("Receita Total", f"R$ {df_filtrado['valor_total'].sum():.2f}")
        with col3:
            st.metric("Ticket Médio", f"R$ {df_filtrado['valor_total'].mean():.2f}" if len(df_filtrado) > 0 else "R$ 0.00")
        
        st.markdown("---")
        
        st.subheader("📊 Receita por Dia")
        receita_diaria = df_filtrado.groupby(df_filtrado["data_agendamento"].dt.date)["valor_total"].sum().reset_index()
        st.line_chart(receita_diaria.set_index("data_agendamento"))
        
        st.markdown("---")
        
        st.subheader("📈 Serviços Mais Solicitados")
        servicos_colunas = ["corte_simples", "barba", "sobrancelha", "pigmentacao", "luzes", "descolorimento"]
        servicos_totais = df_filtrado[servicos_colunas].sum()
        st.bar_chart(servicos_totais)
        
        st.markdown("---")
        st.subheader("📋 Detalhamento Financeiro")
        detalhes = df_filtrado[["nome", "horario", "servicos", "valor_total", "data_agendamento"]].sort_values("data_agendamento", ascending=False)
        st.dataframe(detalhes, use_container_width=True)
        
        if st.button("📥 Exportar Relatório (CSV)"):
            csv = df_filtrado.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"relatorio_barbearia_{data_inicio}_{data_fim}.csv",
                mime="text/csv"
            )
    else:
        st.info("Nenhum agendamento realizado ainda.")

# ==================== ABA 3 - LISTA DE AGENDAMENTOS ====================
with tab3:
    st.header("📋 Todos os Agendamentos")
    
    if len(df_agendamentos) > 0:
        df_agendamentos = df_agendamentos.sort_values("data_agendamento", ascending=False)
        
        for idx, row in df_agendamentos.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
                with col1:
                    st.markdown(f"**👤 {row['nome']}**")
                with col2:
                    st.markdown(f"**🕐 {row['horario']}**")
                with col3:
                    st.markdown(f"**✂️ Serviços:** {row['servicos']}")
                with col4:
                    st.markdown(f"**💰 R$ {row['valor_total']}**")
                st.markdown("---")
        
        st.markdown("### 🗑️ Gerenciar Agendamentos")
        agendamentos_para_deletar = st.multiselect(
            "Selecione agendamentos para remover:",
            df_agendamentos.index.tolist(),
            format_func=lambda x: f"{df_agendamentos.loc[x, 'nome']} - {df_agendamentos.loc[x, 'horario']} - R$ {df_agendamentos.loc[x, 'valor_total']}"
        )
        
        if st.button("Remover Selecionados"):
            df_agendamentos = df_agendamentos.drop(agendamentos_para_deletar)
            salvar_dados(df_agendamentos)
            st.success("Agendamentos removidos com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum agendamento cadastrado.")
