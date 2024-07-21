from . import db
import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), unique=False, nullable=False)
    lastname = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    funds = db.relationship('Funds', backref='users')

    def __repr__(self):
        return f"User : '{self.firstname}', '{self.lastname}'"

class Funds(db.Model):
    __tablename__ = 'funds'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'created_at': self.created_at
        }


