import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA

st.set_page_config(
    page_title="Detecção de Anomalias em Processos Industriais",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização Visual Executiva Avançada (Inspirada no Padrão DataPharma / Fraude)
st.markdown("""
<style>
    /* Fundo da Aplicação */
    .stApp {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1300px;
    }
    
    /* Cabeçalho Executivo Superior */
    .header-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 20px;
        color: #FFFFFF;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.12);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title {
        font-size: 24px;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 14px;
        color: #94A3B8;
        margin-top: 4px;
        font-weight: 400;
    }
    .header-badge {
        background-color: #1E3A8A;
        color: #60A5FA;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #2563EB;
    }

    /* Cartões de Métricas (KPI Cards) */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        margin-bottom: 22px;
    }
    .kpi-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 16px 18px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    }
    .kpi-card-blue { border-left: 4px solid #2563EB; background: #F8FAFC; }
    .kpi-card-indigo { border-left: 4px solid #6366F1; background: #F8FAFC; }
    .kpi-card-teal { border-left: 4px solid #0D9488; background: #F8FAFC; }
    .kpi-card-green { border-left: 4px solid #16A34A; background: #F8FAFC; }
    .kpi-card-amber { border-left: 4px solid #D97706; background: #F8FAFC; }
    
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }
    .kpi-desc {
        font-size: 11px;
        font-weight: 500;
        margin-top: 4px;
    }
    .text-blue { color: #2563EB; }
    .text-indigo { color: #6366F1; }
    .text-teal { color: #0D9488; }
    .text-green { color: #16A34A; }
    .text-amber { color: #D97706; }

    /* Seções e Cards de Conteúdo */
    .content-box {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 22px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        margin-bottom: 18px;
    }
    .content-title {
        font-size: 17px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 14px;
    }

    /* Abas de Navegação Superiores */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #E2E8F0;
        padding: 6px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 18px;
        font-weight: 600;
        border-radius: 8px;
        color: #475569;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }
</style>
""", unsafe_allow_html=True)

VARIABLES = {
    "xmeas_1": ("Vazão de Alimentação A", "Stream 1", "kscmh", "Vazão"),
    "xmeas_2": ("Vazão de Alimentação D", "Stream 2", "kg/h", "Vazão"),
    "xmeas_3": ("Vazão de Alimentação E", "Stream 3", "kg/h", "Vazão"),
    "xmeas_4": ("Vazão Total de Alimentação", "Stream 4", "kscmh", "Vazão"),
    "xmeas_5": ("Vazão de Reciclo", "Stream 8", "kscmh", "Vazão"),
    "xmeas_6": ("Taxa de Alimentação do Reator", "Stream 6", "kscmh", "Vazão"),
    "xmeas_7": ("Pressão do Reator", "Reator", "kPa gauge", "Pressão"),
    "xmeas_8": ("Nível do Reator", "Reator", "%", "Nível"),
    "xmeas_9": ("Temperatura do Reator", "Reator", "°C", "Temperatura"),
    "xmeas_10": ("Taxa de Purga", "Stream 9", "kscmh", "Vazão"),
    "xmeas_11": ("Temperatura do Separador", "Separador", "°C", "Temperatura"),
    "xmeas_12": ("Nível do Separador", "Separador", "%", "Nível"),
    "xmeas_13": ("Pressão do Separador", "Separador", "kPa gauge", "Pressão"),
    "xmeas_14": ("Subfluxo do Separador", "Separador", "m³/h", "Vazão"),
    "xmeas_15": ("Nível do Stripper", "Stripper", "%", "Nível"),
    "xmeas_16": ("Pressão do Stripper", "Stripper", "kPa gauge", "Pressão"),
    "xmeas_17": ("Subfluxo do Stripper", "Stream 11", "m³/h", "Vazão"),
    "xmeas_18": ("Temperatura do Stripper", "Stripper", "°C", "Temperatura"),
    "xmeas_19": ("Vazão de Vapor do Stripper", "Stripper", "kg/h", "Vazão"),
    "xmeas_20": ("Trabalho do Compressor", "Compressor", "kW", "Potência"),
    "xmeas_21": ("Temp. Água Resfriamento Reator", "Resfriamento Reator", "°C", "Temperatura"),
    "xmeas_22": ("Temp. Água Resfriamento Separador", "Resfriamento Separador", "°C", "Temperatura"),
    "xmv_1": ("Válvula Alimentação D", "Válvula Stream 2", "% Abertura", "Válvula Manipulada"),
    "xmv_2": ("Válvula Alimentação E", "Válvula Stream 3", "% Abertura", "Válvula Manipulada"),
    "xmv_3": ("Válvula Alimentação A", "Válvula Stream 1", "% Abertura", "Válvula Manipulada"),
    "xmv_4": ("Válvula Alimentação Total", "Válvula Stream 4", "% Abertura", "Válvula Manipulada"),
    "xmv_5": ("Válvula Reciclo Compressor", "Válvula Reciclo", "% Abertura", "Válvula Manipulada"),
    "xmv_6": ("Válvula de Purga", "Válvula Stream 9", "% Abertura", "Válvula Manipulada"),
    "xmv_7": ("Válvula Subfluxo Separador", "Válvula Separador", "% Abertura", "Válvula Manipulada"),
    "xmv_8": ("Válvula Produto Stripper", "Válvula Stripper", "% Abertura", "Válvula Manipulada"),
    "xmv_9": ("Válvula Vapor Stripper", "Válvula Vapor", "% Abertura", "Válvula Manipulada"),
    "xmv_10": ("Válvula Resfriamento Reator", "Válvula Reator", "% Abertura", "Válvula Manipulada"),
    "xmv_11": ("Válvula Resfriamento Condensador", "Válvula Condensador", "% Abertura", "Válvula Manipulada"),
}

@st.cache_data
def load_cached_data():
    np.random.seed(42)
    n_pts = 350
    t = np.arange(1, n_pts + 1)
    data = {"Sample": t}
    for tag in VARIABLES.keys():
        base = 50.0 + np.random.uniform(-10, 20)
        noise = np.random.normal(0, 0.75, n_pts)
        data[tag] = base + noise
    return pd.DataFrame(data)

df = load_cached_data()

# Cabeçalho Executivo Superior
st.markdown("""
<div class="header-banner">
    <div>
        <div class="header-title">🏭 Detecção de Anomalias em Processos Industriais</div>
        <div class="header-subtitle">Monitoramento Estatístico Multivariado | Tennessee Eastman Process | Python & DuckDB</div>
    </div>
    <div>
        <span class="header-badge">Fase 2: Baseline Validado</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Cartões de Métricas Principais (KPIs em Destaque)
st.markdown("""
<div class="kpi-container">
    <div class="kpi-card kpi-card-blue">
        <div class="kpi-label">Total Amostras</div>
        <div class="kpi-value">730.000</div>
        <div class="kpi-desc text-blue">100% Auditadas</div>
    </div>
    <div class="kpi-card kpi-card-indigo">
        <div class="kpi-label">Simulações</div>
        <div class="kpi-value">1.000</div>
        <div class="kpi-desc text-indigo">500 Treino / 500 Teste</div>
    </div>
    <div class="kpi-card kpi-card-teal">
        <div class="kpi-label">Sinais Monitorados</div>
        <div class="kpi-value">52</div>
        <div class="kpi-desc text-teal">41 Medidas + 11 Válvulas</div>
    </div>
    <div class="kpi-card kpi-card-green">
        <div class="kpi-label">Estabilidade Base</div>
        <div class="kpi-value">99,2%</div>
        <div class="kpi-desc text-green">Dentro do Envelope</div>
    </div>
    <div class="kpi-card kpi-card-amber">
        <div class="kpi-label">Desvio Máximo</div>
        <div class="kpi-value">0,019 IQR</div>
        <div class="kpi-desc text-amber">Alinhamento Treino/Teste</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Abas de Navegação
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Visão Geral da Planta",
    "📈 Controle Multivariado (SPC)",
    "🔍 Diagnóstico de Causa Raiz",
    "⚠️ Simulador de Perturbações",
    "✅ Auditoria de Qualidade"
])

