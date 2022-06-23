import datetime
import json
import os
import sys

import jwt

# os.path.join(sys.path[0], '..') points to the parent path.
# sys.path.append adds the path to the searching space.
import pytest

sys.path.append(os.path.join(sys.path[0], '..'))

import user
import post

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
FACEBOOK_DISCOVERY_URL = (
    "https://www.facebook.com/.well-known/openid-configuration"
)


def generate_mock_user_token(app, user_id):
    token = jwt.encode({'id': user_id,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=15)},
                       app.config['SECRET_KEY'])
    return token


# Users with ids 1,3,5,6 have valid info.
# Users with ids 2,4 have invalid info.

def test_facebook(client, app):
    assert client.get('/facebook').status_code == 200


def test_google(client, app):
    assert client.get('/google').status_code == 200


def test_index(client, app):
    # Invalid token provided
    response = client.get('/')
    assert response.status_code == 401
    response = client.get('/', headers={'Authorization': 'Bearer InvalidToken123456'})
    assert response.status_code == 401

    # Invalid user
    token = generate_mock_user_token(app, 2)
    response = client.get('/', headers={'Authorization': 'Bearer {}'.format(token)})
    assert response.status_code == 403

    # Valid user with no query
    token = generate_mock_user_token(app, 1)
    response = client.get('/', headers={'Authorization': 'Bearer {}'.format(token)})
    assert response.status_code == 200

    # Valid user with valid query parameters
    token = generate_mock_user_token(app, 3)
    response = client.get('/',
                          query_string={'page': '2', 'perpage': '3'},
                          headers={'Authorization': 'Bearer {}'.format(token)})
    assert response.status_code == 200

    # Valid user with invalid query parameters
    token = generate_mock_user_token(app, 3)
    response = client.get('/',
                          query_string={'page': 'text', 'perpage': 'notvalid', 'rand': 'text'},
                          headers={'Authorization': 'Bearer {}'.format(token)})
    assert response.status_code == 200


def test_info(client, app):
    # Invalid token provided
    response = client.get('/info')
    assert response.status_code == 401
    response = client.get('/info', headers={'Authorization': 'Bearer InvalidToken123456'})
    assert response.status_code == 401

    # Invalid user
    token = generate_mock_user_token(app, 2)
    response = client.get('/info', headers={'Authorization': 'Bearer {}'.format(token)})
    assert response.status_code == 403

    # Valid user with no query
    token = generate_mock_user_token(app, 1)
    response = client.get('/info', headers={'Authorization': 'Bearer {}'.format(token)})
    assert response.status_code == 200

    # # Valid user with query parameters
    # token = generate_mock_user_token(app, 3)
    # response = client.get('/info',
    #                       query_string={'field1': 'data', 'field2': 'data2'},
    #                       headers={'Authorization': 'Bearer {}'.format(token)})
    assert response.status_code == 200


def test_updateinfo(client, app):
    # Invalid token provided
    response = client.patch('/updateinfo')
    assert response.status_code == 401
    response = client.patch('/updateinfo', headers={'Authorization': 'Bearer InvalidToken123456'})
    assert response.status_code == 401

    # Users with no Content-Type as application/json in header
    token = generate_mock_user_token(app, 2)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token)},
                            data=json.dumps(dict(name='ValidName', phone='0123456789', occupation='ValidOccupation')))
    assert response.status_code == 400

    # Users with no request body
    token = generate_mock_user_token(app, 2)
    response = client.patch('/updateinfo', headers={'Authorization': 'Bearer {}'.format(token),
                                                    'Content-Type': 'application/json'})
    assert response.status_code == 400

    # Users with valid request body
    token = generate_mock_user_token(app, 1)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(name='ValidName', occupation='ValidOccupation')))
    assert response.status_code == 200

    token = generate_mock_user_token(app, 3)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(name='ValidName', phone='0123456789')))
    assert response.status_code == 200

    # Users with invalid request body
    # name is empty
    token = generate_mock_user_token(app, 1)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(name='', occupation='ValidOccupation')))
    assert response.status_code == 400

    # name is not present
    token = generate_mock_user_token(app, 1)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(occupation='ValidOccupation')))
    assert response.status_code == 400

    # Google users with invalid request body
    # occupation is empty
    token = generate_mock_user_token(app, 1)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(name='ValidName', occupation='')))
    assert response.status_code == 400

    # occupation is not present
    token = generate_mock_user_token(app, 1)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(name='ValidName')))
    assert response.status_code == 400

    # phone is not numbers
    token = generate_mock_user_token(app, 1)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(name='ValidName', phone='InvalidPhone', occupation='ValidOccupation')))
    assert response.status_code == 400

    # Facebook users with invalid request body
    # phone is empty
    token = generate_mock_user_token(app, 3)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(name='ValidName', phone='', occupation='ValidOccupation')))
    assert response.status_code == 400

    # phone is not present
    token = generate_mock_user_token(app, 3)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(name='ValidName', occupation='ValidOccupation')))
    assert response.status_code == 400

    # phone is not numbers
    token = generate_mock_user_token(app, 3)
    response = client.patch('/updateinfo',
                            headers={'Authorization': 'Bearer {}'.format(token),
                                     'Content-Type': 'application/json'},
                            data=json.dumps(dict(name='ValidName', phone='InvalidPhone', occupation='ValidOccupation')))
    assert response.status_code == 400


