from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    flagged = db.Column(db.Boolean, default=False)


class Influencer(db.Model):
    __tablename__ = 'influencers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),unique=True,nullable=False)
    # profile_pic = db.Column(db.String(200), nullable=True)
    niche = db.Column(db.String(100), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    total_earnings = db.Column(db.Float,default=0.0)
    platform = db.Column(db.String(50), nullable=False)
    user = db.relationship('User', backref=db.backref('influencer', uselist=False))

    
class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100),nullable=False)
    user = db.relationship('User', backref=db.backref('sponsor', uselist=False))

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text,nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(30), nullable=False, default='public') 
    goals = db.Column(db.String(150))
    niche = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='active')  # 'active', 'completed'
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=False)
    sponsor = db.relationship('Sponsor', backref=db.backref('campaigns', lazy=True))
    ad_requests = db.relationship('AdRequest', backref='campaign', cascade='all, delete-orphan', lazy=True)
   
    @property
    def progress(self):
        accepted_requests = [req for req in self.ad_requests if req.status == 'accepted' or req.status == 'done']
        done_requests = len([req for req in accepted_requests if req.status == 'done'])
        total_accepted_requests = len(accepted_requests)
        return (done_requests / total_accepted_requests) * 100 if total_accepted_requests > 0 else 0

class AdRequest(db.Model):
    __tablename__ = 'ad_requests'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
    message = db.Column(db.String(500),nullable=False)
    requirements = db.Column(db.String(500),nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')   # 'Pending', 'Accepted', 'Rejected', 'done
    influencer = db.relationship('Influencer', backref=db.backref('ad_requests', lazy=True))
    # campaign = db.relationship('Campaign', backref=db.backref('ad_requests',lazy=True))
    

# class Negotiation(db.Model):
#     __tablename__ = 'negotiations'
#     id = db.Column(db.Integer, primary_key=True)
#     ad_request_id = db.Column(db.Integer, db.ForeignKey('ad_requests.id'), nullable=False)
#     new_payment_amount = db.Column(db.Float, nullable=False)
#     message = db.Column(db.String(500))
#     status = db.Column(db.String(50),default='pending') 
#     ad_request = db.relationship('AdRequest', backref=db.backref('negotiations', lazy=True))


class CampaignRequest(db.Model):
    __tablename__ = 'campaign_requests'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50),nullable=False)  # 'Pending', 'Accepted', 'Rejected'
    campaign = db.relationship('Campaign', backref=db.backref('campaign_requests', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('campaign_requests', lazy=True))


with app.app_context():
    db.create_all()

    admin = User.query.filter_by(role='admin').first()
    if not admin:
        password_hash = generate_password_hash('admin')
        admin = User(username='admin', password_hash=password_hash, email='admin@gmail.com', role='admin')
        db.session.add(admin)
        db.session.commit()