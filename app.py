from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
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
    

with app.app_context(): # CREATED DEFAULT DATABASE ENTRIES + Default Admin
    db.create_all()

    admin_email = 'admin@gmail.com'
    admin_user = Admin.query.filter_by(email=admin_email).first()
    if not admin_user:
        admin_user = Admin(name='admin', email=admin_email, password='123456')
        db.session.add(admin_user)

    if Service.query.count()==0:
        ds=[
            Service(name='A.C. Servicing', price=100.0, description='A.C. servicing and maintenance.', time_required='2 hours'),
            Service(name='Plumbing', price=50.0, description='General plumbing services.', time_required='1 hour')
        ]
        db.session.bulk_save_objects(ds)

    if Customer.query.count() == 0:
            dc = [
                Customer(name='Ayush Singh', email='ayush0987singh@gmail.com', password='123456', address='Ghosiyana Lucknow', pincode=226029),
                Customer(name='Rajan Singh', email='rajan@gmail.com', password='123456', address='VIT Chennai', pincode=654321)
            ]
            db.session.bulk_save_objects(dc)

    if Professional.query.count() == 0:
        dp = [
            Professional(name='Prakash Shukla', email='prakash@gmail.com', password='123456', service_name='Plumbing', experience=5, document='plumbing_cert.pdf', address='789 Oak St', pincode=789012),
            Professional(name='Lalit Singh', email='lalit@gmail.com', password='123456', service_name='Electrical', experience=3, document='electrical_cert.pdf', address='321 Pine St', pincode=210987)
        ]
        db.session.bulk_save_objects(dp)

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




@app.route('/logout')
@login_required
def logout():
    logout_user()
    print('You have been logged out.', 'success')
    return redirect(url_for('login'))

# -------------------------------------------------------------------------------

@app.route('/admin/dashboard') #ADMIN DASHBOARD HOME
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        return redirect(url_for('home')) 
    customers = Customer.query.all()
    professionals = Professional.query.all()
    services=Service.query.all()
    return render_template('admin/admin_dashboard.html',admin=current_user, customers=customers, professionals=professionals, services=services)

@app.route('/admin/dashboard/search', methods=["GET","POST"]) # ADMIN DASHBOARD SEARCH
@login_required
def admin_search():
    if not isinstance(current_user, Admin):
        return redirect(url_for('home'))
    
    return render_template("admin/admin_search.html")

@app.route('/admin/dashboard/summary', methods=["GET","POST"]) # ADMIN DASHBOARD SEARCH
@login_required
def admin_summary():
    if not isinstance(current_user, Admin):
        return redirect(url_for('home'))
    
    return render_template("admin/admin_summary.html")
 # -----------------------------------------------------------------------------
# ------------------------------------------------------------------------------ 

@app.route('/customer/dashboard') # CUSTOMER DASH HOME
@login_required
def customer_dashboard():
    if not isinstance(current_user, Customer):
        return redirect(url_for('home'))

    service_history = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    return render_template('customer/customer_dashboard.html', customer=current_user, service_history=service_history)

@app.route('/customer/dashboard/search') # CUSTOMER DASH search
@login_required
def customer_search():
    if not isinstance(current_user, Customer):
        return redirect(url_for('home'))
    return render_template('customer/customer_search.html', customer=current_user)

@app.route('/customer/dashboard/summary') # CUSTOMER DASH summary
@login_required
def customer_summary():
    if not isinstance(current_user, Customer):
        return redirect(url_for('home'))
    return render_template('customer/customer_summary.html', customer=current_user)



@app.route('/customer/dashboard/cleaning_services')
@login_required
def cleaning_services():
    cs1=Service.query.filter(
        or_(
        Service.name.ilike('%Cleaning%'),
        Service.description.ilike('%Cleaning%')
        )
    ).all()
    print(cs1)
    return render_template("customer/cleaning_services.html", services=cs1, customer=current_user)


@app.route('/customer/dashboard/ac_services')
@login_required
def ac_services():
    cs2=Service.query.filter(
        or_(
        Service.name.ilike('%A.c.%'),
        Service.description.ilike('%A.c.%')
        )
    ).all()
    print(cs2)
    return render_template("customer/ac_services.html", services=cs2, customer=current_user)









@app.route("/customer/dashboard/cleaning_services/book/<uuid:service_id>", methods=["GET", "POST"])
def book_service(service_id):
    service = Service.query.get(service_id)
    if request.method == "POST":
        customer_id = current_user.id  
        date_of_request = request.form.get("date_of_request")
        date_of_completion = request.form.get("date_of_completion")
        remarks = request.form.get("remarks")
        
        new_request = ServiceRequest(
            service_id=service.id,
            customer_id=customer_id,
            date_of_request=date_of_request,
            date_of_completion=date_of_completion,
            remarks=remarks
        )
        
        db.session.add(new_request)
        db.session.commit()
        flash("Service booked successfully!", "success")
        return redirect(url_for('customer_dashboard'))

    return render_template("customer/book_service.html", service=service)













# ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------

@app.route('/professional/dashboard')  # PRO DASH HOME
@login_required
def professional_dashboard():
    if not isinstance(current_user, Professional):
        return redirect(url_for('home'))
    return render_template('professional/professional_dashboard.html', professional=current_user) 

@app.route('/professional/dashboard/search') 
@login_required
def professional_search():
    if not isinstance(current_user, Professional):
        return redirect(url_for('home'))
    return render_template('professional/professional_search.html', professional=current_user) 

@app.route('/professional/dashboard/summary') 
@login_required
def professional_summary():
    if not isinstance(current_user, Professional):
        return redirect(url_for('home'))
    return render_template('professional/professional_summary.html', professional=current_user) 

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

@app.route('/admin/dashboard/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        time_required = request.form.get("time_required")

        new_service = Service(name=name, price=price, description=description, time_required=time_required)

        db.session.add(new_service)
        db.session.commit()
        print("SERVICE ADDED SUCCESSFULLY!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template("admin/add_service.html")

@app.route('/admin/dashboard/edit_service/<uuid:id>', methods=["GET", "POST"])
@login_required
def edit_service(id):
    service = Service.query.get_or_404(id)

    if request.method == "POST":
        service.name = request.form.get("name")
        service.price = request.form.get("price")
        service.description = request.form.get("description")
        service.time_required = request.form.get("time_required")

        db.session.commit()
        flash("Service updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template("admin/edit_service.html", service=service)

@app.route('/admin/dashboard/delete_service/<uuid:id>', methods=["POST"])
@login_required
def delete_service(id):
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    print("SERVICE DELETED SUCCESSFULLY!", "success")
    return redirect(url_for('admin_dashboard'))

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------













@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")





if __name__=='__main__':
    app.run(debug=True)
