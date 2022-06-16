# Imports
# Python standard libraries
import json
import os

import requests
# Third-party libraries
from flask import Flask, request, url_for, jsonify
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
# Internal imports
from werkzeug.exceptions import abort, HTTPException

import db
import post
from user import User

# App setup
app = Flask(__name__, instance_relative_config=True)
# Used to cryptographically sign cookies. Needs to be kept secret in production.
# Good secret_keys look like this: '54e25d8e90717cb2f61cb3617ca5cf1734d606caceedff64ed4d4b80b4e8af2e'
# app.secret_key = os.environ.get("SECRET_KEY")
# Good to know: https://stackoverflow.com/questions/640938/what-is-the-maximum-size-of-a-web-browsers-cookies-key
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'anhblogwebapp.sqlite'),
)

# load the instance config, if it exists
app.config.from_pyfile('config.py', silent=True)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Configuration
# Make sure variables of the same name are included in the config.py file in the instance folder.
# Logins using Google and Facebook won't be possible otherwise.
GOOGLE_CLIENT_ID = app.config.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = app.config.get('GOOGLE_CLIENT_SECRET', None)
FACEBOOK_CLIENT_ID = app.config.get('FACEBOOK_CLIENT_ID', None)
FACEBOOK_CLIENT_SECRET = app.config.get('FACEBOOK_CLIENT_SECRET', None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
FACEBOOK_DISCOVERY_URL = (
    "https://www.facebook.com/.well-known/openid-configuration"
)

# Access token to be compared with a user-supplied token in order to verify user
access_token_to_compare = ''

# Database setup
# Run "flask init-db" to initialise db
# Remember to change directory and activate venv
db.init_app(app)

# OAuth 2 google and facebook client setup
google_client = WebApplicationClient(GOOGLE_CLIENT_ID)
facebook_client = WebApplicationClient(FACEBOOK_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(email):
    return User.get(email)


def get_provider_cfg(discovery_url):
    return requests.get(discovery_url).json()


@app.route("/facebook", methods=["GET"])
def facebook_login():
    facebook_provider_cfg = get_provider_cfg(FACEBOOK_DISCOVERY_URL)
    facebook_authorization_endpoint = facebook_provider_cfg["authorization_endpoint"]

    facebook_request_uri = facebook_client.prepare_request_uri(
        facebook_authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email"],
    )
    print(facebook_request_uri)
    return jsonify({'URI': facebook_request_uri, 'message': "Access the URI below through a browser to login."}), 200


@app.route("/facebook/callback/loginuser", methods=["POST"])
def facebook_login_user():
    # Attempts to login the user, creating a user object and add it to the database if it is not in the database.
    access_token, email = '', ''
    data = request.get_json()
    # Set values of attributes if they are provided in the request body
    if 'access_token' in data:
        access_token = data['access_token']
    if 'email' in data:
        email = data['body']

    # access_token is required
    if required_field_is_null(data, 'access_token'):
        return abort(400, "access_token cannot be empty. Include an 'access_token'` field in the request body and "
                          "make sure it is not empty.")
    # email is required
    if required_field_is_null(data, 'email'):
        return abort(400, 'email cannot be empty. Include an `email` field in the request body and '
                          'make sure it is not empty.')

    # access_token provided must be the same as the server's saved access_token
    if access_token != access_token_to_compare:
        return abort(400, 'Value of access_token is not correct.')

    # The temporary user object does not have an id. When it is put into the db, it will automatically get a unique one.
    user = User(
        id_='', name='', email=email, phone='', occupation='', is_gg=0, is_fb=1
    )

    # Doesn't exist? Add it to the database.
    if not User.get(email):
        User.create('', email, '', '', 0, 1)
        user_created = True
        print("Adding new user {} to database".format(user.email))
    else:
        user_created = False
        print("User {} already in database".format(user.email))

    # Begin user session by logging the user in
    login_user(user)
    if user_created:
        return jsonify({'message': 'Registration successful. Created an account.'}), 201
    return jsonify({'message': 'Login successful.'}), 200


@app.route("/facebook/callback", methods=["GET"])
def facebook_callback():
    # Needed to modify global copy of access_token
    global access_token_to_compare

    args = request.args
    # If user decides to cancel login.
    if 'error' in args:
        return jsonify({'message': 'User canceled Facebook login. Try again at /facebook'}), 200

    # User proceeds with login.
    code = request.args.get("code")
    print(code)

    # Prepare and send a request to get tokens
    token_url, headers, body = facebook_client.prepare_token_request(
        "https://graph.facebook.com/v14.0/oauth/access_token",
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    print("Token url: {}".format(token_url))
    print("Headers: {}".format(headers))
    print("body: {}".format(body))
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET),
    )
    print("Token response: {}".format(token_response.json()))
    access_token_to_compare = token_response.json()['access_token']
    print("Access_token: {}".format(access_token_to_compare))
    return jsonify({'message': 'Use the code provided in the URI returned as a parameter for the next request.'}), 200


@app.route
@app.route("/google", methods=["GET"])
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_provider_cfg(GOOGLE_DISCOVERY_URL)
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    print(authorization_endpoint)
    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = google_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email"],
    )
    print(request_uri)
    return jsonify({'URI': request_uri, 'message': "Access the URI below through a browser to login."}), 200


