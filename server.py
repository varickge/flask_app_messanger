from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store the list of connected clients
connected_clients = {}
users = {}  # Store user information (username and password)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password and username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('chat_menu'))

        return 'Login failed. Invalid username or password.'

    # Handle GET requests (display login form)
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users:
            return 'Username already exists. Please choose a different one.'

        users[username] = password
        session['username'] = username
        return redirect(url_for('chat_menu'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    # session.pop('username', None)
    return redirect(url_for('main'))


@app.route('/chat')
def chat_menu():
    # Retrieve the username from the session or wherever it's stored
    username = session.get('username')
    return render_template('chat.html', username=username)

@socketio.on('connect')
def handle_connect():
    if 'username' not in session:
        return False
    username = session['username']
    connected_clients[request.sid] = username
    emit('update_users', list(connected_clients.values()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in connected_clients:
        del connected_clients[request.sid]
        emit('update_users', list(connected_clients.values()), broadcast=True)

@socketio.on('message')
def handle_message(message):
    if 'username' in session:
        username = session['username']
        send(f'{username}: {message}', broadcast=True)

if __name__ == '__main__':
    app.secret_key = 'secret!'
    socketio.run(app, host='192.168.10.11', port=8080, debug=True)
