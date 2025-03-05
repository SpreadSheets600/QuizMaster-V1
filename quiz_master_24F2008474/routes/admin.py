from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from models.database import db
from models.models import QuizAttempt, Question, Subject, Chapter, Quiz, User

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
    subject = Subject.query.all()
    chapter = Chapter.query.all()

    return render_template(
        "admin/quiz_list.html", quizzes=quizzes, subjects=subject, chapters=chapter
    )


@admin_bp.route("/quizzes/new", methods=["GET", "POST"])
@login_required
def quiz_new():
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("quiz_name")
        remarks = request.form.get("remarks")
        subject_id = request.form.get("subject_id")
        chapter_id = request.form.get("chapter_id")
        date_of_quiz = request.form.get("date_of_quiz")
        time_duration = request.form.get("time_duration")

        if not name:
            flash("Please Enter The Quiz Name", "error")
            return render_template("admin/quiz_form.html")

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
        return redirect(url_for("admin.quizzes_list", quiz_id=new_quiz.id))

    return render_template(
        "admin/quiz_form.html",
        subjects=Subject.query.all(),
        chapters=Chapter.query.all(),
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
        return redirect(url_for("admin.quizzes_list"), quiz_id=quiz.id)

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
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    return render_template("admin/question_list.html", quiz=quiz, questions=questions)


@admin_bp.route("/quizzes/<int:quiz_id>/questions/new", methods=["GET", "POST"])
@login_required
def question_new(quiz_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")

    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        question_statement = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        correct_option = request.form.get("correct_option")

        marks = request.form.get("marks")
        negetive_marks = request.form.get("negetive_marks")

        question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            marks=marks,
            negetive_marks=negetive_marks,
        )

        db.session.add(question)
        db.session.commit()

        def save_image(file, prefix, quiz_id):
            if file and file.filename != "":
                file_name = secure_filename(file.file_name)
                dot_index = file_name.rfind(".")

                custom_filename = f"{prefix}_{file_name[:dot_index]}"
                file_path = os.path.join(
                    "static", "images", "{quiz_id}", custom_filename
                )
                file.save(file_path)

                return custom_filename
            return ""

        question_image_path = save_image(
            request.files.get("question_image"),
            "Q{quiz_id}-QID{question.id}-question",
            quiz_id="quiz.id",
        )
        option1_image_path = save_image(
            request.files.get("option1_image"),
            "Q{quiz_id}-QID{question.id}-option1",
            quiz_id="quiz.id",
        )
        option2_image_path = save_image(
            request.files.get("option2_image"),
            "Q{quiz_id}-QID{question.id}-option2",
            quiz_id="quiz.id",
        )
        option3_image_path = save_image(
            request.files.get("option3_image"),
            "Q{quiz_id}-QID{question.id}-option3",
            quiz_id="quiz.id",
        )
        option4_image_path = save_image(
            request.files.get("option4_image"),
            "Q{quiz_id}-QID{question.id}-option4",
            quiz_id="quiz.id",
        )

        question.question_image = question_image_path
        question.question_image = option1_image_path
        question.question_image = option2_image_path
        question.question_image = option3_image_path
        question.question_image = option4_image_path

        db.session.commit()

        flash("Question Created Successfully", "success")
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
        negetive_marks = request.form.get("negetive_marks")

        if not (
            question_statement
            and option1
            and option2
            and option3
            and option4
            and correct_option
        ):
            flash("All Fields Are Required", "error")
            return render_template(
                "admin/question_form.html", question=question, quiz=quiz
            )
        try:
            correct_option = int(correct_option)
            if correct_option < 1 or correct_option > 4:
                raise ValueError()
        except ValueError:
            flash("Correct Option Must Be Between 1 And 4", "error")
            return render_template(
                "admin/question_form.html", question=question, quiz=quiz
            )

        question.question_statement = question_statement
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_option = correct_option

        question.marks = marks
        question.negetive_marks = negetive_marks

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

    users = User.query.all()
    return render_template("admin/user_list.html", users=users)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
def user_delete(user_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash("User Deleted Successfully", "success")
    return redirect(url_for("admin.users_list"))


@admin_bp.route("/users/<int:user_id>/promote", methods=["POST"])
def user_promote(user_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)
    user.role = "admin"

    db.session.commit()

    flash("User Promoted To Admin", "success")
    return redirect(url_for("admin.users_list"))


@admin_bp.route("/users/<int:user_id>/demote", methods=["POST"])
def user_demote(user_id):
    if current_user.role != "admin":
        flash("Access Denied", "error")

    user = User.query.get_or_404(user_id)
    user.role = "user"

    db.session.commit()

    flash("User Demoted To User", "success")
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
