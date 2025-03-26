from flask import Flask, request, jsonify
import os
import MySQLdb
import hashlib
import base64

app = Flask(__name__)

# MySQL        ㅇㅇ
app.config['MYSQL_HOST'] = 'tuk_mysql'
app.config['MYSQL_USER'] = 'journey'
app.config['MYSQL_PASSWORD'] = 'Qwer!234'
app.config['MYSQL_DB'] = 'journey'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQLdb.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    passwd=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

#               
def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def generate_salt(length=16):
    return base64.b64encode(os.urandom(length)).decode('utf-8')

#      API
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print("request data\n",data)

    username = data.get('username')
    password = data.get('userpassword')        

    print(f"login part\nusername: {username}\nuserpasswd: {password}\n")
    
    cursor = mysql.cursor()
    # 라이브러리 MYSQLdb는 값을 전달할 때, ***튜플***로 넘겨주어야 한다. 아래 (,)로 지정한 이유가 그것이며, 꼭 명심하여, 살펴볼 것, 한 시간 날렸음
    cursor.execute("SELECT password_hash, salt FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    print("print user: ")
    print(user)
    
    if not user:
        return jsonify({'result': 'fail', 'message': '존재하지 않는 사용자입니다.'})
    elif user:
        input_hash = hash_password(password, user[1])
        if input_hash == user[0]:
            return jsonify({'result': 'success', 'message': '        '})
    
    return jsonify({'result': 'fail', 'message': '                   '})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    useremail = data.get('useremail')
    userpassword = data.get('userpassword')
    
    salt = generate_salt()
    hashed_pw = hash_password(userpassword, salt)

    print(f"register part\nusername: {username} \nuseremail: {useremail} \nuserpasswd: {userpassword} \nsalt: {salt} \nhash_password: {hashed_pw}\n\n")

    cursor = mysql.cursor()
    cursor.execute(
        "INSERT INTO users (username, useremail, password_hash, salt, created_at) VALUES (%s, %s, %s, %s, NOW())",
        (username, useremail, hashed_pw, salt)
    )
    mysql.commit()

    #print("====Debug Part====\n")


    return jsonify({'result': 'test', 'message': '제발 되어 주세요..'})

if __name__ == '__main__':
    app.run(host='localhost', port=5000)