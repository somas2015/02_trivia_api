import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, render_template, request, Response, flash
import random
import numpy as np
import random

from models import setup_db, Question, Category


ASKED_QUESTIONS = [0]
QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route('/')
    def hello():
        return('Hello World!')

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories/', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formated_categories = [category.format() for category in categories]

        return jsonify({
           'success': True,
           'categories': formated_categories
        })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of
    the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions/', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        print(selection)
        current_questions = paginate_questions(request, selection)
        print(current_questions)
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
        })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_id(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except:
            abort(422)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at
    the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/add_questions/', methods=['POST'])
    def add_new_questions():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        try:
            question = Question(
                question=new_question, answer=new_answer,
                difficulty=new_difficulty, category=new_category)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except:
            abort(422)

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()

        search_expression = body.get('search', None)
        look_for = '%{}%'.format(search_expression)

        try:
            selection = Question.query.filter(
                Question.question.ilike(look_for)).all()

            if selection is None:
                abort(404)

            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except:
            abort(422)

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/questions/', methods=['POST'])
    def search_question_by_category():
        body = request.get_json()

        category_id = body.get('category', None)

        try:
            selection = Question.query.filter(
                Question.category == category_id).all()

            if selection is None:
                abort(404)

            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except:
            abort(422)

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/questions/play_quiz', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        category_id = body.get('category', None)
        asked_before = False
        try:
            question = Question.query.with_entities(
                Question.id).filter(Question.category == category_id).all()
            random_num = random.randint(0, len(question)-1)
            if question is None:
                abort(404)

            current_question = question[random_num][0]
            question_name = "Asked before"
            previous_question_id = ASKED_QUESTIONS[len(ASKED_QUESTIONS) - 1]

            for id in ASKED_QUESTIONS:
                if id == current_question:
                    asked_before = True
                    previous_question_name = (
                        Question.query.with_entities(Question.question).filter(
                            Question.id == previous_question_id).one_or_none())
                    break

            if asked_before is False:
                ASKED_QUESTIONS.append(current_question)
                question_name = (Question.query.with_entities(
                    Question.question).filter(
                        Question.id == current_question).one_or_none())
                previous_question_name = (Question.query.with_entities(
                        Question.question).filter(
                            Question.id == previous_question_id).one_or_none())
                if(previous_question_name is None):
                    previous_question_name = "Not asked yet"

            else:
                question_name = "Asked Before"

            return jsonify({
                'success': True,
                'question': question_name,
                'previous_question': previous_question_name
            })

        except:
            abort(422)

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

    return app
