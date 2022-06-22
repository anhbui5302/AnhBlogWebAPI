from db import get_db


def get(user_id):
    # Gets a user from a db given its id
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE id = ?", (user_id,)
    ).fetchone()
    return user


def get_by_email(email, type_):
    # Gets a user from a db given its email and type
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE email = ? AND type = ?", (email, type_,)
    ).fetchone()
    return user


def create(name, email, phone, occupation, type_):
    # Creates a new user with the provided info and saves to db
    db = get_db()
    db.execute(
        "INSERT INTO user (name, email, phone, occupation, type) "
        "VALUES (?, ?, ?, ?, ?)",
        (name, email, phone, occupation, type_),
    )
    db.commit()


def update(user_id, name, phone, occupation):
    # Update data of a user in the database with the new values
    db = get_db()
    db.execute(
        "UPDATE user SET name = ?, phone = ?, occupation = ? WHERE id = ?",
        (name, phone, occupation, user_id),
    )
    db.commit()


def info_valid(user_id, type_):
    # Checks if the info of the user with id and type provided is valid. Returns True if it is, False otherwise.
    db = get_db()
    if type_ == 'Google':
        user = db.execute(
            "SELECT * FROM user WHERE id = ? AND (name <> '') AND (occupation <> '')", (user_id,)
        ).fetchone()
    elif type_ == 'Facebook':
        user = db.execute(
            "SELECT * FROM user WHERE id = ? AND (name <> '') AND (phone <> '')", (user_id,)
        ).fetchone()
    # Somehow type is neither 'Google' nor 'Facebook'
    else:
        user = None

    if user:
        return True
    return False
