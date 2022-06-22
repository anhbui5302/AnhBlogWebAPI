# Imports
# Python standard libraries
import datetime
import json
import os
from os.path import join, dirname
from functools import wraps

import requests
# Third-party libraries
from flask import Flask, request, url_for, jsonify
from oauthlib.oauth2 import WebApplicationClient
from dotenv import load_dotenv
import jwt
# Internal imports
from werkzeug.exceptions import abort, HTTPException

import db
import post
import user

# App setup
app = Flask(__name__, instance_relative_config=True)
# Used to cryptographically sign cookies or other things and kept secret in production.
# Use the following command to generate a good secret key: $ python -c 'import secrets; print(secrets.token_hex())'.
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'anhblogwebapp.sqlite'),
)

# Load the instance config, if it exists.
app.config.from_pyfile('config.py', silent=True)

# Ensure the instance folder exists.
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
# Load environment variables.
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
# Database setup
# Run "flask init-db" to initialise db.
# Remember to change directory and activate venv.
db.init_app(app)

# OAuth 2 google and facebook client setup.
google_client = WebApplicationClient(GOOGLE_CLIENT_ID)
facebook_client = WebApplicationClient(FACEBOOK_CLIENT_ID)


def get_provider_cfg(discovery_url):
    return requests.get(discovery_url).json()


@app.route("/facebook", methods=["GET"])
def facebook_login():
    # Find out what URL to hit for Facebook login.
    facebook_provider_cfg = get_provider_cfg(FACEBOOK_DISCOVERY_URL)
    facebook_authorization_endpoint = facebook_provider_cfg["authorization_endpoint"]

    # Construct the request for Facebook login and provide scopes specifying which user info the client is getting
    # from Facebook.
    facebook_request_uri = facebook_client.prepare_request_uri(
        facebook_authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["email"],
    )
    return jsonify({'URI': facebook_request_uri, 'message': "Access the URI below through a browser to login."}), 200


@app.route("/facebook/callback", methods=["GET"])
def facebook_callback():
    args = request.args
    # If user decides to cancel login.
    if 'error' in args:
        return abort(401, 'User canceled Facebook login. Try again at /facebook.')

    # User proceeds with login.
    code = args.get("code")

    # Prepare and send a request to get tokens.
    token_url, headers, body = facebook_client.prepare_token_request(
        "https://graph.facebook.com/v14.0/oauth/access_token",
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET),
    )

    facebook_client.parse_request_body_response(json.dumps(token_response.json()))
    # Get user info.
    payload = {'fields': 'email'}
    uri, headers, body = facebook_client.add_token("https://graph.facebook.com/me")
    userinfo_response = requests.get(uri, headers=headers, data=body, params=payload)

    # Return error if email does not exist.
    if userinfo_response.json().get("email"):
        users_email = userinfo_response.json()["email"]
    else:
        return abort(400, 'User email not available. Login using another account with a valid email address.')

    # Create a user in the db if it doesn't exist.
    if not user.get_by_email(users_email, 'Facebook'):
        user.create('', users_email, '', '', 'Facebook')

    user_ = user.get_by_email(users_email, 'Facebook')
    # Generate a token for the authenticated user. 'exp' is the time the token expires, set to be 60 minutes after
    # creation.
    token = jwt.encode({'id': user_[0],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},
                       app.config['SECRET_KEY'])
    return jsonify({'message': 'Login successful. Send the provided token as a bearer token in the header of your '
                               'HTTP request to the API to authenticate yourself.',
                    'token': token}), 200


@app.route("/google", methods=["GET"])
def google_login():
    # Find out what URL to hit for Google login.
    google_provider_cfg = get_provider_cfg(GOOGLE_DISCOVERY_URL)
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Construct the request for Google login and provide scopes specifying which user info the client is getting
    # from Google.
    request_uri = google_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email"],
    )

    return jsonify({'URI': request_uri, 'message': "Access the URI below through a browser to login."}), 200


