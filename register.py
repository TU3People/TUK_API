import requests

def test_register(username, useremail, userpassword):
    url = 'http://localhost:5000/register'
    data = {
        'username': username,
        'useremail': useremail,
        'userpassword': userpassword
    }
    try:
        res = requests.post(url, json=data)
        print(f"Status Code: {res.status_code}")
        try:
            print("Response JSON:", res.json())
        except ValueError:
            print("응답이 JSON이 아닙니다:")
            print("응답 내용:", res.text)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

if __name__ == "__main__" :
    username = input("username: ")
    useremail = input("useremail: ")
    userpassword = input("userpassword: ")
    test_register(username, useremail, userpassword)