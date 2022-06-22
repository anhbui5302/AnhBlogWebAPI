# Contains functions relating to posts
from db import get_db


def get_homepage():
    # Shows posts that are on the home page, most recent first
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, name'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return posts


def get_user_page(user_id):
    # Shows posts that are made by one user
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, name'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY created DESC', (user_id,)
    ).fetchall()

    # Convert type Row to tuple to avoid datatype Row not serializable error
    posts = [tuple(row) for row in posts]
    return posts


def get_post_details(post_id):
    # Shows a post with its full body that's not limited to the first 100 characters
    # Shows posts that are on the home page, most recent first
    db = get_db()
    post = db.execute(
        'SELECT p.id, title, body, created, author_id, name'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?', (post_id,)
    ).fetchone()
    return post


def insert_post(author_id, title, body):
    # Insert a post into the db
    db = get_db()
    db.execute(
        "INSERT INTO post (author_id, title, body) "
        "VALUES (?, ?, ?)",
        (author_id, title, body),
    )
    db.commit()


def is_liked(liker_id, post_id):
    # Returns True if there is a record of a user liking a post in the db
    db = get_db()
    user = db.execute(
        "SELECT * FROM like WHERE post_id = ? AND user_id = ?", (post_id, liker_id)
    ).fetchone()

    if user:
        return True
    return False


def insert_like(liker_id, post_id):
    # Insert a like into the db
    db = get_db()
    db.execute(
        "INSERT INTO like (post_id, user_id) "
        "VALUES (?, ?)",
        (post_id, liker_id),
    )
    db.commit()


def delete_like(liker_id, post_id):
    # Delete a like from the db
    db = get_db()
    db.execute(
        "DELETE FROM like "
        "WHERE post_id = ? AND user_id = ?", (post_id, liker_id),
    )
    db.commit()


def get_liked_users(post_id):
    # Get all users who liked a post
    db = get_db()
    users = db.execute(
        'SELECT u.id, name, email, phone, occupation, type'
        ' FROM like l JOIN user u ON l.user_id = u.id'
        ' WHERE l.post_id = ?'
        ' ORDER BY created DESC', (post_id,)
    ).fetchall()

    # Convert type Row to tuple to avoid datatype Row not serializable error
    users = [tuple(user) for user in users]
    return users
