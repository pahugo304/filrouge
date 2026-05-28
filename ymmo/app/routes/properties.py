from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Property, PropertyImage, Favorite, Appointment, PropertyType, TransactionType, PropertyStatus, UserRole, User
from datetime import datetime
import os, uuid
from werkzeug.utils import secure_filename

properties_bp = Blueprint('properties', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@properties_bp.route('/<int:id>')
def detail(id):
    prop = Property.query.get_or_404(id)
    prop.views_count = (prop.views_count or 0) + 1
    db.session.commit()
    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(user_id=current_user.id, property_id=id).first() is not None
    similar = Property.query.filter(Property.city==prop.city, Property.id!=prop.id, Property.status==PropertyStatus.DISPONIBLE, Property.transaction_type==prop.transaction_type).limit(3).all()
    agents = User.query.filter_by(role=UserRole.AGENT).limit(5).all()
    return render_template('properties/detail.html', property=prop, is_favorited=is_favorited, similar=similar, agents=agents)

@properties_bp.route('/ajouter', methods=['GET', 'POST'])
@login_required
def add():
    if current_user.role not in [UserRole.AGENT, UserRole.ADMIN]:
        flash('Accès réservé aux agents.', 'danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        prop = Property(
            title=request.form.get('title'), description=request.form.get('description'),
            property_type=PropertyType(request.form.get('property_type')),
            transaction_type=TransactionType(request.form.get('transaction_type')),
            price=float(request.form.get('price', 0)),
            surface=float(request.form.get('surface', 0) or 0) or None,
            rooms=int(request.form.get('rooms', 0) or 0) or None,
            bedrooms=int(request.form.get('bedrooms', 0) or 0) or None,
            bathrooms=int(request.form.get('bathrooms', 0) or 0) or None,
            floor=int(request.form.get('floor', 0) or 0) or None,
            year_built=int(request.form.get('year_built', 0) or 0) or None,
            energy_class=request.form.get('energy_class') or None,
            address=request.form.get('address'), city=request.form.get('city'),
            zip_code=request.form.get('zip_code'), region=request.form.get('region'),
            has_parking='has_parking' in request.form, has_garden='has_garden' in request.form,
            has_pool='has_pool' in request.form, has_balcony='has_balcony' in request.form,
            has_elevator='has_elevator' in request.form, has_cellar='has_cellar' in request.form,
            is_furnished='is_furnished' in request.form, is_featured='is_featured' in request.form,
            agent_id=current_user.id, agency_id=current_user.agency_id,
        )
        db.session.add(prop)
        db.session.flush()
        for i, image in enumerate(request.files.getlist('images')):
            if image and allowed_file(image.filename):
                ext = image.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                db.session.add(PropertyImage(property_id=prop.id, filename=filename, is_main=(i==0)))
        db.session.commit()
        flash('Bien ajouté avec succès !', 'success')
        return redirect(url_for('properties.detail', id=prop.id))
    return render_template('properties/form.html', property_types=PropertyType, transaction_types=TransactionType, prop=None)

@properties_bp.route('/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def edit(id):
    prop = Property.query.get_or_404(id)
    if current_user.role == UserRole.CLIENT or (current_user.role == UserRole.AGENT and prop.agent_id != current_user.id):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        prop.title = request.form.get('title')
        prop.description = request.form.get('description')
        prop.price = float(request.form.get('price', 0))
        prop.surface = float(request.form.get('surface', 0) or 0) or None
        prop.rooms = int(request.form.get('rooms', 0) or 0) or None
        prop.bedrooms = int(request.form.get('bedrooms', 0) or 0) or None
        prop.bathrooms = int(request.form.get('bathrooms', 0) or 0) or None
        prop.status = PropertyStatus(request.form.get('status'))
        prop.city = request.form.get('city')
        prop.zip_code = request.form.get('zip_code')
        prop.address = request.form.get('address')
        prop.energy_class = request.form.get('energy_class') or None
        prop.has_parking = 'has_parking' in request.form
        prop.has_garden = 'has_garden' in request.form
        prop.has_pool = 'has_pool' in request.form
        prop.has_balcony = 'has_balcony' in request.form
        prop.has_elevator = 'has_elevator' in request.form
        prop.is_featured = 'is_featured' in request.form
        for i, image in enumerate(request.files.getlist('images')):
            if image and image.filename and allowed_file(image.filename):
                ext = image.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                existing_main = PropertyImage.query.filter_by(property_id=prop.id, is_main=True).first()
                db.session.add(PropertyImage(property_id=prop.id, filename=filename, is_main=(existing_main is None and i==0)))
        db.session.commit()
        flash('Bien mis à jour.', 'success')
        return redirect(url_for('properties.detail', id=prop.id))
    return render_template('properties/form.html', property_types=PropertyType, transaction_types=TransactionType, statuses=PropertyStatus, prop=prop)

@properties_bp.route('/<int:id>/supprimer', methods=['POST'])
@login_required
def delete(id):
    prop = Property.query.get_or_404(id)
    if not current_user.is_admin and prop.agent_id != current_user.id:
        flash('Non autorisé.', 'danger')
        return redirect(url_for('main.index'))
    db.session.delete(prop)
    db.session.commit()
    flash('Bien supprimé.', 'success')
    return redirect(url_for('dashboard.index'))

@properties_bp.route('/<int:id>/favori', methods=['POST'])
@login_required
def toggle_favorite(id):
    prop = Property.query.get_or_404(id)
    existing = Favorite.query.filter_by(user_id=current_user.id, property_id=id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed', 'count': prop.favorites_count})
    db.session.add(Favorite(user_id=current_user.id, property_id=id))
    db.session.commit()
    return jsonify({'status': 'added', 'count': prop.favorites_count})

@properties_bp.route('/<int:id>/rdv', methods=['POST'])
@login_required
def book_appointment(id):
    prop = Property.query.get_or_404(id)
    agent_id = request.form.get('agent_id', type=int)
    date_str = request.form.get('scheduled_at')
    notes = request.form.get('notes', '')
    try:
        scheduled = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
    except (ValueError, TypeError):
        flash('Date invalide.', 'danger')
        return redirect(url_for('properties.detail', id=id))
    db.session.add(Appointment(client_id=current_user.id, agent_id=agent_id or (prop.agent_id or 1), property_id=id, scheduled_at=scheduled, notes=notes))
    db.session.commit()
    flash('Rendez-vous demandé ! Un agent vous contactera.', 'success')
    return redirect(url_for('properties.detail', id=id))