@app.route("/google/callback")
def google_callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_provider_cfg(GOOGLE_DISCOVERY_URL)
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    print("Token url: {}".format(token_url))
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    print("Token response: {}".format(token_response.json()))
    # Parse the tokens
    google_client.parse_request_body_response(json.dumps(token_response.json()))
    print(google_client.parse_request_body_response(json.dumps(token_response.json())))
    # Now that you have tokens, let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = google_client.add_token(userinfo_endpoint)
    #print("URI: {}".format(uri))
    #print("headers: {}".format(headers))
    #print("body: {}".format(body))
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    #print(userinfo_response.json())
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google

    # The temporary user object does not have an id. When it is put into the db, it will automatically get a unique one.
    user = User(
        id_='', name='', email=users_email, phone='', occupation='', is_gg=1, is_fb=0
    )

    # Doesn't exist? Add it to the database.
    if not User.get(users_email):
        User.create('', users_email, '', '', 1, 0)
        print("Adding new user {} to database".format(user.email))
    else:
        print("User {} already in database".format(user.email))

    # Begin user session by logging the user in
    login_user(user)

    return jsonify({'message': 'Login sucessful'}), 200


def info_valid(user):
    # Check if the user has updated their info with valid data depending on account type
    if (user.is_gg == 1 & User.google_info_valid(user.email)) | \
            (user.is_fb == 1 & True):
        # True is placeholder for fb's info valid function
        return True
    return False


def valid_info_required(func):
    # Decorator to check if user has provided the correct info and denies them access otherwise.
    def wrapper(*args, **kwargs):
        if info_valid(current_user):
            result = func(*args, **kwargs)
            return result
        else:
            return abort(403, "This account does not have the necessary info to access this page. Update your info by "
                              "sending a POST request to /updateinfo. In the request body provide your name as 'name', "
                              "phone number as 'phone' and occupation as 'occupation' in JSON format. Google users do "
                              "not need to provide a phone number. Facebook users do not need to provide an occupation."
                              "")

    # Renaming the function name to avoid AssertationError
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/", methods=["GET"])
@login_required
@valid_info_required
def index():
    args = request.args
    # If args is not provided, generate some default values
    if 'page' not in args:
        page = 1
    else:
        page = int(args['page'])

    if 'perpage' not in args:
        perpage = 5
    else:
        perpage = int(args['perpage'])

    start_index = (page - 1) * perpage
    end_index = page * perpage

    # Shows all posts by all users
    posts = post.get_homepage()
    final_posts = posts[start_index:end_index]
    output = []
    for post_ in final_posts:
        # Shows first 100 chars of body
        body_to_show = post_[2][:100]
        likes_to_show = format_likes_to_display(post_[0])
        post_data = \
            {'title': post_[1], 'body': body_to_show, 'created': post_[3], 'author_id': post_[4],
             'author_name': post_[5], 'likes': likes_to_show}
        output.append(post_data)

    return jsonify({'posts': output, 'next_page': '{}?page={}&perpage={}'.format(url_for("index"), page + 1, perpage)})


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    # Logs the user out
    logout_user()
    return jsonify({'message': 'Successfully logged out!'}), 200


