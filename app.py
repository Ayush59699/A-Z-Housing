from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_ , func
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Admin, Customer, Professional, Service, ServiceRequest
from forms import LoginForm, RegisterForm, ServiceForm,ProfessionalSignupForm
import os, uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from collections import Counter


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
            Service(name='A.C. Repair', price=100.0, description='A.C. Cleaning and maintenance.', time_required='2 hours'),
            Service(name='Cooking', price=50.0, description='Delicious Cooking service, 3X/Day, 5 Days a week', time_required='3 hour'),
            Service(name='Cleaning', price=100.0, description='House Cleaning and maintainance', time_required='2 hour'),
            Service(name='Gardening', price=120.0, description='Garden renovation and other gardening works', time_required='4 hour'),
            Service(name='Saloon', price=110.0, description='Home saloon package', time_required='2 hour')
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
            Professional(name='Prakash Shukla', email='prakash@gmail.com', password='123456', service_name='Cooking', experience=5, document='Assignment4.pdf', address='789 Oak St', pincode=789012),
            Professional(name='Lalit Singh', email='lalit@gmail.com', password='123456', service_name='Cleaning', experience=3, document='electrical_cert.pdf', address='321 Pine St', pincode=210987),
            Professional(name='Amarnath Yadav', email='amar@gmail.com', password='123456', service_name='A.C. Repair', experience=3, document='ac_cert.pdf', address='3asihkdne St', pincode=210987),
            Professional(name='Aman Singh', email='aman@gmail.com', password='123456', service_name='Saloon', experience=3, document='Saloon_cert.pdf', address='kasgjd St', pincode=210987),
            Professional(name='Sumit Srivastava', email='sumit@gmail.com', password='123456', service_name='Gardening', experience=3, document='garden_cert.pdf', address='ashdhjg St', pincode=210987)    
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
            password=form.password.data,  
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

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# -------------------------------------------------------------------------------

@app.route('/admin/dashboard') #ADMIN DASHBOARD HOME
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        return redirect(url_for('home')) 
    customers = Customer.query.all()
    newProfessionals=Professional.query.filter(Professional.is_valid.is_(None)).all()
    acceptedProfessionals=Professional.query.filter(Professional.is_valid==True).all()
    rejectedProfessionals=Professional.query.filter(Professional.is_valid==False).all()
    services=Service.query.all()
    ser_req=ServiceRequest.query.join(Professional, isouter=True).all()
    
    return render_template('admin/admin_dashboard.html',ser_req=ser_req , 
                           admin=current_user, 
                           customers=customers, 
                           professionals=acceptedProfessionals,
                           newPros=newProfessionals, 
                           rejectedProfessionals=rejectedProfessionals,
                           services=services)


# Approve professional
@app.route('/admin/dashboard/approve_professional/<uuid:professional_id>', methods=["POST"])
@login_required
def approve_professional(professional_id):
    professional=Professional.query.get(professional_id)
    if professional:
        professional.is_valid=True
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Reject Professional
@app.route('/admin/dashboard/reject_professional/<uuid:professional_id>', methods=["POST"])
@login_required
def reject_professional(professional_id):
    professional=Professional.query.get(professional_id)
    if professional:
        professional.is_valid=False
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Delete professional's approval request
@app.route('/admin/dashboard/delete_professional/<uuid:professional_id>', methods=['POST'])
@login_required
def delete_professional(professional_id):
    professional=Professional.query.filter_by(id=professional_id).delete()
    print("Rejected professional record", professional)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# View Pro Details
@app.route('/admin/dashboard/view_pro_details/<uuid:professional_id>')
@login_required
def view_pro_details(professional_id):
    if not isinstance(current_user, Admin):
        return redirect(url_for('home'))
    
    professional = Professional.query.get(professional_id)
    if not professional:
        return redirect(url_for('admin_dashboard'))  
    return render_template('admin/validate_pro_details.html', admin=current_user,professional=professional)