@app.route("/google/callback")
def google_callback():
    args = request.args
    # If the user cancel login.
    if 'error' in args:
        return abort(401, 'User canceled Google login. Try again at /facebook.')
    # Get authorization code Google sent back.
    code = args.get("code")

    # Find out what URL to hit to get the access token.
    google_provider_cfg = get_provider_cfg(GOOGLE_DISCOVERY_URL)
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens.
    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens.
    google_client.parse_request_body_response(json.dumps(token_response.json()))

    # Use the token received to hit the URL from Google that gives the user's email.
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = google_client.add_token(userinfo_endpoint)

    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Make sure email is verified by Google.
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
    else:
        return abort(400, 'User email not available or not verified by Google.')

    # Create a user in the db if it doesn't exist.
    if not user.get_by_email(users_email, 'Google'):
        user.create('', users_email, '', '', 'Google')

    user_ = user.get_by_email(users_email, 'Google')
    # Generate a token for the authenticated user. 'exp' is the time the token expires, set to be 60 minutes after
    # creation.
    token = jwt.encode({'id': user_[0],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},
                       app.config['SECRET_KEY'])
    return jsonify({'message': 'Login successful. Send the provided token as a bearer token in the header of your '
                               'HTTP request to the API to authenticate yourself.',
                    'token': token}), 200


def token_required(func):
    # Decorator to check if the user has provided the correct token to authenticate themselves.
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the token from the header.
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
        else:
            token = ''

        if not token:
            return abort(401, 'Token is missing.')

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], ['HS256'], verify_signature=True)
            # Pass data into decorated function.
            kwargs['user_data'] = data
        # An exception is thrown when jwt cannot decode the token provided (i.e. it is not correct). InvalidTokenError
        # is the base exception when decode() fails on a token. Others can be found on pyjwt's API page.
        # Error name: type(exception).__name__
        # Error args: exception.args
        except jwt.exceptions.InvalidTokenError:
            return abort(401, 'Token is invalid or has expired.')
        return func(*args, **kwargs)

    return wrapper


def author_post_mismatch(author_id, post_):
    # Checks if a post belongs to an author.
    author_id = int(author_id)
    if post_ is None:
        abort(404, 'Resource not found! The specified post does not exist.')
    elif (author_id != post_[4]) or (post_ is None):
        abort(404, 'Resource not found! The specified post does not belong to the specified user.')


def format_likes_to_display(post_id):
    # Get the list of users who like a post and format a string to be displayed.

    users = post.get_liked_users(post_id)

    if len(users) == 0:
        return 'No one has liked this post yet.'
    elif len(users) == 1:
        return '{} liked this post.'.format(users[0][1])
    elif len(users) == 2:
        return '{} and {} liked this post.'.format(users[0][1], users[1][1])
    else:
        return '{}, {} and {} other people liked this post.'.format(users[0][1], users[1][1], len(users) - 2)


def format_posts_to_display(posts):
    # Format a string that display a list of posts.
    output = []
    for post_ in posts:
        # Shows first 100 chars of body.
        body_to_show = post_[2][:100]
        likes_to_show = format_likes_to_display(post_[0])
        post_data = \
            {'title': post_[1], 'body': body_to_show, 'created': post_[3], 'author_id': post_[4],
             'author_name': post_[5], 'likes': likes_to_show}
        output.append(post_data)
    return output


def get_value(dict_, name, default):
    # Returns value of a key given its name and a dictionary. Default value given if it is not in the
    # dictionary or its value in the dictionary is '' (i.e. empty)
    val = dict_.get(name)
    if val is None or val == '':
        return default
    return val


def message_403():
    # Returns the message to display when a 403 is thrown
    return ("This account does not have the necessary info to access this page. Update your info by "
            "sending a POST request to /updateinfo. In the request body provide your name as 'name', "
            "phone number as 'phone' and occupation as 'occupation' in JSON format. Google users do "
            "not need to provide a phone number. Facebook users do not need to provide an occupation.")


