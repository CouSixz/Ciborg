# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from collections import defaultdict
import random

# Dicionário para rastrear as atribuições
assignment_counter = defaultdict(int)

# Configuração inicial
st.set_page_config(
    page_title="Ciborg",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Reduzir margem superior
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Título
st.title("Ciborg - Gestão de Ordens de Serviço (OS) 🚀 - Desenvolvido por Cauã Morente de Oliveira")

# Tabs
tab_rac, tab_gtf, tab_zkm = st.tabs(["RAC", "GTF", "ZKM"])

# Dados
df_os = pd.DataFrame()
df_team = pd.DataFrame()

# Definição das alçadas
bins = [0, 2000, 5000, 10000, float('inf')]
labels = ["0 Á 2.000", "2.001 Á 5.000", "5.001 Á 10.000", "10.001 Acima"]

def define_alçadas(df):
    if "VALOR TOTAL" in df.columns:
        df["ALÇADA"] = pd.cut(df["VALOR TOTAL"], bins=bins, labels=labels, right=False)
    return df

# Sidebar para uploads, filtros e configurações
with st.sidebar:
    st.header("Controles 🛠️")
    
    # Seção para Upload de Arquivos
    st.subheader("Carregar Arquivos")
    uploaded_os = st.file_uploader(
        label="Carregar OS 📂",
        type=["xlsx"],
        help="Carregue o arquivo de ordens de serviço (formato Excel).",
        key="file_uploader"
    )
    uploaded_team = st.file_uploader(
        label="Carregar Equipe 👥",
        type=["xlsx"],
        help="Carregue o arquivo da equipe (formato Excel).",
        key="team_uploader"
    )
    
    # Feedback de carregamento
    if uploaded_os:
        df_os = pd.read_excel(uploaded_os)
        df_os["Data Criação O.S"] = pd.to_datetime(df_os["Data Criação O.S"], format="%d/%m/%Y %H:%M:%S")
        df_os["DIAS ABERTA"] = (pd.Timestamp.now() - df_os["Data Criação O.S"]).dt.days
        
        # Definir alçadas conforme a equipe
        bins = [0, 2000, 5000, 10000, float('inf')]
        labels = ["0 Á 2.000", "2.001 Á 5.000", "5.001 Á 10.000", "10.001 Acima"]
        df_os["ALÇADA"] = pd.cut(df_os["VALOR TOTAL"], bins=bins, labels=labels, right=True)
        st.success("✅ OS carregadas com sucesso!")
    else:
        st.warning("⚠️ Nenhuma OS carregada.")
    
    if uploaded_team:
        df_team = pd.read_excel(uploaded_team)
        df_team = df_team[df_team['STATUS'] == 'Ativo']
        st.success("✅ Equipe carregada com sucesso!")
    else:
        st.warning("⚠️ Nenhuma equipe carregada.")
    
    # Separador visual
    st.markdown("---")
    
    # Seção de Filtros
    st.subheader("Filtros para Distribuição 🔍")
    if not df_os.empty:
        fornecedores = df_os['FORNECEDOR'].unique().tolist()
        selected_fornecedores = st.multiselect(
            "Filtrar por Fornecedor",
            options=fornecedores,
            help="Selecione os fornecedores para filtrar as ordens de serviço."
        )
        
        alçadas_equipe = df_team['ALÇADA'].unique().tolist()
        selected_alçadas = st.multiselect(
            "Filtrar por Alçada",
            options=alçadas_equipe,
            help="Selecione as alçadas para filtrar a distribuição."
        )
    
    # Separador visual
    st.markdown("---")
    
    # Seção de Seleção de Tela
    st.subheader("Configurações 🎛️")
    current_tab = st.selectbox(
        "Selecione a tela para distribuição",
        ["RAC", "GTF", "ZKM"],
        help="Escolha a tela correspondente à BU para realizar a distribuição."
    )

# Função para criar o resumo por faixa de valor (como texto)
def create_value_range_summary(df):
    if df.empty or "VALOR TOTAL" not in df.columns:
        return "<p style='font-size: 18px; color: gray;'>Nenhum dado disponível para análise.</p>"
    
    # Contar o número de pendências em cada faixa
    value_summary = df["ALÇADA"].value_counts().sort_index()
    
    html = []
    html.append('<div style="display: flex; gap: 15px; align-items: center; width: 100%;">')
    
    for label, count in value_summary.items():
        card = f'''
            <div style="
                background-color: #262730;
                padding: 15px 25px;
                border-radius: 8px;
                text-align: center;
                flex: 1;
                min-width: 150px;
                max-width: 250px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            ">
                <span style="color: white; font-size: 14px;">{label}</span>
                <strong style="color: white; font-size: 20px; margin: 10px 0;">{count}</strong>
                <span style="color: #aaa; font-size: 12px;">pendências</span>
            </div>
        '''
        html.append(card.strip())
    html.append('</div>')
    return ''.join(html)

# Função para criar cards de status
def create_status_cards(df, status_mapping):
    st.subheader("Status Atuais")
    total = df.shape[0]
    cols = st.columns(len(status_mapping)+1)
    
    # Cards de status
    for i, (full, short) in enumerate(status_mapping.items()):
        with cols[i]:
            count = df[df["STATUS - OS"] == full].shape[0]
            card_style = """
                background: #262730;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            """
            st.markdown(f"""
            <div style='{card_style}'>
                <div style='font-size: 16px; color: #fff;'>{short}</div>
                <div style='font-size: 24px; font-weight: bold; color: #4CAF50; margin: 10px 0;'>{count}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Card total
    with cols[-1]:
        total_style = """
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        """
        st.markdown(f"""
        <div style='{total_style}'>
            <div style='font-size: 16px; color: #fff;'>TOTAL</div>
            <div style='font-size: 24px; font-weight: bold; color: #FF5722; margin: 10px 0;'>{total}</div>
        </div>
        """, unsafe_allow_html=True)

# Função para criar gráficos
def create_top_chart(data, x_field, y_field, title, color="#1f77b4"):
    data = data.sort_values(x_field, ascending=False).head(20)
    bar_step = 40
    bars = alt.Chart(data).mark_bar(color=color).encode(
        x=alt.X(f"{x_field}:Q", title="Pendências"),
        y=alt.Y(f"{y_field}:N", sort="-x", title=""),
        tooltip=[y_field, x_field]
    ).properties(
        height=500,
        width=bar_step * len(data)
    )
    labels = bars.mark_text(
        align='left',
        baseline='middle',
        dx=10,
        fontWeight='bold',
        fontSize=16,
        color='black'
    ).encode(
        text=alt.Text(f"{x_field}:Q", format=".0f")
    )
    return (bars + labels).configure_axis(
        labelFontSize=10,
        titleFontSize=12
    ).configure_view(
        strokeWidth=0
    )

if st.button("Distribuir OS"):
    if df_os.empty or df_team.empty:
        st.error("Carregue OS e Equipe primeiro.")
    else:
        # Inicializa o contador de atribuições
        assignment_counter = defaultdict(int)

        filtered_os = df_os.copy()
        
        # Aplica filtros somente se selecionados
        if selected_fornecedores:
            filtered_os = filtered_os[filtered_os["FORNECEDOR"].isin(selected_fornecedores)]
        if selected_alçadas:
            filtered_os = filtered_os[filtered_os["ALÇADA"].isin(selected_alçadas)]
        
        # Filtra BU apenas se a aba específica for selecionada
        if current_tab == "RAC":
            filtered_os = filtered_os[filtered_os["TIPO BU"].isin(["RAC", "Moover"])]
        elif current_tab == "GTF":
            filtered_os = filtered_os[filtered_os["TIPO BU"] == "GTF"]
        elif current_tab == "ZKM":
            filtered_os = filtered_os[filtered_os["TIPO BU"] == "Zero KM"]

        assignments = []
        undistributed_os = []  # Lista para armazenar OS não distribuídas

        for os_record in filtered_os.to_dict(orient="records"):
            try:
                valor_os = float(os_record.get("VALOR TOTAL", 0))
            except:
                valor_os = 0
            status = str(os_record.get("STATUS - OS", "")).strip()

            # Lógica de distribuição ajustada
            if status in [
                "Aguardando Aprovação Movida N2",
                "Aguardando Aprovação Movida N3",
                "Aguardando Aprovação Movida N4",
                "Aguardando Aprovação Movida NQ",
                "Aguardando Qualificação NQ",  # Novo status adicionado
                "Aguardando Aprovação da Alçada"  # Novo status adicionado
            ]:
                valid_members = df_team[df_team["ALÇADA"].str.strip().str.upper() == "N2"]
            elif status == "Aguardando Aprovação Movida N1":
                # Distribui por valor
                if valor_os < 2000:
                    valid_members = df_team[df_team["ALÇADA"].str.strip() == "0 Á 2.000"]
                elif 2000 <= valor_os < 5000:
                    valid_members = df_team[df_team["ALÇADA"].str.strip() == "2.001 Á 5.000"]
                elif 5000 <= valor_os < 10000:
                    valid_members = df_team[df_team["ALÇADA"].str.strip() == "5.001 Á 10.000"]
                else:
                    valid_members = df_team[df_team["ALÇADA"].str.strip() == "10.001 Acima"]
            else:
                # Ignora outros status ou trata conforme necessário
                undistributed_os.append({
                    'Nº da OS': os_record.get("Nº - OS", "N/A"),
                    'Motivo': f"Status '{status}' não mapeado."
                })
                continue

            # Atribuição balanceada
            if not valid_members.empty:
                valid_member_ids = valid_members['UserID'].tolist()
                
                # Atualiza o contador com novos membros, se necessário
                for uid in valid_member_ids:
                    if uid not in assignment_counter:
                        assignment_counter[uid] = 0

                # Encontra o membro com menos atribuições
                min_assignments = min(assignment_counter[uid] for uid in valid_member_ids)
                candidates = [uid for uid in valid_member_ids if assignment_counter[uid] == min_assignments]

                # Seleciona aleatoriamente entre os candidatos com menos atribuições
                selected_uid = random.choice(candidates)

                # Atualiza o contador de atribuições
                assignment_counter[selected_uid] += 1

                # Seleciona o membro pelo UserID escolhido
                member = valid_members[valid_members['UserID'] == selected_uid].iloc[0]

                # Adiciona a atribuição à lista
                assignments.append({
                    'Nº da OS': os_record.get("Nº - OS", "N/A"),
                    'Id do Usuário Responsável': member["UserID"],
                    'Responsável': member["NOMES"],
                    'Alçada': member["ALÇADA"],
                    'Valor': valor_os,
                    'Status': status
                })
            else:
                # Registra OS que não puderam ser distribuídas por falta de membros válidos
                undistributed_os.append({
                    'Nº da OS': os_record.get("Nº - OS", "N/A"),
                    'Motivo': f"Nenhum membro válido para alçada '{os_record.get('ALÇADA', 'N/A')}'."
                })

        # Exibe resultados
        if assignments:
            df_assign = pd.DataFrame(assignments)
            st.dataframe(df_assign)
            
            # Criação do arquivo Excel em memória
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_assign.to_excel(writer, index=False, sheet_name='Distribuição_OS')
            output.seek(0)
            
            # Botão de download
            st.download_button(
                label=".Download Excel",
                data=output,
                file_name='distribuicao_os.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.warning("Nenhuma OS distribuída.")

        # Relatório de OS não distribuídas
        if undistributed_os:
            st.subheader("OS Não Distribuídas")
            df_undistributed = pd.DataFrame(undistributed_os)
            st.dataframe(df_undistributed)

# Aba RAC
with tab_rac:
    st.header("Resumo RAC")
    df_rac = df_os[df_os["TIPO BU"].isin(["RAC", "Moover"])] if not df_os.empty else pd.DataFrame()
    
    if not df_rac.empty:
        st.markdown(create_value_range_summary(df_rac), unsafe_allow_html=True)
        
        status_mapping = {
            "Aguardando Aprovação da Alçada": "Aprovação da Alçada",
            "Aguardando Aprovação Movida N1": "Aprovação Movida N1",
            "Aguardando Aprovação Movida N2": "Aprovação Movida N2",
            "Aguardando Aprovação Movida N3": "Aprovação Movida N3",
            "Aguardando Aprovação Movida N4": "Aprovação Movida N4",
            "Aguardando Qualificação NQ": "Qualificação NQ"
        }
        create_status_cards(df_rac, status_mapping)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader("Piores 20 Regionais")
            top_regionais = df_rac["REGIONAL"].value_counts().reset_index(name="Pendências")
            st.altair_chart(create_top_chart(top_regionais, "Pendências", "REGIONAL", "Piores 20 Regionais"), use_container_width=True)
        with col2:
            st.subheader("Piores 20 Filiais")
            top_filiais = df_rac["FILIAL"].value_counts().reset_index(name="Pendências")
            st.altair_chart(create_top_chart(top_filiais, "Pendências", "FILIAL", "Piores 20 Filiais"), use_container_width=True)
        with col3:
            st.subheader("Piores 20 Fornecedores")
            top_fornecedores = df_rac["FORNECEDOR"].value_counts().reset_index(name="Pendências")
            st.altair_chart(create_top_chart(top_fornecedores, "Pendências", "FORNECEDOR", "Piores 20 Fornecedores"), use_container_width=True)
        with col4:
            st.subheader("OS Mais Antigas (Piores 20)")
            os_antigas = df_rac.sort_values(by="DIAS ABERTA", ascending=False).head(20)
            st.dataframe(
                os_antigas[["Nº - OS", "Data Criação O.S", "DIAS ABERTA"]],
                height=500,
                column_config={
                    "DIAS ABERTA": st.column_config.NumberColumn("Dias Abertos", format="%d dias")
                }
            )

# Aba GTF
with tab_gtf:
    st.header("Resumo GTF")
    df_gtf = df_os[df_os["TIPO BU"] == "GTF"] if not df_os.empty else pd.DataFrame()
    
    if not df_gtf.empty:
        st.markdown(create_value_range_summary(df_gtf), unsafe_allow_html=True)
        create_status_cards(df_gtf, status_mapping)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader("Piores 20 Clientes")
            top_clientes = df_gtf["CLIENTE"].value_counts().reset_index(name="Pendências")
            st.altair_chart(create_top_chart(top_clientes, "Pendências", "CLIENTE", "Piores 20 Clientes"), use_container_width=True)
        with col2:
            st.subheader("Piores 20 Fornecedores (por CNPJ)")
            cnpj_counts = df_gtf["CNPJ/CPF"].value_counts().reset_index(name="Pendências")
            cnpj_to_fornecedor = df_gtf.set_index("CNPJ/CPF")["FORNECEDOR"].to_dict()
            cnpj_counts["Fornecedor"] = cnpj_counts["CNPJ/CPF"].map(cnpj_to_fornecedor).fillna("Não identificado")
            st.altair_chart(create_top_chart(cnpj_counts, "Pendências", "Fornecedor", "Piores 20 Fornecedores (por CNPJ)"), use_container_width=True)
        with col3:
            st.subheader("OS Mais Antigas (Piores 20)")
            os_antigas = df_gtf.sort_values(by="DIAS ABERTA", ascending=False).head(20)
            st.dataframe(
                os_antigas[["Nº - OS", "Data Criação O.S", "DIAS ABERTA"]],
                height=500,
                column_config={
                    "DIAS ABERTA": st.column_config.NumberColumn("Dias Abertos", format="%d dias")
                }
            )

# Aba ZKM
with tab_zkm:
    st.header("Resumo ZKM")
    df_zkm = df_os[df_os["TIPO BU"] == "Zero KM"] if not df_os.empty else pd.DataFrame()
    
    if not df_zkm.empty:
        st.markdown(create_value_range_summary(df_zkm), unsafe_allow_html=True)
        create_status_cards(df_zkm, status_mapping)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader("Piores 20 Regionais")
            top_regionais = df_zkm["REGIONAL"].value_counts().reset_index(name="Pendências")
            st.altair_chart(create_top_chart(top_regionais, "Pendências", "REGIONAL", "Piores 20 Regionais"), use_container_width=True)
        with col2:
            st.subheader("Piores 20 Filiais")
            top_filiais = df_zkm["FILIAL"].value_counts().reset_index(name="Pendências")
            st.altair_chart(create_top_chart(top_filiais, "Pendências", "FILIAL", "Piores 20 Filiais"), use_container_width=True)
        with col3:
            st.subheader("Piores 20 Fornecedores")
            top_fornecedores = df_zkm["FORNECEDOR"].value_counts().reset_index(name="Pendências")
            st.altair_chart(create_top_chart(top_fornecedores, "Pendências", "FORNECEDOR", "Piores 20 Fornecedores"), use_container_width=True)
        with col4:
            st.subheader("OS Mais Antigas (Piores 20)")
            os_antigas = df_zkm.sort_values(by="DIAS ABERTA", ascending=False).head(20)
            st.dataframe(
                os_antigas[["Nº - OS", "Data Criação O.S", "DIAS ABERTA"]],
                height=500,
                column_config={
                    "DIAS ABERTA": st.column_config.NumberColumn("Dias Abertos", format="%d dias")
                }
            )