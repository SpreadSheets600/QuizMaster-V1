from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied", "error")
        return redirect(url_for("auth.login"))

    return render_template("admin_dashboard.html")
