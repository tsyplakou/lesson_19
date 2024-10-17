from flask import Flask, render_template, request, redirect, url_for

from models import Recipe, Comment
from db import get_session
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)


def validate_name(val):
    return isinstance(val, str) and len(val) > 0 and val.isalpha()


def validate_string(val):
    return isinstance(val, str) and len(val) > 0


def validate_prep_time(val):
    return isinstance(val, int) and 0 < val < 999


def recipe_to_dict(recipe):
    return {
        'id': recipe.id,
        'name': recipe.name,
        'category': recipe.category,
        'description': recipe.description,
        'prep_time': recipe.prep_time,
        'instructions': recipe.instructions,
    }


def comments_to_dict(comments):
    return [{
        key: getattr(comment, key)
        for key in ('id', 'recipe_id', 'content', 'created_at')
    } for comment in comments]


RECIPE_REQUIRED_FIELDS = {
    'name': validate_name,
    'category': validate_string,
    'description': validate_string,
    'prep_time': validate_prep_time,
    'instructions': validate_string,
}
ORDERING_QUERY_KEY = 'ordering'


@app.route('/')
def redirect_to_recipes():
    return redirect(url_for('recipes'))


# /recipes GET/POST ?filtering&sorting
# /recipes/<id> GET/PUT/PATCH/DELETE

@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    if request.method == 'GET':
        # sorting
        ordering = 'id'
        asc = True
        if ORDERING_QUERY_KEY in request.args:
            ordering = request.args[ORDERING_QUERY_KEY]

            if ordering.startswith('-'):
                asc = False
                ordering = ordering[1:]

            if ordering not in RECIPE_REQUIRED_FIELDS:
                ordering = 'id'

        # filtering
        filters = {}
        for key in RECIPE_REQUIRED_FIELDS:
            if key in request.args:
                if not RECIPE_REQUIRED_FIELDS[key](request.args[key]):
                    return {'error': f'{key} is invalid'}, 400
                filters[key] = request.args[key]

        print(f'Ordering: {ordering}, Ascending: {asc}, Filtering: {filters}')

        with get_session() as session:
            recipes = session.query(Recipe).filter_by(
                **filters
            ).order_by(
                getattr(Recipe, ordering)
            ).all()
            recipes_data = [
                 recipe_to_dict(recipe)
                 for recipe in recipes
            ]

        return recipes_data
    elif request.method == 'POST':
        for key in RECIPE_REQUIRED_FIELDS:
            if key not in request.json:
                return {'error': f'{key} is required'}, 400
            elif not RECIPE_REQUIRED_FIELDS[key](request.json[key]):
                return {'error': f'{key} is invalid'}, 400

        with get_session() as session:
            recipe = Recipe(**request.json)
            session.add(recipe)
            session.commit()
            return {'message': 'Recipe added successfully'}, 201


@app.route(
    '/recipes/<int:recipe_id>/',
    methods=['GET', 'PUT', 'PATCH', 'DELETE'],
)
def recipe(recipe_id):
    with get_session() as session:
        try:
            recipe = session.query(Recipe).filter_by(id=recipe_id).one()
        except NoResultFound:
            return {'error': 'Recipe not found'}, 404

        if request.method == 'GET':
            recipe_dict = recipe_to_dict(recipe)

            comments = session.query(Comment).filter_by(recipe_id=recipe_id)
            recipe_dict['comments'] = (
                comments_to_dict(comments)
            )
            return recipe_dict
        elif request.method == 'PUT':
            for key in RECIPE_REQUIRED_FIELDS:
                if key not in request.json:
                    return {'error': f'{key} is required'}, 400
                elif not RECIPE_REQUIRED_FIELDS[key](request.json[key]):
                    return {'error': f'{key} is invalid'}, 400

            for key, value in request.json.items():
                setattr(recipe, key, value)

            return {'message': 'Recipe updated successfully'}, 200
        elif request.method == 'PATCH':
            for key in request.json:
                if key not in RECIPE_REQUIRED_FIELDS:
                    return {'error': f'{key} is not allowed'}, 400
                elif not RECIPE_REQUIRED_FIELDS[key](request.json[key]):
                    return {'error': f'{key} is invalid'}, 400

            for key, value in request.json.items():
                setattr(recipe, key, value)

            return {'message': 'Recipe updated successfully'}, 200
        elif request.method == 'DELETE':
            session.delete(recipe)
            return {'message': 'Recipe deleted successfully'}, 204


if __name__ == '__main__':
    app.run(debug=True)
