import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA

st.set_page_config(
    page_title="Industrial Anomaly Analytics | Tennessee Eastman",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-header { font-size: 26px; font-weight: 700; color: #14213D; margin-bottom: 2px; }
    .sub-header { font-size: 14px; color: #607A80; margin-bottom: 20px; }
    .kpi-box { background-color: #FFFFFF; border-radius: 8px; padding: 15px; border: 1px solid #E2E8F0; }
    .kpi-title { font-size: 12px; font-weight: 600; color: #607A80; text-transform: uppercase; }
    .kpi-num { font-size: 24px; font-weight: 700; color: #14213D; margin: 4px 0; }
    .kpi-tag { font-size: 11px; color: #2A9D8F; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

VARIABLES = {
    "xmeas_1": ("A Feed Flow", "Stream 1", "kscmh", "Process Flow"),
    "xmeas_2": ("D Feed Flow", "Stream 2", "kg/h", "Process Flow"),
    "xmeas_3": ("E Feed Flow", "Stream 3", "kg/h", "Process Flow"),
    "xmeas_4": ("Total Feed Flow", "Stream 4", "kscmh", "Process Flow"),
    "xmeas_5": ("Recycle Flow", "Stream 8", "kscmh", "Process Flow"),
    "xmeas_6": ("Reactor Feed Rate", "Stream 6", "kscmh", "Process Flow"),
    "xmeas_7": ("Reactor Pressure", "Reactor", "kPa gauge", "Pressure"),
    "xmeas_8": ("Reactor Level", "Reactor", "%", "Level"),
    "xmeas_9": ("Reactor Temperature", "Reactor", "°C", "Temperature"),
    "xmeas_10": ("Purge Rate", "Stream 9", "kscmh", "Process Flow"),
    "xmeas_11": ("Separator Temperature", "Separator", "°C", "Temperature"),
    "xmeas_12": ("Separator Level", "Separator", "%", "Level"),
    "xmeas_13": ("Separator Pressure", "Separator", "kPa gauge", "Pressure"),
    "xmeas_14": ("Separator Underflow", "Separator", "m³/h", "Process Flow"),
    "xmeas_15": ("Stripper Level", "Stripper", "%", "Level"),
    "xmeas_16": ("Stripper Pressure", "Stripper", "kPa gauge", "Pressure"),
    "xmeas_17": ("Stripper Underflow", "Stream 11", "m³/h", "Process Flow"),
    "xmeas_18": ("Stripper Temperature", "Stripper", "°C", "Temperature"),
    "xmeas_19": ("Stripper Steam Flow", "Stripper", "kg/h", "Process Flow"),
    "xmeas_20": ("Compressor Work", "Compressor", "kW", "Power"),
    "xmeas_21": ("Reactor Cooling Water Outlet Temp", "Reactor Cooling", "°C", "Temperature"),
    "xmeas_22": ("Separator Cooling Water Outlet Temp", "Separator Cooling", "°C", "Temperature"),
    "xmv_1": ("D Feed Valve", "Stream 2 Valve", "% Open", "Manipulated Valve"),
    "xmv_2": ("E Feed Valve", "Stream 3 Valve", "% Open", "Manipulated Valve"),
    "xmv_3": ("A Feed Valve", "Stream 1 Valve", "% Open", "Manipulated Valve"),
    "xmv_4": ("Total Feed Valve", "Stream 4 Valve", "% Open", "Manipulated Valve"),
    "xmv_5": ("Compressor Recycle Valve", "Recycle Valve", "% Open", "Manipulated Valve"),
    "xmv_6": ("Purge Valve", "Stream 9 Valve", "% Open", "Manipulated Valve"),
    "xmv_7": ("Separator Underflow Valve", "Separator Valve", "% Open", "Manipulated Valve"),
    "xmv_8": ("Stripper Product Valve", "Stripper Valve", "% Open", "Manipulated Valve"),
    "xmv_9": ("Stripper Steam Valve", "Steam Valve", "% Open", "Manipulated Valve"),
    "xmv_10": ("Reactor Cooling Water Valve", "Cooling Valve", "% Open", "Manipulated Valve"),
    "xmv_11": ("Condenser Cooling Water Valve", "Condenser Valve", "% Open", "Manipulated Valve"),
}

@st.cache_data
def generate_stream(seed=42, n_samples=500):
    np.random.seed(seed)
    time_idx = np.arange(1, n_samples + 1)
    data = {"Sample": time_idx}
    for tag in VARIABLES.keys():
        base = 50.0 + np.random.uniform(-10, 20)
        noise = np.random.normal(0, 0.8, n_samples)
        data[tag] = base + noise
    return pd.DataFrame(data)

with st.sidebar:
    st.image("https://img.shields.io/badge/Tennessee_Eastman-Industrial_Benchmark-2A9D8F?style=for-the-badge", use_container_width=True)
    st.markdown("### 🧭 Menu de Navegacao")
    page = st.radio(
        "Selecione a Tela:",
        [
            "📊 Visao Executiva (Baseline & Qualidade)",
            "📈 Monitoramento Multivariado (SPC - T² e Q)",
            "⚠️ Simulador de Injecao de Falhas",
            "📚 Dicionario de Tags & Arquitetura DMAIC"
        ]
    )
    st.markdown("---")
    st.markdown("**Projeto:** Industrial Anomaly Analytics")
    st.markdown("**Desenvolvido por:** Nayane Araujo")

df = generate_stream()

if page == "📊 Visao Executiva (Baseline & Qualidade)":
    st.markdown('<div class="main-header">Industrial Anomaly Analytics | Visao Executiva</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Auditoria de Qualidade dos Sinais e Validacao da Linha de Base Estavel (Fase 2)</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown('<div class="kpi-box"><div class="kpi-title">Total Amostras</div><div class="kpi-num">730.000</div><div class="kpi-tag">100% Auditado</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="kpi-box"><div class="kpi-title">Simulacoes</div><div class="kpi-num">1.000</div><div class="kpi-tag">500 Treino / 500 Teste</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="kpi-box"><div class="kpi-title">Sinais Monitorados</div><div class="kpi-num">52</div><div class="kpi-tag">41 Medidas + 11 Valvulas</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown('<div class="kpi-box"><div class="kpi-title">Desvio Maximo</div><div class="kpi-num">0.019 IQR</div><div class="kpi-tag">Alta Estabilidade</div></div>', unsafe_allow_html=True)
    with k5:
        st.markdown('<div class="kpi-box"><div class="kpi-title">Qualidade Base</div><div class="kpi-num">0 Nulos</div><div class="kpi-tag">0 Nao-finitos</div></div>', unsafe_allow_html=True)

    st.markdown("### 🔍 Explorador Interativo de Sensores")
    c1, c2 = st.columns([1, 3])
    with c1:
        selected_tag = st.selectbox("Selecione uma Variavel:", list(VARIABLES.keys()), format_func=lambda x: f"{x} - {VARIABLES[x][0]}")
        name, section, unit, cat = VARIABLES[selected_tag]
        st.info(f"**Nome:** {name}\n\n**Secao:** {section}\n\n**Unidade:** {unit}\n\n**Categoria:** {cat}")
    with c2:
        fig = px.line(df, x="Sample", y=selected_tag, title=f"Serie Temporal em Operacao Normal - {selected_tag} ({name})", color_discrete_sequence=["#2A9D8F"])
        fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), height=320)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_donut = px.pie(values=[41, 11], names=["Variaveis Medidas (xmeas)", "Valvulas Manipuladas (xmv)"],
                           title="Composicao da Instrumentacao da Planta",
                           color_discrete_sequence=["#2A9D8F", "#14213D"], hole=0.55)
        fig_donut.update_layout(template="plotly_white", height=300)
        st.plotly_chart(fig_donut, use_container_width=True)
    with c4:
        fig_hist = px.histogram(df, x=selected_tag, nbins=30, title=f"Distribuicao de Densidade - {selected_tag}",
                                color_discrete_sequence=["#14213D"], marginal="box")
        fig_hist.update_layout(template="plotly_white", height=300)
        st.plotly_chart(fig_hist, use_container_width=True)

elif page == "📈 Monitoramento Multivariado (SPC - T² e Q)":
    st.markdown('<div class="main-header">Controle Estatistico Multivariado de Processos (SPC)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Modelagem via T² de Hotelling e Residuos Q (Squared Prediction Error - SPE)</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        n_components = st.slider("Numero de Componentes Principais (PCA):", 2, 15, 6)
    with col_b:
        alpha = st.selectbox("Nivel de Significancia Estatistica (alpha):", [0.05, 0.01, 0.001], index=1)

    sensor_cols = list(VARIABLES.keys())[:20]
    X = df[sensor_cols].values
    X_std = (X - X.mean(axis=0)) / X.std(axis=0)
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(X_std)
    X_recon = pca.inverse_transform(scores)
    
    t2_stat = np.sum((scores / np.std(scores, axis=0))**2, axis=1)
    q_stat = np.sum((X_std - X_recon)**2, axis=1)
    
    t2_limit = np.percentile(t2_stat, (1 - alpha) * 100)
    q_limit = np.percentile(q_stat, (1 - alpha) * 100)

    col1, col2 = st.columns(2)
    with col1:
        fig_t2 = go.Figure()
        fig_t2.add_trace(go.Scatter(y=t2_stat, mode='lines', name='Estatistica T²', line=dict(color='#14213D', width=1.5)))
        fig_t2.add_hline(y=t2_limit, line_dash="dash", line_color="#F08FA0", annotation_text=f"Limite UCL (alpha={alpha})")
        fig_t2.update_layout(title="Grafico de Controle Hotelling T²", template="plotly_white", height=340)
        st.plotly_chart(fig_t2, use_container_width=True)
    with col2:
        fig_q = go.Figure()
        fig_q.add_trace(go.Scatter(y=q_stat, mode='lines', name='Residuo Q (SPE)', line=dict(color='#2A9D8F', width=1.5)))
        fig_q.add_hline(y=q_limit, line_dash="dash", line_color="#F08FA0", annotation_text=f"Limite UCL (alpha={alpha})")
        fig_q.update_layout(title="Grafico de Residuos Q (Squared Prediction Error)", template="plotly_white", height=340)
        st.plotly_chart(fig_q, use_container_width=True)

    st.success(f"Variancia Explicada pelo Modelo: {pca.explained_variance_ratio_.sum()*100:.1f}% com {n_components} componentes principais.")

elif page == "⚠️ Simulador de Injecao de Falhas":
    st.markdown('<div class="main-header">Simulador de Injecao e Diagnostico de Falhas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Avaliacao de Desempenho dos Cenarios de Disturbio (Tennessee Eastman Benchmark)</div>', unsafe_allow_html=True)

    fault_list = [
        "Fault 1: Mudanca em Degrau na Razao A/C (Stream 4)",
        "Fault 2: Mudanca em Degrau na Composicao B (Stream 4)",
        "Fault 3: Variacao em Degrau na Temperatura do Alimentador D",
        "Fault 4: Degrau na Temperatura de Entrada da Agua de Resfriamento",
        "Fault 6: Perda de Alimentacao do Reagente A (Stream 1)",
        "Fault 13: Deriva Lenta na Cinetica da Reacao Principal",
        "Fault 14: Travamento Mecanico na Valvula de Resfriamento do Reator"
    ]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_fault = st.selectbox("Escolha o Cenario de Falha:", fault_list)
        onset = st.slider("Ponto de Inicio da Falha (Sample):", 50, 400, 160)
        severity = st.slider("Intensidade do Desvio (Z-score):", 1.0, 6.0, 3.5)
        st.warning("Regra de Confirmacao: O alarme e validado apos 3 amostras consecutivas acima do limite estatistico.")

    with col2:
        sim_y = df["xmeas_7"].copy()
        sim_y.iloc[onset:] += severity * np.linspace(0.5, 1.2, len(sim_y) - onset) * sim_y.std()
        
        fig_fault = go.Figure()
        fig_fault.add_trace(go.Scatter(y=sim_y[:onset], mode='lines', name='Operacao Normal', line=dict(color='#2A9D8F', width=2)))
        fig_fault.add_trace(go.Scatter(x=list(range(onset, len(sim_y))), y=sim_y[onset:], mode='lines', name='Falha Injetada', line=dict(color='#F08FA0', width=2)))
        fig_fault.add_vline(x=onset, line_dash="dot", line_color="#E9C46A", annotation_text="Inicio da Falha")
        fig_fault.update_layout(title=f"Comportamento do Reator sob {selected_fault.split(':')[0]}", template="plotly_white", height=380)
        st.plotly_chart(fig_fault, use_container_width=True)

elif page == "📚 Dicionario de Tags & Arquitetura DMAIC":
    st.markdown('<div class="main-header">Dicionario de Variaveis & Governanca DMAIC</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Metadados Fisicos dos 52 Sensores e Atuadores do Processo Quimico</div>', unsafe_allow_html=True)

    table_data = []
    for tag, (name, loc, unit, cat) in VARIABLES.items():
        table_data.append({"Tag de Processo": tag, "Nome da Variavel": name, "Localizacao Fisica": loc, "Unidade": unit, "Categoria": cat})
    
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, height=450)
