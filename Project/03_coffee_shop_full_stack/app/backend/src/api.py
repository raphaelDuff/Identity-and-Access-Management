import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, abort, redirect, url_for
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS, cross_origin

from .database.models import *
from .auth.auth import requires_auth, AuthError


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
    load_dotenv()
    # app.secret_key = os.getenv("APP_SECRET_KEY")

    CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    # Initialize the app with the extension
    app.config.from_object("src.database.config")
    print("app config: ", app.config)

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

    # ROUTES
    @app.route("/drinks", methods=["GET"])
    def get_drinks():
        stmt_select_all_drinks = select(Drink).order_by(Drink.id)
        drinks = db.session.scalars(stmt_select_all_drinks).all()
        list_drinks = [drink.short() for drink in drinks]
        if len(drinks) == 0:
            abort(404)
        return jsonify({"success": True, "drinks": list_drinks})

    @app.route("/drinks-detail", methods=["GET"])
    @requires_auth("get:drinks-detail")
    def get_drinks_detail(token):
        stmt_select_all_drinks = select(Drink).order_by(Drink.id)
        drinks = db.session.scalars(stmt_select_all_drinks).all()
        list_drinks = [drink.long() for drink in drinks]
        if len(drinks) == 0:
            abort(404)
        return jsonify({"success": True, "drinks": list_drinks})

    @app.route("/drinks", methods=["POST"])
    @requires_auth("post:drinks")
    def post_drink(token):
        try:
            data = request.get_json()
            drink_title = data.get("title", None)
            drink_recipe = json.dumps(data.get("recipe", None))

            if drink_title is None or drink_recipe is None:
                abort(400)

            new_drink = Drink(title=drink_title, recipe=drink_recipe)
            db.session.add(new_drink)
            db.session.commit()
            # return redirect(
            #     url_for(
            #         "get_drinks",
            #         result=jsonify({"success": True, "drinks": new_drink.long()}),
            #     )
            # )
            return (
                jsonify({"success": True, "drinks": new_drink.long()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/drinks/<int:id>", methods=["PATCH"])
    @requires_auth("patch:drinks")
    def update_drink(token, id):
        try:
            stmt_drink_by_id = select(Drink).where(Drink.id == id)
            selected_drink = db.session.scalars(stmt_drink_by_id).one_or_none()
            if selected_drink is None:
                abort(404)

            data = request.get_json()
            if not data:
                abort(400)
            selected_drink.title = data.get("title", selected_drink.title)
            selected_drink.recipe = json.dumps(
                data.get("recipe", selected_drink.recipe)
            )
            db.session.add(selected_drink)
            db.session.commit()
            return (
                jsonify({"success": True, "drinks": selected_drink.long()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/drinks/<int:id>", methods=["DELETE"])
    @requires_auth("delete:drinks")
    def delete_drink(token, id):
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

    @app.errorhandler(AuthError)
    def handle_auth_error(e):
        response = jsonify(e.error)
        response.status_code = e.status_code
        return response

    return app


# Error Handling


"""
@TODO implement error handler for AuthError
    error handler should conform to general task above
"""

if __name__ == "__main__":
    create_app()
