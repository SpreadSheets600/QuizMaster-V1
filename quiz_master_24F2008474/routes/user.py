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
from sqlalchemy import desc, func, distinct
from datetime import datetime, timedelta


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

    for attempt in recent_attempts:
        attempt.quiz = Quiz.query.get(attempt.quiz_id)
        if attempt.quiz:
            attempt.subject = Subject.query.get(attempt.quiz.subject_id)
            if attempt.quiz.chapter_id:
                attempt.quiz.chapter = Chapter.query.get(attempt.quiz.chapter_id)

    one_week_ago = datetime.now() - timedelta(days=7)
    upcoming_quizzes = (
        Quiz.query.filter(Quiz.date_of_quiz >= one_week_ago).limit(5).all()
    )

    for quiz in upcoming_quizzes:
        quiz.subject = Subject.query.get(quiz.subject_id)
        if quiz.chapter_id:
            quiz.chapter = Chapter.query.get(quiz.chapter_id)

    subject_performance = (
        db.session.query(
            Subject.id,
            Subject.name,
            func.avg(Score.total_score).label("avg_score"),
            func.count(distinct(Quiz.id)).label("quiz_count"),
        )
        .join(Quiz, Quiz.subject_id == Subject.id)
        .join(Score, (Score.quiz_id == Quiz.id) & (Score.user_id == current_user.id))
        .group_by(Subject.id, Subject.name)
        .all()
    )

    return render_template(
        "user_dashboard.html",
        subjects=subjects,
        recent_attempts=recent_attempts,
        upcoming_quizzes=upcoming_quizzes,
        subject_performance=subject_performance,
        Chapter=Chapter,
        Subject=Subject,
    )


# ---------------------------------------------------------------------------- #
#                                SUBJECT ROUTES                                #
# ---------------------------------------------------------------------------- #


@user_bp.route("/subjects")
@login_required
def subjects_list():
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    subjects = Subject.query.all()
    return render_template("user/subjects_list.html", subjects=subjects)


@user_bp.route("/subjects/<int:subject_id>/quizzes")
@login_required
def subject_quizzes(subject_id):
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()

    chapter_id = request.args.get("chapter_id", type=int)
    search_term = request.args.get("search", "")
    sort_by = request.args.get("sort", "date")

    query = Quiz.query.filter_by(subject_id=subject_id)

    if chapter_id:
        query = query.filter(Quiz.chapter_id == chapter_id)

    if search_term:
        query = query.filter(Quiz.quiz_name.ilike(f"%{search_term}%"))

    if sort_by == "name":
        query = query.order_by(Quiz.quiz_name)
    elif sort_by == "chapter":
        query = query.order_by(Quiz.chapter_id, Quiz.quiz_name)
    else:
        query = query.order_by(desc(Quiz.date_of_quiz))

    quizzes = query.all()

    user_attempts = {}
    for quiz in quizzes:
        attempt = (
            Score.query.filter_by(quiz_id=quiz.id, user_id=current_user.id)
            .order_by(desc(Score.timestamp_of_attempt))
            .first()
        )

        if attempt:
            user_attempts[quiz.id] = attempt
    quiz_stats = {
        "total": len(quizzes),
        "attempted": len(user_attempts),
        "remaining": len(quizzes) - len(user_attempts),
    }

    for chapter in chapters:
        chapter.quiz_count = Quiz.query.filter_by(chapter_id=chapter.id).count()

    return render_template(
        "user/subject_quiz.html",
        subject=subject,
        chapters=chapters,
        quizzes=quizzes,
        user_attempts=user_attempts,
        chapter_id=chapter_id,
        search=search_term,
        sort_by=sort_by,
        quiz_stats=quiz_stats,
    )


# ---------------------------------------------------------------------------- #
#                                 SEARCH ROUTES                                #
# ---------------------------------------------------------------------------- #


@user_bp.route("/search")
@login_required
def search_quizzes():
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    search_term = request.args.get("q", "")

    if not search_term or len(search_term) < 3:
        flash("Please enter at least 3 characters to search", "warning")
        return redirect(url_for("user.user_dashboard"))

    quiz_results = Quiz.query.filter(Quiz.quiz_name.ilike(f"%{search_term}%")).all()
    subject_results = Subject.query.filter(Subject.name.ilike(f"%{search_term}%")).all()
    chapter_results = Chapter.query.filter(Chapter.name.ilike(f"%{search_term}%")).all()

    user_attempts = {}
    for quiz in quiz_results:
        attempt = Score.query.filter_by(
            quiz_id=quiz.id, user_id=current_user.id
        ).first()
        if attempt:
            user_attempts[quiz.id] = attempt

    return render_template(
        "search_results.html",
        search_term=search_term,
        quiz_results=quiz_results,
        subject_results=subject_results,
        chapter_results=chapter_results,
        user_attempts=user_attempts,
        Subject=Subject,
    )