@app.route("/info", methods=["GET"])
@login_required
def get_info():
    # Shows the info of the authenticated user
    user = User.get(current_user.email)
    if not user:
        return abort(404, 'Uh oh. You don\'t seem to exist in the db? Something must be wrong')
    user_data = {'id': user.id, 'name': user.name, 'email': user.email, 'phone': user.phone,
                 'occupation': user.occupation, 'is_gg': user.is_gg, 'is_fb': user.is_fb}

    return jsonify(user_data)


def required_field_is_null(data, field):
    # Check if required field to process request from the request body is null

    if field not in data:
        return True

    if data[field] == '':
        return True

    return False


@app.route("/updateinfo", methods=["PUT"])
@login_required
def updateinfo():
    # Attempts to update authenticated user's info
    data = request.get_json()
    name, phone, occupation = '', '', ''

    # Set values of attributes if they are provided in the request body
    if 'name' in data:
        name = data['name']
    if 'phone' in data:
        phone = data['phone']
    if 'occupation' in data:
        occupation = data['occupation']

    # name is always required
    if required_field_is_null(data, 'name'):
        # Handles title missing
        return abort(400, "Username cannot be empty. Include a `name` field in the request body")

    # occupation is required for google users
    if (required_field_is_null(data, 'occupation')) & (current_user.is_gg == 1):
        # Handles body missing
        return abort(400, 'User occupation cannot be empty. Include a `occupation` field in the request body"')

    # phone is required for facebook users
    if (required_field_is_null(data, 'phone')) & (current_user.is_fb == 1):
        # Handles body missing
        return abort(400, 'User phone cannot be empty. Include a `phone` field in the request body"')

    current_user.update(current_user.email, name, phone, occupation)

    return jsonify({'message': 'User info successfully updated!'}), 200


def format_likes_to_display(post_id):
    # Get the list of users who like a post and format a string to be displayed

    users = post.get_liked_users(post_id)

    if len(users) == 0:
        return 'No one has liked this post yet.'
    elif len(users) == 1:
        return '{} and {} liked this post.'.format(users[0][1], users[1][1])
    elif len(users) == 2:
        return '{} and {} liked this post.'.format(users[0][1], users[1][1])
    else:
        return '{}, {} and {} other people liked this post.'.format(users[0][1], users[1][1], len(users) - 2)


@app.route('/create', methods=['POST'])
@login_required
@valid_info_required
def create_post():
    title, body = '', ''
    # Attempts to create a new post using the provided info
    data = request.get_json()
    # Set values of attributes if they are provided in the request body
    if 'title' in data:
        title = data['title']
    if 'body' in data:
        body = data['body']

    # Title is required
    if required_field_is_null(data, 'title'):
        return abort(400, "Post title cannot be empty. Include a `title` field in the request body and "
                          "make sure it is not empty.")
    # Body is required
    if required_field_is_null(data, 'body'):
        return abort(400, 'Post body cannot be empty. Include a `body` field in the request body and '
                          'make sure it is not empty.')

    post.insert_post(current_user.id, title, body)

    return jsonify({'message': 'New post created!'}), 201


