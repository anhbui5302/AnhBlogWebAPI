import sys
import os

sys.path.append(os.path.join(sys.path[0], '..'))

import user


# Test create() and get_by_email() in user
def test_create(client, app):
    with app.app_context():
        test_email = 'test@example.com'
        if not user.get_by_email(test_email, 'Google'):
            user.create('', test_email, '', '', 'Google')
        user_ = user.get_by_email(test_email, 'Google')
        assert user_


# Test info_valid()
def test_info_valid(client, app):
    with app.app_context():
        # Valid Google user
        assert user.info_valid(1, 'Google') is True
        assert user.info_valid(1, 'Facebook') is False
        assert user.info_valid(1, 'Invalid') is False
        # Valid Facebook user
        assert user.info_valid(3, 'Google') is False
        assert user.info_valid(3, 'Facebook') is True
        assert user.info_valid(3, 'Invalid') is False
        # Invalid Google user
        assert user.info_valid(2, 'Google') is False
        assert user.info_valid(2, 'Facebook') is False
        assert user.info_valid(2, 'Invalid') is False
        # Invalid Facebook user
        assert user.info_valid(4, 'Google') is False
        assert user.info_valid(4, 'Facebook') is False
        assert user.info_valid(4, 'Invalid') is False