@app.route("/", methods=["GET"])
@token_required
# @valid_info_required
def index(**kwargs):
    # Shows the homepage, containing all posts by all users, which is paginated.
    user_data = kwargs.get('user_data')
    user_ = user.get(user_data.get('id'))
    user_id, user_type = user_[0], user_[5]
    args = request.args

    # Checks if user has valid info required
    if not user.info_valid(user_id, user_type):
        return abort(403, message_403())

    # If args are not provided, generate some default values.
    # Also checks if the values contain only numbers
    page = (get_value(args, 'page', '1'))
    if page.isdecimal():
        page = int(page)
    else:
        page = 1

    perpage = (get_value(args, 'perpage', '5'))
    if perpage.isdecimal():
        perpage = int(perpage)
    else:
        perpage = 5

    start_index = (page - 1) * perpage
    end_index = page * perpage

    # Shows all posts by all users
    posts = post.get_homepage()
    # Get all posts in a page and format them for displaying
    final_posts = posts[start_index:end_index]
    output = format_posts_to_display(final_posts)

    return jsonify({'posts': output,
                    'next_page': '{}?page={}&perpage={}'.format(url_for("index"), page + 1, perpage)}), 200


@app.route("/info", methods=["GET"])
@token_required
def get_info(**kwargs):
    # Shows the info of the authenticated user
    user_data = kwargs.get('user_data')
    user_ = user.get(user_data.get('id'))
    user_id, user_type = user_[0], user_[5]

    # Checks if user has valid info required
    if not user.info_valid(user_id, user_type):
        return abort(403, message_403())

    if not user_:
        return abort(404, 'Uh oh. You don\'t seem to exist in the db? Something must be wrong.')
    output = {'id': user_[0], 'name': user_[1], 'email': user_[2], 'phone': user_[3],
              'occupation': user_[4], 'type': user_[5]}

    return jsonify(output), 200


@app.route("/updateinfo", methods=["PATCH"])
@token_required
def updateinfo(**kwargs):
    # Attempts to update authenticated user's info
    user_data = kwargs.get('user_data')
    user_ = user.get(user_data.get('id'))

    user_id, user_type = user_[0], user_[5]
    data = request.get_json()

    # name is always required
    name = get_value(data, 'name', '')
    if name == '':
        # Handles name missing
        return abort(400, 'Username cannot be empty. Include a `name` field in the request body and '
                          'make sure it is not empty.')

    # occupation is required for Google users
    occupation = get_value(data, 'occupation', '')
    if (occupation == '') and (user_type == 'Google'):
        # Handles occupation missing
        return abort(400, 'User occupation cannot be empty. Include a `occupation` field in the request body and '
                          'make sure it is not empty.')

    # phone is required for Facebook users
    phone = get_value(data, 'phone', '')
    if user_type == 'Facebook':
        if phone == '':
            # Handles phone missing
            return abort(400, 'User phone cannot be empty. Include a `phone` field in the request body and '
                              'make sure it is not empty.')
        if not phone.isdecimal():
            # Handles phone not valid
            return abort(400, 'User phone can only contain numbers.')
    user.update(user_id, name, phone, occupation)

    return jsonify({'message': 'User info successfully updated!'}), 200


@app.route('/create', methods=['POST'])
@token_required
def create_post(**kwargs):
    # Attempts to create a new post using the provided info
    user_data = kwargs.get('user_data')
    user_ = user.get(user_data.get('id'))
    user_id, user_type = user_[0], user_[5]
    data = request.get_json()

    # Checks if user has valid info required
    if not user.info_valid(user_id, user_type):
        return abort(403, message_403())

    # Title is required
    title = get_value(data, 'title', '')
    if title == '':
        # Handles title missing
        return abort(400, 'Post title cannot be empty. Include a `title` field in the request body and '
                          'make sure it is not empty.')
    # Body is required
    body = get_value(data, 'body', '')
    if body == '':
        # Handles body missing
        return abort(400, 'Post body cannot be empty. Include a `body` field in the request body and '
                          'make sure it is not empty.')

    post.insert_post(user_id, title, body)

    return jsonify({'message': 'New post created!'}), 201


