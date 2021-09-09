from creativecoin import db

def commit_db():
    db.session.commit()