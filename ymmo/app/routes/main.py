from flask import Blueprint, render_template, request
from app.models import Property, PropertyType, TransactionType, PropertyStatus
from app.services.analytics import AnalyticsService
from sqlalchemy import or_

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured = Property.query.filter_by(is_featured=True, status=PropertyStatus.DISPONIBLE).limit(6).all()
    recent = Property.query.filter_by(status=PropertyStatus.DISPONIBLE).order_by(Property.created_at.desc()).limit(8).all()
    stats = AnalyticsService.get_market_overview()
    hot_zones = AnalyticsService.get_hot_zones()
    return render_template('main/index.html', featured=featured, recent=recent, stats=stats, hot_zones=hot_zones)

@main_bp.route('/recherche')
def search():
    query = request.args.get('q', '')
    transaction = request.args.get('transaction', '')
    property_type = request.args.get('type', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_surface = request.args.get('min_surface', type=float)
    max_surface = request.args.get('max_surface', type=float)
    rooms = request.args.get('rooms', type=int)
    city = request.args.get('city', '')
    sort = request.args.get('sort', 'recent')
    page = request.args.get('page', 1, type=int)

    pq = Property.query.filter_by(status=PropertyStatus.DISPONIBLE)
    if query:
        pq = pq.filter(or_(Property.title.ilike(f'%{query}%'), Property.city.ilike(f'%{query}%')))
    if city:
        pq = pq.filter(Property.city.ilike(f'%{city}%'))
    if transaction:
        try:
            pq = pq.filter_by(transaction_type=TransactionType(transaction))
        except ValueError:
            pass
    if property_type:
        try:
            pq = pq.filter_by(property_type=PropertyType(property_type))
        except ValueError:
            pass
    if min_price:
        pq = pq.filter(Property.price >= min_price)
    if max_price:
        pq = pq.filter(Property.price <= max_price)
    if min_surface:
        pq = pq.filter(Property.surface >= min_surface)
    if max_surface:
        pq = pq.filter(Property.surface <= max_surface)
    if rooms:
        pq = pq.filter(Property.rooms >= rooms)

    if sort == 'price_asc':
        pq = pq.order_by(Property.price.asc())
    elif sort == 'price_desc':
        pq = pq.order_by(Property.price.desc())
    elif sort == 'surface':
        pq = pq.order_by(Property.surface.desc())
    else:
        pq = pq.order_by(Property.created_at.desc())

    properties = pq.paginate(page=page, per_page=12, error_out=False)
    return render_template('main/search.html', properties=properties,
        property_types=PropertyType, transaction_types=TransactionType,
        current_filters=dict(q=query, transaction=transaction, type=property_type,
            min_price=min_price, max_price=max_price, min_surface=min_surface,
            max_surface=max_surface, rooms=rooms, city=city, sort=sort))

@main_bp.route('/estimation')
def estimation():
    return render_template('main/estimation.html', property_types=PropertyType)

@main_bp.route('/agences')
def agencies():
    from app.models import Agency
    return render_template('main/agencies.html', agencies=Agency.query.all())

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')
