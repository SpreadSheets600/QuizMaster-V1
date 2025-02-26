from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

user_bp = Blueprint("user", __name__)


@user_bp.route("/dashboard")
@login_required
def user_dashboard():
    if not current_user.is_authenticated or current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("user_dashboard.html")
