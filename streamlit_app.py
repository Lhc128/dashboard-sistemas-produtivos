"""Painel Vila Aurora · ENG4550 Projeto Integrado em Sistemas Produtivos · Grupo 1

Rodar:  pip install -r requirements.txt   e depois   streamlit run streamlit_app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

try:
    from streamlit_option_menu import option_menu
except ImportError:  # o painel funciona mesmo sem o pacote, com um menu simples
    option_menu = None

DATA = Path(__file__).parent / "data"

# ------------------------------------------------------------------ paleta escura
FUNDO = "#0B1626"      # fundo da página
LATERAL = "#0F2038"    # barra lateral
PAINEL = "#12233A"     # cartões
CABEC = "#1A3556"      # cabeçalho dos cartões de KPI
BORDA = "#22406A"
AZUL = "#2E86DE"       # série principal
CIANO = "#56CCF2"      # série secundária
ROXO = "#8E7CF0"
AMBAR = "#F2B544"
CORAL = "#F0645A"
VERDE = "#3CCB8F"
TEXTO = "#E8EEF6"
SUAVE = "#93A6BF"
GRADE = "#1E3350"
SERIES = [AZUL, CIANO, AMBAR, ROXO, "#4FD1A5"]

st.set_page_config(page_title="Painel Vila Aurora", page_icon="🌅", layout="wide", initial_sidebar_state="expanded")

pio.templates["aurora_dark"] = go.layout.Template(layout=dict(
    font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=12, color=TEXTO),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", colorway=SERIES,
    xaxis=dict(automargin=True, gridcolor=GRADE, linecolor=BORDA, zeroline=False, tickfont=dict(color=SUAVE), title=dict(font=dict(color=SUAVE))),
    yaxis=dict(automargin=True, gridcolor=GRADE, linecolor=BORDA, zeroline=False, tickfont=dict(color=SUAVE), title=dict(font=dict(color=SUAVE))),
    hoverlabel=dict(bgcolor=PAINEL, bordercolor=BORDA, font=dict(color=TEXTO, family="Inter, Arial")),
    legend=dict(font=dict(color=SUAVE)), separators=",.",
))
pio.templates.default = "aurora_dark"

FONTE = "'Inter', 'Segoe UI', Arial, sans-serif"
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, p, li, label {{ font-family: {FONTE}; }}
.stApp {{ background: {FUNDO}; color: {TEXTO}; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1400px; }}
h1, h2, h3, h4 {{ font-family: {FONTE} !important; color: {TEXTO} !important; }}

/* barra lateral */
[data-testid="stSidebar"] {{ background: {LATERAL}; border-right: 1px solid {BORDA}; }}
[data-testid="stSidebar"] * {{ color: {TEXTO}; }}
[data-testid="stSidebar"] [data-baseweb="select"] > div {{ background: {PAINEL}; border-color: {BORDA}; }}
[data-testid="stSidebar"] span[data-baseweb="tag"] {{ background: {CABEC} !important; border: 1px solid {BORDA}; }}
.logo {{ text-align: center; margin: .2rem 0 1rem; }}
.logo .nm {{ font-weight: 800; font-size: 1.35rem; letter-spacing: .04em; margin-top: .3rem;
             background: linear-gradient(90deg, {AZUL}, {ROXO}); -webkit-background-clip: text; background-clip: text; color: transparent !important; }}
.logo .sb {{ font-size: .75rem; color: {SUAVE} !important; }}
.filtro {{ font-weight: 700; font-size: 1.05rem; margin: .4rem 0 .2rem; }}
.side-box {{ background: {PAINEL}; border: 1px solid {BORDA}; border-radius: 10px; padding: .75rem .85rem; font-size: .8rem; line-height: 1.5; color: {SUAVE} !important; }}
.side-box b {{ color: {AMBAR} !important; }}

/* títulos */
.titulo {{ display: flex; align-items: center; gap: .6rem; font-weight: 800; font-size: 1.55rem; margin-bottom: .2rem; }}
.sub {{ color: {SUAVE}; font-size: .85rem; margin-bottom: 1.1rem; }}
.pagina {{ font-weight: 700; font-size: 1.25rem; margin: .4rem 0 .7rem; }}
.pagina span {{ color: {CIANO}; }}

/* expander estilo "Tabela" */
[data-testid="stExpander"] details {{ background: {PAINEL}; border: 1px solid {BORDA}; border-radius: 8px; }}
[data-testid="stExpander"] summary {{ color: {TEXTO}; }}

/* cartões de KPI: cabeçalho com alfinete + valor */
.kgrid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; margin: 1rem 0 .6rem; }}
.kc .hd {{ background: {CABEC}; border: 1px solid {BORDA}; border-radius: 6px; padding: .65rem .8rem; font-weight: 600; font-size: .88rem;
           box-shadow: 0 6px 18px -10px rgba(0,0,0,.6); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.kc .cap {{ font-size: .76rem; color: {SUAVE}; margin: .55rem 0 .05rem; }}
.kc .vl {{ font-size: 1.85rem; font-weight: 700; line-height: 1.15; font-variant-numeric: tabular-nums; }}
.kc .vl small {{ font-size: .9rem; color: {SUAVE}; font-weight: 500; margin-left: 3px; }}
.kc .nt {{ font-size: .74rem; margin-top: .15rem; }}
.nt.bad {{ color: {CORAL}; }} .nt.ok {{ color: {VERDE}; }} .nt.neu {{ color: {SUAVE}; }}
hr.sep {{ border: none; border-top: 1px solid {BORDA}; margin: .9rem 0 1.1rem; }}

/* blocos de gráfico */
[class*="st-key-card"] {{ background: {PAINEL}; border: 1px solid {BORDA} !important; border-radius: 10px; padding: .9rem 1rem 1rem; height: auto !important; }}
.gt {{ font-weight: 700; font-size: .95rem; margin-bottom: .1rem; }}
.gd {{ font-size: .78rem; color: {SUAVE}; margin-bottom: .3rem; line-height: 1.4; }}
.say {{ background: {PAINEL}; border: 1px solid {BORDA}; border-left: 4px solid {CIANO}; border-radius: 8px; padding: .8rem 1rem; font-size: .92rem; line-height: 1.55; margin-bottom: .4rem; }}
.say b {{ color: {CIANO}; }}

/* plano */
.steps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; }}
.step {{ background: {PAINEL}; border: 1px solid {BORDA}; border-top: 3px solid {AZUL}; border-radius: 8px; padding: 1rem; }}
.step .n {{ font-size: .72rem; color: {CIANO}; font-weight: 700; letter-spacing: .08em; }}
.step .t {{ font-weight: 700; margin: .25rem 0 .35rem; }}
.step .x {{ font-size: .84rem; color: {SUAVE}; line-height: 1.5; }}
.rec {{ font-size: .86rem; line-height: 1.55; color: {TEXTO}; padding-bottom: .4rem; }}
.rec .tag {{ display: inline-block; background: rgba(60,203,143,.14); color: {VERDE}; font-weight: 600; font-size: .74rem; border-radius: 999px; padding: 3px 10px; margin-bottom: .5rem; }}
.light {{ display: flex; gap: 10px; align-items: flex-start; font-size: .86rem; margin-bottom: 8px; }}
.light i {{ width: 12px; height: 12px; border-radius: 50%; margin-top: 4px; flex: none; background: var(--c); box-shadow: 0 0 10px var(--c); }}
.foot {{ color: {SUAVE}; font-size: .76rem; margin-top: 1.5rem; padding-top: .9rem; border-top: 1px solid {BORDA}; }}
[data-testid="stDataFrame"] {{ border: 1px solid {BORDA}; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ dados
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
CORFAM = dict(zip(FAMILIAS, SERIES))
CORCAN = dict(zip(CANAIS, [AZUL, CORAL, CIANO, AMBAR]))


def br(v, casas=0):
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def rs_mil(v):
    return "R$ " + br(v / 1000, 1) + " mil"


def html(s):
    st.markdown(s, unsafe_allow_html=True)


def cab(titulo, desc=""):
    html(f'<div class="gt">{titulo}</div>' + (f'<div class="gd">{desc}</div>' if desc else ""))


def grafico(fig, h=330, legenda=True):
    fig.update_layout(height=h, margin=dict(l=4, r=8, t=10, b=4), showlegend=legenda,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text="") if legenda else None)
    st.plotly_chart(fig, use_container_width=True, theme=None, config={"displaylogo": False})


def kpi(icone, rotulo, legenda, valor, unidade="", nota="", estado="neu"):
    return (f'<div class="kc"><div class="hd">{icone} {rotulo}</div><div class="cap">{legenda}</div>'
            f'<div class="vl">{valor}<small>{unidade}</small></div><div class="nt {estado}">{nota}</div></div>')


def kgrid(*cards):
    html('<div class="kgrid">' + "".join(cards) + "</div>")


def tabela(nome, df):
    with st.expander(f"Tabela · {nome}"):
        st.dataframe(df, hide_index=True, use_container_width=True)


LOGO = f"""
<div class="logo">
<svg width="92" height="92" viewBox="0 0 100 100" role="img" aria-label="Logo Vila Aurora">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{AZUL}"/><stop offset="1" stop-color="{ROXO}"/></linearGradient></defs>
  <polygon points="50,4 90,27 90,73 50,96 10,73 10,27" fill="none" stroke="url(#g)" stroke-width="7" stroke-linejoin="round"/>
  <polygon points="50,20 76,35 76,65 50,80 24,65 24,35" fill="url(#g)" opacity=".18"/>
  <path d="M30 62 A20 20 0 0 1 70 62" fill="none" stroke="{AMBAR}" stroke-width="5" stroke-linecap="round"/>
  <line x1="26" y1="68" x2="74" y2="68" stroke="url(#g)" stroke-width="5" stroke-linecap="round"/>
  <line x1="50" y1="30" x2="50" y2="38" stroke="{AMBAR}" stroke-width="4" stroke-linecap="round"/>
  <line x1="33" y1="38" x2="37" y2="43" stroke="{AMBAR}" stroke-width="4" stroke-linecap="round"/>
  <line x1="67" y1="38" x2="63" y2="43" stroke="{AMBAR}" stroke-width="4" stroke-linecap="round"/>
