from models.models import Subject, Chapter, Quiz, Score, Question
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request
from models.database import db

api_bp = Blueprint("api", __name__)


@api_bp.route("/subjects", methods=["GET"])
def get_subjects():
    subjects = Subject.query.all()
    return jsonify(
        {
            "success": True,
            "subjects": [
                {
                    "id": subject.id,
                    "name": subject.name,
                    "description": subject.description,
                }
                for subject in subjects
            ],
        }
    )


@api_bp.route("/subjects/<int:subject_id>", methods=["GET"])
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify(
        {
            "success": True,
            "subject": {
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
            },
        }
    )


@api_bp.route("/chapters", methods=["GET"])
def get_chapters():
    subject_id = request.args.get("subject_id", type=int)

    if subject_id:
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    else:
        chapters = Chapter.query.all()

    return jsonify(
        {
            "success": True,
            "chapters": [
                {
                    "id": chapter.id,
                    "name": chapter.name,
                    "description": chapter.description,
                    "subject_id": chapter.subject_id,
                }
                for chapter in chapters
            ],
        }
    )


@api_bp.route("/quizzes", methods=["GET"])
def get_quizzes():
    subject_id = request.args.get("subject_id", type=int)
    chapter_id = request.args.get("chapter_id", type=int)

    query = Quiz.query

    if subject_id:
        query = query.filter(Quiz.subject_id == subject_id)

    if chapter_id:
        query = query.filter(Quiz.chapter_id == chapter_id)

    quizzes = query.all()

    return jsonify(
        {
            "success": True,
            "quizzes": [
                {
                    "id": quiz.id,
                    "name": quiz.quiz_name,
                    "subject_id": quiz.subject_id,
                    "chapter_id": quiz.chapter_id,
                    "date": quiz.date_of_quiz.strftime("%Y-%m-%d"),
                    "time_duration": quiz.time_duration,
                    "description": quiz.remarks,
                }
                for quiz in quizzes
            ],
        }
    )


@api_bp.route("/scores", methods=["GET"])
def get_scores():
    quiz_id = request.args.get("quiz_id", type=int)
    user_id = request.args.get("user_id", type=int)

    query = Score.query

    if current_user.role != "admin":
        query = query.filter(Score.user_id == current_user.id)
    elif user_id:  # Admin can filter by user_id
        query = query.filter(Score.user_id == user_id)

    if quiz_id:
        query = query.filter(Score.quiz_id == quiz_id)

    scores = query.all()

    return jsonify(
        {
            "success": True,
            "scores": [
                {
                    "id": score.id,
                    "user_id": score.user_id,
                    "quiz_id": score.quiz_id,
                    "correct_answers": score.correct_answers,
                    "wrong_answers": score.wrong_answers,
                    "skipped": score.skipped,
                    "total_score": score.total_score,
                    "timestamp": score.timestamp_of_attempt.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
                for score in scores
            ],
        }
    )
