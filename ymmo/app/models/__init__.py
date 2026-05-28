from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

class UserRole(enum.Enum):
    CLIENT = 'client'
    AGENT = 'agent'
    ADMIN = 'admin'

class PropertyType(enum.Enum):
    APPARTEMENT = 'Appartement'
    MAISON = 'Maison'
    VILLA = 'Villa'
    BUREAU = 'Bureau'
    COMMERCE = 'Commerce'
    TERRAIN = 'Terrain'
    IMMEUBLE = 'Immeuble'

class TransactionType(enum.Enum):
    VENTE = 'Vente'
    LOCATION = 'Location'

class PropertyStatus(enum.Enum):
    DISPONIBLE = 'Disponible'
    SOUS_COMPROMIS = 'Sous compromis'
    VENDU = 'Vendu'
    LOUE = 'Loué'
    RETIRE = 'Retiré'

class AppointmentStatus(enum.Enum):
    EN_ATTENTE = 'En attente'
    CONFIRME = 'Confirmé'
    ANNULE = 'Annulé'
    REALISE = 'Réalisé'

class Agency(db.Model):
    __tablename__ = 'agencies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    zip_code = db.Column(db.String(10))
    region = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    agents = db.relationship('User', backref='agency', lazy=True)
    properties = db.relationship('Property', backref='agency', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.CLIENT, nullable=False)
    agency_id = db.Column(db.Integer, db.ForeignKey('agencies.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', foreign_keys='Appointment.client_id', backref='client', lazy=True)
    managed_appointments = db.relationship('Appointment', foreign_keys='Appointment.agent_id', backref='agent', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_agent(self):
        return self.role == UserRole.AGENT

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Property(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    property_type = db.Column(db.Enum(PropertyType), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    status = db.Column(db.Enum(PropertyStatus), default=PropertyStatus.DISPONIBLE)
    price = db.Column(db.Float, nullable=False)
    surface = db.Column(db.Float)
    rooms = db.Column(db.Integer)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    floor = db.Column(db.Integer)
    total_floors = db.Column(db.Integer)
    year_built = db.Column(db.Integer)
    energy_class = db.Column(db.String(2))
    ges_class = db.Column(db.String(2))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(10))
    region = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    has_parking = db.Column(db.Boolean, default=False)
    has_garden = db.Column(db.Boolean, default=False)
    has_pool = db.Column(db.Boolean, default=False)
    has_balcony = db.Column(db.Boolean, default=False)
    has_elevator = db.Column(db.Boolean, default=False)
    has_cellar = db.Column(db.Boolean, default=False)
    is_furnished = db.Column(db.Boolean, default=False)
    agency_id = db.Column(db.Integer, db.ForeignKey('agencies.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    views_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sold_at = db.Column(db.DateTime)
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='property', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='property', lazy=True)
    agent = db.relationship('User', foreign_keys=[agent_id], backref='properties')

    @property
    def main_image(self):
        img = PropertyImage.query.filter_by(property_id=self.id, is_main=True).first()
        if img:
            return img.filename
        first = PropertyImage.query.filter_by(property_id=self.id).first()
        return first.filename if first else 'default_property.jpg'

    @property
    def price_per_m2(self):
        if self.surface and self.surface > 0:
            return round(self.price / self.surface, 0)
        return None

    @property
    def favorites_count(self):
        return len(self.favorites)

class PropertyImage(db.Model):
    __tablename__ = 'property_images'
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'property_id', name='unique_favorite'),)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.EN_ATTENTE)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=True)
    subject = db.Column(db.String(200))
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SaleRecord(db.Model):
    __tablename__ = 'sale_records'
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=True)
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    property_type = db.Column(db.String(50))
    transaction_type = db.Column(db.String(20))
    price = db.Column(db.Float)
    surface = db.Column(db.Float)
    rooms = db.Column(db.Integer)
    price_per_m2 = db.Column(db.Float)
    sold_at = db.Column(db.DateTime)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    agency_id = db.Column(db.Integer, db.ForeignKey('agencies.id'), nullable=True)
