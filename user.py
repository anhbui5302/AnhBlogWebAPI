from flask_login import UserMixin

from db import get_db


class User(UserMixin):
    def __init__(self, id_, name, email, phone, occupation, is_gg, is_fb):
        self.id = id_
        self.name = name
        self.email = email
        self.phone = phone
        self.occupation = occupation
        self.is_gg = is_gg
        self.is_fb = is_fb

    def get_id(self):
        # Needed for flask_login's requirements
        return self.id

    @staticmethod
    def get(user_id):
        # Gets a user from a db given its id
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], phone=user[3], occupation=user[4], is_gg=user[5], is_fb=user[6]
        )
        return user

    @staticmethod
    def get_gg_by_email(email):
        # Gets a google user from a db given its email and type
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE email = ? AND is_gg = 1", (email,)
        ).fetchone()
        if not user:
            return None
        user = User(
            id_=user[0], name=user[1], email=user[2], phone=user[3], occupation=user[4], is_gg=user[5], is_fb=user[6]
        )
        return user

    @staticmethod
    def get_fb_by_email(email):
        # Gets a facebook user from a db given its email and type
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE email = ? AND is_fb = 1", (email,)
        ).fetchone()
        if not user:
            return None
        user = User(
            id_=user[0], name=user[1], email=user[2], phone=user[3], occupation=user[4], is_gg=user[5], is_fb=user[6]
        )
        return user

    @staticmethod
    def create(name, email, phone, occupation, is_gg, is_fb):
        # Creates a new user with the provided info and saves to db
        db = get_db()
        db.execute(
            "INSERT INTO user (name, email, phone, occupation, is_gg, is_fb) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, phone, occupation, is_gg, is_fb),
        )
        db.commit()

    @staticmethod
    def update(user_id, name, phone, occupation):
        # Update data of a user in the database with the new values
        db = get_db()
        db.execute(
            "UPDATE user SET name = ?, phone = ?, occupation = ? WHERE id = ?",
            (name, phone, occupation, user_id),
        )
        db.commit()

    @staticmethod
    def google_info_valid(user_id):
        # If name or occupation of user with the specified id is null then return False. Otherwise, return True.
        db = get_db()

        user = db.execute(
            "SELECT * FROM user WHERE id = ? AND (name <> '') AND (occupation <> '')", (user_id,)
        ).fetchone()

        if user:
            return True
        return False

    @staticmethod
    def facebook_info_valid(user_id):
        # If name or phone of user with the specified id is null then return False. Otherwise, return True.
        db = get_db()

        user = db.execute(
            "SELECT * FROM user WHERE id = ? AND (name <> '') AND (phone <> '')", (user_id,)
        ).fetchone()

        if user:
            return True
        return False
