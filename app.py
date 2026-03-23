import streamlit as st
import pandas as pd
import datetime
import os
import base64

# Configuração da página
st.set_page_config(
    page_title="Barbearia App",
    page_icon="✂️",
    layout="wide"
)

# Arquivo para armazenar agendamentos
ARQUIVO_DADOS = "agendamentos.csv"

# Função para carregar dados
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        # Criar DataFrame vazio com as colunas corretas
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
st.title("✂️ Barbearia do Seu Zé - Sistema de Agendamento")
st.markdown("---")

# Abas principais
tab1, tab2, tab3 = st.tabs(["📅 Agendamento Online", "📊 Contabilidade", "📋 Lista de Agendamentos"])

# ==================== ABA 1 - AGENDAMENTO ONLINE ====================
with tab1:
    st.header("📅 Faça seu Agendamento")
    
    # Carregar o HTML interativo
    html_path = os.path.join("frontend", "agendamento.html")
    
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Injetar CSS extra para melhor visualização no Streamlit
        st.components.v1.html(html_content, height=800, scrolling=True)
        
        # Área para receber dados do JavaScript via query params
        st.markdown("---")
        st.info("💡 Após preencher o formulário acima, o agendamento será registrado automaticamente.")
        
        # Verificar se há dados passados via query string (do JavaScript)
        query_params = st.query_params
        
        if "dados_agendamento" in query_params:
            try:
                import json
                dados_json = json.loads(query_params["dados_agendamento"])
                
                # Adicionar ao DataFrame
                novo_agendamento = pd.DataFrame([dados_json])
                df_agendamentos = pd.concat([df_agendamentos, novo_agendamento], ignore_index=True)
                salvar_dados(df_agendamentos)
                
                st.success("✅ Agendamento realizado com sucesso!")
                st.balloons()
                
                # Limpar query params para não duplicar ao recarregar
                st.query_params.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao processar agendamento: {e}")
    else:
        st.error(f"Arquivo HTML não encontrado em: {html_path}")
        st.info("Certifique-se de criar a pasta 'frontend' e colocar o arquivo 'agendamento.html' dentro dela.")

# ==================== ABA 2 - CONTABILIDADE ====================
with tab2:
    st.header("💰 Contabilidade da Barbearia")
    
    if len(df_agendamentos) > 0:
        # Converter coluna de data para datetime
        df_agendamentos["data_agendamento"] = pd.to_datetime(df_agendamentos["data_agendamento"])
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data Início", df_agendamentos["data_agendamento"].min().date())
        with col2:
            data_fim = st.date_input("Data Fim", df_agendamentos["data_agendamento"].max().date())
        
        # Filtrar por período
        mask = (df_agendamentos["data_agendamento"].dt.date >= data_inicio) & \
               (df_agendamentos["data_agendamento"].dt.date <= data_fim)
        df_filtrado = df_agendamentos[mask]
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Agendamentos", len(df_filtrado))
        with col2:
            st.metric("Receita Total", f"R$ {df_filtrado['valor_total'].sum():.2f}")
        with col3:
            st.metric("Ticket Médio", f"R$ {df_filtrado['valor_total'].mean():.2f}" if len(df_filtrado) > 0 else "R$ 0.00")
        
        st.markdown("---")
        
        # Gráficos
        st.subheader("📊 Receita por Dia")
        
        # Agrupar por data
        receita_diaria = df_filtrado.groupby(df_filtrado["data_agendamento"].dt.date)["valor_total"].sum().reset_index()
        st.line_chart(receita_diaria.set_index("data_agendamento"))
        
        st.markdown("---")
        
        # Serviços mais vendidos
        st.subheader("📈 Serviços Mais Solicitados")
        
        servicos_colunas = ["corte_simples", "barba", "sobrancelha", "pigmentacao", "luzes", "descolorimento"]
        servicos_totais = df_filtrado[servicos_colunas].sum()
        
        st.bar_chart(servicos_totais)
        
        # Tabela detalhada
        st.markdown("---")
        st.subheader("📋 Detalhamento Financeiro")
        
        detalhes = df_filtrado[["nome", "horario", "servicos", "valor_total", "data_agendamento"]].sort_values("data_agendamento", ascending=False)
        st.dataframe(detalhes, use_container_width=True)
        
        # Botão para exportar
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
        # Ordenar por data mais recente
        df_agendamentos = df_agendamentos.sort_values("data_agendamento", ascending=False)
        
        # Mostrar cards de agendamentos
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
        
        # Opção para deletar agendamentos
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
