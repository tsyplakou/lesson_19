from flask import Flask, render_template, request


app = Flask(__name__)


@app.route('/')
def index():
    return render_template(
        'small_index.html',
        text='This is a small template.',
    )


if __name__ == '__main__':
    app.run(debug=True)
