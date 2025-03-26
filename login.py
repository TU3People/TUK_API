import requests

def test_login(username, userpassword):
    url = 'http://localhost:5000/login'
    data = {
        'username': username,
        'userpassword': userpassword
    }
    try:
        res = requests.post(url, json=data)
        print(f"Status Code: {res.status_code}")
        try:
            print("Response JSON:", res.json())
            print(res.json())
        except ValueError:
            print("응답이 JSON이 아닙니다:")
            print("응답 내용:", res.text)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

if __name__ == "__main__" :
    username = input("username: ")
    userpassword = input("userpassword: ")
    test_login(username, userpassword)