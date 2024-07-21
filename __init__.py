from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:khadde@localhost:5432/postgres'

db = SQLAlchemy()

db.init_app(app)

# @app.route('/hello')
# def hello_world():
#     return 'Hello, World!'


# @app.route('/')
# def home():
#     return render_template("index.html")

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', debug=True)

