from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
import pytz

app = Flask(__name__)
app.secret_key =  os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///portfolio.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ist = pytz.timezone('Asia/Kolkata')

db = SQLAlchemy(app)
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'portfolio.db')


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(ist))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    github_link = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(ist))

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100))
    company = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    description = db.Column(db.Text)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(100))
    institution = db.Column(db.String(100))
    year = db.Column(db.String(100))
    marks = db.Column(db.Float, nullable=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    proficiency = db.Column(db.String(10)) 

@app.route('/', methods=["GET", "POST"])
def home():
    projects = Project.query.order_by(Project.date_created.desc()).all()
    about = "" 
    experiences = Experience.query.all()
    educations = Education.query.all()
    skills = Skill.query.all()

    if request.method == "POST":
        contact = Contact(
            name=request.form.get('name'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            message=request.form.get('message')
        )
        db.session.add(contact)
        db.session.commit()
        flash("Message sent successfully!", "success")
        return redirect(url_for('home'))

    return render_template(
        'index.html',
        projects=projects,
        about=about,
        experiences=experiences,
        educations=educations,
        skills=skills
    )

@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('admin/login.html')

@app.route('/admin/dashboard', methods=["GET", "POST"])
def admin_dashboard():
    if 'user' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('admin_login'))

    if request.method == "POST" and 'title' in request.form:
        new_project = Project(
            title=request.form['title'],
            description=request.form['description'],
            github_link=request.form['github_link']
        )
        db.session.add(new_project)
        db.session.commit()
        flash("Project added successfully", "success")
        return redirect(url_for('admin_dashboard'))

    projects = Project.query.order_by(Project.date_created.desc()).all()
    experiences = Experience.query.all()
    educations = Education.query.all()
    skills = Skill.query.all()
    return render_template('admin/dashboard.html',
        projects=projects,
        experiences=experiences,
        educations=educations,
        skills=skills
    )

@app.route('/admin/experience/add', methods=['POST'])
def add_experience():
    if 'user' not in session: return redirect(url_for('admin_login'))
    exp = Experience(
        role=request.form['title'],
        company=request.form['company'],
        duration=request.form['duration'],
        description=request.form['details']
    )
    db.session.add(exp)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/experience/delete/<int:id>')
def delete_experience(id):
    if 'user' not in session: return redirect(url_for('admin_login'))
    Experience.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/education/add', methods=['POST'])
def add_education():
    if 'user' not in session: 
        return redirect(url_for('admin_login'))

    edu = Education(
        degree=request.form['degree'],
        institution=request.form['institution'],
        year=request.form['year'],
        marks=request.form['percentage/cgpa']
    )
    db.session.add(edu)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/education/delete/<int:id>')
def delete_education(id):
    if 'user' not in session: return redirect(url_for('admin_login'))
    Education.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/skill/add', methods=['POST'])
def add_skill():
    if 'user' not in session: return redirect(url_for('admin_login'))
    skill = Skill(
        name=request.form['name'],
        proficiency=request.form['proficiency']
    )
    db.session.add(skill)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/skill/delete/<int:id>')
def delete_skill(id):
    if 'user' not in session: return redirect(url_for('admin_login'))
    Skill.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully", "info")
    return redirect(url_for('home'))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
