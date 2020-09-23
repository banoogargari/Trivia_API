import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    
    CORS(app)
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
        return response
    
    
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formated_categories = [category.format() for category in categories]

        if categories is None:
            abort(404)
        
        return jsonify({
            'success': True,
            'categories': formated_categories,
            'total_category': len(categories)
        })

    
    
    
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()
        formated_categories = [category.format() for category in categories]

        if current_questions is None:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': formated_categories
        })

    
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)
        
        question.delete()

        return jsonify({
            'success': True,
            'deleted': question_id
        })
    
    
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_jason()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
                'total_question': len(question)
            })
        except:
            abort(422)
    
    
    @app.route('/questions/search', methods=['POST'])
    def search_term():
        body = request.get_jason()

        search_term = body.get('searchTerm', None)
        if search_term is None:
            abort(404)
        search_term:
            searchResults = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        
        formated_questions = [question.format() for question in searchResults]
        return jsonify({
            'success': True,
            'questions': formated_questions,
            'totalQuestion': len(searchResults)
        })
    
    
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def show_question_category(category_id):
        questionCategory = Question.query.filter(Question.category == category_id).one_or_none()

        if questionCategory is None:
            abort(404)
        
        formated_questions = [question.format() for question in questionCategory]
        
        return jsonify({
            'success': True,
            'questions': formated_questions,
            'total_questions': len(questionCategory),
            'current_category': category_id

        })
    
    

    @app.route('/quizes', methods=['POST'])
    def take_quizes():
        selection = Question.query.order_by(Question.id).all()
        body = request.get_jason()
        category_id = body.get('quiz_category')['id']
        previous_question = body.get('previous_question')
        
        if category_id == 0:
            selection = Question.query.order_by(Question.id).all()
        else:
            selection = Question.query.filter(Question.category == category_id).all()
        
        selected_questions = []

        for question in selection:
            if question not in previous_question:
                selected_questions.append(question.format())

        resulted_question =  random.choice(resulted_question)

        return jsonify({
            'success': True,
            'questions': resulted_question
        })
    
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

return app