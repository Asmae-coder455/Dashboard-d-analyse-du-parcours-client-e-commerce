# KitchenTools — Dashboard d'analyse du parcours client e-commerce (V2)

Analysez le comportement des visiteurs d'une boutique en ligne : tunnel de conversion, performance des sources de trafic, chiffre d'affaires mensuel et indicateurs clés (CA, panier moyen, taux de conversion, revenu par visiteur).

Cette **version 2** automatise entièrement le pipeline : un **script Python (pandas)** lit le fichier de données, calcule tous les indicateurs et génère `data.js`, consommé par un **dashboard HTML/JavaScript (Chart.js)**. Elle remplace la [version 1](#transition-v1--v2-de-mysql-manuel-à-python-automatisé), qui reposait sur MySQL et des chiffres copiés à la main.

> 📦 **Version 1 (MySQL, manuelle)** : dépôt [`mon_projet_data`](https://github.com/Asmae-coder455/mon_projet_data) — conservé en ligne comme référence historique.

---

## Table des matières

1. [Architecture](#architecture)
2. [Transition V1 → V2](#transition-v1--v2-de-mysql-manuel-à-python-automatisé)
3. [Prérequis](#prérequis)
4. [Installation et lancement](#installation-et-lancement)
5. [Données](#données)
6. [Indicateurs calculés](#indicateurs-calculés)
7. [Fonctionnalités du dashboard](#fonctionnalités-du-dashboard)
8. [Référence du script](#référence-du-script)
9. [État d'avancement](#état-davancement)
10. [Dépannage](#dépannage)
11. [Aide-mémoire](#aide-mémoire)

---

## Architecture

```
mon_projet_data_V2_script_Python/
├── user_events.csv            # Données sources : événements utilisateurs (Kaggle)
├── generate_data.py           # Script Python : lit le CSV, calcule les indicateurs, écrit data.js
├── data.js                    # GÉNÉRÉ automatiquement : constante JavaScript DATA
├── dashboard_ecommerce.html   # Dashboard (HTML/CSS/JS + Chart.js)
└── README.md
```

| Composant | Technologies | Rôle |
|---|---|---|
| Source de données | Kaggle (fichier CSV) | Événements utilisateurs bruts |
| Traitement | Python 3, pandas | Calcul des KPI, tunnel, sources, mensuel |
| Visualisation | HTML, CSS, JavaScript, Chart.js 4.4.1 (CDN) | Dashboard |

**Flux général (V2) :**

```
user_events.csv ──► generate_data.py (pandas) ──► data.js (const DATA) ──► dashboard_ecommerce.html
```

`data.js` est chargé par le HTML via `<script src="data.js"></script>` : le dashboard s'ouvre directement dans le navigateur, sans serveur.

---

## Transition V1 → V2 : de MySQL manuel à Python automatisé

### Rappel : la version 1

Dépôt : [`mon_projet_data`](https://github.com/<votre-compte>/mon_projet_data)

Dans la V1, le flux était entièrement manuel :

```
Données ──► base MySQL ──► requêtes SQL exécutées une à une ──► résultats copiés à la main ──► dashboard HTML (chiffres écrits en dur)
```

1. Les données étaient importées dans une **base MySQL**.
2. Les requêtes d'analyse (tunnel de conversion, revenu par source, CA mensuel, KPI) étaient **exécutées manuellement** dans MySQL.
3. Les résultats étaient **copiés-collés** dans le code du dashboard HTML, sous forme de **chiffres statiques**.

### Pourquoi cette approche ne convenait plus

| Limite de la V1 | Conséquence |
|---|---|
| Chiffres écrits en dur dans le HTML | Le dashboard ne reflète jamais l'état réel des données dès qu'elles changent |
| Copier-coller manuel des résultats | Risque d'erreurs de saisie, oublis, valeurs obsolètes |
| Requêtes lancées une par une | Processus long, non reproductible, dépendant de la personne qui l'exécute |
| Dépendance à un serveur MySQL | Installation, configuration et import de la base nécessaires pour simplement relancer l'analyse |
| Aucun lien automatique entre données et affichage | Chaque mise à jour = refaire tout le travail à la main |

### La version 2

Un script Python prend en charge toute la chaîne :

1. **Lecture** du fichier `user_events.csv` (plus besoin de base MySQL).
2. **Calcul** de tous les indicateurs avec pandas, qui reproduit la logique des requêtes SQL de la V1.
3. **Génération** du fichier `data.js`, qui expose la constante `DATA`.
4. **Affichage** : `dashboard_ecommerce.html` lit `DATA` directement. Plus aucun chiffre écrit à la main.

### Ce qui change concrètement

| | V1 — `mon_projet_data` | V2 — ce dépôt |
|---|---|---|
| Source des données | Base MySQL | Fichier `user_events.csv` |
| Calcul des indicateurs | Requêtes SQL lancées à la main | Script Python (pandas), une seule commande |
| Transfert vers le dashboard | Copier-coller des résultats | Fichier `data.js` généré automatiquement |
| Chiffres du dashboard | Statiques, écrits en dur | Dynamiques, lus depuis `DATA` |
| Mise à jour | Refaire toutes les étapes | `python generate_data.py` puis recharger la page |
| Reproductibilité | Faible | Totale (même entrée, même résultat) |
| Prérequis | MySQL + client SQL | Python + pandas |

### Correspondance SQL → pandas

Chaque requête de la V1 a un équivalent dans `generate_data.py` :

| Logique SQL (V1) | Équivalent Python (V2) |
|---|---|
| `UPDATE` des montants `0` en `NULL` | `load_events` : `df.loc[df["amount"] == 0, "amount"] = None` |
| Requête de revenu et de funnel global (CA, panier moyen, conversion) | `compute_kpis` |
| CTE `WITH` des étapes du tunnel, `COUNT(DISTINCT user_id)` | `compute_funnel` : `nunique()` par `event_type` |
| `GROUP BY traffic_source` + `ORDER BY chiffre_affaires DESC` | `compute_sources` : `groupby` + `sort_values(ascending=False)` |
| Agrégation du CA par mois | `compute_monthly` |

> Le script ne se connecte **pas** à MySQL et n'exécute pas de SQL : il réimplémente la même logique avec pandas, directement sur le CSV.

### Migrer de la V1 à la V2

1. Cloner ce dépôt (V2). L'ancien dépôt `mon_projet_data` reste disponible pour consulter les requêtes SQL d'origine et la première version du dashboard.
2. Placer `user_events.csv` à côté de `generate_data.py`.
3. Lancer `python generate_data.py` pour produire `data.js`.
4. Ouvrir `dashboard_ecommerce.html`.

### Pourquoi garder la V1 en ligne

- Elle documente la démarche d'analyse SQL initiale (requêtes, modèle de données).
- Elle permet de comparer les résultats V1 et V2 pour **vérifier** que le script reproduit bien les chiffres de MySQL.
- Elle montre l'évolution du projet, du prototype manuel au pipeline automatisé.

---

## Prérequis

| Outil | Version |
|---|---|
| Python | 3.9+ |
| pandas | dernière version stable |
| Navigateur | récent (Chrome, Firefox, Edge) ; connexion internet pour Chart.js et Google Fonts |
| Git | pour le suivi de version |

> MySQL n'est **plus nécessaire** en V2. Il reste utile uniquement pour rejouer les requêtes de la V1.

---

## Installation et lancement

### 1. Cloner le dépôt

```bash
git clone <url-du-depot-v2>
cd mon_projet_data_V2_script_Python
```

### 2. Créer un environnement virtuel et installer les dépendances

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install pandas
```

### 3. Générer les données du dashboard

```bash
python generate_data.py
```

Options :

```bash
python generate_data.py --csv chemin/vers/user_events.csv --out data.js
```

Le terminal affiche un récapitulatif (CA total, AOV, CVR, RPV, taille du tunnel, sources).

### 4. Ouvrir le dashboard

Ouvrez `dashboard_ecommerce.html` dans votre navigateur (double-clic). À chaque changement de données, relancez l'étape 3 puis rechargez la page.

---

## Données

Fichier : `user_events.csv` — un événement par ligne.

| Colonne | Description |
|---|---|
| `event_id` | Identifiant unique de l'événement |
| `user_id` | Identifiant du visiteur |
| `event_type` | `page_view`, `add_to_cart`, `checkout_start`, `payment_info`, `purchase` |
| `event_date` | Date et heure de l'événement |
| `product_id` | Produit concerné |
| `amount` | Montant (renseigné pour les achats) ; `0` est converti en valeur nulle au chargement |
| `traffic_source` | Source du trafic (`organic`, `email`, `social`, `paid_ads`, …) |

Volumétrie actuelle : environ 9 400 événements, 5 000 visiteurs uniques, 6 produits, période du 30 décembre 2025 au 3 février 2026.

> Source d'origine : jeu de données Kaggle `<nom-du-dataset>` (à renseigner).

---

## Indicateurs calculés

| Indicateur | Définition | Fonction |
|---|---|---|
| CA | Somme des montants des achats | `compute_kpis` |
| AOV (panier moyen) | CA / nombre de commandes | `compute_kpis` |
| CVR (taux de conversion) | Acheteurs uniques / visiteurs uniques × 100 | `compute_kpis` |
| RPV (revenu par visiteur) | CA / visiteurs uniques | `compute_kpis` |
| Tunnel de conversion | Utilisateurs uniques à chaque étape, de la vue de page à l'achat | `compute_funnel` |
| Performance par source | Visiteurs, achats et revenu par source de trafic, triés par revenu décroissant | `compute_sources` |
| CA mensuel | Revenu des achats par mois | `compute_monthly` |

---

## Fonctionnalités du dashboard

- **Cartes KPI** animées : CA, panier moyen, taux de conversion, revenu par visiteur
- **Tunnel de conversion** en cinq étapes (Page View → Add to Cart → Checkout Start → Payment Info → Purchase)
- **Répartition par source de trafic** : graphique en anneau (Chart.js)
- **Évolution du chiffre d'affaires** : courbe mensuelle (Chart.js)
- Interface en français, polices Fraunces et DM Mono, date du jour affichée automatiquement
- **Données dynamiques** : mises à jour en une commande (`python generate_data.py`)

---

## Référence du script

`generate_data.py`

| Fonction | Rôle |
|---|---|
| `load_events(csv_path)` | Charge le CSV, convertit les dates, remplace les montants `0` par `None` |
| `compute_kpis(df)` | CA, AOV, CVR, RPV |
| `compute_funnel(df)` | Comptes d'utilisateurs uniques par étape + couleurs |
| `compute_sources(df)` | Visiteurs, achats, revenu par source, avec libellés et couleurs |
| `compute_monthly(df)` | CA par mois (12 valeurs) |
| `build_data(csv_path)` | Assemble le dictionnaire complet `DATA` |
| `write_js(data, output_path)` | Écrit `data.js` (`const DATA = {...};`) et affiche le résumé |
| `main()` | Interface en ligne de commande (`--csv`, `--out`) |

Structure de `DATA` : `kpi`, `funnel`, `sources`, `monthly`.

---

## État d'avancement

### Fait
- V1 : analyse SQL sous MySQL et premier dashboard statique (dépôt `mon_projet_data`)
- V2 : pipeline complet CSV → Python → `data.js` → dashboard
- KPI, tunnel de conversion, analyse par source, CA mensuel, tous calculés automatiquement
- Dashboard avec animations et graphiques Chart.js alimentés par `DATA`

### À faire
- Regrouper le CA mensuel par **année et mois** : le script regroupe actuellement par numéro de mois seul, ce qui mélange les années et laisse la plupart des mois à 0 sur une période de cinq semaines
- Comparer systématiquement les résultats V1 (MySQL) et V2 (Python) pour valider l'équivalence
- Ajouter des filtres (période, source, produit) dans le dashboard
- Ajouter le taux de passage entre chaque étape du tunnel
- Ajouter des tests (`pytest`) et un `requirements.txt`

---

## Dépannage

### `❌ Fichier introuvable : user_events.csv`
Le script cherche le CSV dans le dossier courant. Lancez-le depuis le dossier du projet ou indiquez le chemin : `python generate_data.py --csv chemin/vers/user_events.csv`.

### `ModuleNotFoundError: No module named 'pandas'`
L'environnement virtuel n'est pas activé, ou pandas n'est pas installé : activez `.venv` puis `pip install pandas`.

### Le dashboard est vide ou affiche des zéros
`data.js` doit se trouver dans le **même dossier** que `dashboard_ecommerce.html`. Relancez `python generate_data.py` et rechargez la page (Ctrl + F5).

### Les graphiques ne s'affichent pas
Chart.js est chargé depuis un CDN : vérifiez la connexion internet et la console du navigateur (F12).

### Caractères accentués illisibles dans `data.js`
Le fichier est écrit en UTF-8. Ouvrez-le avec un éditeur configuré en UTF-8.

---

## Aide-mémoire

```bash
# Installation (une seule fois)
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux : source .venv/bin/activate
pip install pandas

# Mise à jour des données du dashboard
python generate_data.py

# Avec options
python generate_data.py --csv user_events.csv --out data.js

# Puis ouvrir dashboard_ecommerce.html dans le navigateur
```
