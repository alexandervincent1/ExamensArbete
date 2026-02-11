from flask import Flask, render_template, redirect, url_for, session, request
import os
import warnings
warnings.filterwarnings("ignore")

from backend.db import initialize_database, save_message, get_existing_message_ids
from backend.gmail import login as gmail_login, logout as gmail_logout, my_emails
from backend.ai import classify_email

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    return redirect(url_for('dashboard')) if session.get('logged_in') else render_template('login.html')


@app.route('/login')
def login():
    try:
        gmail_login()  # Startar OAuth om token saknas
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    except Exception as e:
        session['msg'] = f'❌ Login misslyckades: {str(e)}'
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    try: gmail_logout()
    except: pass
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@app.route('/dashboard/<folder>')
def dashboard(folder=None):
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    conn = initialize_database()
    if not conn:
        return render_template('dashboard.html', emails=[], folders=[], total_count=0, current_folder='all', logged_in=True)
    
    cursor = conn.cursor(dictionary=True)
    
    if folder and folder != 'all':
        cursor.execute("SELECT * FROM gmail_messages WHERE ai_folder = %s ORDER BY imported_at DESC", (folder,))
    else:
        cursor.execute("SELECT * FROM gmail_messages ORDER BY imported_at DESC")
    emails = cursor.fetchall()
    
    cursor.execute("SELECT ai_folder as name, COUNT(*) as count FROM gmail_messages WHERE ai_folder IS NOT NULL GROUP BY ai_folder")
    folders = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) as total FROM gmail_messages")
    total = cursor.fetchone()['total']
    conn.close()
    
    return render_template('dashboard.html', emails=emails, folders=folders, total_count=total, current_folder=folder or 'all', logged_in=True)


@app.route('/email/<int:id>')
def view_email(id):
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    conn = initialize_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM gmail_messages WHERE id = %s", (id,))
    email = cursor.fetchone()
    conn.close()
    
    return render_template('email_view.html', email=email, logged_in=True) if email else redirect(url_for('dashboard'))


@app.route('/fetch', methods=['GET', 'POST'])
def fetch_emails():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        antal = int(request.form.get('antal', 5))
        gmail_login()
        
        conn = initialize_database()
        if not conn:
            session['msg'] = '❌ Kunde inte ansluta till databasen'
            return redirect(url_for('dashboard'))
        existing_ids = get_existing_message_ids(conn)
        msgs = my_emails(antal + len(existing_ids))
        
        saved = 0
        for m in msgs:
            if saved >= antal:
                break
            if m['id'] in existing_ids:
                continue
            
            ai = classify_email(m['subject'], m['body'])
            save_message(conn, m['id'], m['sender'], m['subject'], m['body'], ai.get('folder'), ai.get('summary'), ai.get('subject'), m['timestamp'])
            saved += 1
        
        conn.close()
        session['msg'] = f'✅ {saved} nya mejl!' if saved else f'ℹ️ Inga nya mejl att hämta'
        return redirect(url_for('dashboard'))
    
    return render_template('fetch.html', logged_in=True)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_email(id):
    if session.get('logged_in'):
        conn = initialize_database()
        conn.cursor().execute("DELETE FROM gmail_messages WHERE id = %s", (id,))
        conn.commit()
        conn.close()
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/delete-selected', methods=['POST'])
def delete_selected():
    if session.get('logged_in'):
        ids = request.form.getlist('selected_emails')
        if ids:
            conn = initialize_database()
            conn.cursor().execute(f"DELETE FROM gmail_messages WHERE id IN ({','.join(['%s']*len(ids))})", ids)
            conn.commit()
            conn.close()
            session['msg'] = f'🗑️ {len(ids)} mejl borttagna!'
    return redirect(request.referrer or url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