#Block Professional
@app.route('/admin/dashboard/block_professional/<uuid:professional_id>', methods=['POST'])
@login_required
def block_professional(professional_id):
    if not isinstance(current_user, Admin):
        return redirect(url_for('home'))
    
    guy=Professional.query.get(professional_id)
    if guy:
        guy.is_blocked=True
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Unblock Professional
@app.route('/admin/dashboard/unblock_professional/<uuid:professional_id>', methods=['POST'])
@login_required
def unblock_professional(professional_id):
    if not isinstance(current_user,Admin):
        return redirect(url_for('home'))
    guy=Professional.query.get(professional_id)
    if guy:
        guy.is_blocked=False
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Block Customer
@app.route('/admin/dashboard/block_customer/<uuid:customer_id>', methods=["POST"])
@login_required
def block_customer(customer_id):
    guy = Customer.query.get(customer_id)
    if guy:
        guy.is_blocked = True
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Unblock Customer
@app.route('/admin/dashboard/unblock_customer/<uuid:customer_id>', methods=["POST"])
@login_required
def unblock_customer(customer_id):
    guy = Customer.query.get(customer_id)
    if guy:
        guy.is_blocked = False
        db.session.commit()
    return redirect(url_for('admin_dashboard'))











@app.route('/admin/dashboard/validate_pro_details/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads'), filename)




@app.route('/admin/dashboard/search', methods=["GET","POST"]) # ADMIN DASHBOARD SEARCH
@login_required
def admin_search():
    if not isinstance(current_user, Admin):
        return redirect(url_for('home'))
    
    results = []
    result_heading = ""
    search_field = request.form.get("search_field")
    search_text = request.form.get("search_text")

    if search_field and search_text:
        if search_field == "services":
            result_heading = "Services"
            results = Service.query.filter(Service.name.ilike(f"%{search_text}%")).all()

        elif search_field == "professionals":
            result_heading = "Professionals"
            results = Professional.query.filter(Professional.name.ilike(f"%{search_text}%")).all()

        elif search_field == "customers":
            result_heading = "Customers"
            results = Customer.query.filter(Customer.name.ilike(f"%{search_text}%")).all()

        elif search_field == "service_requests":
            result_heading = "Service Requests"
            results = (
                ServiceRequest.query
                .join(Service, ServiceRequest.service_id == Service.id)
                .join(Customer, ServiceRequest.customer_id == Customer.id)
                .filter(
                    (Service.name.ilike(f"%{search_text}%")) |
                    (ServiceRequest.status.ilike(f"%{search_text}%")) |
                    (Service.description.ilike(f"%{search_text}%"))
                )
                .all())

    return render_template('admin/admin_search.html', aname=current_user,
        results=results, result_heading=result_heading, search_field=search_field
    )
    

@app.route('/admin/dashboard/summary', methods=["GET","POST"]) # ADMIN DASHBOARD Summary
@login_required
def admin_summary():
    
    
    if not isinstance(current_user, Admin):
        return redirect(url_for('home'))
    
    status_data = {
        "Requested": ServiceRequest.query.filter_by(status="requested").count(),
        "Accepted": ServiceRequest.query.filter_by(status="accepted").count(),
        "Closed": ServiceRequest.query.filter_by(status="Closed").count(),
    }

    ratings_data = {
        "1 star": ServiceRequest.query.filter(ServiceRequest.rating == 1).count(),
        "2 stars": ServiceRequest.query.filter(ServiceRequest.rating == 2).count(),
        "3 stars": ServiceRequest.query.filter(ServiceRequest.rating == 3).count(),
        "4 stars": ServiceRequest.query.filter(ServiceRequest.rating == 4).count(),
        "5 stars": ServiceRequest.query.filter(ServiceRequest.rating == 5).count(),
        "Not Rated": ServiceRequest.query.filter(ServiceRequest.rating == None).count(),  # Ratings not given
    }

    sr=ServiceRequest.query.all()
    sc=Counter([r.service.name for r in sr])
    services=list(sc.keys())
    requests_count=list(sc.values())

    avg_ratings_query = (
        db.session.query(
            Service.name,
            func.avg(ServiceRequest.rating).label('avg_rating')
        )
        .join(Service, Service.id == ServiceRequest.service_id)
        .filter(ServiceRequest.rating.isnot(None)) 
        .group_by(Service.name)
        .all()
    )
    srv=[ row[0] for row in avg_ratings_query]
    avgr=[ row[1] for row in avg_ratings_query]



    return render_template("admin/admin_summary.html", aname=current_user,
                           status_data=status_data,
                            ratings_data=ratings_data,
                             services=services,
                              requests_count=requests_count, rat_services=srv,
                               avg_ratings=avgr )


