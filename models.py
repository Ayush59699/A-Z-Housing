from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import os, uuid
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



class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float)
    description = db.Column(db.String(200))
    time_required = db.Column(db.String(50))

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True)
    date_of_request = db.Column(db.String(50))
    status = db.Column(db.String(20), default="requested")
    remarks = db.Column(db.String(200))
