import os
import subprocess
import pickle
import sqlite3
from flask import Flask, request

app = Flask(__name__)

# Security vulnerability: Hardcoded credentials
DB_PASSWORD = "super_secret_password123"

# Security vulnerability: Unsafe deserialization
def load_user_data(data):
    return pickle.loads(data)  # Dangerous!

# Security vulnerability: SQL injection
def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"  # SQL injection vulnerable
    cursor.execute(query)
    return cursor.fetchone()

# Security vulnerability: Command injection
def run_command(command):
    return subprocess.check_output(command, shell=True)  # Dangerous!

# Security vulnerability: Insecure file handling
def read_file(filename):
    return open(filename).read()  # No proper file handling

# Security vulnerability: Debug mode in production
app.debug = True

if __name__ == "__main__":
    app.run() 