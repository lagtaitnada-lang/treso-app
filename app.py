import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="TrésoBoard — PME Maroc Services",
    layout="wide"
)

st.markdown("""
<style>
    .alert-danger  { background:#FEF2F2; border-left:4px solid #DC2626; padding:10px 14px; border-radius:6px; margin:6px 0; color:#7F1D1D; font-size:0.85rem; }
    .alert-warning { background:#FFFBEB; border-left:4px solid #D97706; padding:10px 14px; border-radius:6px; margin:6px 0; color:#78350F; font-size:0.85rem; }
    .alert-info    { background:#EFF6FF; border-left:4px solid #3B82F6; padding:10px 14px; border-radius:6px; margin:6px 0; color:#1E3A5F; font-size:0.85rem; }
    .alert-success { background:#F0FDF4; border-left:4px solid #059669; padding:10px 14px; border-radius:6px; margin:6px 0; color:#14532D; font-size:0.85rem; }
</style>
""", unsafe_allow_html=True)

SEUIL_ALERTE  = 15000
SOLDE_INITIAL = 50000

# Plotly shared theme
CHART_ARGS = dict(
    plot_bgcolor="#FAFAFA",
    paper_bgcolor="#FAFAFA",
    font_color="#374151",
    margin=dict(t=20, b=20, l=0, r=0),
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
st.title("TrésoBoard")
st.caption("PME Maroc Services  ·  Gestion de trésorerie  ·  Casablanca")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "Vue d'ensemble",
    "Flux de trésorerie",
    "Échéancier",
    "Prévision 8 semaines"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Solde actuel (MAD)",
                  f"{solde_actuel:,.0f}",
                  delta=f"Seuil : {SEUIL_ALERTE:,}",
                  delta_color="normal" if solde_actuel >= SEUIL_ALERTE else "inverse")
    with c2:
        st.metric("Entrées — 3 mois (MAD)", f"+{entrees_total:,.0f}")
    with c3:
        st.metric("Sorties — 3 mois (MAD)", f"-{sorties_total:,.0f}")
    with c4:
        net = entrees_total - sorties_total
        st.metric("Résultat net (MAD)", f"{net:+,.0f}")

    st.divider()

    # Alerts
    st.subheader("Alertes")
    has_alert = False
    if solde_actuel < SEUIL_ALERTE:
        st.markdown(f'<div class="alert-danger">Solde actuel ({solde_actuel:,.0f} MAD) inférieur au seuil d\'alerte de {SEUIL_ALERTE:,} MAD — risque de rupture de trésorerie.</div>', unsafe_allow_html=True)
        has_alert = True
    if not retards.empty:
        st.markdown(f'<div class="alert-danger">{len(retards)} échéance(s) en retard — montant total : {retards["montant"].sum():,.0f} MAD.</div>', unsafe_allow_html=True)
        has_alert = True
    if not grosses.empty:
        st.markdown(f'<div class="alert-warning">{len(grosses)} échéance(s) supérieure(s) à 25 000 MAD à venir — vérifier la liquidité disponible.</div>', unsafe_allow_html=True)
        has_alert = True
    if not has_alert:
        st.markdown('<div class="alert-success">Aucune alerte critique. La trésorerie est dans les limites normales.</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">Prévision sur 8 semaines disponible dans l\'onglet dédié.</div>', unsafe_allow_html=True)

    st.divider()

    # Charts
    months    = ["Janvier 2025", "Février 2025", "Mars 2025"]
    entrees_m = [60500, 57000, 45500]
    sorties_m = [48300, 45800, 49100]
    soldes_m  = [SOLDE_INITIAL + entrees_m[0] - sorties_m[0]]
    for i in range(1, 3):
        soldes_m.append(soldes_m[-1] + entrees_m[i] - sorties_m[i])

    cl, cr = st.columns(2)

    with cl:
        st.subheader("Encaissements vs Décaissements")
        df_bar = pd.DataFrame({
            "Mois": months * 2,
            "Montant": entrees_m + sorties_m,
            "Flux": ["Encaissements"] * 3 + ["Décaissements"] * 3
        })
        fig = px.bar(df_bar, x="Mois", y="Montant", color="Flux", barmode="group",
                     color_discrete_map={"Encaissements": "#059669", "Décaissements": "#DC2626"})
        fig.update_layout(**CHART_ARGS, bargap=0.3, bargroupgap=0.1,
                          legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                      xanchor="right", x=1))
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor="#E5E7EB", tickformat=",.0f", title="MAD")
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with cr:
        st.subheader("Évolution du solde")
        df_line = pd.DataFrame({"Mois": months, "Solde": soldes_m})
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_line["Mois"], y=df_line["Solde"],
            mode="lines+markers",
            line=dict(color="#2563EB", width=2.5),
            marker=dict(color="#2563EB", size=8),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.07)"
        ))
        fig2.add_hline(y=SEUIL_ALERTE, line_dash="dot", line_color="#DC2626",
                       line_width=1.5, annotation_text="Seuil d'alerte",
                       annotation_font_size=11, annotation_font_color="#DC2626")
        fig2.update_layout(**CHART_ARGS)
        fig2.update_xaxes(showgrid=False)
        fig2.update_yaxes(gridcolor="#E5E7EB", tickformat=",.0f", title="MAD")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Transactions récentes")
    last5 = tx.sort_values("date", ascending=False).head(5).copy()
    last5["Montant (MAD)"] = last5.apply(
        lambda r: f"+{r['montant']:,.0f}" if r["type"] == "encaissement" else f"-{r['montant']:,.0f}", axis=1)
    last5["Date"] = last5["date"].dt.strftime("%d/%m/%Y")
    last5["Sens"] = last5["type"].map({"encaissement": "Encaissement", "paiement": "Décaissement"})
    st.dataframe(
        last5[["Date","description","categorie","Sens","Montant (MAD)"]].rename(columns={
            "description": "Description", "categorie": "Catégorie"}),
        hide_index=True, use_container_width=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FLUX
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Enregistrer un nouveau flux")
    with st.form("form_flux", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1: f_date    = st.date_input("Date", value=datetime.today())
        with c2: f_desc    = st.text_input("Description")
        with c3: f_type    = st.selectbox("Sens", ["encaissement","paiement"],
                                           format_func=lambda x: "Encaissement" if x=="encaissement" else "Décaissement")
        c4, c5 = st.columns(2)
        with c4: f_montant = st.number_input("Montant (MAD)", min_value=0.0, step=100.0)
        with c5: f_cat     = st.selectbox("Catégorie", ["Ventes","Salaires","Loyer","Fournisseurs","TVA","CNSS","Autre"])
        if st.form_submit_button("Enregistrer le flux"):
            if f_desc and f_montant > 0:
                new = pd.DataFrame([{"date": pd.Timestamp(f_date), "description": f_desc,
                                     "categorie": f_cat, "type": f_type, "montant": f_montant}])
                st.session_state.transactions = pd.concat([st.session_state.transactions, new], ignore_index=True)
                st.success(f"Flux enregistré — {f_desc}  ·  {f_montant:,.0f} MAD")
                st.rerun()
            else:
                st.warning("Veuillez compléter tous les champs obligatoires.")

    st.divider()
    st.subheader("Historique complet")
    df_tx = tx.sort_values("date", ascending=False).copy()
    df_tx["Montant (MAD)"] = df_tx.apply(
        lambda r: f"+{r['montant']:,.0f}" if r["type"]=="encaissement" else f"-{r['montant']:,.0f}", axis=1)
    df_tx["Date"] = df_tx["date"].dt.strftime("%d/%m/%Y")
    df_tx["Sens"] = df_tx["type"].map({"encaissement": "Encaissement", "paiement": "Décaissement"})
    st.dataframe(
        df_tx[["Date","description","categorie","Sens","Montant (MAD)"]].rename(columns={
            "description": "Description", "categorie": "Catégorie"}),
        hide_index=True, use_container_width=True
    )
    st.download_button("Exporter transactions.csv",
                       tx.to_csv(index=False).encode("utf-8"), "transactions.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ÉCHÉANCIER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Ajouter une échéance")
    with st.form("form_ech", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1: e_date    = st.date_input("Date d'échéance", value=datetime.today())
        with c2: e_desc    = st.text_input("Description")
        with c3: e_type    = st.selectbox("Type", ["encaiss","paiement"],
                                           format_func=lambda x: "À encaisser" if x=="encaiss" else "À régler")
        c4, c5 = st.columns(2)
        with c4: e_montant = st.number_input("Montant (MAD)", min_value=0.0, step=100.0, key="em")
        with c5: e_statut  = st.selectbox("Statut", ["En attente","Réglé","Retard"])
        if st.form_submit_button("Enregistrer l'échéance"):
            if e_desc and e_montant > 0:
                new = pd.DataFrame([{"date": pd.Timestamp(e_date), "description": e_desc,
                                     "type": e_type, "statut": e_statut, "montant": e_montant}])
                st.session_state.echeances = pd.concat([st.session_state.echeances, new], ignore_index=True)
                st.success(f"Échéance enregistrée — {e_desc}  ·  {e_montant:,.0f} MAD")
                st.rerun()
            else:
                st.warning("Veuillez compléter tous les champs obligatoires.")

    st.divider()
    st.subheader("Échéances — 8 semaines à venir")
    cf1, cf2 = st.columns(2)
    with cf1: ft = st.selectbox("Filtrer par type", ["Tous","encaiss","paiement"],
                                 format_func=lambda x: "Tous" if x=="Tous" else ("À encaisser" if x=="encaiss" else "À régler"))
    with cf2: fs = st.selectbox("Filtrer par statut", ["Tous","En attente","Réglé","Retard"])

    df_e = ech.copy()
    if ft != "Tous": df_e = df_e[df_e["type"]==ft]
    if fs != "Tous": df_e = df_e[df_e["statut"]==fs]
    df_e = df_e.sort_values("date").copy()
    df_e["Montant (MAD)"] = df_e.apply(
        lambda r: f"+{r['montant']:,.0f}" if r["type"]=="encaiss" else f"-{r['montant']:,.0f}", axis=1)
    df_e["Type"] = df_e["type"].map({"encaiss":"À encaisser","paiement":"À régler"})
    df_e["Date"] = df_e["date"].dt.strftime("%d/%m/%Y")
    st.dataframe(
        df_e[["Date","description","Type","statut","Montant (MAD)"]].rename(columns={
            "description":"Description","statut":"Statut"}),
        hide_index=True, use_container_width=True
    )
    st.download_button("Exporter echeances.csv",
                       ech.to_csv(index=False).encode("utf-8"), "echeances.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PRÉVISION
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Prévision de trésorerie sur 8 semaines")

    base_date = datetime(2025, 4, 7)
    rows_p, running = [], solde_actuel
    for i in range(8):
        start = base_date + timedelta(weeks=i)
        end   = start + timedelta(days=6)
        wech  = ech[(ech["date"]>=pd.Timestamp(start))&(ech["date"]<=pd.Timestamp(end))]
        e_in  = wech[wech["type"]=="encaiss"]["montant"].sum()
        e_out = wech[wech["type"]=="paiement"]["montant"].sum()
        running += e_in - e_out
        rows_p.append({"Semaine": f"S{i+1}",
                        "Période": f"{start.strftime('%d/%m')}–{end.strftime('%d/%m')}",
                        "Entrées": e_in, "Sorties": e_out, "Solde prévu": running})

    df_prev   = pd.DataFrame(rows_p)
    solde_fin = df_prev["Solde prévu"].iloc[-1]
    min_solde = df_prev["Solde prévu"].min()
    tot_e     = df_prev["Entrées"].sum()
    tot_s     = df_prev["Sorties"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Solde de départ (MAD)", f"{solde_actuel:,.0f}")
    c2.metric("Entrées prévues (MAD)", f"+{tot_e:,.0f}")
    c3.metric("Sorties prévues (MAD)", f"-{tot_s:,.0f}")
    c4.metric("Solde fin S8 (MAD)", f"{solde_fin:,.0f}",
              delta=f"Min. : {min_solde:,.0f}",
              delta_color="normal" if min_solde >= SEUIL_ALERTE else "inverse")

    # Projection chart
    pt_colors = ["#DC2626" if s < SEUIL_ALERTE else "#D97706" if s < 30000 else "#059669"
                 for s in df_prev["Solde prévu"]]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df_prev["Semaine"], y=df_prev["Solde prévu"],
        mode="lines+markers",
        line=dict(color="#2563EB", width=2.5),
        marker=dict(color=pt_colors, size=10, line=dict(width=2, color="white")),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.06)"
    ))
    fig3.add_hline(y=SEUIL_ALERTE, line_dash="dot", line_color="#DC2626", line_width=1.5,
                   annotation_text=f"Seuil d'alerte · {SEUIL_ALERTE:,} MAD",
                   annotation_font_size=11, annotation_font_color="#DC2626",
                   annotation_position="bottom right")
    fig3.update_layout(**{**CHART_ARGS, "height": 360})
    fig3.update_xaxes(showgrid=False)
    fig3.update_yaxes(gridcolor="#E5E7EB", tickformat=",.0f", title="MAD")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Détail par semaine")
    df_show = df_prev.copy()
    df_show["Entrées"]     = df_show["Entrées"].apply(lambda x: f"+{x:,.0f} MAD")
    df_show["Sorties"]     = df_show["Sorties"].apply(lambda x: f"-{x:,.0f} MAD")
    df_show["Solde prévu"] = df_show["Solde prévu"].apply(lambda x: f"{x:,.0f} MAD")
    st.dataframe(df_show, hide_index=True, use_container_width=True)