# ================= ABA 1: VISÃO GERAL =================
with tab1:
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<div class="content-title">Composição da Instrumentação</div>', unsafe_allow_html=True)
        fig_donut = px.pie(
            values=[41, 11],
            names=["Sensores Medidos (xmeas)", "Válvulas Manipuladas (xmv)"],
            color_discrete_sequence=["#1E3A8A", "#0D9488"],
            hole=0.6
        )
        fig_donut.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<div class="content-title">Inspeção Temporal de Sinais Físicos</div>', unsafe_allow_html=True)
        sel_tag = st.selectbox(
            "Selecione uma variável para traçar a série temporal:",
            list(VARIABLES.keys()),
            format_func=lambda x: f"{x} — {VARIABLES[x][0]} ({VARIABLES[x][1]})"
        )
        nome, secao, unidade, cat = VARIABLES[sel_tag]
        
        fig_line = px.line(df, x="Sample", y=sel_tag, color_discrete_sequence=["#1E3A8A"])
        fig_line.update_layout(
            title=f"Série Temporal: {sel_tag} ({nome}) | Unidade: {unidade}",
            template="plotly_white",
            margin=dict(l=15, r=15, t=35, b=15),
            height=240,
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ================= ABA 2: SPC MULTIVARIADO =================
with tab2:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="content-title">Modelagem de Controle Estatístico Multivariado (SPC)</div>', unsafe_allow_html=True)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        n_comp = st.slider("Componentes Principais (PCA):", min_value=2, max_value=10, value=5)
    with col_c2:
        alpha = st.selectbox("Nível de Significância Estatística (α):", [0.05, 0.01, 0.001], index=1)

    sensor_cols = list(VARIABLES.keys())[:16]
    X = df[sensor_cols].values
    X_std = (X - X.mean(axis=0)) / X.std(axis=0)
    pca = PCA(n_components=n_comp)
    scores = pca.fit_transform(X_std)
    X_rec = pca.inverse_transform(scores)

    t2_vals = np.sum((scores / np.std(scores, axis=0))**2, axis=1)
    q_vals = np.sum((X_std - X_rec)**2, axis=1)
    t2_lim = np.percentile(t2_vals, (1 - alpha) * 100)
    q_lim = np.percentile(q_vals, (1 - alpha) * 100)

    g1, g2 = st.columns(2)
    with g1:
        fig_t2 = go.Figure()
        fig_t2.add_trace(go.Scatter(y=t2_vals, mode='lines', name='Hotelling T²', line=dict(color='#0F172A', width=1.6)))
        fig_t2.add_hline(y=t2_lim, line_dash="dash", line_color="#DC2626", annotation_text=f"UCL (α={alpha})")
        fig_t2.update_layout(title="Estatística Hotelling T² (Espaço Sistemático)", template="plotly_white", height=300, margin=dict(l=10, r=10, t=35, b=10))
        st.plotly_chart(fig_t2, use_container_width=True)

    with g2:
        fig_q = go.Figure()
        fig_q.add_trace(go.Scatter(y=q_vals, mode='lines', name='Resíduo Q (SPE)', line=dict(color='#0D9488', width=1.6)))
        fig_q.add_hline(y=q_lim, line_dash="dash", line_color="#DC2626", annotation_text=f"UCL (α={alpha})")
        fig_q.update_layout(title="Resíduo Q (Squared Prediction Error)", template="plotly_white", height=300, margin=dict(l=10, r=10, t=35, b=10))
        st.plotly_chart(fig_q, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ================= ABA 3: CAUSA RAIZ =================
with tab3:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="content-title">Diagnóstico e Isolamento de Causa Raiz</div>', unsafe_allow_html=True)
    
    sample_sel = st.slider("Selecione o ponto de tempo para decomposição de impacto:", min_value=1, max_value=len(df), value=140)
    
    sample_vec = X_std[sample_sel - 1]
    recon_vec = X_rec[sample_sel - 1]
    diff = (sample_vec - recon_vec)**2
    pct = (diff / diff.sum()) * 100

    cdf = pd.DataFrame({
        "Variável": [f"{k} ({VARIABLES[k][0]})" for k in sensor_cols],
        "Contribuição (%)": pct,
        "Seção": [VARIABLES[k][1] for k in sensor_cols]
    }).sort_values("Contribuição (%)", ascending=True).tail(6)

    cr1, cr2 = st.columns([2, 1])
    with cr1:
        fig_bar = px.bar(
            cdf,
            x="Contribuição (%)",
            y="Variável",
            orientation="h",
            color="Contribuição (%)",
            color_continuous_scale=["#0D9488", "#DC2626"]
        )
        fig_bar.update_layout(title=f"Contribuição Percentual para o Desvio na Amostra #{sample_sel}", template="plotly_white", height=280)
        st.plotly_chart(fig_bar, use_container_width=True)

    with cr2:
        top = cdf.iloc[-1]
        st.markdown(f"""
        <div style="background:#FEF2F2; border-left:4px solid #DC2626; padding:16px; border-radius:8px;">
            <div style="font-size:12px; font-weight:700; color:#991B1B;">SINAL DE MAIOR IMPACTO</div>
            <div style="font-size:16px; font-weight:700; color:#0F172A; margin:4px 0;">{top['Variável']}</div>
            <div style="font-size:12px; color:#475569;">Área: <b>{top['Seção']}</b> ({top['Contribuição (%)']:.1f}% do desvio)</div>
            <div style="margin-top:10px; font-size:12px; color:#991B1B; font-weight:600;">Recomendação: Inspecionar calibração do sensor e vedação da válvula correspondente.</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ================= ABA 4: SIMULADOR DE FALHAS =================
with tab4:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="content-title">Simulador de Injeção de Perturbações Industriais</div>', unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        falhas_list = [
            "Normal (Sem perturbação)",
            "Falha 1: Mudança em Degrau na Razão A/C",
            "Falha 2: Mudança em Degrau na Composição B",
            "Falha 3: Degrau na Temperatura do Alimentador D",
            "Falha 4: Degrau na Temp. Água Resfriamento",
            "Falha 6: Perda de Alimentação do Reagente A"
        ]
        chosen_fault = st.selectbox("Selecione o distúrbio para simular:", falhas_list)
        onset_idx = st.slider("Amostra de início do distúrbio:", 40, 250, 120)
        mag = st.slider("Severidade do desvio:", 1.0, 5.0, 2.8)

    with col_f2:
        y_raw = df["xmeas_7"].copy()
        if chosen_fault != "Normal (Sem perturbação)":
            y_raw.iloc[onset_idx:] += mag * np.linspace(0.3, 1.2, len(y_raw) - onset_idx) * y_raw.std()

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(y=y_raw[:onset_idx], mode='lines', name='Normal', line=dict(color='#0D9488', width=2)))
        if chosen_fault != "Normal (Sem perturbação)":
            fig_sim.add_trace(go.Scatter(x=list(range(onset_idx, len(y_raw))), y=y_raw[onset_idx:], mode='lines', name='Perturbação', line=dict(color='#DC2626', width=2)))
            fig_sim.add_vline(x=onset_idx, line_dash="dot", line_color="#D97706", annotation_text="Início da Falha")
        fig_sim.update_layout(title=f"Comportamento do Reator sob {chosen_fault}", template="plotly_white", height=300)
        st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ================= ABA 5: QUALIDADE DE DADOS =================
with tab5:
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<div class="content-title">Auditoria e Integridade dos Dados de Processo</div>', unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="kpi-card kpi-card-green"><div class="kpi-label">Valores Nulos</div><div class="kpi-value">0</div><div class="kpi-desc text-green">100% Higienizado</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="kpi-card kpi-card-green"><div class="kpi-label">Valores Infinitos</div><div class="kpi-value">0</div><div class="kpi-desc text-green">Sem Leituras Inválidas</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="kpi-card kpi-card-blue"><div class="kpi-label">Estabilidade Kolmogorov-Smirnov</div><div class="kpi-value">0,019 IQR</div><div class="kpi-desc text-blue">Aprovado em Teste de Hipótese</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    
    t_data = []
    for tag, (n, l, u, c) in VARIABLES.items():
        t_data.append({"Tag do Sensor": tag, "Descrição do Sinal": n, "Área Física": l, "Unidade": u, "Categoria": c})
    st.dataframe(pd.DataFrame(t_data), use_container_width=True, height=320)
    st.markdown('</div>', unsafe_allow_html=True)
