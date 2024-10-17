from flask import Flask, render_template, request, redirect, url_for

import db

app = Flask(__name__)


def validate_name(val):
    return isinstance(val, str) and len(val) > 0 and val.isalpha()


def validate_prep_time(val):
    return isinstance(val, int) and val > 0 and val < 999


def recipe_data_to_dict(recipe_data):
    return {
        key: recipe_data[index]
        for index, key in enumerate(('id',) + tuple(RECIPE_REQUIRED_FIELDS))
    }


def comments_to_dict(comments):
    return [{
        key: comment_data[index]
        for index, key in enumerate(('id', 'recipe_id', 'content', 'created_at'))
    } for comment_data in comments]


RECIPE_REQUIRED_FIELDS = {
    'name': validate_name,
    'category': validate_name,
    'description': validate_name,
    'prep_time': validate_prep_time,
    'instructions': validate_name,
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

        return [
             recipe_data_to_dict(recipe)
             for recipe in db.get_all_recipes(ordering, asc)
        ]
    elif request.method == 'POST':
        for key in RECIPE_REQUIRED_FIELDS:
            if key not in request.json:
                return {'error': f'{key} is required'}, 400
            elif not RECIPE_REQUIRED_FIELDS[key](request.json[key]):
                return {'error': f'{key} is invalid'}, 400

        db.add_recipe(**request.json)
        return {'message': 'Recipe added successfully'}, 201


@app.route(
    '/recipes/<int:recipe_id>/',
    methods=['GET', 'PUT', 'PATCH', 'DELETE'],
)
def recipe(recipe_id):
    recipe_data = db.get_recipe_by_id(recipe_id)
    if not recipe_data:
        return {'error': 'Recipe not found'}, 404

    if request.method == 'GET':
        recipe_dict = recipe_data_to_dict(recipe_data)
        recipe_dict['comments'] = (
            comments_to_dict(db.get_recipe_comments(recipe_id))
        )
        return recipe_dict
    elif request.method == 'PUT':
        for key in RECIPE_REQUIRED_FIELDS:
            if key not in request.json:
                return {'error': f'{key} is required'}, 400
            elif not RECIPE_REQUIRED_FIELDS[key](request.json[key]):
                return {'error': f'{key} is invalid'}, 400

        db.update_recipe(recipe_id, **request.json)
        return {'message': 'Recipe updated successfully'}, 200
    elif request.method == 'PATCH':
        for key in request.json:
            if key not in RECIPE_REQUIRED_FIELDS:
                return {'error': f'{key} is not allowed'}, 400
            elif not RECIPE_REQUIRED_FIELDS[key](request.json[key]):
                return {'error': f'{key} is invalid'}, 400

        receipt_dict = recipe_data_to_dict(recipe_data)
        receipt_dict.update(request.json)
        db.update_recipe(**receipt_dict)
        return {'message': 'Recipe updated successfully'}, 200
    elif request.method == 'DELETE':
        db.delete_recipe(recipe_id)
        return {'message': 'Recipe deleted successfully'}, 204


if __name__ == '__main__':
    app.run(debug=True)
