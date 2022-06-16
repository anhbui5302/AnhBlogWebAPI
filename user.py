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
        return self.email

    @staticmethod
    def get(email):
        # Gets a user from db given email
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE email = ?", (email,)
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
    def update(email, name, phone, occupation):
        # Update data of a user in the database with the new values
        db = get_db()
        db.execute(
            "UPDATE user SET name = ?, phone = ?, occupation = ? WHERE email = ?",
            (name, phone, occupation, email),
        )
        db.commit()

    @staticmethod
    def google_info_valid(email):
        # If name or occupation of user with the specified id is null then return False. Otherwise, return True.
        db = get_db()

        user = db.execute(
            "SELECT * FROM user WHERE email = ? AND (name <> '') AND (occupation <> '')", (email,)
        ).fetchone()

        if user:
            return True
        return False

    @staticmethod
    def facebook_info_valid(email):
        # If name or phone of user with the specified id is null then return False. Otherwise, return True.
        db = get_db()

        user = db.execute(
            "SELECT * FROM user WHERE email = ? AND (name <> '') AND (phone <> '')", (email,)
        ).fetchone()

        if user:
            return True
        return False
