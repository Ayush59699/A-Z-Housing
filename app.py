from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Admin, Customer, Professional, Service, ServiceRequest
from forms import LoginForm, RegisterForm, ServiceForm,ProfessionalSignupForm
import os, uuid
from werkzeug.utils import secure_filename


app = Flask(__name__)

UPLOAD_FOLDER='uploads/'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"]=16 * 1024 * 1024
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

basedir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =  f"sqlite:///{os.path.join(basedir, 'instance', 'db.sqlite')}"
app.config['SECRET_KEY'] = 'my-secret-key'

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        user_uuid=uuid.UUID(user_id)
        return db.session.get(Admin, user_uuid) or \
            db.session.get(Customer, user_uuid) or \
            db.session.get(Professional, user_uuid)
    except ValueError:
        return None
    

with app.app_context():
    db.create_all()

    admin_email = 'admin@gmail.com'
    admin_user = Admin.query.filter_by(email=admin_email).first()
    
    if not admin_user:
        admin_user = Admin(name='admin', email=admin_email, password='123456')
        db.session.add(admin_user)
        db.session.commit()




@app.route('/')
def home():
    return render_template('home.html')
 


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.email.data)

        user = Admin.query.filter_by(email=form.email.data).first() 
        if not user:
            user=Customer.query.filter_by(email=form.email.data).first() 
        if not user:
            user= Professional.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)

            if isinstance(user, Admin):
                return redirect(url_for('admin_dashboard'))
            elif isinstance(user, Customer):
                return redirect(url_for('customer_dashboard'))
            elif isinstance(user, Professional):
                return redirect(url_for('professional_dashboard'))
        print('Login Falied ', 'danger')

    return render_template('login.html', form=form)


@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = Customer(
            name=form.fullname.data,
            email=form.email.data,
            password=form.password.data,  # Make sure to hash this in production
            address=form.address.data,
            pincode=form.pincode.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/register-professional', methods=['GET', 'POST'])
def register_professional():
    form = ProfessionalSignupForm()
    if form.validate_on_submit():

        document_filename = secure_filename(form.document.data.filename) 
        document_path = os.path.join(app.config['UPLOAD_FOLDER'], document_filename)
        form.document.data.save(document_path)  

        new_professional = Professional(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,  
            service_name=form.service_name.data,
            experience=form.experience.data,
            document=document_path,  
            address=form.address.data,
            pincode=form.pincode.data
        )
        db.session.add(new_professional)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))  

    return render_template('register_professional.html', form=form)




@app.route('/admin/dashboard/search')
@login_required
def admin_search():
    return render_template('admin_search.html')


@app.route('/admin/dashboard/summary')
@login_required
def admin_summary():
    return render_template('admin_summary.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    print('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    customers = Customer.query.all()
    professionals = Professional.query.all()
    return render_template('admin_dashboard.html',admin=current_user, customers=customers, professionals=professionals)



@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    return render_template('customer_dashboard.html', customer=current_user)



@app.route('/professional/dashboard')
@login_required
def professional_dashboard():
    return render_template('professional_dashboard.html', professional=current_user)


@app.route('/service/new', methods=['GET', 'POST'])
@login_required
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        new_service = Service(name=form.name.data, price=form.price.data, description=form.description.data)
        db.session.add(new_service)
        db.session.commit()
        flash('Service added successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_service.html', form=form)

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__=='__main__':
    app.run(debug=True)
