from flask import Flask, request, render_template, jsonify, send_file
import requests, uuid, sqlite3, os
from db import init_db

app = Flask(__name__)
init_db()

STORAGE_NODES = [
    "http://localhost:6001",
    "http://localhost:6002"
]

def choose_node():
    return STORAGE_NODES[uuid.uuid4().int % len(STORAGE_NODES)]


@app.route('/')
def upload_page():
    return render_template("upload.html")


# ===== UPLOAD =====
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    title = request.form['title']

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".txt", ".pdf"]:
        return "Chỉ hỗ trợ TXT và PDF"

    file_id = str(uuid.uuid4())
    node = choose_node()

    requests.post(
        f"{node}/store",
        files={'file': file},
        data={'file_id': file_id, 'ext': ext}
    )

    conn = sqlite3.connect("ebooks.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO ebooks VALUES (?, ?, ?, ?)",
        (file_id, title, node, ext)
    )
    conn.commit()
    conn.close()

    if ext == ".pdf":
        return f"Link đọc PDF: http://localhost:5000/read_pdf/{file_id}"
    else:
        return f"Link đọc TXT: http://localhost:5000/read_txt/{file_id}"


# ===== READ TXT =====
@app.route('/read_txt/<file_id>')
def read_txt(file_id):
    return render_template("reader.html", file_id=file_id)


@app.route('/content')
def content():
    file_id = request.args.get('file_id')
    page = int(request.args.get('page'))
    page_size = 5

    start = page * page_size
    end = start + page_size

    conn = sqlite3.connect("ebooks.db")
    c = conn.cursor()
    c.execute("SELECT node_url FROM ebooks WHERE id=?", (file_id,))
    node = c.fetchone()[0]
    conn.close()

    res = requests.get(
        f"{node}/read_txt",
        params={"file_id": file_id, "start": start, "end": end}
    )

    return jsonify(res.json())


# ===== READ PDF =====
@app.route('/read_pdf/<file_id>')
def read_pdf(file_id):
    conn = sqlite3.connect("ebooks.db")
    c = conn.cursor()
    c.execute("SELECT node_url FROM ebooks WHERE id=?", (file_id,))
    node = c.fetchone()[0]
    conn.close()

    return send_file(
        requests.get(
            f"{node}/read_pdf",
            params={"file_id": file_id},
            stream=True
        ).raw,
        mimetype="application/pdf"
    )


if __name__ == '__main__':
    app.run(port=5000, debug=True)
