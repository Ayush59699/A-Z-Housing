from flask import render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import app,db
from models import User
from models import Service, Professional, Customer


# Landing page
@app.route("/")
def index():
    return render_template('index.html')



# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials, please try again.")
            return redirect(url_for('login'))

        session["user_id"] = user.id
        session["user_name"] = user.name

        flash("Login successful.")
        return redirect(url_for('userDash'))  #Dashboard ka url
    
    return render_template("login.html")


# Personal User Dashboard
@app.route('/userDash')
def userDash():
    user_id = session.get('user_id')   
    user = User.query.get(user_id)   

    if user is None:
        flash("You need to log in first!", "warning")
        return redirect(url_for('login'))  

    return render_template('userDash.html', user=user)   



# registration Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email address already exists.")
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User registered successfully!", "success")
            return redirect(url_for('login')) 
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('register'))

    return render_template("register.html")

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from the session
    flash("You have been logged out!", "info")
    return redirect(url_for('index'))  # Redirect to the home page after logout