def test_create(client, app):
    # Invalid token provided
    response = client.post('/create')
    assert response.status_code == 401
    response = client.post('/create', headers={'Authorization': 'Bearer InvalidToken123456',
                                               'Content-Type': 'application/json'},
                           data=json.dumps(dict(title='ValidTitle', body='ValidBody')))
    assert response.status_code == 401

    # Invalid user
    token = generate_mock_user_token(app, 2)
    response = client.post('/create', headers={'Authorization': 'Bearer {}'.format(token),
                                               'Content-Type': 'application/json'},
                           data=json.dumps(dict(title='ValidTitle', body='ValidBody')))

    assert response.status_code == 403
    # Valid user
    token = generate_mock_user_token(app, 3)
    response = client.post('/create', headers={'Authorization': 'Bearer {}'.format(token),
                                               'Content-Type': 'application/json'},
                           data=json.dumps(dict(title='ValidTitle', body='ValidBody')))
    assert response.status_code == 201

    # Valid user with invalid data
    # title is not present
    token = generate_mock_user_token(app, 3)
    response = client.post('/create', headers={'Authorization': 'Bearer {}'.format(token),
                                               'Content-Type': 'application/json'},
                           data=json.dumps(dict(body='ValidBody')))
    assert response.status_code == 400

    # title is empty
    token = generate_mock_user_token(app, 3)
    response = client.post('/create', headers={'Authorization': 'Bearer {}'.format(token),
                                               'Content-Type': 'application/json'},
                           data=json.dumps(dict(title='', body='ValidBody')))
    assert response.status_code == 400

    # body is not present
    token = generate_mock_user_token(app, 3)
    response = client.post('/create', headers={'Authorization': 'Bearer {}'.format(token),
                                               'Content-Type': 'application/json'},
                           data=json.dumps(dict(title='ValidTitle')))
    assert response.status_code == 400

    # body is empty
    token = generate_mock_user_token(app, 3)
    response = client.post('/create', headers={'Authorization': 'Bearer {}'.format(token),
                                               'Content-Type': 'application/json'},
                           data=json.dumps(dict(title='ValidTitle', body='')))
    assert response.status_code == 400


