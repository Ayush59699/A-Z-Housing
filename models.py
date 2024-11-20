from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()
 
class Admin(UserMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80))

class Customer(UserMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80))
    address = db.Column(db.String(80))  
    pincode = db.Column(db.Integer) 
    is_blocked=db.Column(db.Boolean, default=False) 



class Professional(UserMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80))
    service_name = db.Column(db.String(80))
    experience = db.Column(db.Integer)
    document = db.Column(db.String(200))  
    address = db.Column(db.String(200))
    pincode = db.Column(db.Integer)
    is_valid= db.Column(db.Boolean, nullable=True)
    is_blocked=db.Column(db.Boolean, default=False)

class Service(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80))
    price = db.Column(db.Float)
    description = db.Column(db.String(200))
    time_required = db.Column(db.String(50))

class ServiceRequest(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = db.Column(UUID(as_uuid=True), db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(UUID(as_uuid=True), db.ForeignKey('professional.id'), nullable=True)
    date_of_request = db.Column(db.String(50), nullable=False)  
    date_of_completion = db.Column(db.String(50), nullable=True)  
    status = db.Column(db.String(20), default="requested")  # assigned/closed/ requested
    remarks = db.Column(db.String(200), nullable=True)
    rating = db.Column(db.Integer)
    
    service = db.relationship('Service', backref='service_requests')
    customer = db.relationship('Customer', backref='service_requests')
    professional = db.relationship('Professional', backref='service_requests')
    