@app.route('/<author_id>/posts', methods=['GET'])
@token_required
def user_posts(author_id, **kwargs):
    # Shows all posts made by a user
    user_data = kwargs.get('user_data')
    user_ = user.get(user_data.get('id'))
    user_id, user_type = user_[0], user_[5]

    # Checks if user has valid info required
    if not user.info_valid(user_id, user_type):
        return abort(403, message_403())

    posts = post.get_user_page(author_id)
    output = format_posts_to_display(posts)
    return jsonify({'posts': output}), 200


@app.route('/<author_id>/posts/<post_id>', methods=['GET'])
@token_required
def post_details(author_id, post_id, **kwargs):
    # Shows details of a post
    user_data = kwargs.get('user_data')
    user_ = user.get(user_data.get('id'))
    user_id, user_type = user_[0], user_[5]

    # Checks if user has valid info required
    if not user.info_valid(user_id, user_type):
        return abort(403, message_403())

    post_ = post.get_post_details(post_id)
    author_post_mismatch(author_id, post_)
    likes_to_show = format_likes_to_display(post_id)
    post_data = \
        {'title': post_[1], 'body': post_[2], 'created': post_[3],
         'author_id': post_[4], 'author_name': post_[5], 'likes': likes_to_show}

    return jsonify(post_data), 200


@app.route('/<author_id>/posts/<post_id>/like', methods=['POST'])
@token_required
def like_post(author_id, post_id, **kwargs):
    # Make the authenticated user like a post
    user_data = kwargs.get('user_data')
    user_ = user.get(user_data.get('id'))
    user_id, user_type = user_[0], user_[5]

    # Checks if user has valid info required
    if not user.info_valid(user_id, user_type):
        return abort(403, message_403())

    post_ = post.get_post_details(post_id)
    author_post_mismatch(author_id, post_)

    # If user has already liked the post, returns 400
    if post.is_liked(user_id, post_id):
        abort(400, 'You have already liked the post!')

    post.insert_like(user_id, post_id)
    return jsonify({'message': 'Liked the post!'}), 201


@app.route('/<author_id>/posts/<post_id>/like', methods=['DELETE'])
@token_required
def unlike_post(author_id, post_id, **kwargs):
    # Make the authenticated user unlike a post
    user_data = kwargs.get('user_data')
    user_ = user.get(user_data.get('id'))
    user_id, user_type = user_[0], user_[5]

    # Checks if user has valid info required
    if not user.info_valid(user_id, user_type):
        return abort(403, message_403())

    post_ = post.get_post_details(post_id)
    author_post_mismatch(author_id, post_)

    # If the authenticated user has not liked the post previously, returns 400
    if not post.is_liked(user_id, post_id):
        abort(400, 'You have not liked the post!')

    post.delete_like(user_id, post_id)
    return jsonify({'message': 'Removed like from post!'}), 200


@app.route('/<author_id>/posts/<post_id>/likes', methods=['GET'])
@token_required
def view_likes(author_id, post_id, **kwargs):
    # View all users who liked a post
    user_data = kwargs.get('user_data')
    user_ = user.get(user_data.get('id'))
    user_id, user_type = user_[0], user_[5]

    # Checks if user has valid info required
    if not user.info_valid(user_id, user_type):
        return abort(403, message_403())

    post_ = post.get_post_details(post_id)
    author_post_mismatch(author_id, post_)

    users = post.get_liked_users(post_id)

    output = []

    for user_ in users:
        user_data = {'id': user_[0], 'name': user_[1], 'email': user_[2], 'phone': user_[3],
                     'occupation': user_[4], 'type': user_[5]}
        output.append(user_data)
    return jsonify({'users': output}), 200


@app.errorhandler(HTTPException)
def handle_exception(e):
    # Return JSON instead of HTML for HTTP errors.
    # start with the correct headers and status code from the error
    response = e.get_response()

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
