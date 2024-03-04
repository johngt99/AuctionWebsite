from email.policy import default
from auction import db, login_manager
from auction import bcrypt
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Model of the user table on the DB
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    phone_number = db.Column(db.String(), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    items = db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


#Model of the item table on the DB
class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    start_price = db.Column(db.Integer(), nullable=False)    
    description = db.Column(db.String(length=1024), nullable=False)
    image = db.Column(db.String(20), nullable=False, unique=True, default='default.jpg')
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    seller = db.Column(db.String(20))
    date_created = db.Column(db.DateTime)
    show_date = db.Column(db.String(10))
    duration = db.Column(db.Integer(), default=1)
    curr_bid = db.Column(db.Integer(), nullable=False)
    last_bidder = db.Column(db.Integer(), default=None)
    highest_bidder_id = db.Column(db.Integer(), default=None)
    item_sold = db.Column(db.Boolean(), default=False)
    
    def __repr__(self):
        return f'Item {self.name}'
    
    def sold(self):
          self.status=0
          db.session.commit()  