# ------------------------------------------------------------------------------ 

@app.route('/customer/dashboard') # CUSTOMER DASH HOME
@login_required
def customer_dashboard():
    if not isinstance(current_user, Customer):
        return redirect(url_for('home'))
    
    
    service_history = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    return render_template('customer/customer_dashboard.html', customer=current_user, service_history=service_history)


@app.route('/customer/dashboard/search', methods=["GET","POST"]) # CUSTOMER DASH search
@login_required
def customer_search():
    if not isinstance(current_user, Customer):
        return redirect(url_for('home'))
    
    results=[]
    sq=request.args.get('q','')

    if sq:
        results=Service.query.filter(
            or_(
                Service.name.ilike(f"%{sq}%"),
                Service.description.ilike(f"%{sq}%")
            )
        ).all()

    return render_template('customer/customer_search.html', customer=current_user,
                           results=results,
                           sq=sq)





@app.route('/customer/dashboard/summary') # CUSTOMER DASH summary
@login_required
def customer_summary():
    if not isinstance(current_user, Customer):
        return redirect(url_for('home'))
    
    status_data = {
        "Requested": ServiceRequest.query.filter_by(customer_id=current_user.id, status="requested").count(),
        "Accepted": ServiceRequest.query.filter_by(customer_id=current_user.id, status="accepted").count(),
        "Closed": ServiceRequest.query.filter_by(customer_id=current_user.id, status="Closed").count(),
    }

    return render_template('customer/customer_summary.html', customer=current_user, status_data=status_data)


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
        Service.name.ilike('%A.C.%'),
        Service.description.ilike('%A.C.%')
        )
    ).all()
    print(cs2)
    return render_template("customer/ac_services.html", services=cs2, customer=current_user)


@app.route('/customer/dashboard/cooking_services',)
@login_required
def cooking_services():
    cs2=Service.query.filter(
        or_(
        Service.name.ilike('%Cook%'),
        Service.description.ilike('%Cook%')
        )
    ).all()
    print(cs2)
    return render_template("customer/cooking_services.html", services=cs2, customer=current_user)

@app.route('/customer/dashboard/saloon_services',)
@login_required
def saloon_services():
    cs2=Service.query.filter(
        or_(
        Service.name.ilike('%Saloon%'),
        Service.description.ilike('%Hair%')
        )
    ).all()
    print(cs2)
    return render_template("customer/saloon_services.html", services=cs2, customer=current_user)

@app.route('/customer/dashboard/garden_services',)
@login_required
def garden_services():
    cs2=Service.query.filter(
        or_(
        Service.name.ilike('%Garden%'),
        Service.description.ilike('%Garden%')
        )
    ).all()
    print(cs2)
    return render_template("customer/garden_services.html", services=cs2, customer=current_user)


@app.route("/customer/dashboard/book/<uuid:service_id>", methods=["GET", "POST"])
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

    return render_template("customer/book_service.html", service=service, customer=current_user)

 
# Closing Request button route
@app.route('/customer/dashboard/close_req/<uuid:request_id>', methods=['GET', 'POST'])
def close_service_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    service_request.date_of_completion = datetime.now().strftime('%Y-%m-%d')
    
    if service_request.status=='Closed':
        print("This request is already closed!!")
        return redirect(url_for('customer_dashboard'))
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        remarks = request.form.get('remarks')
        
        service_request.status = 'Closed'
        #service_request.date_of_completion = datetime.now()
        
        service_request.rating = rating  
        service_request.remarks = remarks  
        db.session.commit()
        
        flash('Service request closed successfully!', 'success')
        return redirect(url_for('customer_dashboard'))  

    professional=None
    if service_request.professional_id:
        professional=Professional.query.get(service_request.professional_id)

    return render_template('customer/close_service_request.html', 
                           service_request=service_request,
                           professional=professional
                           )


