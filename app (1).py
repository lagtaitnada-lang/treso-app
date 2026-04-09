import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="TrésoBoard — PME Maroc Services",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }

    .app-header { border-bottom: 1px solid #E5E7EB; padding-bottom: 1.25rem; margin-bottom: 2rem; }
    .app-title { font-size: 1.5rem; font-weight: 600; color: #0F172A; letter-spacing: -0.02em; margin: 0; }
    .app-subtitle { font-size: 0.75rem; color: #6B7280; margin-top: 4px; font-weight: 400; text-transform: uppercase; letter-spacing: 0.08em; }

    .kpi-card { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 1.25rem 1.5rem; }
    .kpi-label { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #6B7280; margin-bottom: 0.5rem; }
    .kpi-value { font-size: 1.6rem; font-weight: 600; color: #0F172A; letter-spacing: -0.02em; line-height: 1.1; }
    .kpi-value.positive { color: #059669; }
    .kpi-value.negative { color: #DC2626; }
    .kpi-value.warning  { color: #D97706; }
    .kpi-sub { font-size: 0.72rem; color: #9CA3AF; margin-top: 4px; }

    .alert { padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.82rem; margin-bottom: 8px; font-weight: 400; line-height: 1.5; }
    .alert-danger  { background:#FEF2F2; border-left:3px solid #DC2626; color:#7F1D1D; }
    .alert-warning { background:#FFFBEB; border-left:3px solid #D97706; color:#78350F; }
    .alert-info    { background:#EFF6FF; border-left:3px solid #3B82F6; color:#1E3A5F; }
    .alert-success { background:#F0FDF4; border-left:3px solid #059669; color:#14532D; }

    .section-label { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #6B7280; margin-bottom: 0.75rem; margin-top: 0.25rem; }

    .stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid #E5E7EB; background: transparent; }
    .stTabs [data-baseweb="tab"] { border-radius: 0; padding: 0.6rem 1.25rem; font-size: 0.82rem; font-weight: 500; color: #6B7280; border-bottom: 2px solid transparent; margin-bottom: -1px; }
    .stTabs [aria-selected="true"] { color: #0F172A !important; border-bottom: 2px solid #0F172A !important; background: transparent !important; }

    .stFormSubmitButton button { background: #0F172A !important; color: #FFFFFF !important; border-radius: 6px !important; font-size: 0.82rem !important; font-weight: 500 !important; border: none !important; padding: 0.5rem 1.5rem !important; }
    .stDownloadButton button { background: transparent !important; border: 1px solid #D1D5DB !important; border-radius: 6px !important; color: #374151 !important; font-size: 0.78rem !important; font-weight: 500 !important; }

    hr { border-color: #F3F4F6; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
SEUIL_ALERTE  = 15000
SOLDE_INITIAL = 50000
COLOR_POS     = "#059669"
COLOR_NEG     = "#DC2626"
COLOR_WARN    = "#D97706"
COLOR_BLUE    = "#3B82F6"

CHART_LAYOUT = dict(
    font_family="Inter",
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=20, b=20, l=0, r=0),
    xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#6B7280")),
    yaxis=dict(gridcolor="#F3F4F6", tickfont=dict(size=11, color="#6B7280"), tickformat=",.0f"),
    height=300,
)

# ── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_transactions():
    rows = [
        ("2025-01-05","Vente Maroc Tech SARL","Ventes","encaissement",42000),
        ("2025-01-10","Salaires janvier","Salaires","paiement",28000),
        ("2025-01-15","Loyer bureaux","Loyer","paiement",8500),
        ("2025-01-20","Vente Atlas Consulting","Ventes","encaissement",18500),
        ("2025-01-28","Fournisseur IT Supplies","Fournisseurs","paiement",6200),
        ("2025-01-31","TVA janvier","TVA","paiement",5800),
        ("2025-02-05","Vente Casatec","Ventes","encaissement",35000),
        ("2025-02-10","Salaires février","Salaires","paiement",28000),
        ("2025-02-15","Loyer bureaux","Loyer","paiement",8500),
        ("2025-02-18","Vente Souss Digital","Ventes","encaissement",22000),
        ("2025-02-25","CNSS février","CNSS","paiement",4200),
        ("2025-02-28","TVA février","TVA","paiement",5100),
        ("2025-03-03","Vente RabatPro","Ventes","encaissement",31000),
        ("2025-03-05","Fournisseur Fournitures","Fournisseurs","paiement",3800),
        ("2025-03-10","Salaires mars","Salaires","paiement",28000),
        ("2025-03-15","Loyer bureaux","Loyer","paiement",8500),
        ("2025-03-20","Vente Fès Solutions","Ventes","encaissement",14500),
        ("2025-03-28","CNSS mars","CNSS","paiement",4200),
        ("2025-03-31","TVA mars","TVA","paiement",4600),
    ]
    df = pd.DataFrame(rows, columns=["date","description","categorie","type","montant"])
    df["date"] = pd.to_datetime(df["date"])
    return df

@st.cache_data
def load_echeances():
    rows = [
        ("2025-04-07","Facture Maroc Tech SARL","encaiss","En attente",38000),
        ("2025-04-10","Salaires avril","paiement","En attente",28000),
        ("2025-04-12","Loyer avril","paiement","En attente",8500),
        ("2025-04-15","Facture Atlas Consulting","encaiss","Retard",22000),
        ("2025-04-18","Fournisseur IT","paiement","En attente",5500),
        ("2025-04-20","TVA avril","paiement","En attente",5200),
        ("2025-04-25","Vente Casatec (prévu)","encaiss","En attente",30000),
        ("2025-04-30","CNSS avril","paiement","En attente",4200),
        ("2025-05-05","Facture RabatPro","encaiss","En attente",25000),
        ("2025-05-10","Salaires mai","paiement","En attente",28000),
        ("2025-05-12","Loyer mai","paiement","En attente",8500),
        ("2025-05-20","Facture Fès Solutions","encaiss","En attente",18000),
        ("2025-05-25","TVA mai","paiement","En attente",4800),
        ("2025-05-31","CNSS mai","paiement","En attente",4200),
        ("2025-06-05","Facture Souss Digital","encaiss","En attente",20000),
        ("2025-06-10","Salaires juin","paiement","En attente",28000),
    ]
    df = pd.DataFrame(rows, columns=["date","description","type","statut","montant"])
    df["date"] = pd.to_datetime(df["date"])
    return df

if "transactions" not in st.session_state:
    st.session_state.transactions = load_transactions()
if "echeances" not in st.session_state:
    st.session_state.echeances = load_echeances()

tx  = st.session_state.transactions
ech = st.session_state.echeances

entrees_total = tx[tx["type"]=="encaissement"]["montant"].sum()
sorties_total = tx[tx["type"]=="paiement"]["montant"].sum()
solde_actuel  = SOLDE_INITIAL + entrees_total - sorties_total
retards       = ech[ech["statut"]=="Retard"]
grosses       = ech[(ech["montant"]>=25000)&(ech["statut"]=="En attente")]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <p class="app-title">TrésoBoard</p>
  <p class="app-subtitle">PME Maroc Services &nbsp;·&nbsp; Gestion de trésorerie &nbsp;·&nbsp; Casablanca</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Vue d'ensemble", "Flux de trésorerie", "Échéancier", "Prévision 8 semaines"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    net = entrees_total - sorties_total
    solde_class = "negative" if solde_actuel<SEUIL_ALERTE else "warning" if solde_actuel<30000 else "positive"
    net_class   = "positive" if net >= 0 else "negative"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Solde actuel</div><div class="kpi-value {solde_class}">{solde_actuel:,.0f} <span style="font-size:.9rem;font-weight:400">MAD</span></div><div class="kpi-sub">Seuil d\'alerte : {SEUIL_ALERTE:,} MAD</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Entrées — 3 mois</div><div class="kpi-value positive">+{entrees_total:,.0f} <span style="font-size:.9rem;font-weight:400">MAD</span></div><div class="kpi-sub">Janvier · Février · Mars 2025</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Sorties — 3 mois</div><div class="kpi-value negative">-{sorties_total:,.0f} <span style="font-size:.9rem;font-weight:400">MAD</span></div><div class="kpi-sub">Charges, salaires, taxes</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Résultat net</div><div class="kpi-value {net_class}">{net:+,.0f} <span style="font-size:.9rem;font-weight:400">MAD</span></div><div class="kpi-sub">Entrées moins sorties</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Alertes actives</div>', unsafe_allow_html=True)

    has_alert = False
    if solde_actuel < SEUIL_ALERTE:
        st.markdown(f'<div class="alert alert-danger">Solde actuel ({solde_actuel:,.0f} MAD) inférieur au seuil d\'alerte de {SEUIL_ALERTE:,} MAD — risque de rupture de trésorerie.</div>', unsafe_allow_html=True)
        has_alert = True
    if not retards.empty:
        st.markdown(f'<div class="alert alert-danger">{len(retards)} échéance(s) en retard de paiement — montant total : {retards["montant"].sum():,.0f} MAD.</div>', unsafe_allow_html=True)
        has_alert = True
    if not grosses.empty:
        st.markdown(f'<div class="alert alert-warning">{len(grosses)} échéance(s) supérieure(s) à 25 000 MAD à venir — vérifier la liquidité disponible.</div>', unsafe_allow_html=True)
        has_alert = True
    if not has_alert:
        st.markdown('<div class="alert alert-success">Aucune alerte critique. La trésorerie est dans les limites normales.</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert alert-info">Prévision sur 8 semaines disponible dans l\'onglet dédié.</div>', unsafe_allow_html=True)

    st.divider()

    months    = ["Janvier 2025","Février 2025","Mars 2025"]
    entrees_m = [60500, 57000, 45500]
    sorties_m = [48300, 45800, 49100]
    soldes_m  = [SOLDE_INITIAL + entrees_m[0] - sorties_m[0]]
    for i in range(1,3): soldes_m.append(soldes_m[-1]+entrees_m[i]-sorties_m[i])

    cl, cr = st.columns(2)
    with cl:
        st.markdown('<div class="section-label">Entrées vs Sorties</div>', unsafe_allow_html=True)
        df_bar = pd.DataFrame({"Mois":months*2,"Montant":entrees_m+sorties_m,
                               "Flux":["Encaissements"]*3+["Décaissements"]*3})
        fig = px.bar(df_bar, x="Mois", y="Montant", color="Flux", barmode="group",
                     color_discrete_map={"Encaissements":COLOR_POS,"Décaissements":COLOR_NEG})
        fig.update_layout(**CHART_LAYOUT, bargap=0.3, bargroupgap=0.08,
                          legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=11)))
        fig.update_yaxes(title="MAD", title_font=dict(size=11,color="#6B7280"))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with cr:
        st.markdown('<div class="section-label">Évolution du solde</div>', unsafe_allow_html=True)
        df_line = pd.DataFrame({"Mois":months,"Solde":soldes_m})
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_line["Mois"],y=df_line["Solde"],mode="lines+markers",
            line=dict(color=COLOR_BLUE,width=2),marker=dict(color=COLOR_BLUE,size=7),
            fill="tozeroy",fillcolor="rgba(59,130,246,0.06)"))
        fig2.add_hline(y=SEUIL_ALERTE,line_dash="dot",line_color=COLOR_NEG,line_width=1,
                       annotation_text="Seuil",annotation_font_size=10,annotation_font_color=COLOR_NEG)
        fig2.update_layout(**CHART_LAYOUT)
        fig2.update_yaxes(title="MAD",title_font=dict(size=11,color="#6B7280"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-label">Transactions récentes</div>', unsafe_allow_html=True)
    last5 = tx.sort_values("date",ascending=False).head(5).copy()
    last5["Montant (MAD)"] = last5.apply(lambda r:f"+{r['montant']:,.0f}" if r["type"]=="encaissement" else f"-{r['montant']:,.0f}",axis=1)
    last5["Date"] = last5["date"].dt.strftime("%d/%m/%Y")
    last5["Sens"] = last5["type"].map({"encaissement":"Encaissement","paiement":"Décaissement"})
    st.dataframe(last5[["Date","description","categorie","Sens","Montant (MAD)"]].rename(columns={"description":"Description","categorie":"Catégorie"}),hide_index=True,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FLUX
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">Enregistrer un nouveau flux</div>', unsafe_allow_html=True)
    with st.form("form_flux", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1: f_date    = st.date_input("Date", value=datetime.today())
        with c2: f_desc    = st.text_input("Description")
        with c3: f_type    = st.selectbox("Sens",["encaissement","paiement"],format_func=lambda x:"Encaissement" if x=="encaissement" else "Décaissement")
        c4,c5 = st.columns(2)
        with c4: f_montant = st.number_input("Montant (MAD)",min_value=0.0,step=100.0)
        with c5: f_cat     = st.selectbox("Catégorie",["Ventes","Salaires","Loyer","Fournisseurs","TVA","CNSS","Autre"])
        if st.form_submit_button("Enregistrer"):
            if f_desc and f_montant>0:
                new = pd.DataFrame([{"date":pd.Timestamp(f_date),"description":f_desc,"categorie":f_cat,"type":f_type,"montant":f_montant}])
                st.session_state.transactions = pd.concat([st.session_state.transactions,new],ignore_index=True)
                st.success(f"Flux enregistré — {f_desc} · {f_montant:,.0f} MAD")
                st.rerun()
            else: st.warning("Veuillez compléter tous les champs obligatoires.")

    st.divider()
    st.markdown('<div class="section-label">Historique complet</div>', unsafe_allow_html=True)
    df_tx = tx.sort_values("date",ascending=False).copy()
    df_tx["Montant (MAD)"] = df_tx.apply(lambda r:f"+{r['montant']:,.0f}" if r["type"]=="encaissement" else f"-{r['montant']:,.0f}",axis=1)
    df_tx["Date"] = df_tx["date"].dt.strftime("%d/%m/%Y")
    df_tx["Sens"] = df_tx["type"].map({"encaissement":"Encaissement","paiement":"Décaissement"})
    st.dataframe(df_tx[["Date","description","categorie","Sens","Montant (MAD)"]].rename(columns={"description":"Description","categorie":"Catégorie"}),hide_index=True,use_container_width=True)
    st.download_button("Exporter CSV",tx.to_csv(index=False).encode("utf-8"),"transactions.csv","text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ÉCHÉANCIER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-label">Ajouter une échéance</div>', unsafe_allow_html=True)
    with st.form("form_ech", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1: e_date    = st.date_input("Date d'échéance",value=datetime.today())
        with c2: e_desc    = st.text_input("Description")
        with c3: e_type    = st.selectbox("Type",["encaiss","paiement"],format_func=lambda x:"À encaisser" if x=="encaiss" else "À régler")
        c4,c5 = st.columns(2)
        with c4: e_montant = st.number_input("Montant (MAD)",min_value=0.0,step=100.0,key="em")
        with c5: e_statut  = st.selectbox("Statut",["En attente","Réglé","Retard"])
        if st.form_submit_button("Enregistrer"):
            if e_desc and e_montant>0:
                new = pd.DataFrame([{"date":pd.Timestamp(e_date),"description":e_desc,"type":e_type,"statut":e_statut,"montant":e_montant}])
                st.session_state.echeances = pd.concat([st.session_state.echeances,new],ignore_index=True)
                st.success(f"Échéance enregistrée — {e_desc} · {e_montant:,.0f} MAD")
                st.rerun()
            else: st.warning("Veuillez compléter tous les champs obligatoires.")

    st.divider()
    st.markdown('<div class="section-label">Échéances — 8 semaines</div>', unsafe_allow_html=True)
    cf1,cf2 = st.columns(2)
    with cf1: ft = st.selectbox("Filtrer par type",["Tous","encaiss","paiement"],format_func=lambda x:"Tous" if x=="Tous" else("À encaisser" if x=="encaiss" else "À régler"))
    with cf2: fs = st.selectbox("Filtrer par statut",["Tous","En attente","Réglé","Retard"])
    df_e = ech.copy()
    if ft!="Tous": df_e = df_e[df_e["type"]==ft]
    if fs!="Tous": df_e = df_e[df_e["statut"]==fs]
    df_e = df_e.sort_values("date").copy()
    df_e["Montant (MAD)"] = df_e.apply(lambda r:f"+{r['montant']:,.0f}" if r["type"]=="encaiss" else f"-{r['montant']:,.0f}",axis=1)
    df_e["Type"] = df_e["type"].map({"encaiss":"À encaisser","paiement":"À régler"})
    df_e["Date"] = df_e["date"].dt.strftime("%d/%m/%Y")
    st.dataframe(df_e[["Date","description","Type","statut","Montant (MAD)"]].rename(columns={"description":"Description","statut":"Statut"}),hide_index=True,use_container_width=True)
    st.download_button("Exporter CSV",ech.to_csv(index=False).encode("utf-8"),"echeances.csv","text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PRÉVISION
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    base_date = datetime(2025,4,7)
    rows_p, running = [], solde_actuel
    for i in range(8):
        start = base_date+timedelta(weeks=i); end = start+timedelta(days=6)
        wech  = ech[(ech["date"]>=pd.Timestamp(start))&(ech["date"]<=pd.Timestamp(end))]
        e_in  = wech[wech["type"]=="encaiss"]["montant"].sum()
        e_out = wech[wech["type"]=="paiement"]["montant"].sum()
        running += e_in-e_out
        rows_p.append({"Semaine":f"S{i+1}","Période":f"{start.strftime('%d/%m')}–{end.strftime('%d/%m')}",
                       "Entrées":e_in,"Sorties":e_out,"Solde prévu":running})

    df_prev   = pd.DataFrame(rows_p)
    solde_fin = df_prev["Solde prévu"].iloc[-1]
    min_solde = df_prev["Solde prévu"].min()
    tot_e     = df_prev["Entrées"].sum()
    tot_s     = df_prev["Sorties"].sum()
    fin_class = "negative" if solde_fin<SEUIL_ALERTE else "warning" if solde_fin<30000 else "positive"

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Solde de départ</div><div class="kpi-value">{solde_actuel:,.0f} <span style="font-size:.9rem;font-weight:400">MAD</span></div><div class="kpi-sub">Situation actuelle</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Entrées prévues</div><div class="kpi-value positive">+{tot_e:,.0f} <span style="font-size:.9rem;font-weight:400">MAD</span></div><div class="kpi-sub">8 prochaines semaines</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Sorties prévues</div><div class="kpi-value negative">-{tot_s:,.0f} <span style="font-size:.9rem;font-weight:400">MAD</span></div><div class="kpi-sub">8 prochaines semaines</div></div>',unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Solde fin S8</div><div class="kpi-value {fin_class}">{solde_fin:,.0f} <span style="font-size:.9rem;font-weight:400">MAD</span></div><div class="kpi-sub">Min. : {min_solde:,.0f} MAD</div></div>',unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Projection du solde</div>', unsafe_allow_html=True)

    pt_colors = [COLOR_NEG if s<SEUIL_ALERTE else COLOR_WARN if s<30000 else COLOR_POS for s in df_prev["Solde prévu"]]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_prev["Semaine"],y=df_prev["Solde prévu"],mode="lines+markers",
        line=dict(color=COLOR_BLUE,width=2),
        marker=dict(color=pt_colors,size=9,line=dict(width=2,color="white")),
        fill="tozeroy",fillcolor="rgba(59,130,246,0.05)"
    ))
    fig3.add_hline(y=SEUIL_ALERTE,line_dash="dot",line_color=COLOR_NEG,line_width=1,
                   annotation_text=f"Seuil d'alerte · {SEUIL_ALERTE:,} MAD",
                   annotation_font_size=10,annotation_font_color=COLOR_NEG,
                   annotation_position="bottom right")
    fig3.update_layout(**{**CHART_LAYOUT,"height":340})
    fig3.update_yaxes(title="MAD",title_font=dict(size=11,color="#6B7280"))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-label">Détail hebdomadaire</div>', unsafe_allow_html=True)
    df_show = df_prev.copy()
    df_show["Entrées"]     = df_show["Entrées"].apply(lambda x:f"+{x:,.0f} MAD")
    df_show["Sorties"]     = df_show["Sorties"].apply(lambda x:f"-{x:,.0f} MAD")
    df_show["Solde prévu"] = df_show["Solde prévu"].apply(lambda x:f"{x:,.0f} MAD")
    st.dataframe(df_show,hide_index=True,use_container_width=True)