</svg>
<div class="nm">VILA AURORA</div><div class="sb">Analytics do projeto · Grupo 1</div>
</div>"""

PAGINAS = ["Visão geral", "Previsão", "Estoques", "Plano de ação"]
ICONES = ["house", "graph-up", "box-seam", "compass"]

# ------------------------------------------------------------------ barra lateral
with st.sidebar:
    html(LOGO)
    html('<div class="filtro">Filtre os dados</div>')
    fam_sel = st.multiselect("Selecione a família", FAMILIAS, default=FAMILIAS)
    can_sel = st.multiselect("Selecione o canal", CANAIS, default=CANAIS)
    st.write("")
    if option_menu:
        pagina = option_menu("Menu principal", PAGINAS, icons=ICONES, menu_icon="list", default_index=0,
                             styles={"container": {"padding": "6px", "background-color": PAINEL, "border": f"1px solid {BORDA}", "border-radius": "10px"},
                                     "menu-title": {"font-size": "1.15rem", "font-weight": "700", "color": TEXTO},
                                     "menu-icon": {"color": TEXTO},
                                     "icon": {"color": CIANO, "font-size": "15px"},
                                     "nav-link": {"font-size": "14px", "color": TEXTO, "margin": "2px 0", "--hover-color": CABEC, "border-radius": "6px"},
                                     "nav-link-selected": {"background-color": AZUL, "color": "white", "font-weight": "600"}})
    else:
        pagina = st.radio("Menu principal", PAGINAS)
    st.write("")
    html('<div class="side-box"><b>Cenário do Grupo 1</b><br>Promoção de +60% em F3 na semana 25 · teto ESG de 18 viagens/mês · '
         'mix loja 70%, e-commerce 15%, marketplace 10%, retira 5%.</div>')

if not fam_sel or not can_sel:
    st.warning("Selecione ao menos uma família e um canal na barra lateral.")
    st.stop()

html('<div class="titulo">🌅 Vila Aurora · Analytics do Projeto</div>'
     '<div class="sub">ENG4550 · Projeto Integrado em Sistemas Produtivos · 22 lojas · cerca de 4.200 SKUs · 104 semanas de histórico</div>')
html(f'<div class="pagina">Página: <span>{pagina}</span></div>')

km = D["kpi_mensal"]
kf = D["kpi_familia_canal"].query("familia in @fam_sel and canal in @can_sel")
dm = D["demanda_semanal"].query("familia in @fam_sel and canal in @can_sel")

# ================================================================== VISÃO GERAL
if pagina == "Visão geral":
    tabela("KPIs mensais", km)
    fill, viag = km.fill_rate_pct.mean(), km.viagens_extras.mean()
    co2, canc = km.co2_urgencias_kg.mean(), km.cancelamento_ecommerce_pct.mean()
    acima = int((km.viagens_extras > km.teto_esg_viagens).sum())
    kgrid(kpi("📌", "Fill rate", "média mensal", br(fill, 1), "%", f"{br(META['Fill rate'] - fill, 1)} p.p. abaixo da meta de 97%", "bad"),
          kpi("📌", "Viagens extras", "média por mês", br(viag, 1), "", f"meta ≤ {br(META['Viagens emergenciais'])}", "bad"),
          kpi("📌", "CO₂e urgências", "média por mês", br(co2), "kg", f"meta ≤ {br(META['CO2e de urgências'])} kg", "bad"),
          kpi("📌", "Cancelamento online", "média do e-commerce", br(canc, 1), "%", f"meta ≤ {br(META['Cancelamento e-commerce'])}%", "bad"),
          kpi("📌", "Meses acima do teto", "viagens > 18", str(acima), "de 24", "teto ESG do cenário", "bad"))
    html('<hr class="sep">')

    g1, g2 = st.columns(2, gap="medium")
    with g1, st.container(key="card_fill"):
        cab("Fill rate mensal", "Nenhum mês chegou à meta de 97%.")
        fig = go.Figure(go.Scatter(x=km.mes, y=km.fill_rate_pct, mode="lines+markers", line=dict(color=AZUL, width=2.5),
                                   marker=dict(size=6, color=CIANO), fill="tozeroy", fillcolor="rgba(46,134,222,.12)",
                                   hovertemplate="%{x|%b/%Y}<br><b>%{y:.1f}%</b><extra></extra>"))
        fig.add_hline(y=97, line_dash="dash", line_color=VERDE, annotation_text="meta 97%", annotation_font_color=VERDE)
        fig.update_yaxes(range=[85, 99], dtick=2, ticksuffix="%")
        grafico(fig, legenda=False)
    with g2, st.container(key="card_viag"):
        cab("Viagens emergenciais por mês", "Vermelho: acima do teto ESG de 18. Cada viagem custa R$ 1.250 e emite 42 kg de CO₂e.")
        cores = [CORAL if v > t else AZUL for v, t in zip(km.viagens_extras, km.teto_esg_viagens)]
        fig = go.Figure(go.Bar(x=km.mes, y=km.viagens_extras, marker=dict(color=cores, cornerradius=3),
                               customdata=km.co2_urgencias_kg, hovertemplate="%{x|%b/%Y}<br><b>%{y} viagens</b><br>%{customdata} kg CO₂e<extra></extra>"))
        fig.add_hline(y=18, line_dash="dash", line_color=CORAL, annotation_text="teto 18", annotation_font_color=CORAL)
        fig.add_hline(y=12, line_dash="dot", line_color=VERDE, annotation_text="meta 12", annotation_font_color=VERDE)
        grafico(fig, legenda=False)

    g3, g4 = st.columns(2, gap="medium")
    with g3, st.container(key="card_matriz"):
        cab("Matriz impacto × evidência", "Cinco problemas priorizados, escala de 1 a 10.")
        pb = D["problemas"].copy()
        pb["grupo"] = pb.prioridade.le(2).map({True: "Prioridade 1–2", False: "Prioridade 3–5"})
        fig = px.scatter(pb, x="evidencia", y="impacto", size="tamanho", text="id", hover_name="problema", color="grupo",
                         hover_data={"detalhe": True, "tamanho": False, "id": False, "grupo": False},
                         color_discrete_map={"Prioridade 1–2": CORAL, "Prioridade 3–5": AZUL}, size_max=44,
                         labels={"evidencia": "Evidência", "impacto": "Impacto"})
        fig.update_traces(textposition="middle center", textfont=dict(color="white", size=12), marker=dict(opacity=.92, line=dict(width=0)))
        fig.update_xaxes(range=[5.5, 10.8]); fig.update_yaxes(range=[5.5, 10.8])
        grafico(fig)
    with g4, st.container(key="card_canal"):
        cab("Fill rate por família e canal", "O e-commerce tem mais ruptura em todas as famílias.")
        piv = kf.groupby(["familia", "canal"], as_index=False).fill_rate_pct.mean()
        fig = px.bar(piv, x="fill_rate_pct", y="familia", color="canal", barmode="group", orientation="h", color_discrete_map=CORCAN,
                     labels={"fill_rate_pct": "Fill rate médio (%)", "familia": ""}, category_orders={"canal": CANAIS, "familia": FAMILIAS[::-1]})
        fig.update_traces(marker_cornerradius=2, hovertemplate="%{y}<br>%{x:.1f}%<extra></extra>")
        fig.add_vline(x=97, line_dash="dash", line_color=VERDE)
        fig.update_xaxes(range=[84, 98.5], ticksuffix="%")
        grafico(fig)

# ================================================================== PREVISÃO
elif pagina == "Previsão":
    fam = D["familias"].set_index("familia")
    tabela("Perfil e modelo por família", D["familias"])
    total = dm.demanda_un.sum()
    pico = dm.groupby(["semana", "familia"]).demanda_un.sum().max()
    f3 = fam.loc["F3 · Mercearia"]
    kgrid(kpi("📌", "Demanda total", "soma das 104 semanas (filtro)", br(total / 1e6, 2), "mi un"),
          kpi("📌", "Média semanal", "por família selecionada", br(total / 104 / len(fam_sel)), "un"),
          kpi("📌", "Maior semana", "pico de uma família", br(pico), "un", "Promoção F3 na semana 25", "neu"),
          kpi("📌", "Melhor WAPE", "F3 · ARIMA(1,0,1)", br(f3.wape_pct, 1), "%", "erro de previsão no teste", "ok"),
          kpi("📌", "Pior WAPE", "F2 · SES", br(fam.wape_pct.max(), 1), "%", "absorvido pelo estoque de segurança", "bad"))
    html('<hr class="sep">')

    with st.container(key="card_demanda"):
        cab("Demanda semanal por família", "Pontos âmbar: semanas com evento do calendário. Faixa clara: período de teste dos modelos (79–104).")
        serie = dm.groupby(["semana", "data", "familia"], as_index=False).agg(demanda_un=("demanda_un", "sum"), evento=("evento", "first"))
        fig = go.Figure()
        fig.add_vrect(x0=78.5, x1=104.5, fillcolor=CIANO, opacity=0.06, line_width=0)
        for f in [x for x in FAMILIAS if x in fam_sel]:
            s = serie[serie.familia == f]
            fig.add_trace(go.Scatter(x=s.semana, y=s.demanda_un, name=f, mode="lines", line=dict(color=CORFAM[f], width=2),
                                     customdata=s[["data", "evento"]], hovertemplate=f"<b>{f}</b><br>Semana %{{x}} · %{{customdata[0]|%d/%m/%Y}}<br>%{{y:,.0f}} un<br>%{{customdata[1]}}<extra></extra>"))
        ev = serie[serie.evento != ""]
        fig.add_trace(go.Scatter(x=ev.semana, y=ev.demanda_un, mode="markers", name="evento", marker=dict(color=AMBAR, size=7), hoverinfo="skip"))
        fig.update_xaxes(title="Semana"); fig.update_yaxes(title="Demanda (un)")
        grafico(fig, 380)

    g1, g2 = st.columns([3, 2], gap="medium")
    with g1, st.container(key="card_wape"):
        cab("WAPE por modelo e família (%)", "Mais escuro: menor erro dentro da família. Vazio: modelo não testado.")
        w = D["wape_modelos"].pivot(index="modelo", columns="familia", values="wape_pct")
        rank = w.rank(axis=0, pct=True)
        fig = go.Figure(go.Heatmap(z=rank.values, x=[c.split(" · ")[1] for c in w.columns], y=w.index,
                                   text=w.map(lambda v: "" if pd.isna(v) else br(v, 1)).values, texttemplate="%{text}",
                                   colorscale=[[0, AZUL], [0.5, "#1D4E80"], [1, "#16304D"]], showscale=False, xgap=2, ygap=2,
                                   customdata=w.values, hovertemplate="%{y} · %{x}<br>WAPE <b>%{customdata:.2f}%</b><extra></extra>"))
        fig.update_yaxes(autorange="reversed", showgrid=False); fig.update_xaxes(showgrid=False, side="top")
        grafico(fig, 480, legenda=False)
    with g2:
        with st.container(key="card_bench"):
            cab("AutoETS × Naive (Q4)", "Redução do erro no holdout de 20 semanas.")
            b = D["benchmark_q4"]
            fig = px.bar(b, x="metrica", y="reducao_pct", color="sku", barmode="group", text=b.reducao_pct.map(lambda v: f"−{br(v)}%"),
                         color_discrete_sequence=[AZUL, CIANO], labels={"metrica": "", "reducao_pct": "Redução (%)"})
            fig.update_traces(marker_cornerradius=3, textposition="outside", cliponaxis=False)
            fig.update_yaxes(range=[0, 58])
            grafico(fig, 270)
        with st.container(key="card_ranking"):
            cab("WAPE do modelo recomendado por família", "Azul: famílias estáveis; coral: erro alto, tratado com estoque de segurança.")
            r = D["familias"].sort_values("wape_pct")
            fig = go.Figure(go.Bar(x=r.wape_pct, y=r.familia, orientation="h", marker=dict(color=[AZUL if v < 15 else CORAL for v in r.wape_pct], cornerradius=3),
                                   text=r.wape_pct.map(lambda v: f"{br(v, 1)}%"), textposition="outside", cliponaxis=False,
                                   customdata=r.modelo, hovertemplate="%{y}<br>%{customdata}<br>WAPE %{x:.1f}%<extra></extra>"))
            fig.update_xaxes(range=[0, 42], ticksuffix="%")
            grafico(fig, 200, legenda=False)

# ================================================================== ESTOQUES
elif pagina == "Estoques":
    pol = D["politicas_q11"]; ex = D["experimentos_q12"]
    tabela("Simulação das políticas (Q11)", pol.drop(columns=["cenario_id"]))
    f1 = pol[pol.cenario_id == "F1 (R,S) · previsão · promoção"].iloc[0]
    f1q = pol[pol.cenario_id == "F1 (Q,r) · previsão · promoção"].iloc[0]
    f3 = pol[pol.cenario_id == "F3 (Q,r) · previsão · promoção"].iloc[0]
    ref = ex[ex.alternativa == "Reforço de 40% por 3 semanas"].iloc[0]
    perm = ex[ex.alternativa.str.startswith("Proteção permanente")].iloc[0]
    kgrid(kpi("📌", "F1 · (R,S) semanal", "custo anual simulado", rs_mil(f1.custo_medio_rs), "", f"descarte {br(f1.descarte_pct, 2)}% · recomendada", "ok"),
          kpi("📌", "F1 · (Q,r) lote EOQ", "custo anual simulado", rs_mil(f1q.custo_medio_rs), "", f"descarte {br(f1q.descarte_pct, 2)}% · reprova", "bad"),
          kpi("📌", "F3 · (Q,r) promoção", "custo anual simulado", rs_mil(f3.custo_medio_rs), "", f"fill {br(f3.fill_pct, 1)}% · recomendada", "ok"),
          kpi("📌", "F3 · reforço pontual", "40% por 3 semanas", rs_mil(ref.custo_rs), "", f"{rs_mil(perm.custo_rs - ref.custo_rs)} mais barato", "ok"),
          kpi("📌", "Fill rate simulado", "melhor política de F1", br(f1.fill_pct, 0), "%", "p05 de 100%", "ok"))
    html('<hr class="sep">')

    with st.container(key="card_pol"):
        cab("Custo anual por política (Q11)", "364 dias, 20 replicações, z = 1,65. Barras de erro: desvio-padrão. Cinza: reprovada nos critérios Q10.")
        p2 = pol.sort_values("custo_medio_rs")
        fig = go.Figure(go.Bar(x=p2.custo_medio_rs, y=p2.cenario_id, orientation="h",
                               marker=dict(color=[AZUL if a == "Sim" else "#3A4E6B" for a in p2.aprovada], cornerradius=3),
                               error_x=dict(type="data", array=p2.custo_dp_rs, color=SUAVE, thickness=1.2, width=4),
                               text=p2.custo_medio_rs.map(rs_mil), textposition="inside", insidetextanchor="start", textfont=dict(color="white"),
                               customdata=p2[["fill_pct", "descarte_pct", "motivo"]],
                               hovertemplate="<b>%{y}</b><br>Custo R$ %{x:,.0f}<br>Fill %{customdata[0]}% · descarte %{customdata[1]}%<br>%{customdata[2]}<extra></extra>"))
        fig.update_xaxes(tickprefix="R$ ")
        grafico(fig, 360, legenda=False)

    g1, g2 = st.columns(2, gap="medium")
    with g1, st.container(key="card_q12"):
        cab("Experimentos de ponto de virada (Q12)")
        e = st.segmented_control("Experimento", ["Lote × validade", "Reforço pontual", "Lead time"], default="Lote × validade", label_visibility="collapsed")
        sub = ex[ex.exp == (e or "Lote × validade")]
        cores = [CORAL if i == sub.custo_rs.values.argmax() else AZUL for i in range(len(sub))]
        fig = go.Figure(go.Bar(x=sub.custo_rs, y=sub.alternativa, orientation="h", marker=dict(color=cores, cornerradius=3),
                               text=sub.custo_rs.map(rs_mil), textposition="outside", cliponaxis=False, hovertemplate="%{y}<br>R$ %{x:,.0f}<extra></extra>"))
        fig.update_xaxes(range=[0, sub.custo_rs.max() * 1.45], tickprefix="R$ ")
        grafico(fig, 250, legenda=False)
        for _, r in sub.iterrows():
            html(f'<div class="gd"><b style="color:{TEXTO}">{r.alternativa}:</b> {r.leitura}</div>')
    with g2, st.container(key="card_sslt"):
        cab("Estoque de segurança de F3 × lead time", "σ residual = 463 un. Dobrar o lead time de 7 para 14 dias eleva o SS em cerca de 22%.")
        sl = D["ss_lead_time_f3"]
        fig = px.line(sl, x="lead_time_dias", y="estoque_seguranca_un", color="nivel_servico", markers=True,
                      color_discrete_sequence=[CIANO, AZUL, AMBAR], labels={"lead_time_dias": "Lead time (dias)", "estoque_seguranca_un": "SS (un)", "nivel_servico": ""})
        fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
        grafico(fig, 320)

    cs = D["cenarios_semana25"]
    vals = [f"{br(cs.valor[0])}%", f"{br(cs.valor[1])} un", f"semana {br(cs.valor[2])}"]
    html('<div class="gt" style="margin-top:1rem">Semana 25 em F3: um pico de 5,8 desvios que já está no histórico</div>')
    kgrid(*[kpi("📌", r.cenario, r.indicador, v, "", r.leitura, "bad" if i == 0 else "ok") for i, (v, (_, r)) in enumerate(zip(vals, cs.iterrows()))])

# ================================================================== PLANO
else:
    tabela("KPIs, baseline e metas", D["metas_kpi"])
    html('<div class="say">O ganho estatístico só vira resultado operacional se a <b>sequência for respeitada</b>: dados confiáveis primeiro, '
         'depois previsão por família, estoques segmentados e uma rotina semanal de S&amp;OE.</div>')
    etapas = [("Sanear dados e WMS", "Higienização cadastral e baixa automática no CD: fim dos 8% de falha e das 120 h semanais de contagem."),
              ("Previsão por família", "ARIMA em F1 e F3, SES em F2, regressão com tendência e eventos em F4, Random Forest em F5."),
              ("Estoques segmentados", "Fim da regra de 2 semanas: (R,S) semanal em F1; (Q,r) em F3 com reforço antes da semana 25."),
              ("S&amp;OE com gatilhos", "Reunião semanal com Operações, CD, Comercial e ESG; semáforos ligados aos KPIs.")]
    html('<div class="steps">' + "".join(f'<div class="step"><div class="n">ETAPA {i}</div><div class="t">{t}</div><div class="x">{x}</div></div>'
                                         for i, (t, x) in enumerate(etapas, 1)) + "</div>")
    st.write("")
    g1, g2, g3 = st.columns(3, gap="medium")
    with g1, st.container(key="card_rf1"):
        cab("F1 · Perecíveis")
        html('<div class="rec"><span class="tag">(R,S) semanal pela previsão</span><br>Reposição semanal de lote pequeno. Com lote limitado à validade '
             '(2.948 un em vez de 4.975), a (Q,r) cai de R$ 100,8 mil para R$ 14,6 mil por ano. FEFO obrigatório.</div>')
    with g2, st.container(key="card_rf3"):
        cab("F3 · Mercearia")
        html('<div class="rec"><span class="tag">(Q,r) com reforço pontual</span><br>z = 1,65 na rotina e reforço de 40% nas três semanas antes da promoção. '
             'Dobrar o lead time leva o custo de R$ 32 mil para R$ 66 mil por ano.</div>')
    with g3, st.container(key="card_sem"):
        cab("Semáforo de S&amp;OE")
        html(f'<div class="light"><i style="--c:{VERDE}"></i><span><b>Verde:</b> metas atendidas.</span></div>'
             f'<div class="light"><i style="--c:{AMBAR}"></i><span><b>Amarelo:</b> projeção ≥ 10 viagens ou fill rate &lt; 97,5%.</span></div>'
             f'<div class="light"><i style="--c:{CORAL}"></i><span><b>Vermelho:</b> ≥ 12 viagens ou fill rate &lt; 96%.</span></div>'
             f'<div class="gd" style="padding-bottom:.3rem">Gatilho: promoção comunicada com duas semanas de antecedência.</div>')
    st.info("Limites da simulação: demanda uniforme nos dias da semana, pool único por família, ruptura como venda perdida e só duas temporadas no histórico.", icon="ℹ️")

html('<div class="foot">Fontes: bases do caso Vila Aurora (Blocos 1 e 2) e resultados do Grupo 1 (Brief Executivo, Relatório Parcial, Relatório do Bloco 3, '
     'Políticas de Estoque Q10–Q12, notebook Q4). Davi Aguiar · Isabella Alvine · Júlia Lobianco · Lucas Cuan · Prof. Rodrigo Caiado · PUC-Rio 2026.2</div>')