# ----------------------------------------------------------------------------
# ------------------------------------------------------------------------------

@app.route('/professional/dashboard')  # PRO DASH HOME
@login_required
def professional_dashboard():
    if not isinstance(current_user, Professional):
        return redirect(url_for('home'))
    
    sr=ServiceRequest.query.join(Service).filter(
        or_( 
            Service.name.ilike(f"%{current_user.service_name}%"),
            Service.description.ilike(f"%{current_user.service_name}%")
        ),
        ServiceRequest.professional_id.is_(None), # SHOWS ONLY unassigned requests
        ServiceRequest.status != 'Closed'
    ).all()

    ar = ServiceRequest.query.filter_by(professional_id=current_user.id, status='accepted').all()
    rr = ServiceRequest.query.filter_by(professional_id=current_user.id, status='declined').all()

    return render_template('professional/professional_dashboard.html', 
                           professional=current_user, 
                           service_requests=sr,
                           accepted_requests=ar,
                           rejected_requests=rr) 

# Accept request
@app.route('/professional/dashboard/request/<uuid:request_id>/accept', methods=["POST"])
def accept_request(request_id):
    request = ServiceRequest.query.get(request_id)
    if request and request.professional_id is None:
        request.professional_id = current_user.id
        request.status = 'accepted'
        db.session.commit()
        flash("Service request accepted.")
    return redirect(url_for('professional_dashboard'))

# Decline request
@app.route('/professional/dashboard/request/<uuid:request_id>/decline', methods=["POST"])
def decline_request(request_id):
    request = ServiceRequest.query.get(request_id)
    if request and request.professional_id is None:
        request.status = 'declined'
        db.session.commit()
        flash("Service request declined.")
    return redirect(url_for('professional_dashboard'))


@app.route('/professional/dashboard/search', methods=["GET","POST"]) 
@login_required
def professional_search():
    if not isinstance(current_user, Professional):
        return redirect(url_for('home'))
    
    query = ServiceRequest.query.join(Customer).join(Service)  
    search_params = {}

    search_field = request.form.get("search_field")
    search_text = request.form.get("search_text")

    if search_field and search_text and search_text.strip() :
        if search_field == 'date_of_request':
            search_params['date_of_request'] = search_text
            query = query.filter(ServiceRequest.date_of_request == search_text)

        elif search_field == 'address':
            search_params['address'] = search_text
            query = query.filter(Customer.address.ilike(f"%{search_text}%"))

        elif search_field == 'pincode':
            if search_text.isdigit():
                search_params['pincode'] = int(search_text)
                query = query.filter(Customer.pincode == int(search_text))
            else:
                flash("Invalid Pincode")
                return redirect(url_for('professional_search'))
    else:
        flash("Enter search Text"," warning")
        results=[]
        return render_template('professional/professional_search.html', 
                               professional=current_user, results=results, 
                               search_params=search_params)


    query=query.filter(Service.name == current_user.service_name)
    results = query.all()
    return render_template('professional/professional_search.html', professional=current_user, 
                           results=results,
                           search_params=search_params) 


@app.route('/professional/dashboard/summary') 
@login_required
def professional_summary():
    if not isinstance(current_user, Professional):
        return redirect(url_for('home'))
    
    service_request_counts = (
        db.session.query(
            ServiceRequest.status, 
            db.func.count(ServiceRequest.id)
        )
        .filter(ServiceRequest.professional_id == current_user.id)
        .group_by(ServiceRequest.status)
        .all()
    )
    status_data = {status: count for status, count in service_request_counts}
    
    rating_counts = (
        db.session.query(
            ServiceRequest.rating,
            db.func.count(ServiceRequest.id)
        )
        .filter(ServiceRequest.professional_id == current_user.id)
        .filter(ServiceRequest.rating.isnot(None))  # Exclude null ratings
        .group_by(ServiceRequest.rating)
        .all()
    )
    ratings_data = {str(rating): count for rating, count in rating_counts}

    return render_template('professional/professional_summary.html', 
                           status_data=status_data,
                           professional=current_user,
                           ratings_data=ratings_data) 

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















if __name__=='__main__':
    app.run(debug=True)
