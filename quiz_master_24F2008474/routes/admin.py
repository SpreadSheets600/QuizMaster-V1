from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func
from datetime import datetime
import os

from models.database import db
from models.models import QuizAttempt, Question, Subject, Chapter, Quiz, User, Score

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    question = Question.query.all()
    subject = Subject.query.all()
    chapter = Chapter.query.all()
    quiz = Quiz.query.all()
    users = User.query.all()

    return render_template(
        "admin_dashboard.html",
        subject=subject,
        chapter=chapter,
        question=question,
        quiz=quiz,
        users=users,
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


@admin_bp.route("/chapters")
@login_required
def chapters_list():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    subject_id = request.args.get("subject_id", type=int)

    if subject_id:
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        subject = Subject.query.get_or_404(subject_id)
        return render_template(
            "admin/chapter_list.html", chapters=chapters, subject=subject
        )
    else:
        chapters = Chapter.query.all()
        return render_template("admin/chapter_list.html", chapters=chapters)


@admin_bp.route("/chapters/new", methods=["GET", "POST"])
@login_required
def chapter_new():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        subject_id = request.form.get("subject_id")

        if not name:
            flash("Chapter name is required", "error")
            return render_template(
                "admin/chapter_form.html", subjects=Subject.query.all()
            )

        if not subject_id:
            flash("Subject is required", "error")
            return render_template(
                "admin/chapter_form.html", subjects=Subject.query.all()
            )

        exsisting_chapter = Chapter.query.filter_by(name=name).first()
        if exsisting_chapter:
            flash("Chapter Already Exists", "error")
            return render_template(
                "admin/chapter_form.html", subjects=Subject.query.all()
            )

        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)

        db.session.add(new_chapter)
        db.session.commit()

        flash("Chapter Created Successfully", "success")
        return redirect(url_for("admin.chapters_list"))

    return render_template("admin/chapter_form.html", subjects=Subject.query.all())


