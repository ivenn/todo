from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)

    users = db.relationship('User', backref='role' )

    def __repr__(self):
        return '<Role %r>' % (self.name)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, index=True)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


    def __init__(self, username,):
        self.username = username

    def __repr__(self):
        return '<User %r>' % (self.username)