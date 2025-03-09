from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
)
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import desc, func


from models.database import db
from models.models import Subject, Chapter, Quiz, Question, Score, QuizAttempt, User

user_bp = Blueprint("user", __name__)


@user_bp.route("/dashboard")
@login_required
def user_dashboard():
    if not current_user.is_authenticated or current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    subjects = Subject.query.all()

    recent_attempts = (
        Score.query.filter_by(user_id=current_user.id)
        .order_by(desc(Score.timestamp_of_attempt))
        .limit(5)
        .all()
    )

    return render_template(
        "user_dashboard.html", subjects=subjects, recent_attempts=recent_attempts
    )


@user_bp.route("/subjects/<int:subject_id>/quizzes")
@login_required
def subject_quizzes(subject_id):
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()

    quizzes = Quiz.query.filter_by(subject_id=subject_id).all()

    user_attempts = {}
    for quiz in quizzes:
        attempt = (
            Score.query.filter_by(quiz_id=quiz.id, user_id=current_user.id)
            .order_by(desc(Score.timestamp_of_attempt))
            .first()
        )

        if attempt:
            user_attempts[quiz.id] = attempt

    return render_template(
        "user/quizzes.html",
        subject=subject,
        chapters=chapters,
        quizzes=quizzes,
        user_attempts=user_attempts,
    )


@user_bp.route("/quiz/<int:quiz_id>/start")
@login_required
def quiz_start(quiz_id):
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    quiz = Quiz.query.get_or_404(quiz_id)

    # Check if user has already attempted this quiz
    existing_attempt = Score.query.filter_by(
        quiz_id=quiz_id, user_id=current_user.id
    ).first()

    if existing_attempt:
        flash(
            "You have already attempted this quiz. Would you like to try again?",
            "warning",
        )
        return render_template(
            "user/quiz_retake.html", quiz=quiz, previous_score=existing_attempt
        )

    question_count = Question.query.filter_by(quiz_id=quiz_id).count()
    if question_count == 0:
        flash("This quiz has no questions yet.", "error")
        return redirect(url_for("user.subject_quizzes", subject_id=quiz.subject_id))

    return render_template(
        "user/quiz_start.html", quiz=quiz, question_count=question_count
    )


@user_bp.route("/quiz/<int:quiz_id>/take", methods=["GET", "POST"])
@login_required
def quiz_take(quiz_id):
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    quiz = Quiz.query.get_or_404(quiz_id)

    # Check if this is a deliberate retake attempt (from the retake button)
    is_retake = request.args.get("retake", "0") == "1"

    existing_attempt = Score.query.filter_by(
        quiz_id=quiz_id, user_id=current_user.id
    ).first()

    # Only redirect to retake page if it's not already a retake request
    if existing_attempt and request.method == "GET" and not is_retake:
        flash(
            "You have already attempted this quiz. Would you like to try again?",
            "warning",
        )
        return redirect(url_for("user.quiz_start", quiz_id=quiz_id))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == "POST":
        end_time = datetime.now()
        start_time = datetime.fromisoformat(session.get("quiz_start_time"))

        time_taken = (end_time - start_time).total_seconds() // 60

        user_answers = {}
        for question in questions:
            answer_key = f"question_{question.id}"
            if answer_key in request.form:
                user_answers[question.id] = int(request.form[answer_key])

        total_correct = 0
        total_wrong = 0
        total_score = 0
        total_skipped = 0

        for question in questions:
            if question.id in user_answers:
                user_answer = user_answers[question.id]
                if user_answer == question.correct_options:
                    total_correct += 1
                    total_score += question.marks
                else:
                    total_wrong += 1
                    total_score -= question.negative_marks
            else:
                total_skipped += 1

        if total_score < 0:
            total_score = 0

        new_score = Score(
            quiz_id=quiz_id,
            user_id=current_user.id,
            total_score=total_score,
            correct_answers=total_correct,
            wrong_answers=total_wrong,
            skipped=total_skipped,
        )
        db.session.add(new_score)

        for question_id, answer in user_answers.items():
            quiz_attempt = QuizAttempt(
                quiz_id=quiz_id,
                user_id=current_user.id,
                question_id=question_id,
                answers=str(answer),
                start_time=start_time,
                end_time=end_time,
            )
            db.session.add(quiz_attempt)

        db.session.commit()

        return redirect(url_for("user.quiz_results", score_id=new_score.id))

    session["quiz_start_time"] = datetime.now().isoformat()

    hours, minutes = map(int, quiz.time_duration.split(":"))
    duration_minutes = hours * 60 + minutes

    return render_template(
        "user/quiz_take.html",
        quiz=quiz,
        questions=questions,
        duration_minutes=duration_minutes,
    )


@user_bp.route("/quiz/<int:score_id>/result")
@login_required
def quiz_results(score_id):
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    score = Score.query.filter_by(id=score_id, user_id=current_user.id).first_or_404()

    quiz = Quiz.query.get_or_404(score.quiz_id)

    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    attempts = QuizAttempt.query.filter_by(
        quiz_id=quiz.id, user_id=current_user.id
    ).all()

    user_answers = {}
    for attempt in attempts:
        user_answers[attempt.question_id] = int(attempt.answers)

    return render_template(
        "user/quiz_results.html",
        score=score,
        quiz=quiz,
        questions=questions,
        user_answers=user_answers,
    )


@user_bp.route("/my-scores")
@login_required
def my_scores():
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    scores = (
        Score.query.filter_by(user_id=current_user.id)
        .order_by(desc(Score.timestamp_of_attempt))
        .all()
    )

    subjects = {}
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if quiz:
            subject_id = quiz.subject_id
            if subject_id not in subjects:
                subject = Subject.query.get(subject_id)
                subjects[subject_id] = {"name": subject.name, "quizzes": {}}

            if quiz.id not in subjects[subject_id]["quizzes"]:
                subjects[subject_id]["quizzes"][quiz.id] = {
                    "name": quiz.quiz_name,
                    "attempts": [],
                }

            subjects[subject_id]["quizzes"][quiz.id]["attempts"].append(score)

    return render_template("user/my_scores.html", subjects=subjects)
