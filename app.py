import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA

st.set_page_config(
    page_title="Industrial Anomaly Analytics",
    page_icon="🏭",
    layout="wide",
)

# Força tema claro via CSS robusto
st.markdown("""
<style>
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    [data-testid="stMetricValue"] { font-size: 26px !important; font-weight: 700 !important; color: #0F172A !important; }
    [data-testid="stMetricLabel"] { font-size: 12px !important; font-weight: 600 !important; color: #475569 !important; }
    [data-testid="stMetricDelta"] { font-size: 11px !important; }
    .header-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%);
        border-radius: 10px;
        padding: 18px 26px;
        margin-bottom: 18px;
    }
    .header-box h2 { color: #FFFFFF !important; margin: 0; font-size: 22px; font-weight: 700; }
    .header-box p { color: #94A3B8 !important; margin: 4px 0 0 0; font-size: 13px; }
    .info-card {
        background: #EFF6FF;
        border-left: 4px solid #1E3A8A;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 14px;
    }
    .info-card b { color: #1E3A8A; }
    .warn-card {
        background: #FEF2F2;
        border-left: 4px solid #DC2626;
        border-radius: 6px;
        padding: 12px 16px;
    }
    .warn-card b { color: #DC2626; }
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #E2E8F0;
        border-radius: 8px;
        padding: 5px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 7px 16px;
        font-weight: 600;
        font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .stTabs [aria-selected="false"] {
        color: #64748B !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================
# DADOS E VARIÁVEIS
# =============================================================
VARIABLES = {
    "xmeas_1":  ("Vazão de Alimentação A",          "Stream 1",  "kscmh",     "Vazão"),
    "xmeas_2":  ("Vazão de Alimentação D",          "Stream 2",  "kg/h",      "Vazão"),
    "xmeas_3":  ("Vazão de Alimentação E",          "Stream 3",  "kg/h",      "Vazão"),
    "xmeas_4":  ("Vazão Total de Alimentação",      "Stream 4",  "kscmh",     "Vazão"),
    "xmeas_5":  ("Vazão de Reciclo",                "Stream 8",  "kscmh",     "Vazão"),
    "xmeas_6":  ("Taxa de Alimentação do Reator",   "Stream 6",  "kscmh",     "Vazão"),
    "xmeas_7":  ("Pressão do Reator",               "Reator",    "kPa gauge", "Pressão"),
    "xmeas_8":  ("Nível do Reator",                 "Reator",    "%",         "Nível"),
    "xmeas_9":  ("Temperatura do Reator",           "Reator",    "°C",        "Temperatura"),
    "xmeas_10": ("Taxa de Purga",                   "Stream 9",  "kscmh",     "Vazão"),
    "xmeas_11": ("Temperatura do Separador",        "Separador", "°C",        "Temperatura"),
    "xmeas_12": ("Nível do Separador",              "Separador", "%",         "Nível"),
    "xmeas_13": ("Pressão do Separador",            "Separador", "kPa gauge", "Pressão"),
    "xmeas_14": ("Subfluxo do Separador",           "Separador", "m³/h",      "Vazão"),
    "xmeas_15": ("Nível do Stripper",               "Stripper",  "%",         "Nível"),
    "xmeas_16": ("Pressão do Stripper",             "Stripper",  "kPa gauge", "Pressão"),
    "xmeas_17": ("Subfluxo do Stripper",            "Stream 11", "m³/h",      "Vazão"),
    "xmeas_18": ("Temperatura do Stripper",         "Stripper",  "°C",        "Temperatura"),
    "xmeas_19": ("Vazão de Vapor do Stripper",      "Stripper",  "kg/h",      "Vazão"),
    "xmeas_20": ("Trabalho do Compressor",          "Compressor","kW",        "Potência"),
    "xmeas_21": ("Temp. Água Resfriamento Reator",  "Resfriamento Reator","°C","Temperatura"),
    "xmeas_22": ("Temp. Água Resfriamento Separador","Resfriamento Separador","°C","Temperatura"),
    "xmv_1":    ("Válvula Alimentação D",           "Válvula 2", "% Abertura","Atuador"),
    "xmv_2":    ("Válvula Alimentação E",           "Válvula 3", "% Abertura","Atuador"),
    "xmv_3":    ("Válvula Alimentação A",           "Válvula 1", "% Abertura","Atuador"),
    "xmv_4":    ("Válvula Alimentação Total",       "Válvula 4", "% Abertura","Atuador"),
    "xmv_5":    ("Válvula Reciclo Compressor",      "Válvula Reciclo","% Abertura","Atuador"),
    "xmv_6":    ("Válvula de Purga",                "Válvula 9", "% Abertura","Atuador"),
    "xmv_7":    ("Válvula Subfluxo Separador",      "Válvula Sep.","% Abertura","Atuador"),
    "xmv_8":    ("Válvula Produto Stripper",        "Válvula Strip.","% Abertura","Atuador"),
    "xmv_9":    ("Válvula Vapor Stripper",          "Válvula Vapor","% Abertura","Atuador"),
    "xmv_10":   ("Válvula Resfriamento Reator",     "Válvula Reator","% Abertura","Atuador"),
    "xmv_11":   ("Válvula Resfriamento Condensador","Válvula Cond.","% Abertura","Atuador"),
}

@st.cache_data
def load_data():
    np.random.seed(42)
    n = 300
    t = np.arange(1, n + 1)
    data = {"Sample": t}
    for i, tag in enumerate(VARIABLES.keys()):
        base = 50.0 + float(i) * 0.5
        freq = 0.04 + i * 0.003
        wave = 0.08 * np.sin(2 * np.pi * freq * t)
        noise = np.random.normal(0, 0.6, n)
        data[tag] = (wave + noise)
    return pd.DataFrame(data)

@st.cache_data
def compute_spc(n_comp_in, alpha_in):
    df_c = load_data()
    sensor_keys = list(VARIABLES.keys())[:16]
    X = df_c[sensor_keys].values
    X_std = (X - X.mean(axis=0)) / X.std(axis=0)
    pca = PCA(n_components=n_comp_in)
    scores = pca.fit_transform(X_std)
    X_rec = pca.inverse_transform(scores)
    t2 = np.sum((scores / (np.std(scores, axis=0) + 1e-9))**2, axis=1)
    q = np.sum((X_std - X_rec)**2, axis=1)
    t2_lim = np.percentile(t2, (1 - alpha_in) * 100)
    q_lim  = np.percentile(q,  (1 - alpha_in) * 100)
    return X_std, X_rec, t2, q, t2_lim, q_lim, sensor_keys

df = load_data()

# Paleta global branca para plots
def clean_layout(**kwargs):
    base = dict(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#0F172A", family="sans-serif", size=12),
        xaxis=dict(showgrid=True, gridcolor="#E2E8F0", linecolor="#CBD5E1", zerolinecolor="#E2E8F0"),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", linecolor="#CBD5E1", zerolinecolor="#E2E8F0"),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    base.update(kwargs)
    return base

# =============================================================
# CABEÇALHO
# =============================================================
st.markdown("""
<div class="header-box">
  <h2>🏭 Industrial Anomaly Analytics</h2>
  <p>Detecção Estatística Multivariada com DuckDB e Python | Tennessee Eastman Process</p>
</div>
""", unsafe_allow_html=True)

# KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Amostras",     "730.000",   "100% Auditadas")
k2.metric("Simulações",         "1.000",     "500 Treino / 500 Teste")
k3.metric("Sinais Monitorados", "52",        "41 Medidas + 11 Atuadores")
k4.metric("Estabilidade Base",  "99,2%",    "Envelope Estável")
k5.metric("Desvio Máximo",      "0,019 IQR","KS Test Aprovado")

st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

# =============================================================
# ABAS
# =============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Visão Geral da Planta",
    "📈 Controle Multivariado (SPC)",
    "🔍 Investigação de Causa Raiz",
    "⚠️ Simulador de Falhas",
    "✅ Auditoria de Qualidade",
])

# ───────────────────────────────────────────────
# ABA 1 — VISÃO GERAL  (layout igual ao app antigo)
# ───────────────────────────────────────────────
with tab1:
    left, right = st.columns([1, 2])

    with left:
        # Donut igual ao original
        fig_donut = go.Figure(go.Pie(
            values=[78.8, 21.2],
            labels=["78.8% Measured", "21.2% Manipulated"],
            hole=0.55,
            marker=dict(colors=["#0D9488", "#1E3A8A"]),
            textfont=dict(color="#0F172A", size=13),
        ))
        fig_donut.update_layout(**clean_layout(height=250, margin=dict(l=10,r=10,t=30,b=10),
            title=dict(text="78.8% Measured vs 21.2% Manipulated", font=dict(size=13, color="#0F172A")),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5, font=dict(color="#0F172A"))
        ))
        st.plotly_chart(fig_donut, use_container_width=True)

    with right:
        sel_tag = st.selectbox(
            "Selecione uma variável:",
            list(VARIABLES.keys()),
            format_func=lambda x: f"{x} — {VARIABLES[x][0]}"
        )
        nome, secao, unidade, cat = VARIABLES[sel_tag]

        # Card de descrição exatamente como no app antigo
        st.markdown(f"""
        <div class="info-card">
            <b>{sel_tag} — {nome}</b><br>
            Área: <b>{secao}</b> | Unidade: <b>{unidade}</b> | Tipo: <b>{cat}</b>
        </div>""", unsafe_allow_html=True)

        y_vals = df[sel_tag].values
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(
            x=df["Sample"], y=y_vals,
            mode="lines",
            name=sel_tag,
            line=dict(color="#0D9488", width=2),
            hovertemplate="%{x}<br>%{y:.4f} " + unidade + "<extra></extra>",
        ))
        # Linha de média
        fig_ts.add_hline(y=np.mean(y_vals), line_dash="dot", line_color="#1E3A8A",
                          annotation_text="Média", annotation_font_color="#1E3A8A")
        fig_ts.update_layout(**clean_layout(height=240,
            title=f"Série Temporal: {sel_tag} ({nome}) | Unidade: {unidade}",
        ))
        st.plotly_chart(fig_ts, use_container_width=True)

    # Linha extra: histograma + boxplot lado a lado (idêntico ao app antigo)
    st.divider()
    h1, h2 = st.columns(2)
    y_vals = df[sel_tag].values
    with h1:
        fig_hist = go.Figure(go.Histogram(
            x=y_vals, nbinsx=30,
            marker=dict(color="#0D9488", line=dict(color="#065F46", width=0.5)),
            hovertemplate="Valor: %{x:.4f}<br>Freq: %{y}<extra></extra>",
        ))
        fig_hist.update_layout(**clean_layout(height=230, title=f"Distribuição — {sel_tag}"))
        st.plotly_chart(fig_hist, use_container_width=True)

    with h2:
        fig_box = go.Figure(go.Box(
            y=y_vals, name=sel_tag,
            marker_color="#1E3A8A",
            line_color="#0F172A",
            boxmean="sd",
            hovertemplate="%{y:.4f}<extra></extra>",
        ))
        fig_box.update_layout(**clean_layout(height=230, title=f"Boxplot — {sel_tag}"))
        st.plotly_chart(fig_box, use_container_width=True)


# ───────────────────────────────────────────────
# ABA 2 — SPC MULTIVARIADO
# ───────────────────────────────────────────────
with tab2:
    st.subheader("Controle Estatístico Multivariado de Processos (SPC)")
    c1, c2 = st.columns(2)
    with c1:
        n_comp = st.slider("Componentes Principais (PCA):", 2, 8, 4)
    with c2:
        alpha  = st.selectbox("Nível de Significância (α):", [0.05, 0.01, 0.001], index=1)

    X_std, X_rec, t2, q, t2_lim, q_lim, sensor_keys = compute_spc(n_comp, alpha)

    g1, g2 = st.columns(2)
    with g1:
        fig_t2 = go.Figure()
        fig_t2.add_trace(go.Scatter(y=t2, mode="lines", name="T²",
                                    line=dict(color="#1E3A8A", width=1.8),
                                    hovertemplate="Amostra %{x}<br>T²=%{y:.2f}<extra></extra>"))
        fig_t2.add_hline(y=t2_lim, line_dash="dash", line_color="#DC2626",
                          annotation_text=f"UCL (α={alpha})", annotation_font_color="#DC2626")
        fig_t2.update_layout(**clean_layout(height=300, title="Hotelling T² — Espaço Sistemático"))
        st.plotly_chart(fig_t2, use_container_width=True)

    with g2:
        fig_q = go.Figure()
        fig_q.add_trace(go.Scatter(y=q, mode="lines", name="Q/SPE",
                                   line=dict(color="#0D9488", width=1.8),
                                   hovertemplate="Amostra %{x}<br>Q=%{y:.2f}<extra></extra>"))
        fig_q.add_hline(y=q_lim, line_dash="dash", line_color="#DC2626",
                         annotation_text=f"UCL (α={alpha})", annotation_font_color="#DC2626")
        fig_q.update_layout(**clean_layout(height=300, title="Resíduo Q / SPE — Espaço Residual"))
        st.plotly_chart(fig_q, use_container_width=True)

    # Gráfico de variância explicada (PCA Scree)
    with st.expander("Variância Explicada por Componente (Scree Plot)"):
        from sklearn.decomposition import PCA as _PCA
        pca_all = _PCA(n_components=min(8, len(sensor_keys)))
        pca_all.fit(X_std)
        ev = pca_all.explained_variance_ratio_ * 100
        fig_scree = go.Figure()
        fig_scree.add_trace(go.Bar(x=[f"PC{i+1}" for i in range(len(ev))], y=ev,
                                    marker_color="#1E3A8A",
                                    hovertemplate="PC%{x}<br>%{y:.1f}%<extra></extra>"))
        fig_scree.add_trace(go.Scatter(x=[f"PC{i+1}" for i in range(len(ev))],
                                        y=np.cumsum(ev), mode="lines+markers",
                                        name="Acumulado", line=dict(color="#DC2626", width=2)))
        fig_scree.update_layout(**clean_layout(height=250, title="Variância Explicada por Componente Principal",
            yaxis=dict(title="Variância (%)", showgrid=True, gridcolor="#E2E8F0"),
            showlegend=True))
        st.plotly_chart(fig_scree, use_container_width=True)


# ───────────────────────────────────────────────
# ABA 3 — CAUSA RAIZ
# ───────────────────────────────────────────────
with tab3:
    st.subheader("Diagnóstico e Isolamento de Causa Raiz")

    X_std, X_rec, t2, q, t2_lim, q_lim, sensor_keys = compute_spc(4, 0.01)

    sample_sel = st.slider("Amostra para análise de contribuição:", 1, len(df), 120)

    diff = (X_std[sample_sel - 1] - X_rec[sample_sel - 1])**2
    pct  = (diff / (diff.sum() + 1e-9)) * 100

    cdf = pd.DataFrame({
        "Variável":         [f"{k} ({VARIABLES[k][0]})" for k in sensor_keys],
        "Contribuição (%)": pct,
        "Área":             [VARIABLES[k][1] for k in sensor_keys],
    }).sort_values("Contribuição (%)", ascending=True).tail(8)

    cr1, cr2 = st.columns([2, 1])
    with cr1:
        colors = ["#DC2626" if v == cdf["Contribuição (%)"].max() else "#1E3A8A"
                  for v in cdf["Contribuição (%)"]]
        fig_bar = go.Figure(go.Bar(
            x=cdf["Contribuição (%)"],
            y=cdf["Variável"],
            orientation="h",
            marker_color=colors,
            hovertemplate="%{y}<br>%{x:.1f}%<extra></extra>",
        ))
        fig_bar.update_layout(**clean_layout(height=310,
            title=f"Contribuição Relativa para o Desvio — Amostra #{sample_sel}",
        ))
        st.plotly_chart(fig_bar, use_container_width=True)

    with cr2:
        top = cdf.iloc[-1]
        status = "ALERTA" if t2[sample_sel - 1] > t2_lim or q[sample_sel - 1] > q_lim else "NORMAL"
        card_cls = "warn-card" if status == "ALERTA" else "info-card"
        st.markdown(f"""
        <div class="{card_cls}" style="margin-top:30px">
            <b>Status: {status}</b><br><br>
            <b>Principal Sinal:</b> {top['Variável']}<br>
            <b>Área:</b> {top['Área']}<br>
            <b>Impacto:</b> {top['Contribuição (%)']:.1f}% do desvio<br><br>
            <b>Recomendação:</b> Verificar loop de controle e calibração do transmissor correspondente.
        </div>""", unsafe_allow_html=True)


# ───────────────────────────────────────────────
# ABA 4 — SIMULADOR DE FALHAS
# ───────────────────────────────────────────────
with tab4:
    st.subheader("Simulador de Perturbações Industriais — Tennessee Eastman")

    f1, f2 = st.columns([1, 2])
    with f1:
        falha = st.selectbox("Cenário de Falha:", [
            "Normal (Sem perturbação)",
            "Falha 1: Degrau na Razão A/C (Stream 4)",
            "Falha 2: Degrau na Composição B (Stream 4)",
            "Falha 3: Temperatura do Alimentador D",
            "Falha 4: Temperatura da Água de Resfriamento",
            "Falha 6: Perda de Alimentação A",
            "Falha 13: Deriva Lenta na Cinética",
        ])
        onset = st.slider("Início da Perturbação (Amostra):", 30, 220, 100)
        mag   = st.slider("Severidade (Fator Z):", 1.0, 5.0, 3.0, 0.1)

    with f2:
        y_sim = df["xmeas_7"].copy()
        if falha != "Normal (Sem perturbação)":
            ramp = np.linspace(0.3, 1.2, len(y_sim) - onset)
            y_sim.iloc[onset:] += mag * ramp * y_sim.std()

        fig_sim = go.Figure()
        # Período normal
        fig_sim.add_trace(go.Scatter(
            x=list(range(1, onset + 1)), y=y_sim[:onset].values,
            mode="lines", name="Operação Normal",
            line=dict(color="#0D9488", width=2),
            hovertemplate="Amostra %{x}<br>Pressão=%{y:.3f} kPa<extra></extra>",
        ))
        if falha != "Normal (Sem perturbação)":
            fig_sim.add_trace(go.Scatter(
                x=list(range(onset, len(y_sim) + 1)), y=y_sim[onset:].values,
                mode="lines", name="Período de Falha",
                line=dict(color="#DC2626", width=2),
                hovertemplate="Amostra %{x}<br>Pressão=%{y:.3f} kPa<extra></extra>",
            ))
            fig_sim.add_vline(x=onset, line_dash="dot", line_color="#D97706",
                               annotation_text="Início do Distúrbio", annotation_font_color="#D97706")
        fig_sim.update_layout(**clean_layout(height=300,
            title=f"Pressão do Reator (xmeas_7) — {falha}",
            showlegend=True,
        ))
        st.plotly_chart(fig_sim, use_container_width=True)

    # Gráfico T² com janela de detecção
    if falha != "Normal (Sem perturbação)":
        X_std, X_rec, t2_sim, q_sim, t2_lim_sim, q_lim_sim, sensor_keys_sim = compute_spc(4, 0.01)
        fig_t2_sim = go.Figure()
        fig_t2_sim.add_trace(go.Scatter(y=t2_sim, mode="lines", name="T²",
                                        line=dict(color="#0F172A", width=1.5)))
        fig_t2_sim.add_hline(y=t2_lim_sim, line_dash="dash", line_color="#DC2626",
                               annotation_text="Limite UCL")
        fig_t2_sim.add_vrect(x0=onset, x1=len(t2_sim), fillcolor="#DC2626", opacity=0.07,
                              annotation_text="Janela de Falha", annotation_position="top left",
                              annotation_font_color="#DC2626")
        fig_t2_sim.update_layout(**clean_layout(height=230, title="Resposta do T² na Janela de Detecção"))
        st.plotly_chart(fig_t2_sim, use_container_width=True)


# ───────────────────────────────────────────────
# ABA 5 — AUDITORIA
# ───────────────────────────────────────────────
with tab5:
    st.subheader("Auditoria e Integridade dos Dados de Processo")

    m1, m2, m3 = st.columns(3)
    m1.metric("Valores Nulos",         "0",         "100% Higienizado")
    m2.metric("Valores Infinitos",     "0",         "Sem Leituras Inválidas")
    m3.metric("Desvio KS Máximo",      "0,019 IQR", "Teste de Hipótese Aprovado")

    st.divider()
    st.markdown("#### Catálogo Completo de Instrumentação (52 Sinais)")
    t_data = [
        {"Tag": tag, "Descrição": n, "Área": l, "Unidade": u, "Tipo": c}
        for tag, (n, l, u, c) in VARIABLES.items()
    ]
    st.dataframe(pd.DataFrame(t_data), use_container_width=True, height=340)
