from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config.from_object(Config)

# Koneksi ke database
def get_db_connection():
    conn = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    return conn

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        return redirect(url_for('dashboard'))
    else:
        flash('Username atau password salah')
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM guru")
    gurus = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('dashboard.html', gurus=gurus)

@app.route('/add_guru', methods=['GET', 'POST'])
def add_guru():
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        mata_pelajaran = request.form['mata_pelajaran']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO guru (nama, email, mata_pelajaran) VALUES (%s, %s, %s)", (nama, email, mata_pelajaran))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('add_guru.html')

@app.route('/edit_guru/<int:id>', methods=['GET', 'POST'])
def edit_guru(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        mata_pelajaran = request.form['mata_pelajaran']
                   cursor.execute("UPDATE guru SET nama = %s, email = %s, mata_pelajaran = %s WHERE id = %s", 
                          (nama, email, mata_pelajaran, id))
           conn.commit()
           cursor.close()
           conn.close()
           return redirect(url_for('dashboard'))

       cursor.execute("SELECT * FROM guru WHERE id = %s", (id,))
       guru = cursor.fetchone()
       cursor.close()
       conn.close()

       return render_template('edit_guru.html', guru=guru)

   @app.route('/delete_guru/<int:id>', methods=['POST'])
   def delete_guru(id):
       conn = get_db_connection()
       cursor = conn.cursor()
       cursor.execute("DELETE FROM guru WHERE id = %s", (id,))
       conn.commit()
       cursor.close()
       conn.close()
       return redirect(url_for('dashboard'))

   @app.route('/logout')
   def logout():
       session.pop('user_id', None)
       return redirect(url_for('home'))

   if __name__ == '__main__':
       app.run(debug=True)