# Creating a class to have methods share the same parametrized arguments
# Name of class need to start with Test for pytest to detect it
@pytest.mark.parametrize('author_id', ['1', '6', '9999', 'abcd'])
class TestParameterize:
    # Tests will be carried out with various author ids and post ids. Intended behaviour is that response returns a 404
    # when author_id or post_id is not valid.
    @staticmethod
    def test_user_posts(client, app, author_id):
        # Invalid token provided
        response = client.get('/{}/posts'.format(author_id))
        assert response.status_code == 401
        response = client.get('/{}/posts'.format(author_id), headers={'Authorization': 'Bearer InvalidToken123456'})
        assert response.status_code == 401

        # Invalid user
        token = generate_mock_user_token(app, 2)
        response = client.get('/{}/posts'.format(author_id), headers={'Authorization': 'Bearer {}'.format(token)})
        assert response.status_code == 403

        # Valid user
        token = generate_mock_user_token(app, 1)
        response = client.get('/{}/posts'.format(author_id), headers={'Authorization': 'Bearer {}'.format(token)})

        # If author does not exist in db
        if not user.get(author_id):
            assert response.status_code == 404
        else:
            assert response.status_code == 200

    @staticmethod
    @pytest.mark.parametrize('post_id', ['1', '2', '3', '4', '12', '9999', 'abcd'])
    def test_post_details(client, app, author_id, post_id):
        # Invalid token provided
        response = client.get('/{}/posts/{}'.format(author_id, post_id))
        assert response.status_code == 401
        response = client.get('/{}/posts/{}'.format(author_id, post_id),
                              headers={'Authorization': 'Bearer InvalidToken123456'})
        assert response.status_code == 401

        # Invalid user
        token = generate_mock_user_token(app, 2)
        response = client.get('/{}/posts/{}'.format(author_id, post_id),
                              headers={'Authorization': 'Bearer {}'.format(token)})
        assert response.status_code == 403

        # Valid user
        token = generate_mock_user_token(app, 1)
        response = client.get('/{}/posts/{}'.format(author_id, post_id),
                              headers={'Authorization': 'Bearer {}'.format(token)})
        # If both author and post exists
        post_ = post.get_post_details(post_id)
        if user.get(author_id) and (post_ is not None):
            author_id = int(author_id)
            # If author didn't write post
            if author_id != post_[4]:
                assert response.status_code == 404
            # If author wrote the post
            else:
                assert response.status_code == 200
        else:
            assert response.status_code == 404

    @staticmethod
    @pytest.mark.parametrize('post_id', ['1', '4', '12', '9999', 'abcd'])
    def test_post_like(client, app, author_id, post_id):
        # Invalid token provided
        response = client.post('/{}/posts/{}/like'.format(author_id, post_id))
        assert response.status_code == 401
        response = client.post('/{}/posts/{}/like'.format(author_id, post_id),
                               headers={'Authorization': 'Bearer InvalidToken123456'})
        assert response.status_code == 401

        # Invalid user
        token = generate_mock_user_token(app, 2)
        response = client.post('/{}/posts/{}/like'.format(author_id, post_id),
                               headers={'Authorization': 'Bearer {}'.format(token)})
        assert response.status_code == 403

        # Valid user with ids
        ids = [1, 3]
        for id_ in ids:
            user_id = id_
            token = generate_mock_user_token(app, user_id)
            user_liked_the_post = post.is_liked(user_id, post_id)
            response = client.post('/{}/posts/{}/like'.format(author_id, post_id),
                                   headers={'Authorization': 'Bearer {}'.format(token)})
            # If both author and post exists
            post_ = post.get_post_details(post_id)
            if user.get(author_id) and (post_ is not None):
                author_id = int(author_id)
                # If author didn't write post
                if author_id != post_[4]:
                    assert response.status_code == 404
                # If author wrote the post
                else:
                    pass
                    # If user has already liked post
                    if user_liked_the_post:
                        assert response.status_code == 400
                    else:
                        assert response.status_code == 201
            else:
                assert response.status_code == 404

    @staticmethod
    @pytest.mark.parametrize('post_id', ['1', '4', '12', '9999', 'abcd'])
    def test_post_unlike(client, app, author_id, post_id):
        # Invalid token provided
        response = client.delete('/{}/posts/{}/like'.format(author_id, post_id))
        assert response.status_code == 401
        response = client.delete('/{}/posts/{}/like'.format(author_id, post_id),
                                 headers={'Authorization': 'Bearer InvalidToken123456'})
        assert response.status_code == 401

        # Invalid user
        token = generate_mock_user_token(app, 2)
        response = client.delete('/{}/posts/{}/like'.format(author_id, post_id),
                                 headers={'Authorization': 'Bearer {}'.format(token)})
        assert response.status_code == 403

        # Valid user with ids
        ids = [1, 3]
        for id_ in ids:
            user_id = id_
            token = generate_mock_user_token(app, user_id)
            user_liked_the_post = post.is_liked(user_id, post_id)
            response = client.delete('/{}/posts/{}/like'.format(author_id, post_id),
                                     headers={'Authorization': 'Bearer {}'.format(token)})
            # If both author and post exists
            post_ = post.get_post_details(post_id)
            if user.get(author_id) and (post_ is not None):
                author_id = int(author_id)
                # If author didn't write post
                if author_id != post_[4]:
                    assert response.status_code == 404
                # If author wrote the post
                else:
                    pass
                    # If user has already liked post
                    if user_liked_the_post:
                        assert response.status_code == 200
                    else:
                        assert response.status_code == 400
            else:
                assert response.status_code == 404

    @staticmethod
    @pytest.mark.parametrize('post_id', ['1', '4', '12', '9999', 'abcd'])
    def test_post_likes(client, app, author_id, post_id):
        # Invalid token provided
        response = client.get('/{}/posts/{}/likes'.format(author_id, post_id))
        assert response.status_code == 401
        response = client.get('/{}/posts/{}/likes'.format(author_id, post_id),
                              headers={'Authorization': 'Bearer InvalidToken123456'})
        assert response.status_code == 401

        # Invalid user
        token = generate_mock_user_token(app, 2)
        response = client.get('/{}/posts/{}/likes'.format(author_id, post_id),
                              headers={'Authorization': 'Bearer {}'.format(token)})
        assert response.status_code == 403

        # Valid user
        token = generate_mock_user_token(app, 1)
        response = client.get('/{}/posts/{}/likes'.format(author_id, post_id),
                              headers={'Authorization': 'Bearer {}'.format(token)})
        # If both author and post exists
        post_ = post.get_post_details(post_id)
        if user.get(author_id) and (post_ is not None):
            author_id = int(author_id)
            # If author didn't write post
            if author_id != post_[4]:
                assert response.status_code == 404
            # If author wrote the post
            else:
                assert response.status_code == 200
        else:
            assert response.status_code == 404