# ---------------------------------------------------------------------------- #
#                                  QUIZ ROUTES                                 #
# ---------------------------------------------------------------------------- #


@user_bp.route("/quizzes")
@login_required
def user_quizzes():
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    subject_id = request.args.get("subject_id", type=int)
    chapter_id = request.args.get("chapter_id", type=int)
    search_term = request.args.get("search", "")
    sort_by = request.args.get("sort", "date")

    query = Quiz.query

    if subject_id:
        query = query.filter(Quiz.subject_id == subject_id)

        if chapter_id:
            query = query.filter(Quiz.chapter_id == chapter_id)

    if search_term:
        query = query.filter(Quiz.quiz_name.ilike(f"%{search_term}%"))

    if sort_by == "name":
        query = query.order_by(Quiz.quiz_name)
    elif sort_by == "subject":
        query = query.order_by(Quiz.subject_id, Quiz.quiz_name)
    else:
        query = query.order_by(desc(Quiz.date_of_quiz))

    quizzes = query.all()

    user_attempts = {}
    for quiz in quizzes:
        attempt = (
            Score.query.filter_by(quiz_id=quiz.id, user_id=current_user.id)
            .order_by(desc(Score.timestamp_of_attempt))
            .first()
        )
        if attempt:
            user_attempts[quiz.id] = attempt

    subjects = Subject.query.all()

    chapters = []
    if subject_id:
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()

    return render_template(
        "user/quiz_list.html",
        quizzes=quizzes,
        user_attempts=user_attempts,
        subjects=subjects,
        chapters=chapters,
        subject_id=subject_id,
        chapter_id=chapter_id,
        search=search_term,
        sort_by=sort_by,
        Subject=Subject,
        Chapter=Chapter,
    )


@user_bp.route("/quiz/<int:quiz_id>/start")
@login_required
def quiz_start(quiz_id):
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    quiz = Quiz.query.get_or_404(quiz_id)

    today = datetime.now().date()
    if quiz.date_of_quiz > today:
        flash(
            f"This quiz will be available on {quiz.date_of_quiz.strftime('%Y-%m-%d')}",
            "warning",
        )
        return redirect(url_for("user.subject_quizzes", subject_id=quiz.subject_id))

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

    subject = Subject.query.get(quiz.subject_id)
    chapter = Chapter.query.get(quiz.chapter_id) if quiz.chapter_id else None

    return render_template(
        "user/quiz_start.html",
        quiz=quiz,
        subject=subject,
        chapter=chapter,
        question_count=question_count,
    )


@user_bp.route("/quiz/<int:quiz_id>/take", methods=["GET", "POST"])
@login_required
def quiz_take(quiz_id):
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    quiz = Quiz.query.get_or_404(quiz_id)

    is_retake = request.args.get("retake", "0") == "1"

    existing_attempt = Score.query.filter_by(
        quiz_id=quiz_id, user_id=current_user.id
    ).first()

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
    subject = Subject.query.get(quiz.subject_id)
    chapter = Chapter.query.get(quiz.chapter_id) if quiz.chapter_id else None

    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    attempts = QuizAttempt.query.filter_by(
        quiz_id=quiz.id, user_id=current_user.id
    ).all()

    question_results = []
    for question in questions:
        user_answer = -1
        for attempt in attempts:
            if attempt.question_id == question.id:
                user_answer = int(attempt.answers)
                break

        result = {
            "question": question,
            "user_answer": user_answer,
            "is_correct": user_answer == question.correct_options,
            "is_skipped": user_answer == -1,
            "correct_option": question.correct_options,
            "options": [
                {"text": question.option1, "index": 0},
                {"text": question.option2, "index": 1},
                {"text": question.option3, "index": 2},
                {"text": question.option4, "index": 3},
            ],
        }
        question_results.append(result)

    import io
    import base64
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)

    categories = ["Correct", "Incorrect", "Skipped"]
    values = [score.correct_answers, score.wrong_answers, score.skipped]
    colors = ["#2dce89", "#f5365c", "#ffd600"]

    bars = ax.bar(categories, values, color=colors)
    ax.set_title("Quiz Performance")
    ax.set_ylabel("Number of Questions")

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.1,
            f"{int(height)}",
            ha="center",
            va="bottom",
        )

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    buf.seek(0)

    performance_chart = base64.b64encode(buf.getbuffer()).decode("ascii")

    total_questions = score.correct_answers + score.wrong_answers + score.skipped
    accuracy = (
        (score.correct_answers / total_questions * 100) if total_questions > 0 else 0
    )

    summary_stats = {
        "total_score": score.total_score,
        "total_questions": total_questions,
        "correct_answers": score.correct_answers,
        "wrong_answers": score.wrong_answers,
        "skipped": score.skipped,
        "accuracy": round(accuracy, 1),
        "date": score.timestamp_of_attempt.strftime("%d %b %Y, %I:%M %p"),
    }

    return render_template(
        "user/quiz_results.html",
        score=score,
        quiz=quiz,
        subject=subject,
        chapter=chapter,
        question_results=question_results,
        summary_stats=summary_stats,
        performance_chart=performance_chart,
    )


