from flask import Flask, request, redirect, url_for, render_template, send_file
import sqlite3
import os
from datetime import datetime, date
import csv

app = Flask(__name__)
DATABASE = 'expenses.db'

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM expenses ORDER BY date DESC')
    expenses = c.fetchall()
    
    # Calculate total expense
    c.execute('SELECT SUM(amount) FROM expenses')
    total_expense = c.fetchone()[0] or 0.0
    
    # Calculate today's expense
    today_date = date.today().strftime('%Y-%m-%d')
    c.execute('SELECT SUM(amount) FROM expenses WHERE date LIKE ?', (today_date + '%',))
    today_expense = c.fetchone()[0] or 0.0

    conn.close()
    return render_template('index.html', expenses=expenses, total_expense=total_expense, today_expense=today_expense)

@app.route('/add', methods=['POST'])
def add_expense():
    description = request.form['description']
    amount = request.form['amount']
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO expenses (description, amount, date) VALUES (?, ?, ?)', (description, amount, date))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/download')
def download_csv():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT description, amount, date FROM expenses')
    expenses = c.fetchall()
    conn.close()

    csv_filename = 'expenses.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Description', 'Amount', 'Date'])
        csvwriter.writerows(expenses)

    return send_file(csv_filename, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
