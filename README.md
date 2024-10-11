# Profile-Analysis-and-Skill-Filtering-Application---42733060
Here’s the `README.md` file for your profile analysis and skill filtering application:

---

# Profile Analysis and Skill Filtering Application

## Description
This is a web-based profile analysis and skill filtering application built using Flask, SQLite, and machine learning models. It allows recruiters to upload candidate resumes, extract skills and other relevant information, and match candidates with job descriptions based on a skill-filtering algorithm. The application includes an admin and candidate dashboard for easy management and profile review.

## Features
- **User Authentication**: Users (admin and candidates) can log in to access specific dashboards.
- **Resume Uploading**: Candidates can upload resumes, which are processed to extract the name and skills using NLP models.
- **Skill Extraction**: Skills from resumes are extracted using a question-answering model (`deepset/roberta-base-squad2`).
- **Profile Matching**: The system matches job descriptions with the candidates' skills using **SentenceTransformers** and **FAISS** for similarity search.
- **Admin Dashboard**: Admins can view, edit, and delete profiles, and filter candidates based on job descriptions.
- **Database**: The data is stored in an SQLite database, which holds user credentials and profiles (names and skills).

## Technologies Used
- **Flask**: Web framework for creating the web application.
- **SQLite**: Database for storing user profiles and login credentials.
- **PyPDF2**: For extracting text from uploaded PDF resumes.
- **spaCy**: For extracting personal details (name) from the resumes.
- **SentenceTransformers**: For embedding resumes and job descriptions into vectors for skill matching.
- **FAISS**: Used for efficient similarity search during candidate matching.
- **Hugging Face Transformers**: For implementing the question-answering pipeline to extract skills from resumes.
- **Werkzeug**: For secure file handling and password hashing.

## Setup Instructions

### Prerequisites
- Python 3.x installed
- Required Python packages installed. You can install them by running:

    ```bash
    pip install flask PyPDF2 spacy sentence-transformers torch transformers scikit-learn
    ```

- **spaCy model**: Download the required spaCy model:

    ```bash
    python -m spacy download en_core_web_trf
    ```

### Database Setup
1. To initialize the SQLite database, run the following Python script:

    ```python
    import sqlite3
    from werkzeug.security import generate_password_hash

    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    
    # Create a candidate login credential
    username = 'candidate'
    password = 'candidate123'
    hashed_password = generate_password_hash(password)

    # Insert candidate credentials
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                   (username, hashed_password, 'candidate'))

    conn.commit()
    conn.close()
    ```

2. You can add more users (admin or candidates) in a similar way using the SQLite database. Admin role should be set as `'admin'` and candidate role as `'candidate'`.

### Running the Application
1. Clone the repository or download the project files.
2. Navigate to the project directory and initialize the database by running the Flask application:

    ```bash
    python app.py
    ```

3. Open your web browser and go to `http://127.0.0.1:5000/` to view the application.

### Directory Structure
```
.
├── app.py                  # Main Flask application
├── templates/              # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── candidate_dashboard.html
│   ├── result.html
│   └── ...
├── uploads/                # Directory to store uploaded resumes
├── profiles.db             # SQLite database file
└── README.md               # This file
```

## Application Flow
1. **Login**: 
   - Admins and candidates can log in with their credentials. The default candidate login is:
     - Username: `candidate`
     - Password: `candidate123`

2. **Upload Resume**: 
   - Candidates can upload their resumes in PDF format. The application extracts the text, identifies the candidate's name and skills, and stores them in the database.

3. **Admin Dashboard**:
   - Admin users can view all uploaded profiles, edit, or delete profiles. They can also filter candidates by job description.

4. **Candidate Dashboard**:
   - Candidates can view their uploaded resumes and the extracted skills.

## Important Routes
- `/` – Home page
- `/login` – User login page
- `/upload_resume` – Resume uploading for candidates
- `/admin_dashboard` – Admin dashboard to manage profiles
- `/filter_candidates` – Admin can filter candidates based on job description

--- 

This `README.md` provides a clear guide for setting up, using, and understanding the functionality of the profile analysis and skill filtering application.
