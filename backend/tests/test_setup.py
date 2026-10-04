from sqlalchemy import text


def test_uses_test_database_not_dev(db):
    assert db.execute(text("SELECT current_database()")).scalar() == "job_tracker_test"


def test_two_users_seeded(db, two_users):
    a, b = two_users
    assert a.id != b.id
    assert db.execute(text("SELECT count(*) FROM job")).scalar() == 3
