from http import HTTPStatus
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from collections import Mapping

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
@app.route('/')
def index():
    return jsonify({
        'success': True,
        'message':'My Coffee shop'        
    })

'''
@TODO implement endpoint
    GET /drinksa
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': list( map( lambda drink: drink.short(), all_drinks)) # [drink.short() for drink in all_drinks]
    }), HTTPStatus.OK.value



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.all()
    
    try:
        all_drinks = list( map( lambda drink: drink.long(), drinks)) # [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": all_drinks
        }), HTTPStatus.OK.value

    except Exception as err:
        print(err)
        abort(HTTPStatus.UNPROCESSABLE_ENTITY.value)


'''
@TODO implement endpoint
    it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):

    body = request.get_json()

    if('title' and 'recipe' not in body):
        abort(HTTPStatus.UNPROCESSABLE_ENTITY.value)
        
    req_title = body['title']
    recipe_josn = json.dumps(body['recipe'])   
    try:
        recipe_list = json.dumps(['recipe'])
        
        if isinstance(recipe_josn, dict):
            recipe_list.append(recipe_josn)
            drink = Drink(title=req_title, recipe=recipe_list)
        else:
            drink = Drink(title=req_title, recipe=recipe_josn)
            
        drink.insert()
        drinks = Drink.query.all()
        all_drinks = list( map( lambda drink: drink.long(), drinks))
        return jsonify({
            "success": True,
            "drinks": all_drinks

        }), HTTPStatus.OK.value
    except Exception as err:
        print(err)
        abort(HTTPStatus.UNPROCESSABLE_ENTITY.value)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drinks_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drinks_id):
    body = request.get_json()
    req_title = body.get('title', None)
    # req_recipe = body.get('recipe', None)

    drink = Drink.query.filter(Drink.id == drinks_id).one_or_none()
    if drink is None:
        abort(HTTPStatus.NOT_FOUND.value)
    try:
        drink.title = req_title
        drink.update()

        drinks = []
        drinks.append(drink.long())
        return jsonify({
            "success": True,
            "drinks": drinks
        })

    except Exception as err:
        print(err)
        abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drinks_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drinks_id):

    drink = Drink.query.filter(Drink.id == drinks_id).one_or_none()
    if drink is None:
        abort(HTTPStatus.NOT_FOUND.value)
        
    try:
        drink.delete()

        return jsonify({
            "success": True,
            "delete": drinks_id
        })

    except Exception as err:
        print(err)
        abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY.value)
def unprocessable(err):
    return jsonify({
        "success": False,
        "error": HTTPStatus.UNPROCESSABLE_ENTITY.value,
        "message": "unprocessable"
    }), HTTPStatus.UNPROCESSABLE_ENTITY.value


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR.value)
def internal_server_error(err):
    return jsonify({
        "success": False,
        "error": HTTPStatus.INTERNAL_SERVER_ERROR.value,
        "message": "internal server error"
    }), HTTPStatus.INTERNAL_SERVER_ERROR.value


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(HTTPStatus.NOT_FOUND.value)
def resource_not_found(err):
    return jsonify({
        "success": False,
        "error": HTTPStatus.NOT_FOUND.value,
        "message": "resource not found"
    }), HTTPStatus.NOT_FOUND.value


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(HTTPStatus.UNAUTHORIZED.value)
def unauthorized(err):
    return jsonify({
        "success": False,
        "error": HTTPStatus.UNAUTHORIZED.value,
        "message": "unauthorized"
    }), HTTPStatus.UNAUTHORIZED.value


@app.errorhandler(HTTPStatus.FORBIDDEN.value)
def forbidden(err):
    return jsonify({
        "success": False,
        "error": HTTPStatus.FORBIDDEN.value,
        "message": "forbidden"
    }), HTTPStatus.FORBIDDEN.value


@app.errorhandler(AuthError)
def handle_auth_error(err):
    return jsonify({
        "success": False,
        "error": err.status_code,
        "message": err.error
    }), err.status_code