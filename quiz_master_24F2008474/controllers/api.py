from models.models import Subject, Chapter, Quiz, Score
from flask import Blueprint, request, render_template
from flask_login import current_user, login_required
from flask_restful import Api, Resource, reqparse
from models.database import db


api_bp = Blueprint('api', __name__)
api = Api(api_bp)


@api_bp.route('/docs')
def api_docs():
    return render_template('api.html')


subject_parser = reqparse.RequestParser()
subject_parser.add_argument('name', type=str, required=True, help='Name is required')
subject_parser.add_argument('description', type=str)


class SubjectList(Resource):
    def get(self):
        try:
            subjects = Subject.query.all()
            return {
                'success': True,
                'subjects': [
                    {
                        'id': subject.id,
                        'name': subject.name,
                        'description': subject.description,
                    }
                    for subject in subjects
                ],
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

    @login_required
    def post(self):
        if current_user.role != 'admin':
            return {'success': False, 'message': 'Admin privileges required'}, 403

        try:
            args = subject_parser.parse_args()
            new_subject = Subject(name=args['name'], description=args['description'])
            db.session.add(new_subject)
            db.session.commit()

            return {
                'success': True,
                'subject': {
                    'id': new_subject.id,
                    'name': new_subject.name,
                    'description': new_subject.description,
                },
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500


class SubjectResource(Resource):
    def get(self, subject_id):
        try:
            subject = Subject.query.get_or_404(subject_id)
            return {
                'success': True,
                'subject': {
                    'id': subject.id,
                    'name': subject.name,
                    'description': subject.description,
                },
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

    @login_required
    def put(self, subject_id):
        if current_user.role != 'admin':
            return {'success': False, 'message': 'Admin privileges required'}, 403

        try:
            subject = Subject.query.get_or_404(subject_id)
            args = subject_parser.parse_args()

            subject.name = args['name']
            subject.description = args['description']

            db.session.commit()

            return {
                'success': True,
                'subject': {
                    'id': subject.id,
                    'name': subject.name,
                    'description': subject.description,
                },
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500


class ChapterList(Resource):
    def get(self):
        try:
            chapters = Chapter.query.all()
            return {
                'success': True,
                'chapters': [
                    {
                        'id': chapter.id,
                        'name': chapter.name,
                        'subject_id': chapter.subject_id,
                    }
                    for chapter in chapters
                ],
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

    @login_required
    def put(self, chapter_id):
        if current_user.role != 'admin':
            return {'success': False, 'message': 'Admin privileges required'}, 403

        try:
            chapter = Chapter.query.get_or_404(chapter_id)
            args = subject_parser.parse_args()

            chapter.name = args['name']
            chapter.description = args['description']

            db.session.commit()

            return {
                'success': True,
                'chapter': {
                    'id': chapter.id,
                    'name': chapter.name,
                    'description': chapter.description,
                },
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500


class QuizList(Resource):
    def get(self):
        try:
            subject_id = request.args.get('subject_id', type=int)
            chapter_id = request.args.get('chapter_id', type=int)

            query = Quiz.query

            if subject_id:
                query = query.filter(Quiz.subject_id == subject_id)

            if chapter_id:
                query = query.filter(Quiz.chapter_id == chapter_id)

            quizzes = query.all()

            return {
                'success': True,
                'quizzes': [
                    {
                        'id': quiz.id,
                        'name': quiz.quiz_name,
                        'subject_id': quiz.subject_id,
                        'chapter_id': quiz.chapter_id,
                        'date': quiz.date_of_quiz.strftime('%Y-%m-%d'),
                        'time_duration': quiz.time_duration,
                        'description': quiz.remarks,
                    }
                    for quiz in quizzes
                ],
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

    @login_required
    def put(self, quiz_id):
        if current_user.role != 'admin':
            return {'success': False, 'message': 'Admin privileges required'}, 403

        try:
            quiz = Quiz.query.get_or_404(quiz_id)
            args = subject_parser.parse_args()

            quiz.quiz_name = args['name']
            quiz.date_of_quiz = args['date']
            quiz.time_duration = args['time_duration']
            quiz.remarks = args['description']

            db.session.commit()

            return {
                'success': True,
                'quiz': {
                    'id': quiz.id,
                    'name': quiz.quiz_name,
                    'subject_id': quiz.subject_id,
                    'chapter_id': quiz.chapter_id,
                    'date': quiz.date_of_quiz.strftime('%Y-%m-%d'),
                    'time_duration': quiz.time_duration,
                    'description': quiz.remarks,
                },
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500


class ScoreList(Resource):
    def get(self):
        try:
            scores = Score.query.all()
            return {
                'success': True,
                'scores': [
                    {
                        'id': score.id,
                        'user_id': score.user_id,
                        'quiz_id': score.quiz_id,
                        'score': score.score,
                    }
                    for score in scores
                ],
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500


api.add_resource(SubjectList, '/subjects')
api.add_resource(SubjectResource, '/subjects/<int:subject_id>')
api.add_resource(ChapterList, '/chapters')
api.add_resource(QuizList, '/quizzes')
api.add_resource(ScoreList, '/scores')
