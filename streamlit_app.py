"""Painel Vila Aurora · ENG4550 Projeto Integrado em Sistemas Produtivos · Grupo 1

Rodar:  pip install -r requirements.txt   e depois   streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / "data"
AZUL, AZUL2, LARANJA, VERMELHO, VERDE, CINZA = "#1F4E79", "#2E86AB", "#F2A541", "#C62828", "#2E7D32", "#B7BFCC"
SEQ = [AZUL, AZUL2, LARANJA, "#6C8E5A", "#8E7DBE"]

st.set_page_config(page_title="Painel Vila Aurora", page_icon="📦", layout="wide")


# ---------------------------------------------------------------- dados
@st.cache_data
def carregar():
    d = {p.stem: pd.read_csv(p) for p in DATA.glob("*.csv")}
    d["demanda_semanal"]["data"] = pd.to_datetime(d["demanda_semanal"]["data"])
    d["demanda_semanal"]["evento"] = d["demanda_semanal"]["evento"].fillna("")
    for k in ("kpi_mensal", "kpi_familia_canal"):
        d[k]["mes"] = pd.to_datetime(d[k]["mes"])
    return d


D = carregar()
FAMILIAS = sorted(D["familias"]["familia"])
CANAIS = ["Loja", "E-commerce", "Marketplace", "Retira"]
META = D["metas_kpi"].set_index("kpi")["meta"].to_dict()


def br(v, casas=0):
    """Número no formato brasileiro."""
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def rs(v):
    return "R$ " + br(v)


def rs_mil(v):
    return "R$ " + br(v / 1000, 1) + " mil"


def kpi(col, rotulo, valor, nota):
    col.metric(rotulo, valor)
    col.caption(nota)


def layout(fig, h=340, legenda=True):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=30, b=10), template="plotly_white",
                      font=dict(family="Arial", size=12), separators=",.",
                      legend=dict(orientation="h", y=-0.18, x=0) if legenda else dict(), showlegend=legenda)
    return fig


# ---------------------------------------------------------------- barra lateral
st.sidebar.title("Filtros")
fam_sel = st.sidebar.multiselect("Famílias", FAMILIAS, default=FAMILIAS)
can_sel = st.sidebar.multiselect("Canais", CANAIS, default=CANAIS)
st.sidebar.caption("Os filtros valem para os gráficos de demanda e de KPIs por família e canal.")
st.sidebar.divider()
st.sidebar.markdown("**Cenário do Grupo 1**  \nPromoção de +60% em F3 na semana 25 · teto ESG de 18 viagens/mês · mix loja 70%, e-commerce 15%, marketplace 10%, retira 5%.")
if not fam_sel or not can_sel:
    st.warning("Selecione ao menos uma família e um canal na barra lateral.")
    st.stop()

# ---------------------------------------------------------------- cabeçalho
st.caption("ENG4550 · Projeto Integrado em Sistemas Produtivos · Grupo 1")
st.title("Vila Aurora · resultados do projeto")
st.markdown("Diagnóstico, previsão de demanda e políticas de estoque para 22 lojas e cerca de 4.200 SKUs.")

aba1, aba2, aba3, aba4 = st.tabs(["Visão geral", "Previsão de demanda", "Políticas de estoque", "Plano de ação"])

# ================================================================ 1. VISÃO GERAL
with aba1:
    km = D["kpi_mensal"]
    fill, viag = km.fill_rate_pct.mean(), km.viagens_extras.mean()
    co2, canc = km.co2_urgencias_kg.mean(), km.cancelamento_ecommerce_pct.mean()
    acima = int((km.viagens_extras > km.teto_esg_viagens).sum())

    st.markdown(f"Nos 24 meses do histórico, a operação ficou abaixo da meta nos quatro KPIs: fill rate médio de "
                f"**{br(fill, 1)}%** contra {br(META['Fill rate'])}% e **{br(viag, 1)}** viagens emergenciais por mês "
                f"contra {br(META['Viagens emergenciais'])}.")
    c = st.columns(4)
    c[0].metric("Fill rate (média mensal)", f"{br(fill, 1)}%", f"{br(fill - META['Fill rate'], 1)} p.p. vs meta de {br(META['Fill rate'])}%")
    c[1].metric("Viagens emergenciais/mês", br(viag, 1), f"{br(viag - META['Viagens emergenciais'], 1)} vs meta de {br(META['Viagens emergenciais'])}", delta_color="inverse")
    c[2].metric("CO₂e das urgências/mês", f"{br(co2)} kg", f"{br(co2 - META['CO2e de urgências'])} kg vs meta de {br(META['CO2e de urgências'])}", delta_color="inverse")
    c[3].metric("Cancelamento e-commerce", f"{br(canc, 1)}%", f"{br(canc - META['Cancelamento e-commerce'], 1)} p.p. vs meta de {br(META['Cancelamento e-commerce'])}%", delta_color="inverse")

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Fill rate mensal nunca chegou a 97%")
        fig = px.line(km, x="mes", y="fill_rate_pct", markers=True, color_discrete_sequence=[AZUL],
                      labels={"mes": "", "fill_rate_pct": "Fill rate (%)"})
        fig.add_hline(y=META["Fill rate"], line_dash="dash", line_color=VERMELHO, annotation_text="meta 97%")
        fig.update_yaxes(range=[86, 98.5])
        st.plotly_chart(layout(fig, legenda=False), use_container_width=True)
    with g2:
        st.subheader(f"Viagens extras acima do teto ESG em {acima} de 24 meses")
        cores = [VERMELHO if v > t else AZUL for v, t in zip(km.viagens_extras, km.teto_esg_viagens)]
        fig = go.Figure(go.Bar(x=km.mes, y=km.viagens_extras, marker_color=cores,
                               customdata=km.co2_urgencias_kg, hovertemplate="%{x|%b/%Y}<br>%{y} viagens<br>%{customdata} kg CO₂e<extra></extra>"))
        fig.add_hline(y=18, line_dash="dash", line_color=VERMELHO, annotation_text="teto ESG 18")
        fig.add_hline(y=META["Viagens emergenciais"], line_dash="dot", line_color=VERDE, annotation_text="meta 12")
        fig.update_yaxes(title="Viagens/mês")
        st.plotly_chart(layout(fig, legenda=False), use_container_width=True)

    g3, g4 = st.columns(2)
    with g3:
        st.subheader("Matriz impacto × evidência")
        pb = D["problemas"]
        fig = px.scatter(pb, x="evidencia", y="impacto", size="tamanho", text="id", hover_name="problema",
                         hover_data={"detalhe": True, "familias": True, "tamanho": False, "id": False},
                         color=pb.prioridade.le(2).map({True: "Prioridade 1–2", False: "Prioridade 3–5"}),
                         color_discrete_map={"Prioridade 1–2": VERMELHO, "Prioridade 3–5": AZUL}, size_max=40,
                         labels={"evidencia": "Evidência (1–10)", "impacto": "Impacto (1–10)", "color": ""})
        fig.update_traces(textposition="top center")
        fig.update_xaxes(range=[5.5, 10.8]); fig.update_yaxes(range=[5.5, 10.8])
        st.plotly_chart(layout(fig), use_container_width=True)
    with g4:
        st.subheader("Fill rate por família e canal")
        kf = D["kpi_familia_canal"].query("familia in @fam_sel and canal in @can_sel")
        piv = kf.groupby(["familia", "canal"], as_index=False).fill_rate_pct.mean()
        fig = px.bar(piv, x="fill_rate_pct", y="familia", color="canal", barmode="group", orientation="h",
                     color_discrete_sequence=SEQ, labels={"fill_rate_pct": "Fill rate médio (%)", "familia": "", "canal": ""},
                     category_orders={"canal": CANAIS})
        fig.add_vline(x=97, line_dash="dash", line_color=VERMELHO)
        fig.update_xaxes(range=[80, 100])
        st.plotly_chart(layout(fig), use_container_width=True)

# ================================================================ 2. PREVISÃO
with aba2:
    fam = D["familias"].set_index("familia")
    st.markdown(f"Não existe um modelo único para o portfólio. Nas famílias estáveis, modelos simples vencem com erro de 9% a 10% "
                f"(WAPE de **{br(fam.loc['F3 · Mercearia', 'wape_pct'], 1)}%** em F3); nas voláteis, o erro fica entre 24% e 36% "
                f"e precisa ser absorvido pelo estoque de segurança.")

    st.subheader("Demanda semanal (104 semanas)")
    dm = D["demanda_semanal"].query("familia in @fam_sel and canal in @can_sel")
    serie = dm.groupby(["semana", "data", "familia"], as_index=False).agg(demanda_un=("demanda_un", "sum"), evento=("evento", "first"))
    fig = px.line(serie, x="semana", y="demanda_un", color="familia", color_discrete_sequence=SEQ, hover_data={"evento": True, "data": "|%d/%m/%Y"},
                  labels={"semana": "Semana", "demanda_un": "Demanda (un)", "familia": ""}, category_orders={"familia": FAMILIAS})
    fig.add_vrect(x0=78.5, x1=104.5, fillcolor=CINZA, opacity=0.2, line_width=0, annotation_text="teste (79–104)", annotation_position="top left")
    ev = serie[serie.evento != ""]
    fig.add_trace(go.Scatter(x=ev.semana, y=ev.demanda_un, mode="markers", marker=dict(color=LARANJA, size=7), name="semana com evento",
                             text=ev.evento, hovertemplate="Semana %{x}<br>%{y} un<br>%{text}<extra></extra>"))
    if "F3 · Mercearia" in fam_sel:
        p = serie.query("familia == 'F3 · Mercearia' and semana == 25")
        if len(p):
            fig.add_annotation(x=25, y=p.demanda_un.iloc[0], text=f"Promoção F3: {br(p.demanda_un.iloc[0])} un", showarrow=True, arrowhead=2)
    st.plotly_chart(layout(fig, 380), use_container_width=True)

    est = dm.groupby(["familia", "semana"]).demanda_un.sum().groupby("familia").agg(["mean", "std", "max"])
    est["cv"] = est["std"] / est["mean"] * 100
    st.dataframe(est.rename(columns={"mean": "Média/semana", "std": "Desvio", "max": "Pico", "cv": "CV (%)"}).style.format(lambda v: br(v, 1)),
                 use_container_width=True)

    st.subheader("Perfil e modelo recomendado por família")
    tab = D["familias"][["familia", "demanda_media_semanal", "cv_pct", "lead_time_dias", "shelf_life", "modelo", "wape_pct", "observacao"]]
    st.dataframe(tab.rename(columns={"familia": "Família", "demanda_media_semanal": "Demanda/sem", "cv_pct": "CV (%)", "lead_time_dias": "Lead time (d)",
                                     "shelf_life": "Validade", "modelo": "Modelo recomendado", "wape_pct": "WAPE (%)", "observacao": "Observação"}),
                 hide_index=True, use_container_width=True)

    g1, g2 = st.columns([3, 2])
    with g1:
        st.subheader("WAPE por modelo e família (%)")
        w = D["wape_modelos"].pivot(index="modelo", columns="familia", values="wape_pct")
        rank = w.rank(axis=0)  # cor relativa dentro de cada família
        fig = go.Figure(go.Heatmap(z=rank.values, x=w.columns, y=w.index, text=w.map(lambda v: "" if pd.isna(v) else br(v, 1)).values,
                                   texttemplate="%{text}", colorscale=[[0, AZUL], [1, "#E8EEF5"]], showscale=False,
                                   customdata=w.values, hovertemplate="%{y} · %{x}<br>WAPE %{customdata:.2f}%<extra></extra>"))
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(layout(fig, 480, legenda=False), use_container_width=True)
        st.caption("Mais escuro = menor erro dentro da família. Célula vazia = modelo não testado.")
    with g2:
        st.subheader("AutoETS × Naive (Q4)")
        b = D["benchmark_q4"]
        fig = px.bar(b, x="metrica", y="reducao_pct", color="sku", barmode="group", text=b.reducao_pct.map(lambda v: f"−{br(v)}%"),
                     color_discrete_sequence=[AZUL, LARANJA], labels={"metrica": "", "reducao_pct": "Redução do erro (%)", "sku": ""})
        st.plotly_chart(layout(fig, 360), use_container_width=True)
        s = D["ss_q4"]
        c = st.columns(2)
        kpi(c[0], "SS Leite Integral", f"{br(s.ss[0])} un", f"σₑ = {br(s.sigma_e[0], 2)}")
        kpi(c[1], "SS Presunto Parma", f"{br(s.ss[1])} un", f"σₑ = {br(s.sigma_e[1], 2)}")
        st.caption("SS = z · σₑ · √L, com 95% de serviço (z = 1,645) e lead time de 2 semanas.")

# ================================================================ 3. ESTOQUES
with aba3:
    pol = D["politicas_q11"]; ex = D["experimentos_q12"]
    f1 = pol[pol.cenario_id == "F1 (R,S) · previsão · promoção"].iloc[0]
    f1q = pol[pol.cenario_id == "F1 (Q,r) · previsão · promoção"].iloc[0]
    f3 = pol[pol.cenario_id == "F3 (Q,r) · previsão · promoção"].iloc[0]
    ref = ex[ex.alternativa == "Reforço de 40% por 3 semanas"].iloc[0]
    perm = ex[ex.alternativa.str.startswith("Proteção permanente")].iloc[0]
    st.markdown(f"A decisão não é entre (Q,r) e (R,S): é sobre frequência e oportunidade. Em F1, a reposição semanal custa "
                f"**{rs_mil(f1.custo_medio_rs)}** por ano com {br(f1.descarte_pct, 2)}% de descarte; em F3, reforçar o estoque só antes "
                f"da promoção custa **{rs_mil(ref.custo_rs)}**, contra {rs_mil(perm.custo_rs)} da proteção permanente.")
    c = st.columns(4)
    kpi(c[0], "F1 · (R,S) semanal", rs_mil(f1.custo_medio_rs), f"fill {br(f1.fill_pct, 1)}% · descarte {br(f1.descarte_pct, 2)}%")
    kpi(c[1], "F1 · (Q,r) lote EOQ", rs_mil(f1q.custo_medio_rs), f"descarte {br(f1q.descarte_pct, 2)}% · reprova no critério de descarte")
    kpi(c[2], "F3 · (Q,r) na promoção", rs_mil(f3.custo_medio_rs), f"fill {br(f3.fill_pct, 1)}% · {br(f3.estoque_sem, 2)} sem")
    kpi(c[3], "F3 · reforço 40% × 3 sem", rs_mil(ref.custo_rs), f"{rs_mil(perm.custo_rs - ref.custo_rs)} mais barato que a proteção permanente")

    st.subheader("Custo anual simulado por política (Q11)")
    fig = px.bar(pol.sort_values("custo_medio_rs"), x="custo_medio_rs", y="cenario_id", orientation="h", color="aprovada",
                 color_discrete_map={"Sim": AZUL, "Não": CINZA}, error_x="custo_dp_rs",
                 hover_data={"fill_pct": True, "descarte_pct": True, "motivo": True},
                 labels={"custo_medio_rs": "Custo médio anual (R$)", "cenario_id": "", "aprovada": "Aprovada nos critérios Q10"})
    st.plotly_chart(layout(fig, 380), use_container_width=True)
    st.caption("364 dias, 20 replicações, z = 1,65. Barras de erro: desvio-padrão entre replicações. Critérios Q10: fill ≥ 97% e p05 ≥ 95%, ≤ 12 viagens/mês, descarte ≤ 2%.")
    with st.expander("Tabela consolidada da simulação"):
        st.dataframe(pol.drop(columns=["cenario_id"]), hide_index=True, use_container_width=True)

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Experimentos de ponto de virada (Q12)")
        exps = ["Lote × validade", "Reforço pontual", "Lead time"]
        e = st.selectbox("Experimento", exps, key="exp")
        sub = ex[ex.exp == e]
        fig = px.bar(sub, x="custo_rs", y="alternativa", orientation="h", text=sub.custo_rs.map(rs_mil), color_discrete_sequence=[AZUL],
                     hover_data={"leitura": True}, labels={"custo_rs": "Custo anual (R$)", "alternativa": ""})
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(range=[0, sub.custo_rs.max() * 1.25])
        st.plotly_chart(layout(fig, 300, legenda=False), use_container_width=True)
        for _, r in sub.iterrows():
            st.markdown(f"- **{r.alternativa}:** {r.leitura}")
    with g2:
        st.subheader("Estoque de segurança de F3 × lead time")
        sl = D["ss_lead_time_f3"]
        fig = px.line(sl, x="lead_time_dias", y="estoque_seguranca_un", color="nivel_servico", markers=True, color_discrete_sequence=SEQ,
                      labels={"lead_time_dias": "Lead time (dias)", "estoque_seguranca_un": "Estoque de segurança (un)", "nivel_servico": "Nível de serviço"})
        st.plotly_chart(layout(fig, 300), use_container_width=True)
        st.caption("σ residual = 463 un, revisão de 1 semana. Dobrar o lead time de 7 para 14 dias eleva o SS em cerca de 22%.")

    st.subheader("Semana 25 em F3: um pico de 5,8 desvios que já está no histórico")
    cs = D["cenarios_semana25"]
    c = st.columns(3)
    for col, (_, r) in zip(c, cs.iterrows()):
        val = f"{br(r.valor)}%" if r.unidade == "%" else (f"semana {br(r.valor)}" if r.unidade == "semana" else f"{br(r.valor)} {r.unidade}")
        kpi(col, r.cenario, val, f"{r.indicador}. {r.leitura}")

# ================================================================ 4. PLANO
with aba4:
    st.markdown("O ganho estatístico só vira resultado operacional se a sequência for respeitada: dados confiáveis primeiro, "
                "depois previsão por família, estoques segmentados e uma rotina semanal de S&OE.")
    etapas = [("1 · Sanear dados e WMS", "Higienização cadastral (EAN, validade, hierarquia) e baixa automática no CD para eliminar os 8% de falha e as 120 h semanais de contagem."),
              ("2 · Previsão por família", "ARIMA em F1 e F3, SES em F2, regressão com tendência e eventos em F4, Random Forest em F5."),
              ("3 · Estoques segmentados", "Fim da regra de 2 semanas: (R,S) semanal em F1; (Q,r) em F3 com reforço antes da semana 25."),
              ("4 · S&OE com gatilhos", "Reunião semanal com Operações, CD, Comercial e ESG; semáforos ligados aos KPIs e decisor por faixa.")]
    for col, (t, x) in zip(st.columns(4), etapas):
        with col.container(border=True):
            st.markdown(f"**{t}**")
            st.write(x)
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Semáforo de S&OE")
        st.markdown("🟢 **Verde:** metas atendidas  \n🟡 **Amarelo:** projeção ≥ 10 viagens no mês ou fill rate < 97,5%  \n🔴 **Vermelho:** ≥ 12 viagens ou fill rate < 96%")
        st.caption("Gatilho principal: o Comercial comunicar a promoção com duas semanas de antecedência.")
    with g2:
        st.subheader("KPIs, baseline e metas")
        st.dataframe(D["metas_kpi"][["kpi", "baseline_texto", "meta_texto", "decisor"]].rename(columns={"kpi": "KPI", "baseline_texto": "Baseline", "meta_texto": "Meta", "decisor": "Decisor"}),
                     hide_index=True, use_container_width=True)
    st.info("Limites da simulação: demanda uniforme nos dias da semana, pool único por família, ruptura como venda perdida e só duas temporadas no histórico. "
            "O fill rate simulado (≈ 100%) fica acima dos ≈ 92% observados porque falhas de cadastro, atraso do e-commerce e ausência de S&OE não estão no modelo.")

st.divider()
st.caption("Fontes: bases do caso Vila Aurora (Blocos 1 e 2) e resultados do Grupo 1 (Brief Executivo, Relatório Parcial, Relatório do Bloco 3, "
           "Políticas de Estoque Q10–Q12, notebook Q4). Valores de simulação são estimativas condicionadas às premissas do modelo.")
