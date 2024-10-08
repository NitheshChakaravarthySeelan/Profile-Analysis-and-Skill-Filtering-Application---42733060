import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import PyPDF2
import spacy
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '1234' 
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

nlp = spacy.load("en_core_web_trf")
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
qa_pipeline = pipeline('question-answering', model='deepset/roberta-base-squad2')

tokenizer = AutoTokenizer.from_pretrained("bhadresh-savani/bert-base-uncased-emotion")
llm_model = AutoModelForSequenceClassification.from_pretrained("bhadresh-savani/bert-base-uncased-emotion")

DATABASE = 'profiles.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS resumes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        skills TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT
                    )''')
    conn.commit()
    conn.close()

def is_logged_in():
    return 'user' in session

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_skills(text):
    skills_question = "What are the skills mentioned in the resume?"
    skills = qa_pipeline({'context': text, 'question': skills_question})['answer']
    return [skill.strip() for skill in skills.split(',')]

def extract_name_and_skills(text):
    doc = nlp(text)
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not name:
            name = ent.text
    skills_list = extract_skills(text)
    return name, skills_list

def store_profile_in_db(name, skills):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO resumes (name, skills) VALUES (?, ?)", 
                   (name, ', '.join(skills)))
    conn.commit()
    conn.close()

def get_all_profiles():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes")
    profiles = cursor.fetchall()
    conn.close()
    return profiles

def delete_profile(profile_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resumes WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()

def update_profile(profile_id, name, skills):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE resumes SET name = ?, skills = ? WHERE id = ?", 
                   (name, ', '.join(skills), profile_id))
    conn.commit()
    conn.close()

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def filter_candidates(job_description):
    job_embedding = model.encode(job_description)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, skills FROM resumes")
    resume_data = cursor.fetchall()
    conn.close()

    matched_candidates = []
    for name, skills in resume_data:
        candidate_skills = skills if skills else " "  
        candidate_embedding = model.encode(candidate_skills)
        similarity_score = cosine_similarity([job_embedding], [candidate_embedding])[0][0] * 100

        if similarity_score > 20:
            matched_candidates.append((name, skills, similarity_score))

    return matched_candidates

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user'] = user[1]
            session['role'] = user[3]
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('candidate_dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' in session and session['role'] == 'admin':
        profiles = get_all_profiles()
        return render_template('admin_dashboard.html', profiles=profiles)
    return redirect(url_for('login'))

@app.route('/candidate_dashboard')
def candidate_dashboard():
    if 'user' in session and session['role'] == 'candidate':
        return render_template('candidate_dashboard.html')
    return redirect(url_for('login'))

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return redirect(request.url)

    file = request.files['resume']
    if file.filename == '':
        return redirect(request.url)
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    extracted_text = extract_text_from_pdf(file_path)
    name, skills = extract_name_and_skills(extracted_text)
    
    if not name:
        name = "Unknown"
    
    store_profile_in_db(name, skills)
    os.remove(file_path)
    flash('Resume uploaded and processed successfully!')

    return redirect(url_for('index'))

@app.route('/filter_candidates', methods=['POST'])
def filter_candidates_route():
    job_description = request.form['job_description']
    matched_candidates = filter_candidates(job_description)
    return render_template('result.html', matched_candidates=matched_candidates)

@app.route('/admin')
def admin():
    profiles = get_all_profiles()
    return render_template('admin.html', profiles=profiles)

@app.route('/delete_profile/<int:profile_id>', methods=['GET', 'POST'])
def delete_profile_route(profile_id):
    if request.method == 'POST':
        delete_profile(profile_id)
        flash('Profile deleted successfully!')
    return redirect(url_for('admin'))

@app.route('/edit_profile/<int:profile_id>', methods=['GET', 'POST'])
def edit_profile_route(profile_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes WHERE id = ?", (profile_id,))
    profile = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        skills = request.form['skills'].split(',')
        update_profile(profile_id, name, skills)
        flash('Profile updated successfully!')
        return redirect(url_for('admin'))
    
    return render_template('edit_profile.html', profile=profile)

@app.route('/logout')
def logout_user():
    session.pop('user', None)  
    session.pop('role', None)  
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/view_profiles')
def view_profiles():
    profiles = get_all_profiles()  
    return render_template('view_profiles.html', profiles=profiles)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
