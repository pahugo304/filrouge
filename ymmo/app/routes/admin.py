from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Property, Agency, Appointment, UserRole, PropertyStatus
from app.services.analytics import AnalyticsService

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès administrateur requis.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = dict(users=User.query.count(), properties=Property.query.count(), agencies=Agency.query.count(),
        appointments=Appointment.query.count(), available=Property.query.filter_by(status=PropertyStatus.DISPONIBLE).count(),
        sold=Property.query.filter_by(status=PropertyStatus.VENDU).count())
    return render_template('admin/dashboard.html', stats=stats,
        overview=AnalyticsService.get_market_overview(),
        trends=AnalyticsService.get_price_trends(12),
        monthly=AnalyticsService.get_monthly_revenue(),
        agencies_perf=AnalyticsService.get_sales_by_agency(),
        dist=AnalyticsService.get_property_type_distribution(),
        recent_users=User.query.order_by(User.created_at.desc()).limit(5).all(),
        recent_props=Property.query.order_by(Property.created_at.desc()).limit(5).all())

@admin_bp.route('/utilisateurs')
@login_required
@admin_required
def users():
    return render_template('admin/users.html', users=User.query.order_by(User.created_at.desc()).all())

@admin_bp.route('/utilisateurs/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'Utilisateur {"activé" if user.is_active else "désactivé"}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/biens')
@login_required
@admin_required
def properties():
    return render_template('admin/properties.html', properties=Property.query.order_by(Property.created_at.desc()).all())

@admin_bp.route('/agences')
@login_required
@admin_required
def agencies():
    return render_template('admin/agencies.html', agencies=Agency.query.all())

@admin_bp.route('/agences/ajouter', methods=['GET', 'POST'])
@login_required
@admin_required
def add_agency():
    if request.method == 'POST':
        ag = Agency(name=request.form.get('name'), city=request.form.get('city'),
            address=request.form.get('address'), phone=request.form.get('phone'),
            email=request.form.get('email'), zip_code=request.form.get('zip_code'),
            region=request.form.get('region'))
        db.session.add(ag)
        db.session.commit()
        flash('Agence créée.', 'success')
        return redirect(url_for('admin.agencies'))
    return render_template('admin/agency_form.html')

@admin_bp.route('/analytique')
@login_required
@admin_required
def analytics():
    return render_template('admin/analytics.html',
        trends=AnalyticsService.get_price_trends(12),
        top_cities=AnalyticsService.get_top_cities(10),
        dist=AnalyticsService.get_property_type_distribution(),
        monthly=AnalyticsService.get_monthly_revenue(),
        hot_zones=AnalyticsService.get_hot_zones(),
        agencies_perf=AnalyticsService.get_sales_by_agency())
