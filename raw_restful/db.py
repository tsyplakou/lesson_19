from constants import DB_CONNECTION
from db_connect import DBConnect

db = DBConnect(**DB_CONNECTION)


def _add_cursor_wrapper(func):
    def wrapper(*args, **kwargs):
        with db.get_connection().cursor() as __cur:
            return func(__cur, *args, **kwargs)

    return wrapper


@_add_cursor_wrapper
def get_all_recipes(__cur, ordering='id', asc=True):
    __cur.execute(
        'SELECT id, name, category, description, prep_time, instructions, '
        'image_url '
        'FROM recipes ORDER BY {} {}'.format(ordering, 'ASC' if asc else 'DESC')
    )
    return __cur.fetchall()


@_add_cursor_wrapper
def add_recipe(__cur, name, category, description, prep_time, instructions):
    __cur.execute(
        'INSERT INTO recipes '
        '(name, category, description, prep_time, instructions) '
        'VALUES (%s, %s, %s, %s, %s)',
        (name, category, description, prep_time, instructions)
    )


@_add_cursor_wrapper
def get_recipes_by_partial_name(__cur, query):
    __cur.execute(
        '''
        SELECT * FROM recipes
        WHERE name ILIKE %s OR category ILIKE %s
        ''',
        (f'%{query}%', f'%{query}%')
    )
    return __cur.fetchall()


@_add_cursor_wrapper
def get_recipe_by_id(__cur, recipe_id):
    __cur.execute(
        'SELECT id, name, category, description, prep_time, instructions, '
        'image_url '
        'FROM recipes WHERE id = %s',
        (recipe_id,)
    )
    return __cur.fetchone()


@_add_cursor_wrapper
def get_recipe_comments(__cur, recipe_id):
    __cur.execute(
        'SELECT id, recipe_id, content, created_at FROM comments '
        'WHERE recipe_id = %s',
        (recipe_id,)
    )
    return __cur.fetchall()


@_add_cursor_wrapper
def delete_recipe(__cur, id):
    __cur.execute('DELETE FROM recipes WHERE id = %s', (id,))


@_add_cursor_wrapper
def update_recipe(__cur, id, name, category, description, prep_time, instructions):
    __cur.execute(
        'UPDATE recipes SET '
        'name=%s, category=%s, description=%s, prep_time=%s, instructions=%s '
        'WHERE id = %s',
        (name, category, description, prep_time, instructions, id)
    )
