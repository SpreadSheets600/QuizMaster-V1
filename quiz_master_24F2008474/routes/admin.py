from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime

from models.database import db
from models.models import Question, Subject, Chapter, Quiz

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    question_count = Question.query.count()
    subject_count = Subject.query.count()
    chapter_count = Chapter.query.count()
    quiz_count = Quiz.query.count()

    return render_template(
        "admin_dashboard.html",
        subject_count=subject_count,
        chapter_count=chapter_count,
        question_count=question_count,
        quiz_count=quiz_count,
    )


# ---------------------------------------------------------------------------- #
#                                SUBJECT ROUTES                                #
# ---------------------------------------------------------------------------- #


@admin_bp.route("/subjects")
@login_required
def subjects_list():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    subjects = Subject.query.all()
    return render_template("admin/subject_list.html", subjects=subjects)


@admin_bp.route("/subjects/new", methods=["GET", "POST"])
@login_required
def subject_new():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("Subject Name Is Required", "error")
            return render_template("admin/subject_form.html")

        exsisting_subject = Subject.query.filter_by(name=name).first()
        if exsisting_subject:
            flash("Subject Already Exists", "error")
            return render_template("admin/subject_form.html")

        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()

        flash("Subject Created Successfully", "success")
        return redirect(url_for("admin.subjects_list"))

    return render_template("admin/subject_form.html")


@admin_bp.route("/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
def subject_edit(subject_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    subject = Subject.query.get_or_404(subject_id)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("Subject Name Is Required", "error")
            return render_template("admin/subject_form.html", subject=subject)

        exsisting_subject = Subject.query.filter_by(name=name).first()
        if exsisting_subject and exsisting_subject.id != subject_id:
            flash("Subject Already Exists", "error")
            return render_template("admin/subject_form.html", subject=subject)

        subject.name = name
        subject.description = description
        db.session.commit()

        flash("Subject Updated Successfully", "success")
        return redirect(url_for("admin.subjects_list"))

    return render_template("admin/subject_form.html", subject=subject)


@admin_bp.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@login_required
def subject_delete(subject_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    subject = Subject.query.get_or_404(subject_id)

    db.session.delete(subject)
    db.session.commit()

    flash("Subject Deleted Successfully", "success")
    return redirect(url_for("admin.subjects_list"))


# ---------------------------------------------------------------------------- #
#                                CHAPTER ROUTES                                #
# ---------------------------------------------------------------------------- #


@admin_bp.route("/subjects/<int:subject_id>/chapters")
@login_required
def chapters_list(subject_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()

    return render_template(
        "admin/chapter_list.html", subject=subject, chapters=chapters
    )


@admin_bp.route("/subjects/<int:subject_id>/chapters/new", methods=["GET", "POST"])
@login_required
def chapter_new(subject_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    subject = Subject.query.get_or_404(subject_id)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("Chapter name is required", "error")
            return render_template("admin/chapter_form.html", subject=subject)

        exsisting_chapter = Chapter.query.filter_by(name=name).first()
        if exsisting_chapter:
            flash("Chapter Already Exists", "error")
            return render_template("admin/chapter_form.html", subject=subject)

        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)

        db.session.add(new_chapter)
        db.session.commit()

        flash("Chapter Created Successfully", "success")
        return redirect(url_for("admin.chapters_list", subject_id=subject_id))

    return render_template("admin/chapter_form.html", subject=subject)


@admin_bp.route("/chapters/<int:chapter_id>/edit", methods=["GET", "POST"])
@login_required
def chapter_edit(chapter_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    chapter = Chapter.query.get_or_404(chapter_id)
    subject = Subject.query.get_or_404(chapter.subject_id)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("Chapter name is required", "error")
            return render_template(
                "admin/chapter_form.html", chapter=chapter, subject=subject
            )

        chapter.name = name
        chapter.description = description
        db.session.commit()

        flash("Chapter Updated Successfully", "success")
        return redirect(url_for("admin.chapters_list", subject_id=subject.id))

    return render_template("admin/chapter_form.html", chapter=chapter, subject=subject)


@admin_bp.route("/chapters/<int:chapter_id>/delete", methods=["POST"])
@login_required
def chapter_delete(chapter_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id

    db.session.delete(chapter)
    db.session.commit()

    flash("Chapter Deleted Successfully", "success")
    return redirect(url_for("admin.chapters_list", subject_id=subject_id))


# ---------------------------------------------------------------------------- #
#                                  QUIZ ROUTES                                 #
# ---------------------------------------------------------------------------- #
@admin_bp.route("/quizzes")
@login_required
def quizzes_list():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    quizzes = Quiz.query.all()

    return render_template("admin/quiz_list.html", quizzes=quizzes)


@admin_bp.route("/quizzes/new", methods=["GET", "POST"])
@login_required
def quiz_new():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        remarks = request.form.get("remarks")
        subject_id = request.form.get("subject_id")
        chapter_id = request.form.get("chapter_id")
        date_of_quiz = request.form.get("date_of_quiz")
        time_duration = request.form.get("time_duration")

        if not date_of_quiz or not time_duration:
            flash("Date And Time Duration Are Required", "error")
            return render_template("admin/quiz_form.html")

        try:
            date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid Date Format", "error")
            return render_template("admin/quiz_form.html")

        if not time_duration or len(time_duration) != 5 or time_duration[2] != ":":
            flash("Time Duration Must Be In HH:MM Format", "error")
            return render_template("admin/quiz_form.html")

        new_quiz = Quiz(subject_id = subject_id, chapter_id = chapter_id, date_of_quiz = date_of_quiz, time_duration = time_duration, remarks = remarks)
        
        db.session.add(new_quiz)
        db.session.commit()



# ---------------------------------------------------------------------------- #
#                                QUESTION ROUTES                               #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#                                  USER ROUTES                                 #
# ---------------------------------------------------------------------------- #
