from flask import Flask, render_template, jsonify, request
import pandas as pd
import sqlite3
import json
import openai
from pdfminer.high_level import extract_text
from flask_cors import CORS

def load_config(file_name):
    """Load configuration from a JSON file."""
    try:
        with open(file_name) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

# Load configuration
config = load_config('config.json')

# Flask app setup
app = Flask(__name__)
CORS(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True

def connect_db():
    """Establish a connection to the SQLite database."""
    try:
        return sqlite3.connect(config.get("db_path", "app.db"))
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def verify_db_schema():
    """Verify and update database schema dynamically."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(filtered_jobs)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        required_columns = {
            "hidden": "INTEGER DEFAULT 0",
            "cover_letter": "TEXT",
            "resume": "TEXT",
            "applied": "INTEGER DEFAULT 0",
            "interview": "INTEGER DEFAULT 0",
            "rejected": "INTEGER DEFAULT 0",
        }
        for column, column_type in required_columns.items():
            if column not in existing_columns:
                cursor.execute(f"ALTER TABLE filtered_jobs ADD COLUMN {column} {column_type}")
                print(f"Added column: {column}")
        conn.commit()
        conn.close()

def fetch_all_jobs(hidden=False):
    """Fetch jobs from the database with optional filtering."""
    conn = connect_db()
    if conn:
        query = f"SELECT * FROM filtered_jobs WHERE hidden = {int(hidden)}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.sort_values(by='id', ascending=False).to_dict(orient='records')
    return []

def read_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        return extract_text(file_path)
    except Exception as e:
        print(f"PDF read error: {e}")
        return None

def validate_openai_key():
    """Check if OpenAI API key is available."""
    api_key = config.get("OpenAI_API_KEY")
    if not api_key:
        return jsonify({"error": "Missing OpenAI API key in configuration"}), 400
    openai.api_key = api_key
    return None

@app.route('/')
def home():
    """Render the home page."""
    jobs = fetch_all_jobs(hidden=False)
    return render_template('jobs.html', jobs=jobs)

@app.route('/get_all_jobs')
def get_all_jobs():
    """API to fetch all visible jobs."""
    return jsonify(fetch_all_jobs(hidden=False))

@app.route('/job_details/<int:job_id>')
def job_details(job_id):
    """Fetch job details by ID."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM filtered_jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        if job:
            column_names = [desc[0] for desc in cursor.description]
            conn.close()
            return jsonify(dict(zip(column_names, job)))
        conn.close()
    return jsonify({"error": "Job not found"}), 404

@app.route('/update_job/<int:job_id>', methods=['POST'])
def update_job(job_id):
    """Update job attributes dynamically."""
    data = request.json
    valid_columns = {"hidden", "applied", "interview", "rejected"}
    if not data or not set(data).intersection(valid_columns):
        return jsonify({"error": "Invalid update fields"}), 400
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        for column, value in data.items():
            if column in valid_columns:
                cursor.execute(f"UPDATE filtered_jobs SET {column} = ? WHERE id = ?", (value, job_id))
        conn.commit()
        conn.close()
        return jsonify({"success": "Job updated successfully"}), 200
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/get_cover_letter/<int:job_id>')
def get_cover_letter(job_id):
    """Fetch the cover letter for a specific job."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cover_letter FROM filtered_jobs WHERE id = ?", (job_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return jsonify({"cover_letter": result[0]})
    return jsonify({"error": "Cover letter not found"}), 404

@app.route('/get_resume/<int:job_id>', methods=['POST'])
def get_resume(job_id):
    """Generate and store a tailored resume for a specific job."""
    openai_error = validate_openai_key()
    if openai_error:
        return openai_error
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT job_description, title, company FROM filtered_jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        conn.close()
        if job:
            job_data = dict(zip(["job_description", "title", "company"], job))
            resume_text = read_pdf(config.get("resume_path", ""))
            if not resume_text:
                return jsonify({"error": "Resume file not readable"}), 400
            try:
                prompt = (
                    f"Tailor the resume for the job: {job_data['title']} at {job_data['company']}.\n"
                    f"Job description: {job_data['job_description']}\n"
                    f"Current resume: {resume_text}"
                )
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
                )
                tailored_resume = completion.choices[0].message.content
                conn = connect_db()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE filtered_jobs SET resume = ? WHERE id = ?", (tailored_resume, job_id))
                    conn.commit()
                    conn.close()
                return jsonify({"resume": tailored_resume}), 200
            except Exception as e:
                return jsonify({"error": f"OpenAI error: {e}"}), 500
    return jsonify({"error": "Job not found"}), 404

if __name__ == "__main__":
    verify_db_schema()
    app.run(debug=True, port=5001)
