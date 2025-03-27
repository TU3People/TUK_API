from flask import Flask, request, jsonify
import os
import MySQLdb
import hashlib
import base64

from flask_cors import CORS

import datetime
import jwt
from functools import wraps

app = Flask(__name__)
CORS(app, origins=["https://api.prayanne.co.kr"])

# MySQL app config
app.config['MYSQL_HOST'] = 'tuk_mysql'
app.config['MYSQL_USER'] = 'journey'
app.config['MYSQL_PASSWORD'] = 'Qwer!234'
app.config['MYSQL_DB'] = 'journey'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# secret key 수정 필
app.config['SECRET_KEY'] = 'your-secret-key'

mysql = MySQLdb.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    passwd=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)


## 함수 ##

# 패스워드 hash화              
def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
# salt 생성
def generate_salt(length=16):
    return base64.b64encode(os.urandom(length)).decode('utf-8')
# token 생성단
def generate_token(user_id):
   # user_id와 현재 시간, 만료 시간 등을 포함해 JWT 토큰 생성
    payload = {
        'user_id': user_id,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # 30분 유효
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    # PyJWT 2.x 이상은 token이 str 타입으로 반환됨
    return token
# token 필요 전달
def token_required(f):
    """
    토큰이 필요한 API 엔드포인트에 적용할 데코레이터.
    요청 헤더에 포함된 JWT 토큰을 확인하고, 유효하면 해당 endpoint를 실행.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Authorization 헤더에서 토큰 추출 (형식: "Bearer <token>")
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # 토큰 디코딩. 만료되었거나 위조된 토큰이면 예외 발생
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        # 토큰이 유효하면, 현재 사용자 ID를 인자로 넘겨줌
        return f(current_user_id, *args, **kwargs)

    return decorated


# API 단

@app.before_request
def log_request_info():
    print("====log part====\n")
    print(f"REQUEST: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data()}")
    print("================\n\n")

# 로그인
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print("request data\n",data)

    username = data.get('username')
    password = data.get('userpassword')        

    print(f"login part\nusername: {username}\nuserpassword: {password}\n")
    
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
            token = generate_token(username)
            return jsonify({'result': 'success', 'message': username + '님 환영합니다.', 'token': token})
    
    return jsonify({'result': 'fail', 'message': '잘못된 비밀번호를 입력하셨습니다. '})


# 회원 가입
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    useremail = data.get('useremail')
    userpassword = data.get('userpassword')
    
    salt = generate_salt()
    hashed_pw = hash_password(userpassword, salt)

    print(f"register part\nusername: {username} \nuseremail: {useremail} \nuserpasswd: {userpassword} \nsalt: {salt} \nhash_password: {hashed_pw}\n\n")
    
    try:
        cursor = mysql.cursor()
        cursor.execute(
            "INSERT INTO users (username, useremail, password_hash, salt, created_at) VALUES (%s, %s, %s, %s, NOW())",
            (username, useremail, hashed_pw, salt)
        )
        mysql.commit()
        return jsonify({'result': 'success', 'message': '회원가입이 되었습니다.'})
    except Exception as e:
        return jsonify({'result': 'fail', 'message': str(e)})

# Token
@app.route('/protected', methods=['GET'])
@token_required
def protected(current_user_id):
    """
    토큰이 필요한 보호된 엔드포인트.
    데코레이터를 통해 토큰 검증을 진행하고, 유효한 경우 사용자 정보를 반환.
    """
    return jsonify({
        'message': 'This is a protected route.',
        'user_id': current_user_id
    })

if __name__ == '__main__':
    # host를 0.0.0.0 으로 구성해야 외부 접속이 가능함. 뒷통수 얻어맞고 뇌진탕 발현.
    # 127.0.0.1 or localhost로 구성시, 내부 접속만 허용하게 됨.
    # 내부 접속으로 host 구성시 -> 내부 IP인 127.0.0.1만 지정됨.
    # 0.0.0.0 으로 host 구성시 -> 도커 IP인 172.17.~ 이 추가로 지정됨.
    app.run(host='0.0.0.0', port=5000)
