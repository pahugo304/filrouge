"""
Script de seed — peuple la BDD avec des données de démonstration
Lancer : python seed.py
"""
from app import create_app, db
from app.models import (User, UserRole, Agency, Property, PropertyType,
                        TransactionType, PropertyStatus, SaleRecord)
from datetime import datetime, timedelta
import random

app = create_app('development')

CITIES = [
    ('Aix-en-Provence', 'Provence-Alpes-Côte d\'Azur', 5200),
    ('Marseille', 'Provence-Alpes-Côte d\'Azur', 3900),
    ('Lyon', 'Auvergne-Rhône-Alpes', 5100),
    ('Nice', 'Provence-Alpes-Côte d\'Azur', 5800),
    ('Bordeaux', 'Nouvelle-Aquitaine', 4600),
    ('Toulouse', 'Occitanie', 3700),
    ('Montpellier', 'Occitanie', 3500),
    ('Nantes', 'Pays de la Loire', 4000),
    ('Rennes', 'Bretagne', 3600),
    ('Strasbourg', 'Grand Est', 3400),
    ('Lille', 'Hauts-de-France', 3200),
    ('Paris 16ème', 'Île-de-France', 10500),
]

PROPERTY_NAMES = [
    "Appartement lumineux avec vue", "Maison de caractère avec jardin",
    "Villa contemporaine", "Loft industriel rénové",
    "Studio cosy en centre-ville", "Duplex avec terrasse panoramique",
    "Maison familiale 5 pièces", "Appartement standing vue mer",
    "Bien d'exception avec piscine", "T3 idéal investisseur",
    "Charmante maison de ville", "Appartement neuf BBC",
    "Bureaux d'entreprise refaits", "Local commercial quartier animé",
    "Belle villa provençale", "Maison contemporaine RT2020",
]

DESCRIPTIONS = [
    "Magnifique bien situé dans un quartier prisé, à proximité des commerces et des transports. Lumineux, calme et bien exposé.",
    "Coup de cœur assuré pour ce bien d'exception alliant charme et modernité. Prestations haut de gamme et finitions soignées.",
    "Idéalement situé, ce bien bénéficie d'une excellente exposition et d'une vue dégagée. Parfait état général.",
    "Dans une résidence sécurisée avec gardien, ce bien offre tout le confort moderne. Cave et parking inclus.",
    "Rare sur le marché, ce bien atypique séduira les amateurs de beau. Architecture de qualité et matériaux nobles.",
]

