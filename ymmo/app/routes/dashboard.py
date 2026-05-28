from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Property, Favorite, Appointment, UserRole

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    if current_user.is_agent:
        props = Property.query.filter_by(agent_id=current_user.id).order_by(Property.created_at.desc()).all()
        appointments = Appointment.query.filter_by(agent_id=current_user.id).order_by(Appointment.scheduled_at.desc()).limit(10).all()
        return render_template('dashboard/agent.html', properties=props, appointments=appointments)
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    appointments = Appointment.query.filter_by(client_id=current_user.id).order_by(Appointment.scheduled_at.desc()).all()
    return render_template('dashboard/client.html', favorites=favorites, appointments=appointments)
