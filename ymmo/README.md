# 🏠 Ymmo — Plateforme Immobilière

Projet Ynov Campus B2 — UF INFRA & DEV

Plateforme web de gestion immobilière avec analyse de données IA, développée en Python (Flask) + MySQL.

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.10+ / Flask 3.0 |
| Base de données | MySQL / MariaDB |
| ORM | SQLAlchemy + Flask-Migrate |
| Auth | Flask-Login |
| Analyse IA | pandas, scikit-learn (RandomForest) |
| Frontend | HTML/CSS/JS vanilla + Chart.js |
| Upload images | Werkzeug |

---

## Installation

### 1. Prérequis

- Python 3.10+
- MySQL 8.0+ ou MariaDB 10.6+
- pip

### 2. Cloner & environnement virtuel

```bash
git clone <repo>
cd ymmo
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

Créer la BDD MySQL :

```sql
CREATE DATABASE ymmo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ymmo_user'@'localhost' IDENTIFIED BY 'ymmo_password';
GRANT ALL PRIVILEGES ON ymmo_db.* TO 'ymmo_user'@'localhost';
FLUSH PRIVILEGES;
```

Copier et adapter le fichier d'environnement :

```bash
cp .env.example .env
# Éditer .env avec vos identifiants MySQL
```

### 5. Initialiser la base et charger les données de démo

```bash
flask db init
flask db migrate -m "init"
flask db upgrade
python seed.py
```

### 6. Lancer le serveur

```bash
python run.py
```

Accéder à : **http://localhost:5000**

---

## Comptes de démonstration

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Administrateur | admin@ymmo.fr | admin123 |
| Agent | agent@ymmo.fr | agent123 |
| Client | client@ymmo.fr | client123 |

---

## Structure du projet

```
ymmo/
├── app/
│   ├── __init__.py          # Factory Flask
│   ├── models/
│   │   └── __init__.py      # Modèles SQLAlchemy
│   ├── routes/
│   │   ├── main.py          # Pages publiques
│   │   ├── auth.py          # Authentification
│   │   ├── properties.py    # Gestion des biens
│   │   ├── dashboard.py     # Espaces client/agent
│   │   ├── admin.py         # Administration
│   │   └── api.py           # API JSON
│   ├── services/
│   │   └── analytics.py     # IA + analyse de données
│   ├── templates/           # Templates Jinja2
│   │   ├── base.html
│   │   ├── main/
│   │   ├── auth/
│   │   ├── properties/
│   │   ├── dashboard/
│   │   └── admin/
│   └── static/
│       └── img/properties/  # Images uploadées
├── config.py                # Configuration
├── run.py                   # Point d'entrée
├── seed.py                  # Données de démo
├── requirements.txt
└── .env.example
```

---

## Fonctionnalités

###  Côté public
- Recherche avancée avec filtres (type, ville, prix, surface, pièces...)
- Fiches de biens avec galerie photos
- Outil d'estimation IA (RandomForest / heuristique)
- Carte des agences

###  Espace client
- Gestion des favoris
- Prise de rendez-vous
- Historique des RDV

###  Espace agent
- CRUD complet des annonces
- Upload de photos
- Gestion des RDV entrants

###  Administration
- Dashboard avec graphiques (Chart.js)
- Gestion utilisateurs / rôles / agences
- Analytique de marché complète :
  - Tendances des prix au m²
  - CA mensuel par agence
  - Zones géographiques chaudes
  - Distribution par type de bien

###  IA & Données (analytics.py)
- `predict_price()` — Prédiction de prix via RandomForestRegressor
- `get_price_trends()` — Évolution mensuelle des prix
- `get_top_cities()` — Villes les plus actives
- `get_hot_zones()` — Zones dynamiques (6 mois)
- `get_market_overview()` — Indicateurs globaux
- Fallback sur données mock si BDD vide

---

## Variables d'environnement (.env)

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=votre-clé-secrète
DB_HOST=localhost
DB_PORT=3306
DB_USER=ymmo_user
DB_PASSWORD=ymmo_password
DB_NAME=ymmo_db
```

---

## API JSON

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/estimation` | POST | Estimation de prix IA |
| `/api/trends` | GET | Tendances des prix |
| `/api/market-overview` | GET | Vue d'ensemble marché |
| `/api/top-cities` | GET | Top villes |
| `/api/properties/map` | GET | Biens géolocalisés |

---

*Projet réalisé dans le cadre du cursus Ynov Informatique B2 — 2024*
