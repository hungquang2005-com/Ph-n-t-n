from flask import Flask, request, send_file, jsonify
import os

app = Flask(__name__)
STORAGE_FOLDER = "storage"
os.makedirs(STORAGE_FOLDER, exist_ok=True)

# ===== STORE FILE =====
@app.route('/store', methods=['POST'])
def store_file():
    file = request.files['file']
    file_id = request.form['file_id']
    ext = request.form['ext']

    path = os.path.join(STORAGE_FOLDER, file_id + ext)
    file.save(path)

    return jsonify({"status": "stored"}), 200


# ===== READ TXT (PHÂN TRANG) =====
@app.route('/read_txt')
def read_txt():
    file_id = request.args.get('file_id')
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    path = os.path.join(STORAGE_FOLDER, file_id + ".txt")

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()[start:end]

    return jsonify({"content": lines})


# ===== READ PDF (STREAM FILE) =====
@app.route('/read_pdf')
def read_pdf():
    file_id = request.args.get('file_id')
    path = os.path.join(STORAGE_FOLDER, file_id + ".pdf")

    return send_file(
        path,
        mimetype="application/pdf",
        as_attachment=False
    )


if __name__ == '__main__':
    app.run(port=6002, debug=True)
