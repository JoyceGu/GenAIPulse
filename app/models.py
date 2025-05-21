from datetime import datetime
from app import db

# Association tables for many-to-many relationships
library_categories = db.Table('library_categories',
    db.Column('library_id', db.Integer, db.ForeignKey('library.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Library(db.Model):
    """Model for AI libraries/packages"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    language = db.Column(db.String(50), index=True)
    current_version = db.Column(db.String(50))
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    repository_url = db.Column(db.String(255))
    documentation_url = db.Column(db.String(255))
    package_url = db.Column(db.String(255))
    popularity_score = db.Column(db.Float, default=0.0)
    monthly_downloads = db.Column(db.Integer, default=0)
    github_stars = db.Column(db.Integer, default=0)
    
    # Relationships
    categories = db.relationship('Category', secondary=library_categories, 
                              lazy='subquery', backref=db.backref('libraries', lazy=True))
    versions = db.relationship('Version', backref='library', lazy=True)
    
    def __repr__(self):
        return f'<Library {self.name}>'

class Category(db.Model):
    """Model for library categories"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    category_type = db.Column(db.String(50))  # 'functional', 'application', etc.
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Version(db.Model):
    """Model for library version history"""
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=False)
    version_number = db.Column(db.String(50), nullable=False)
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    release_notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Version {self.version_number} of Library {self.library_id}>'

class User(db.Model):
    """Model for application users"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Subscription(db.Model):
    """Model for user subscriptions to library updates"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    language = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Either category or language can be null, but not both
    __table_args__ = (
        db.CheckConstraint('category_id IS NOT NULL OR language IS NOT NULL', name='check_subscription_type'),
    )
    
    def __repr__(self):
        return f'<Subscription {self.id} for User {self.user_id}>' 