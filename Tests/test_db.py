import sqlite3

import pytest
import db


def test_get_close_db(app):
    with app.app_context():
        db_ = db.get_db()
        assert db_ is db.get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db_.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called
