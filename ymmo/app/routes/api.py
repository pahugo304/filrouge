from flask import Blueprint, jsonify, request
from app.models import Property, PropertyStatus
from app.services.analytics import AnalyticsService

api_bp = Blueprint('api', __name__)

@api_bp.route('/estimation', methods=['POST'])
def estimate():
    data = request.get_json()
    city = data.get('city', '')
    property_type = data.get('property_type', 'Appartement')
    surface = float(data.get('surface', 0))
    rooms = int(data.get('rooms', 1))
    bedrooms = int(data.get('bedrooms', 1))
    if not city or not surface:
        return jsonify({'error': 'Paramètres manquants'}), 400
    return jsonify(AnalyticsService.predict_price(city, property_type, surface, rooms, bedrooms))

@api_bp.route('/trends')
def trends():
    return jsonify(AnalyticsService.get_price_trends(request.args.get('months', 12, type=int)))

@api_bp.route('/market-overview')
def market_overview():
    return jsonify(AnalyticsService.get_market_overview())

@api_bp.route('/top-cities')
def top_cities():
    return jsonify(AnalyticsService.get_top_cities(request.args.get('limit', 10, type=int)))

@api_bp.route('/properties/map')
def properties_map():
    props = Property.query.filter(Property.status==PropertyStatus.DISPONIBLE, Property.latitude.isnot(None)).limit(100).all()
    return jsonify([{'id':p.id,'title':p.title,'city':p.city,'price':p.price,'surface':p.surface,'type':p.property_type.value,'transaction':p.transaction_type.value,'lat':p.latitude,'lng':p.longitude} for p in props])