# ---------------------------------------------------------------------------- #
#                            PROFILE AND STATISTICS                            #
# ---------------------------------------------------------------------------- #


@user_bp.route("/scores")
@login_required
def scores():
    if current_user.role != "user":
        return redirect(url_for("admin.admin_dashboard"))

    scores = (
        Score.query.filter_by(user_id=current_user.id)
        .order_by(desc(Score.timestamp_of_attempt))
        .all()
    )

    subjects = {}
    overall_stats = {
        "total_score": 0,
        "total_questions": 0,
        "correct_answers": 0,
        "wrong_answers": 0,
        "skipped": 0,
        "attempts": 0,
        "average_score": 0,
        "best_score": 0,
        "recent_scores": [],
        "subject_performance": {},
        "monthly_attempts": {},
        "weekly_day_distribution": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0},
    }

    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if not quiz:
            continue

        subject_id = quiz.subject_id
        if subject_id not in subjects:
            subject = Subject.query.get(subject_id)
            subjects[subject_id] = {
                "name": subject.name,
                "quizzes": {},
                "total_score": 0,
                "attempts": 0,
                "best_score": 0,
                "average_score": 0,
                "correct_answers": 0,
                "wrong_answers": 0,
                "skipped": 0,
            }

            overall_stats["subject_performance"][subject.name] = {
                "attempts": 0,
                "avg_score": 0,
                "best_score": 0,
            }

        if quiz.id not in subjects[subject_id]["quizzes"]:
            subjects[subject_id]["quizzes"][quiz.id] = {
                "name": quiz.quiz_name,
                "attempts": [],
                "best_score": 0,
                "average_score": 0,
            }

        subjects[subject_id]["quizzes"][quiz.id]["attempts"].append(score)

        quiz_attempts = subjects[subject_id]["quizzes"][quiz.id]["attempts"]
        subjects[subject_id]["quizzes"][quiz.id]["average_score"] = sum(
            s.total_score for s in quiz_attempts
        ) / len(quiz_attempts)
        subjects[subject_id]["quizzes"][quiz.id]["best_score"] = max(
            s.total_score for s in quiz_attempts
        )

        subjects[subject_id]["attempts"] += 1
        subjects[subject_id]["total_score"] += score.total_score
        subjects[subject_id]["correct_answers"] += score.correct_answers
        subjects[subject_id]["wrong_answers"] += score.wrong_answers
        subjects[subject_id]["skipped"] += score.skipped

        if score.total_score > subjects[subject_id]["best_score"]:
            subjects[subject_id]["best_score"] = score.total_score

        overall_stats["total_score"] += score.total_score
        overall_stats["correct_answers"] += score.correct_answers
        overall_stats["wrong_answers"] += score.wrong_answers
        overall_stats["skipped"] += score.skipped
        overall_stats["attempts"] += 1

        if score.total_score > overall_stats["best_score"]:
            overall_stats["best_score"] = score.total_score

        if len(overall_stats["recent_scores"]) < 10:
            overall_stats["recent_scores"].append(
                {
                    "quiz_name": quiz.quiz_name,
                    "subject": Subject.query.get(quiz.subject_id).name,
                    "score": score.total_score,
                    "date": score.timestamp_of_attempt.strftime("%d %b"),
                }
            )

        subj_name = Subject.query.get(quiz.subject_id).name
        overall_stats["subject_performance"][subj_name]["attempts"] += 1
        overall_stats["subject_performance"][subj_name]["avg_score"] = (
            overall_stats["subject_performance"][subj_name]["avg_score"]
            * (overall_stats["subject_performance"][subj_name]["attempts"] - 1)
            + score.total_score
        ) / overall_stats["subject_performance"][subj_name]["attempts"]

        if (
            score.total_score
            > overall_stats["subject_performance"][subj_name]["best_score"]
        ):
            overall_stats["subject_performance"][subj_name]["best_score"] = (
                score.total_score
            )

        month_year = score.timestamp_of_attempt.strftime("%b %Y")
        if month_year not in overall_stats["monthly_attempts"]:
            overall_stats["monthly_attempts"][month_year] = 0
        overall_stats["monthly_attempts"][month_year] += 1

        day_of_week = score.timestamp_of_attempt.weekday()
        overall_stats["weekly_day_distribution"][day_of_week] += 1

    if overall_stats["attempts"] > 0:
        overall_stats["average_score"] = (
            overall_stats["total_score"] / overall_stats["attempts"]
        )

    for subject_id in subjects:
        if subjects[subject_id]["attempts"] > 0:
            subjects[subject_id]["average_score"] = (
                subjects[subject_id]["total_score"] / subjects[subject_id]["attempts"]
            )

    overall_stats["total_questions"] = (
        overall_stats["correct_answers"]
        + overall_stats["wrong_answers"]
        + overall_stats["skipped"]
    )

    overall_stats["recent_scores"].reverse()

    import io
    import base64
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    fig1 = Figure(figsize=(8, 4), dpi=100)
    ax1 = fig1.add_subplot(111)

    categories = ["Correct", "Incorrect", "Skipped"]
    values = [
        overall_stats["correct_answers"],
        overall_stats["wrong_answers"],
        overall_stats["skipped"],
    ]
    colors = ["#2dce89", "#f5365c", "#ffd600"]

    bars = ax1.bar(categories, values, color=colors)
    ax1.set_title("Overall Question Performance")
    ax1.set_ylabel("Number of Questions")

    for bar in bars:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.1,
            f"{int(height)}",
            ha="center",
            va="bottom",
        )

    buf1 = io.BytesIO()
    fig1.tight_layout()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)

    overall_stats["question_distribution_chart"] = base64.b64encode(
        buf1.getbuffer()
    ).decode("ascii")

    if overall_stats["subject_performance"]:
        fig2 = Figure(figsize=(10, 5), dpi=100)
        ax2 = fig2.add_subplot(111)

        subject_names = list(overall_stats["subject_performance"].keys())
        avg_scores = [
            overall_stats["subject_performance"][s]["avg_score"] for s in subject_names
        ]
        best_scores = [
            overall_stats["subject_performance"][s]["best_score"] for s in subject_names
        ]

        x = np.arange(len(subject_names))
        width = 0.35

        ax2.bar(
            x - width / 2, avg_scores, width, label="Average Score", color="#5e72e4"
        )
        ax2.bar(x + width / 2, best_scores, width, label="Best Score", color="#2dce89")

        ax2.set_title("Subject Performance")
        ax2.set_ylabel("Score")
        ax2.set_xticks(x)
        ax2.set_xticklabels(subject_names, rotation=45, ha="right")
        ax2.legend()

        fig2.tight_layout()

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="png")
        buf2.seek(0)

        overall_stats["subject_performance_chart"] = base64.b64encode(
            buf2.getbuffer()
        ).decode("ascii")

    if overall_stats["recent_scores"]:
        fig3 = Figure(figsize=(10, 4), dpi=100)
        ax3 = fig3.add_subplot(111)

        scores = [s["score"] for s in overall_stats["recent_scores"]]
        dates = [s["date"] for s in overall_stats["recent_scores"]]

        ax3.plot(dates, scores, marker="o", linestyle="-", color="#5e72e4")
        ax3.set_title("Recent Score Trend")
        ax3.set_ylabel("Score")
        ax3.set_xlabel("Date")
        ax3.set_xticklabels(dates, rotation=45, ha="right")

        fig3.tight_layout()

        buf3 = io.BytesIO()
        fig3.savefig(buf3, format="png")
        buf3.seek(0)

        overall_stats["score_trend_chart"] = base64.b64encode(buf3.getbuffer()).decode(
            "ascii"
        )

    if overall_stats["monthly_attempts"]:
        fig4 = Figure(figsize=(10, 4), dpi=100)
        ax4 = fig4.add_subplot(111)

        months = list(overall_stats["monthly_attempts"].keys())
        attempts = list(overall_stats["monthly_attempts"].values())

        ax4.bar(months, attempts, color="#5e72e4")
        ax4.set_title("Monthly Quiz Activity")
        ax4.set_ylabel("Number of Attempts")
        ax4.set_xlabel("Month")
        ax4.set_xticklabels(months, rotation=45, ha="right")

        fig4.tight_layout()

        buf4 = io.BytesIO()
        fig4.savefig(buf4, format="png")
        buf4.seek(0)

        overall_stats["monthly_activity_chart"] = base64.b64encode(
            buf4.getbuffer()
        ).decode("ascii")

    fig5 = Figure(figsize=(8, 4), dpi=100)

    fig5.tight_layout()

    buf5 = io.BytesIO()
    fig5.savefig(buf5, format="png")
    buf5.seek(0)

    return render_template(
        "user/scores.html", subjects=subjects, overall_stats=overall_stats
    )


# ---------------------------------------------------------------------------- #
#                                  API ROUTES                                  #
# ---------------------------------------------------------------------------- #


@user_bp.route("/api")
def api_docs():
    return render_template("api.html")
