"""
generate_data.py
─────────────────────────────────────────────────────────────────────────────
Lit user_events.csv (le fichier de données réelles),
exécute toutes les requêtes analytiques (équivalentes au SQL
de Dashboard_analysis_Queries.sql),
et génère un fichier data.js qui expose la constante DATA
utilisée directement par dashboard_ecommerce.html.

Usage :
    python generate_data.py                 → utilise user_events.csv local
    python generate_data.py --csv chemin/   → chemin personnalisé
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import json
import math
from pathlib import Path

import pandas as pd

# ── Couleurs cohérentes avec le dashboard ─────────────────────────────────
SOURCE_COLORS = {
    "organic":  "#e8c547",
    "email":    "#4fc3f7",
    "social":   "#f06292",
    "direct":   "#81c784",
    "paid_ads": "#ff8a65",
}
FUNNEL_COLORS = ["#4fc3f7", "#7986cb", "#ba68c8", "#f06292", "#e8c547"]

# ── Labels lisibles pour les sources ──────────────────────────────────────
SOURCE_LABELS = {
    "organic":  "SEO / Organic",
    "email":    "Email",
    "social":   "Social",
    "direct":   "Direct",
    "paid_ads": "Paid Ads",
}

# ── Noms des mois en français ──────────────────────────────────────────────
MONTHS_FR = [
    "Jan","Fév","Mar","Avr","Mai","Jun",
    "Jul","Aoû","Sep","Oct","Nov","Déc"
]


def load_events(csv_path: Path) -> pd.DataFrame:
    """Charge et prépare le CSV des événements."""
    df = pd.read_csv(csv_path)
    df["event_date"] = pd.to_datetime(df["event_date"])
    # Mettre amount à NULL quand 0 (comme le fait l'UPDATE SQL)
    df.loc[df["amount"] == 0, "amount"] = None
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Équivalent de la requête revenue funnel analysis (funnel_revenue).
    Calcule CA, AOV, taux de conversion, revenu par visiteur.
    """
    purchases = df[df["event_type"] == "purchase"]
    total_visitors = df["user_id"].nunique()
    buyers         = purchases["user_id"].nunique()
    total_revenue  = purchases["amount"].sum()
    total_orders   = len(purchases)

    aov = total_revenue / total_orders if total_orders else 0
    cvr = buyers / total_visitors * 100 if total_visitors else 0
    rpv = total_revenue / total_visitors if total_visitors else 0

    return {
        "ca":  round(total_revenue, 2),
        "aov": round(aov, 2),
        "cvr": round(cvr, 2),
        "rpv": round(rpv, 2),
    }


def compute_funnel(df: pd.DataFrame) -> list:
    """
    Équivalent de la requête funnel_stages (CTE WITH).
    Compte les utilisateurs distincts par étape du tunnel.
    """
    stages = [
        ("Page View",      "page_view"),
        ("Add to Cart",    "add_to_cart"),
        ("Checkout Start", "checkout_start"),
        ("Payment Info",   "payment_info"),
        ("Purchase",       "purchase"),
    ]
    result = []
    for i, (label, event) in enumerate(stages):
        count = df[df["event_type"] == event]["user_id"].nunique()
        result.append({
            "label": label,
            "count": int(count),
            "color": FUNNEL_COLORS[i],
        })
    return result


def compute_sources(df: pd.DataFrame) -> list:
    """
    Équivalent des requêtes par traffic_source :
    - revenue & nombre d'achats par source
    - visiteurs uniques par source
    """
    purchases = df[df["event_type"] == "purchase"]

    # Visiteurs par source
    visitors = (
        df.groupby("traffic_source")["user_id"]
        .nunique()
        .rename("visitors")
    )

    # Revenue et achats par source
    rev_pur = (
        purchases.groupby("traffic_source")
        .agg(revenue=("amount", "sum"), purchases=("event_id", "count"))
    )

    merged = visitors.to_frame().join(rev_pur, how="left").fillna(0)
    merged["revenue"]   = merged["revenue"].round(2)
    merged["purchases"] = merged["purchases"].astype(int)

    # Tri par revenue décroissant (comme ORDER BY chiffre_affaires DESC)
    merged = merged.sort_values("revenue", ascending=False)

    result = []
    for src, row in merged.iterrows():
        result.append({
            "source":    SOURCE_LABELS.get(src, src),
            "revenue":   row["revenue"],
            "visitors":  int(row["visitors"]),
            "purchases": int(row["purchases"]),
            "color":     SOURCE_COLORS.get(src, "#aaaaaa"),
        })
    return result


def compute_monthly(df: pd.DataFrame) -> dict:
    """
    Revenue mensuel – tous les 12 mois présents dans le dataset
    (les mois sans vente valent 0).
    """
    purchases = df[df["event_type"] == "purchase"].copy()
    purchases["month"] = purchases["event_date"].dt.month

    monthly_sum = purchases.groupby("month")["amount"].sum()

    revenue = []
    for m in range(1, 13):
        val = monthly_sum.get(m, 0.0)
        revenue.append(round(float(val), 2))

    return {
        "labels":  MONTHS_FR,
        "revenue": revenue,
    }


def build_data(csv_path: Path) -> dict:
    """Assemble le dictionnaire DATA complet."""
    df = load_events(csv_path)
    return {
        "kpi":     compute_kpis(df),
        "funnel":  compute_funnel(df),
        "sources": compute_sources(df),
        "monthly": compute_monthly(df),
    }


def write_js(data: dict, output_path: Path) -> None:
    """
    Écrit data.js avec la constante DATA au format JSON,
    directement importable dans dashboard_ecommerce.html via :
        <script src="data.js"></script>
    """
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    js_content = f"""// ─────────────────────────────────────────────────────────────────────────
// data.js  —  GÉNÉRÉ AUTOMATIQUEMENT par generate_data.py
// Ne pas modifier manuellement. Relancer le script pour mettre à jour.
// Source : user_events.csv
// ─────────────────────────────────────────────────────────────────────────

const DATA = {json_str};
"""
    output_path.write_text(js_content, encoding="utf-8")
    print(f"✅  data.js généré → {output_path.resolve()}")
    print(f"    CA total     : {data['kpi']['ca']:,.2f} MAD")
    print(f"    AOV          : {data['kpi']['aov']:,.2f} MAD")
    print(f"    CVR          : {data['kpi']['cvr']:.2f} %")
    print(f"    RPV          : {data['kpi']['rpv']:.2f} MAD")
    print(f"    Funnel top   : {data['funnel'][0]['count']} page_views")
    print(f"    Sources      : {[s['source'] for s in data['sources']]}")


def main():
    parser = argparse.ArgumentParser(description="Génère data.js depuis user_events.csv")
    parser.add_argument(
        "--csv",
        default="user_events.csv",
        help="Chemin vers user_events.csv (défaut: ./user_events.csv)",
    )
    parser.add_argument(
        "--out",
        default="data.js",
        help="Fichier JS de sortie (défaut: ./data.js)",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    out_path = Path(args.out)

    if not csv_path.exists():
        print(f"❌  Fichier introuvable : {csv_path}")
        raise SystemExit(1)

    print(f"📂  Lecture de {csv_path} …")
    data = build_data(csv_path)
    write_js(data, out_path)


if __name__ == "__main__":
    main()
