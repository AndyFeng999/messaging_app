import flask
import pymysql
import pymysql.cursors

from flask import request
from flask_bcrypt import Bcrypt

app = flask.Flask(__name__)
bcrypt = Bcrypt(app)

db = pymysql.connect(
    user='root',
    password='testpass',
    host='db',
    database='challenge',
)
        
@app.route('/create', methods=['POST'])
def create_user():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password)
        
        with db.cursor() as cur:
            query = ("INSERT INTO User(username, password) VALUES (%s, %s)")
            cur.execute(query, (username, password_hash))
            db.commit()
            cur.execute("SELECT * from User WHERE User.username = %s", (username,))
            user = cur.fetchone()
            hashed = bcrypt.check_password_hash(user[2], password)
            
        return flask.jsonify({
                'id': user[0],
                'username': user[1],
                'password_hashed': hashed
            })
        
@app.route('/users')
def get_users():
    cur = db.cursor()
    cur.execute("SELECT id, username from User")
    users = cur.fetchall()
    
    return flask.jsonify({
            'users': users
        })
    
@app.route('/messages/<user_id>/<receiver_id>', defaults={'page_number': None, 'page_limit': None}, methods=['GET', 'POST'])
@app.route('/messages/<user_id>/<receiver_id>/<int:page_number>/<int:page_limit>', methods=['GET', 'POST'])
def messages(user_id, receiver_id, page_number, page_limit):
    
    if request.method == 'GET':
        cur = db.cursor()
        query = """SELECT * FROM Message m 
        LEFT JOIN Text ON m.message_id = Text.message_id
        LEFT JOIN Image ON m.message_id = Image.message_id
        LEFT JOIN Video ON m.message_id = Video.message_id
        WHERE ((m.sender_id = %s AND m.receiver_id = %s) OR (m.receiver_id = %s AND m.sender_id = %s))
        ORDER BY m.created DESC"""
        cur.execute(query, (user_id, receiver_id, user_id, receiver_id))
        messages = cur.fetchall()
        
        if page_limit and page_number:
            start_msg = (page_number-1)*page_limit
            end_msg = start_msg + page_limit
            if end_msg > len(messages):
                end_msg = len(messages)
            messages = messages[start_msg:end_msg]
            
        return flask.jsonify({
                'messages': messages,
            })
    
    if request.method == 'POST':
        message_type = request.form['msg_type']
        content = request.form['body']
        query1 = ("INSERT INTO Message(sender_id, receiver_id) VALUES (%s, %s)")
        cur = db.cursor()
        cur.execute(query1, (user_id, receiver_id))
        if message_type == 'video':
            query2 = ("INSERT INTO Video(message_id, video_url, video_length, video_source) VALUES (%s, %s, %s, %s)")
            last_id = cur.lastrowid
            cur.execute(query2, (last_id, content, '2:34', 'YouTube'))
        elif message_type == 'image':
            query2 = ("INSERT INTO Image(message_id, image_url, height, width) VALUES (%s, %s, %s, %s)")
            last_id = cur.lastrowid
            cur.execute(query2, (last_id, content, 480, 480))
        else:
            query2 = ("INSERT INTO Text(message_id, content) VALUES (%s, %s)")
            last_id = cur.lastrowid
            cur.execute(query2, (last_id, content))
        db.commit()
        
        query = """SELECT * FROM Message m 
        LEFT JOIN Text ON m.message_id = Text.message_id
        LEFT JOIN Image ON m.message_id = Image.message_id
        LEFT JOIN Video ON m.message_id = Video.message_id
        WHERE ((m.sender_id = %s AND m.receiver_id = %s) OR (m.receiver_id = %s AND m.sender_id = %s))
        ORDER BY m.created DESC"""
        cur.execute(query, (user_id, receiver_id, user_id, receiver_id))
        messages = cur.fetchall()
        
        return flask.jsonify({
                'messages': messages,
            })