@app.route('/<user_id>/posts', methods=['GET'])
@login_required
@valid_info_required
def user_posts(user_id):
    # Shows all posts made by a user
    posts = post.get_user_page(user_id)
    output = []

    for post_ in posts:
        # Shows first 100 chars of body
        body_to_show = post_[2][:100]
        likes_to_show = format_likes_to_display(post_[0])
        post_data = \
            {'title': post_[1], 'body': body_to_show, 'created': post_[3],
             'author_id': post_[4], 'author_name': post_[5], 'likes': likes_to_show}
        output.append(post_data)
    return jsonify({'posts': output}), 200


@app.route('/<user_id>/posts/<post_id>', methods=['GET'])
@login_required
@valid_info_required
def post_details(user_id, post_id):
    # Shows details of a post
    user_id = int(user_id)
    post_ = post.get_post_details(post_id)

    # If post does not belong to specified user, returns 404
    if user_id != post_[4]:
        abort(404, 'Resource not found! Either the post does not exist, '
                   'or the post does not belong to the specified user.')
    likes_to_show = format_likes_to_display(post_id)
    post_data = \
        {'title': post_[1], 'body': post_[2], 'created': post_[3],
         'author_id': post_[4], 'author_name': post_[5], 'likes': likes_to_show}

    return jsonify(post_data), 200


@app.route('/<user_id>/posts/<post_id>/like', methods=['POST'])
@login_required
@valid_info_required
def like_post(user_id, post_id):
    # Make the authenticated user like a post
    user_id = int(user_id)
    post_ = post.get_post_details(post_id)

    # If post does not belong to specified user, returns 404
    if user_id != post_[4]:
        abort(404, 'Resource not found! Either the post does not exist, '
                   'or the post does not belong to the specified user.')

    # If user has already liked the post, returns 400
    if post.is_liked(current_user.id, post_id):
        abort(400, 'You have already liked the post!')

    post.insert_like(current_user.id, post_id)
    return jsonify({'message': 'Liked the post!'}), 201


@app.route('/<user_id>/posts/<post_id>/like', methods=['DELETE'])
@login_required
@valid_info_required
def unlike_post(user_id, post_id):
    # Make the authenticated user unlike a post
    user_id = int(user_id)
    post_ = post.get_post_details(post_id)

    # If post does not belong to specified user, returns 404
    if user_id != post_[4]:
        abort(404, 'Resource not found! Either the post does not exist, '
                   'or the post does not belong to the specified user.')

    # If the authenticated user has not liked the post previously, returns 400
    if not post.is_liked(current_user.id, post_id):
        abort(400, 'You have not liked the post!')

    post.delete_like(current_user.id, post_id)
    return jsonify({'message': 'Removed like from post!'}), 200


@app.route('/<user_id>/posts/<post_id>/likes', methods=['GET'])
@login_required
@valid_info_required
def view_likes(user_id, post_id):
    # View all users who liked a post
    user_id = int(user_id)
    post_ = post.get_post_details(post_id)
    # If post does not belong to specified user, returns 404

    if user_id != post_[4]:
        abort(404, 'Resource not found! Either the post does not exist, '
                   'or the post does not belong to the specified user.')

    users = post.get_liked_users(post_id)

    output = []

    for user in users:
        user_data = {'id': user[0], 'name': user[1], 'email': user[2], 'phone': user[3],
                     'occupation': user[4], 'is_gg': user[5], 'is_fb': user[6]}
        output.append(user_data)
    return jsonify({'users': output}), 200


@app.errorhandler(HTTPException)
def handle_exception(e):
    # Return JSON instead of HTML for HTTP errors.
    # start with the correct headers and status code from the error
    response = e.get_response()

    # Replace description of error code 401 "Unauthorized"
    if e.code == 401:
        e.description = "The server could not verify that you are authorized to access the URL requested. Make sure " \
                        "you have logged in by accessing /google or /facebook through a browser. "

    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')
