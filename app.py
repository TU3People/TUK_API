from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
# 실제 자료가 저장될 리눅스 디렉토리 경로로 변경하세요.
app.config['UPLOAD_FOLDER'] = '/home/flask/data'

# 예시: 멤버 리스트
members = ["Alice", "Bob", "Charlie"]

# 예시: 주제별로 필요한 자료 목록 (주제: [자료명 리스트])
topics = {
    "Engineering": ["Report", "Diagram"],
    "Design": ["Sketch", "Presentation"],
    "Research": ["Paper", "Data"]
}

# 관리자가 지정한 파일명 양식 함수 (예시: topic_member_material.pdf)
def generate_filename(topic, member, material):
    filename = f"{topic}_{member}_{material}.pdf"
    return filename

@app.route('/')
def index():
    # 멤버 선택 페이지
    return render_template('index.html', members=members)

@app.route('/select_topic', methods=['POST'])
def select_topic():
    member = request.form.get('member')
    if not member or member not in members:
        flash("올바르지 않은 멤버입니다.")
        return redirect(url_for('index'))
    # 멤버를 선택하면 주제 리스트를 보여주는 페이지로 이동
    return render_template('topics.html', member=member, topics=list(topics.keys()))

@app.route('/upload/<member>/<topic>', methods=['GET', 'POST'])
def upload(member, topic):
    if member not in members or topic not in topics:
        flash("올바르지 않은 멤버 또는 주제입니다.")
        return redirect(url_for('index'))
    required_materials = topics[topic]
    if request.method == 'POST':
        # 각 자료에 대해 파일을 받아서 처리
        for material in required_materials:
            file = request.files.get(material)
            if file:
                # 관리자가 지정한 이름 양식에 따라 파일명 생성
                filename = generate_filename(topic, member, material)
                filename = secure_filename(filename)
                # 주제/멤버별 디렉토리 생성 (없으면 생성)
                directory = os.path.join(app.config['UPLOAD_FOLDER'], topic, member)
                os.makedirs(directory, exist_ok=True)
                file_path = os.path.join(directory, filename)
                file.save(file_path)
        flash("파일 업로드가 완료되었습니다.")
        return redirect(url_for('index'))
    return render_template('upload.html', member=member, topic=topic, materials=required_materials)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
