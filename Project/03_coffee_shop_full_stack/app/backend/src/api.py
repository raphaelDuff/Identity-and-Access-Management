import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS

from .models import *


# Enable debug mode.
DEBUG = True
QUESTIONS_PER_PAGE = 10


# def paginate_drinks(request, selection, page_limit_number=QUESTIONS_PER_PAGE):
#     page = request.args.get("page", 1, type=int)
#     start = (page - 1) * page_limit_number
#     end = start + page_limit_number
#     drinks = [drink.short() for drink in selection]
#     current_drinks = drinks[start:end]
#     return current_drinks


def create_app(test_config=None, db=db):
    app = Flask(__name__)
    print("OOBA")
    # Initialize the app with the extension
    app.config.from_object("src.config")

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        # drink_recipe = '[{"name": "water", "color": "blue", "parts": 1}]'
        # drink = Drink(title="water", recipe=drink_recipe)
        # drink2_recipe = '[{"name": "fanta", "color": "orange", "parts": 1}]'
        # drink2 = Drink(title="fanta", recipe=drink2_recipe)
        # drink3_recipe = '[{"name": "coca", "color": "black", "parts": 1}]'
        # drink3 = Drink(title="coca", recipe=drink3_recipe)
        # db.session.add(drink)
        # db.session.add(drink2)
        # db.session.add(drink3)
        # db.session.commit()

    CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTION"
        )
        return response

    # ROUTES
    """
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    """

    @app.route("/drinks", methods=["GET"])
    def get_drinks():
        stmt_select_all_drinks = select(Drink).order_by(Drink.id)
        drinks = db.session.scalars(stmt_select_all_drinks).all()
        list_drinks = [drink.short() for drink in drinks]
        if len(drinks) == 0:
            abort(404)
        return jsonify({"success": True, "drinks": list_drinks})

    """
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    """

    @app.route("/drinks-detail", methods=["GET"])
    def get_drinks_detail():
        stmt_select_all_drinks = select(Drink).order_by(Drink.id)
        drinks = db.session.scalars(stmt_select_all_drinks).all()
        list_drinks = [drink.long() for drink in drinks]
        if len(drinks) == 0:
            abort(404)
        return jsonify({"success": True, "drinks": list_drinks})

    """
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    """

    """
    @TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    """

    """
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    """

    @app.route("/drinks/<int:id>", methods=["DELETE"])
    def delete_drink(id):
        try:
            stmt_drink_by_id = select(Drink).where(Drink.id == id)
            selected_drink = db.session.scalars(stmt_drink_by_id).one_or_none()
            if selected_drink is None:
                abort(404)

            db.session.delete(selected_drink)
            db.session.commit()

            return (
                jsonify(
                    {
                        "success": True,
                        "deleted": id,
                    }
                ),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def internal_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "internal server error"}
            ),
            500,
        )

    return app


# Error Handling


"""
@TODO implement error handler for AuthError
    error handler should conform to general task above
"""

if __name__ == "__main__":
    create_app()
