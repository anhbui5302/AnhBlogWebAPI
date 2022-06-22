from db import get_db

def get(user_id):
    # Gets a user from a db given its id
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE id = ?", (user_id,)
    ).fetchone()
    return user


def get_gg_by_email(email):
    # Gets a Google user from a db given its email and type
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE email = ? AND is_gg = 1", (email,)
    ).fetchone()
    return user


def get_fb_by_email(email):
    # Gets a facebook user from a db given its email and type
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE email = ? AND is_fb = 1", (email,)
    ).fetchone()
    return user


def create(name, email, phone, occupation, is_gg, is_fb):
    # Creates a new user with the provided info and saves to db
    db = get_db()
    db.execute(
        "INSERT INTO user (name, email, phone, occupation, is_gg, is_fb) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (name, email, phone, occupation, is_gg, is_fb),
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


def google_info_valid(user_id):
    # If name or occupation of user with the specified id is null then return False. Otherwise, return True.
    db = get_db()

    user = db.execute(
        "SELECT * FROM user WHERE id = ? AND (name <> '') AND (occupation <> '')", (user_id,)
    ).fetchone()

    if user:
        return True
    return False


def facebook_info_valid(user_id):
    # If name or phone of user with the specified id is null then return False. Otherwise, return True.
    db = get_db()

    user = db.execute(
        "SELECT * FROM user WHERE id = ? AND (name <> '') AND (phone <> '')", (user_id,)
    ).fetchone()

    if user:
        return True
    return False
