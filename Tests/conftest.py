import os
import sys
import tempfile

import pytest

# os.path.join(sys.path[0], '..') points to the parent path.
# sys.path.append adds the path to the searching space.
sys.path.append(os.path.join(sys.path[0], '..'))

import db
from app import app

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

application = app
# def create_test_app():
#     # Creates and configure a test_app then returns it.
#     app = Flask(__name__, instance_relative_config=True)
#
#     # Load the instance config, if it exists.
#     app.config.from_pyfile('config.py', silent=True)
#
#     # Ensure the instance folder exists.
#     try:
#         os.makedirs(app.instance_path)
#     except OSError:
#         pass
#
#     # Load environment variables.
#     dotenv_path = join(dirname(__file__), '.env')
#     load_dotenv(dotenv_path)
#     # Database setup
#     # Run "flask init-db" to initialise db.
#     # Remember to change directory and activate venv.
#     db.init_app(app)
#
#     return app


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = application

    app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
    })
    with app.app_context():
        db.init_db()
        db.get_db().executescript(_data_sql)
    # other setup can go here

    yield app

    # clean up / reset resources here

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