@admin_bp.route("/chapters/<int:chapter_id>/edit", methods=["GET", "POST"])
@login_required
def chapter_edit(chapter_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        subject_id = request.form.get("subject_id")

        if not name:
            flash("Chapter name is required", "error")
            return render_template(
                "admin/chapter_form.html", chapter=chapter, subjects=Subject.query.all()
            )

        if not subject_id:
            flash("Subject is required", "error")
            return render_template(
                "admin/chapter_form.html", chapter=chapter, subjects=Subject.query.all()
            )

        chapter.name = name
        chapter.description = description
        chapter.subject_id = subject_id
        db.session.commit()

        flash("Chapter Updated Successfully", "success")
        return redirect(url_for("admin.chapters_list"))

    return render_template(
        "admin/chapter_form.html", chapter=chapter, subjects=Subject.query.all()
    )


@admin_bp.route("/chapters/<int:chapter_id>/delete", methods=["POST"])
@login_required
def chapter_delete(chapter_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    chapter = Chapter.query.get_or_404(chapter_id)

    db.session.delete(chapter)
    db.session.commit()

    flash("Chapter Deleted Successfully", "success")
    return redirect(url_for("admin.chapters_list"))


# ---------------------------------------------------------------------------- #
#                                  QUIZ ROUTES                                 #
# ---------------------------------------------------------------------------- #
@admin_bp.route("/quizzes")
@login_required
def quizzes_list():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    subject_id = request.args.get("subject_id", "")
    chapter_id = request.args.get("chapter_id", "")
    quiz_date = request.args.get("quiz_date", "")

    query = Quiz.query

    if subject_id:
        query = query.filter(Quiz.subject_id == subject_id)

    if chapter_id:
        query = query.filter(Quiz.chapter_id == chapter_id)

    if quiz_date:
        try:
            date_obj = datetime.strptime(quiz_date, "%Y-%m-%d").date()
            query = query.filter(func.date(Quiz.date_of_quiz) == date_obj)
        except ValueError:
            pass

    quizzes = query.order_by(Quiz.date_of_quiz.desc()).all()

    subjects = Subject.query.all()

    filtered_chapters = []
    if subject_id:
        filtered_chapters = Chapter.query.filter_by(subject_id=subject_id).all()

    return render_template(
        "admin/quiz_list.html",
        quizzes=quizzes,
        subjects=subjects,
        filtered_chapters=filtered_chapters,
        subject_id=subject_id,
        chapter_id=chapter_id,
        quiz_date=quiz_date,
    )


@admin_bp.route("/quizzes/new", methods=["GET", "POST"])
@login_required
def quiz_new():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    subjects = Subject.query.all()
    selected_subject_id = None
    filtered_chapters = []

    if request.method == "POST":
        if "final_submit" not in request.form:
            selected_subject_id = int(request.form.get("subject_id", 0))
            if selected_subject_id:
                filtered_chapters = Chapter.query.filter_by(
                    subject_id=selected_subject_id
                ).all()

            return render_template(
                "admin/quiz_form.html",
                subjects=subjects,
                selected_subject_id=selected_subject_id,
                filtered_chapters=filtered_chapters,
            )

        name = request.form.get("quiz_name")
        remarks = request.form.get("remarks")
        subject_id = request.form.get("subject_id")
        chapter_id = request.form.get("chapter_id")
        date_of_quiz = request.form.get("date_of_quiz")
        time_duration = request.form.get("time_duration")

        if not name:
            flash("Please Enter The Quiz Name", "error")
            return redirect(url_for("admin.quiz_new"))

        if not date_of_quiz or not time_duration:
            flash("Date And Time Duration Are Required", "error")
            return redirect(url_for("admin.quiz_new"))

        try:
            date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid Date Format", "error")
            return redirect(url_for("admin.quiz_new"))

        if not time_duration or len(time_duration) != 5 or time_duration[2] != ":":
            flash("Time Duration Must Be In HH:MM Format", "error")
            return redirect(url_for("admin.quiz_new"))

        new_quiz = Quiz(
            quiz_name=name,
            subject_id=subject_id,
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks,
        )

        db.session.add(new_quiz)
        db.session.commit()

        flash("Quiz Created Successfully", "success")
        return redirect(url_for("admin.quizzes_list"))

    return render_template(
        "admin/quiz_form.html",
        subjects=subjects,
        selected_subject_id=selected_subject_id,
        filtered_chapters=filtered_chapters,
    )


@admin_bp.route("/quizzes/<int:quiz_id>/edit", methods=["GET", "POST"])
@login_required
def quiz_edit(quiz_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    quiz = Quiz.query.get_or_404(quiz_id)
    chapters = Chapter.query.get_or_404(quiz.chapter_id)
    subjects = Subject.query.get_or_404(quiz.subject_id)

    if request.method == "POST":
        name = request.form.get("quiz_name")
        remarks = request.form.get("remarks")
        date_of_quiz = request.form.get("date_of_quiz")
        time_duration = request.form.get("time_duration")

        if not name:
            flash("Please Enter The Quiz Name", "error")
            return render_template(
                "admin/quiz_form.html", quiz=quiz, subjects=subjects, chapters=chapters
            )

        if not date_of_quiz or not time_duration:
            flash("Date And Time Duration Are Required", "error")
            return render_template(
                "admin/quiz_form.html", quiz=quiz, subjects=subjects, chapters=chapters
            )

        try:
            date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid Date Format", "error")
            return render_template(
                "admin/quiz_form.html", quiz=quiz, subjects=subjects, chapters=chapters
            )

        if not time_duration or len(time_duration) != 5 or time_duration[2] != ":":
            flash("Time Duration Must Be In HH:MM Format", "error")
            return render_template(
                "admin/quiz_form.html", quiz=quiz, subjects=subjects, chapters=chapters
            )

        quiz.quiz_name = name
        quiz.date_of_quiz = date_of_quiz
        quiz.time_duration = time_duration
        quiz.remarks = remarks
        db.session.commit()

        flash("Quiz Updated Successfully", "success")
        return redirect(url_for("admin.quizzes_list"))

    return render_template(
        "admin/quiz_form.html", quiz=quiz, subjects=subjects, chapters=chapters
    )


@admin_bp.route("/quizzes/<int:quiz_id>/delete", methods=["POST"])
@login_required
def quiz_delete(quiz_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")

    quiz = Quiz.query.get_or_404(quiz_id)

    db.session.delete(quiz)
    db.session.commit()

    flash("Quiz Deleted Successfully", "success")
    return redirect(url_for("admin.quizzes_list"))


# ---------------------------------------------------------------------------- #
#                                QUESTION ROUTES                               #
# ---------------------------------------------------------------------------- #


@admin_bp.route("/quizzes/<int:quiz_id>/questions")
@login_required
def questions_list(quiz_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    quiz = Quiz.query.get_or_404(quiz_id)

    search = request.args.get("search", "")
    marks = request.args.get("marks", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = Question.query.filter_by(quiz_id=quiz_id)

    if search:
        query = query.filter(Question.question_statement.ilike(f"%{search}%"))

    if marks:
        try:
            marks = int(marks)
            query = query.filter(Question.marks == marks)
        except ValueError:
            pass

    available_marks = (
        db.session.query(Question.marks)
        .filter(Question.quiz_id == quiz_id)
        .distinct()
        .order_by(Question.marks)
        .all()
    )
    available_marks = [mark[0] for mark in available_marks]

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    questions = pagination.items

    return render_template(
        "admin/question_list.html",
        quiz=quiz,
        questions=questions,
        pagination=pagination,
        search=search,
        marks=marks,
        available_marks=available_marks,
    )


@admin_bp.route("/quizzes/<int:quiz_id>/questions/new", methods=["GET", "POST"])
@login_required
def question_new(quiz_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        question_statement = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        correct_option = request.form.get("correct_option")
        marks = request.form.get("marks")
        negative_marks = request.form.get("negative_marks")

        if not (
            question_statement
            and option1
            and option2
            and option3
            and option4
            and correct_option
        ):
            flash("All fields are required", "error")
            return render_template("admin/question_form.html", quiz=quiz)

        try:
            marks = int(marks)
            negative_marks = int(negative_marks)
            correct_option = int(correct_option)
            if correct_option < 1 or correct_option > 4:
                raise ValueError()
        except ValueError:
            flash("Invalid marks or correct option value", "error")
            return render_template("admin/question_form.html", quiz=quiz)

        question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_options=correct_option,
            marks=marks,
            negative_marks=negative_marks,
        )

        db.session.add(question)
        db.session.commit()

        quiz_dir = os.path.join("static", "images", str(quiz_id))

        os.makedirs(quiz_dir, exist_ok=True)

        def save_image(file_field, prefix):
            if file_field and file_field.filename:
                filename = secure_filename(file_field.filename)
                base, ext = os.path.splitext(filename)
                custom_filename = f"{prefix}_{base}{ext}"
                file_path = os.path.join(quiz_dir, custom_filename)
                file_field.save(file_path)
                return custom_filename
            return None

        question_image = save_image(
            request.files.get("question_image"), f"Q{quiz_id}-QID{question.id}-question"
        )
        option1_image = save_image(
            request.files.get("option1_image"), f"Q{quiz_id}-QID{question.id}-option1"
        )
        option2_image = save_image(
            request.files.get("option2_image"), f"Q{quiz_id}-QID{question.id}-option2"
        )
        option3_image = save_image(
            request.files.get("option3_image"), f"Q{quiz_id}-QID{question.id}-option3"
        )
        option4_image = save_image(
            request.files.get("option4_image"), f"Q{quiz_id}-QID{question.id}-option4"
        )

        if question_image:
            question.question_image = question_image
        if option1_image:
            question.option1_image = option1_image
        if option2_image:
            question.option2_image = option2_image
        if option3_image:
            question.option3_image = option3_image
        if option4_image:
            question.option4_image = option4_image

        db.session.commit()

        flash("Question Added Successfully", "success")
        return redirect(url_for("admin.questions_list", quiz_id=quiz_id))

    return render_template("admin/question_form.html", quiz=quiz)


@admin_bp.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
def question_edit(question_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    question = Question.query.get_or_404(question_id)
    quiz = Quiz.query.get_or_404(question.quiz_id)

    if request.method == "POST":
        question_statement = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        correct_option = request.form.get("correct_option")
        marks = request.form.get("marks")
        negative_marks = request.form.get("negative_marks")

        if not (
            question_statement
            and option1
            and option2
            and option3
            and option4
            and correct_option
        ):
            flash("All fields are required", "error")
            return render_template(
                "admin/question_form.html", question=question, quiz=quiz
            )

        try:
            marks = int(marks)
            negative_marks = int(negative_marks)
            correct_option = int(correct_option)
            if correct_option < 1 or correct_option > 4:
                raise ValueError()
        except ValueError:
            flash("Invalid marks or correct option value", "error")
            return render_template(
                "admin/question_form.html", question=question, quiz=quiz
            )

        question.question_statement = question_statement
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_options = correct_option
        question.marks = marks
        question.negative_marks = negative_marks

        quiz_dir = os.path.join("static", "images", str(quiz.id))

        os.makedirs(quiz_dir, exist_ok=True)

        def save_image(file_field, prefix):
            if file_field and file_field.filename:
                filename = secure_filename(file_field.filename)
                base, ext = os.path.splitext(filename)
                custom_filename = f"{prefix}_{base}{ext}"
                file_path = os.path.join(quiz_dir, custom_filename)
                file_field.save(file_path)
                return custom_filename
            return None

        question_image = save_image(
            request.files.get("question_image"), f"Q{quiz.id}-QID{question.id}-question"
        )
        option1_image = save_image(
            request.files.get("option1_image"), f"Q{quiz.id}-QID{question.id}-option1"
        )
        option2_image = save_image(
            request.files.get("option2_image"), f"Q{quiz.id}-QID{question.id}-option2"
        )
        option3_image = save_image(
            request.files.get("option3_image"), f"Q{quiz.id}-QID{question.id}-option3"
        )
        option4_image = save_image(
            request.files.get("option4_image"), f"Q{quiz.id}-QID{question.id}-option4"
        )

        if question_image:
            question.question_image = question_image
        if option1_image:
            question.option1_image = option1_image
        if option2_image:
            question.option2_image = option2_image
        if option3_image:
            question.option3_image = option3_image
        if option4_image:
            question.option4_image = option4_image

        db.session.commit()

        flash("Question Updated Successfully", "success")
        return redirect(url_for("admin.questions_list", quiz_id=quiz.id))

    return render_template("admin/question_form.html", question=question, quiz=quiz)


@admin_bp.route("/questions/<int:question_id>/delete", methods=["POST"])
@login_required
def question_delete(question_id):
    if current_user.role != "admin":
        flash("Access denied", "error")
        return redirect(url_for("auth.login"))

    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id

    if (
        question.question_image
        or question.option1_image
        or question.option2_image
        or question.option3_image
        or question.option4_image
    ):
        quiz_dir = os.path.join("static", "images", str(quiz_id))

        def delete_image(filename):
            if filename:
                file_path = os.path.join(quiz_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)

        delete_image(question.question_image)
        delete_image(question.option1_image)
        delete_image(question.option2_image)
        delete_image(question.option3_image)
        delete_image(question.option4_image)

    db.session.delete(question)
    db.session.commit()

    flash("Question deleted successfully", "success")
    return redirect(url_for("admin.questions_list", quiz_id=quiz_id))


# ---------------------------------------------------------------------------- #
#                                  USER ROUTES                                 #
# ---------------------------------------------------------------------------- #


@admin_bp.route("/users")
@login_required
def users_list():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "")
    role = request.args.get("role", "")

    query = User.query

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_term))
            | (User.full_name.ilike(search_term))
            | (User.email.ilike(search_term))
        )

    if role:
        query = query.filter(User.role == role)

    users = query.order_by(User.username).all()

    return render_template(
        "admin/user_list.html", users=users, search=search, role=role
    )


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def user_delete(user_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    # Don't allow deleting yourself
    if current_user.id == user_id:
        flash("You cannot delete your own account", "error")
        return redirect(url_for("admin.users_list"))

    user = User.query.get_or_404(user_id)

    Score.query.filter_by(user_id=user_id).delete()
    QuizAttempt.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()

    flash("User Deleted Successfully", "success")
    return redirect(url_for("admin.users_list"))


@admin_bp.route("/users/<int:user_id>/promote", methods=["POST"])
@login_required
def user_promote(user_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash("User is already an admin", "info")
        return redirect(url_for("admin.users_list"))

    user.role = "admin"
    db.session.commit()

    flash(f"User '{user.username}' promoted to Admin", "success")
    return redirect(url_for("admin.users_list"))


@admin_bp.route("/users/<int:user_id>/demote", methods=["POST"])
@login_required
def user_demote(user_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    if current_user.id == user_id:
        flash("You cannot demote yourself", "error")
        return redirect(url_for("admin.users_list"))

    user = User.query.get_or_404(user_id)

    if user.role == "user":
        flash("User is already a regular user", "info")
        return redirect(url_for("admin.users_list"))

    user.role = "user"
    db.session.commit()

    flash(f"User '{user.username}' demoted to regular user", "success")
    return redirect(url_for("admin.users_list"))


# ---------------------------------------------------------------------------- #
#                                  STATISTICS                                  #
# ---------------------------------------------------------------------------- #


@admin_bp.route("/statistics")  # Work With Quiz Attempt
@login_required
def statistics():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        quiz_attempt = QuizAttempt.query.all()

    return render_template("admin/statistics.html", quiz_attempt=quiz_attempt)
