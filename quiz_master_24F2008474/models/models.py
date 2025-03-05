from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

from models.database import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(5), nullable=False, default="user")

    scores = db.relationship("Score", back_populates="user")
    quiz_attempts = db.relationship("QuizAttempt", back_populates="user")


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship("Chapter", back_populates="subject")
    quizzes = db.relationship("Quiz", back_populates="subject")


class Chapter(db.Model):
    __tablename__ = "chapters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )

    subject = db.relationship("Subject", back_populates="chapters")
    quizzes = db.relationship("Quiz", back_populates="chapter")


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(
        db.Integer, db.ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    date_of_quiz = db.Column(db.Date, nullable=False)
    quiz_name = db.Column(db.String(100), nullable=False)
    time_duration = db.Column(db.String(5), nullable=False)  # Format HH:MM
    remarks = db.Column(db.Text)

    chapter = db.relationship("Chapter", back_populates="quizzes")
    subject = db.relationship("Subject", back_populates="quizzes")
    questions = db.relationship("Question", back_populates="quiz")
    scores = db.relationship("Score", back_populates="quiz")
    quiz_attempts = db.relationship("QuizAttempt", back_populates="quiz")


class QuizAttempt(db.Model):
    __tablename__ = "quizzes_attempts"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    start_time = db.Column(db.DateTime, default=func.now())
    end_time = db.Column(db.DateTime)

    question_id = db.Column(
        db.Integer, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    answers = db.Column(db.String(500), nullable=False)
    attempt_date = db.Column(db.DateTime, nullable=False, default=datetime.now())

    user = db.relationship("User", back_populates="quiz_attempts")
    quiz = db.relationship("Quiz", back_populates="quiz_attempts")
    question = db.relationship("Question", back_populates="quiz_attempts")


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.Text, nullable=False)
    option2 = db.Column(db.Text, nullable=False)
    option3 = db.Column(db.Text, nullable=False)
    option4 = db.Column(db.Text, nullable=False)
    correct_options = db.Column(db.Integer, nullable=False)

    marks = db.Column(db.Integer, nullable=False, default=4)
    negative_marks = db.Column(db.Integer, nullable=False, default=1)

    question_image = db.Column(db.String(200), nullable=True)
    option1_image = db.Column(db.String(200), nullable=True)
    option2_image = db.Column(db.String(200), nullable=True)
    option3_image = db.Column(db.String(200), nullable=True)
    option4_image = db.Column(db.String(200), nullable=True)

    quiz = db.relationship("Quiz", back_populates="questions")
    quiz_attempts = db.relationship("QuizAttempt", back_populates="question")


class Score(db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    timestamp_of_attempt = db.Column(db.DateTime, default=func.now())
    total_score = db.Column(db.Integer, nullable=False)

    correct_answers = db.Column(db.Integer, nullable=False)
    wrong_answers = db.Column(db.Integer, nullable=False)
    skipped = db.Column(db.Integer, nullable=False)

    quiz = db.relationship("Quiz", back_populates="scores")
    user = db.relationship("User", back_populates="scores")