with app.app_context():
    print("Suppression des données existantes...")
    db.drop_all()
    db.create_all()

    # ── Agences ──────────────────────────────────────────────────────────────
    print("Création des agences...")
    agencies = []
    agency_data = [
        ("Ymmo Aix-en-Provence", "Aix-en-Provence", "1 Cours Mirabeau", "13100", "Provence-Alpes-Côte d'Azur", "04 42 00 00 01", "aix@ymmo.fr"),
        ("Ymmo Marseille", "Marseille", "14 La Canebière", "13001", "Provence-Alpes-Côte d'Azur", "04 91 00 00 02", "marseille@ymmo.fr"),
        ("Ymmo Lyon", "Lyon", "20 Rue de la République", "69001", "Auvergne-Rhône-Alpes", "04 78 00 00 03", "lyon@ymmo.fr"),
        ("Ymmo Nice", "Nice", "5 Promenade des Anglais", "06000", "Provence-Alpes-Côte d'Azur", "04 93 00 00 04", "nice@ymmo.fr"),
        ("Ymmo Bordeaux", "Bordeaux", "8 Allées de Tourny", "33000", "Nouvelle-Aquitaine", "05 56 00 00 05", "bordeaux@ymmo.fr"),
        ("Ymmo Toulouse", "Toulouse", "15 Place du Capitole", "31000", "Occitanie", "05 61 00 00 06", "toulouse@ymmo.fr"),
        ("Ymmo Montpellier", "Montpellier", "3 Place de la Comédie", "34000", "Occitanie", "04 67 00 00 07", "montpellier@ymmo.fr"),
        ("Ymmo Nantes", "Nantes", "10 Place du Commerce", "44000", "Pays de la Loire", "02 40 00 00 08", "nantes@ymmo.fr"),
        ("Ymmo Rennes", "Rennes", "2 Place de la Mairie", "35000", "Bretagne", "02 99 00 00 09", "rennes@ymmo.fr"),
        ("Ymmo Strasbourg", "Strasbourg", "5 Place Gutenberg", "67000", "Grand Est", "03 88 00 00 10", "strasbourg@ymmo.fr"),
        ("Ymmo Lille", "Lille", "12 Grand Place", "59000", "Hauts-de-France", "03 20 00 00 11", "lille@ymmo.fr"),
        ("Ymmo Paris", "Paris", "45 Avenue Montaigne", "75008", "Île-de-France", "01 40 00 00 12", "paris@ymmo.fr"),
    ]
    for name, city, addr, zip_code, region, phone, email in agency_data:
        ag = Agency(name=name, city=city, address=addr, zip_code=zip_code, region=region, phone=phone, email=email)
        db.session.add(ag)
        agencies.append(ag)
    db.session.commit()

    # ── Users ─────────────────────────────────────────────────────────────────
    print("Création des utilisateurs...")
    admin = User(first_name='Admin', last_name='Ymmo', email='admin@ymmo.fr', role=UserRole.ADMIN, agency_id=agencies[0].id)
    admin.set_password('admin123')
    db.session.add(admin)

    agents = []
    for i, ag in enumerate(agencies):
        first_names = ['Sophie', 'Marc', 'Julie', 'Thomas', 'Emma', 'Lucas', 'Chloé', 'Antoine', 'Léa', 'Nicolas', 'Camille', 'Pierre']
        last_names = ['Martin', 'Dubois', 'Bernard', 'Thomas', 'Petit', 'Durand', 'Leroy', 'Moreau', 'Simon', 'Michel', 'Laurent', 'Lefebvre']
        agent = User(
            first_name=first_names[i], last_name=last_names[i],
            email=f'agent{i+1}@ymmo.fr', phone=f'06 {random.randint(10,99):02d} {random.randint(10,99):02d} {random.randint(10,99):02d} {random.randint(10,99):02d}',
            role=UserRole.AGENT, agency_id=ag.id
        )
        agent.set_password('agent123')
        db.session.add(agent)
        agents.append(agent)

    # Demo agent
    demo_agent = User(first_name='Agent', last_name='Démo', email='agent@ymmo.fr', role=UserRole.AGENT, agency_id=agencies[0].id)
    demo_agent.set_password('agent123')
    db.session.add(demo_agent)

    # Demo client
    client = User(first_name='Client', last_name='Démo', email='client@ymmo.fr', role=UserRole.CLIENT)
    client.set_password('client123')
    db.session.add(client)

    db.session.commit()

    # ── Properties ────────────────────────────────────────────────────────────
    print("Création des biens immobiliers...")
    prop_types = list(PropertyType)
    trans_types = list(TransactionType)
    statuses = list(PropertyStatus)
    energy_classes = ['A', 'B', 'C', 'D', 'E']

    properties = []
    for i in range(80):
        city, region, base_pm2 = random.choice(CITIES)
        prop_type = random.choice(prop_types[:5])  # mainly residential
        trans_type = random.choice(trans_types)
        surface = random.randint(25, 350)
        rooms = max(1, surface // 20)
        bedrooms = max(0, rooms - 1)
        price_pm2 = base_pm2 + random.randint(-800, 1200)
        price = surface * price_pm2
        if trans_type == TransactionType.LOCATION:
            price = surface * random.uniform(12, 25)

        agent = random.choice(agents + [demo_agent])
        agency = agent.agency

        prop = Property(
            title=random.choice(PROPERTY_NAMES) + f' — {city}',
            description=random.choice(DESCRIPTIONS),
            property_type=prop_type,
            transaction_type=trans_type,
            status=random.choices(list(PropertyStatus), weights=[70, 10, 10, 5, 5])[0],
            price=round(price, -3),
            surface=float(surface),
            rooms=rooms,
            bedrooms=bedrooms,
            bathrooms=random.randint(1, 3),
            floor=random.randint(0, 6),
            total_floors=random.randint(1, 8),
            year_built=random.randint(1960, 2023),
            energy_class=random.choice(energy_classes),
            ges_class=random.choice(energy_classes),
            city=city,
            region=region,
            zip_code=f'{random.randint(10,99):02d}000',
            has_parking=random.random() > 0.5,
            has_garden=random.random() > 0.6,
            has_pool=random.random() > 0.8,
            has_balcony=random.random() > 0.5,
            has_elevator=random.random() > 0.6,
            has_cellar=random.random() > 0.5,
            is_furnished=random.random() > 0.7,
            is_featured=(i < 6),
            agent_id=agent.id,
            agency_id=agency.id if agency else None,
            views_count=random.randint(0, 500),
        )
        db.session.add(prop)
        properties.append(prop)
    db.session.commit()

    # ── Sale Records (historique analytics) ───────────────────────────────────
    print("Création de l'historique de ventes...")
    for i in range(500):
        city, region, base_pm2 = random.choice(CITIES)
        surface = random.randint(25, 300)
        pm2 = base_pm2 + random.randint(-600, 800)
        price = surface * pm2
        months_ago = random.randint(0, 24)
        sold_date = datetime.utcnow() - timedelta(days=months_ago * 30 + random.randint(0, 29))
        prop_type = random.choice(['Appartement', 'Maison', 'Villa', 'Bureau', 'Commerce', 'Terrain'])

        rec = SaleRecord(
            city=city, region=region,
            property_type=prop_type,
            transaction_type=random.choice(['Vente', 'Location']),
            price=round(price, -2),
            surface=float(surface),
            rooms=max(1, surface // 20),
            price_per_m2=round(pm2, 0),
            sold_at=sold_date,
            year=sold_date.year,
            month=sold_date.month,
            agency_id=random.choice(agencies).id,
        )
        db.session.add(rec)
    db.session.commit()

    print("\n✅ Seed terminé avec succès !")
    print("─" * 40)
    print("Comptes de connexion :")
    print("  Admin  : admin@ymmo.fr  / admin123")
    print("  Agent  : agent@ymmo.fr  / agent123")
    print("  Client : client@ymmo.fr / client123")
    print("─" * 40)
    print(f"  {len(agencies)} agences | {len(agents)+3} utilisateurs | {len(properties)} biens | 500 ventes")
