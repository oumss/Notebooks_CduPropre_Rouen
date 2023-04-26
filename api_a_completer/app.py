import os
from flask import Flask, request, jsonify, flash
from src.model import load_model, predict

from werkzeug.utils import secure_filename

app = Flask(__name__)

load_model()

UPLOAD_FOLDER = "/tmp"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@app.route('/predict', methods=['POST'])
def predict_duration():
    if 'file' not in request.files:
        return jsonify({}), 400
    
    file = request.files['file']
    filename = os.path.join("/tmp", file.filename)
    file.save(filename)
    # TODO : Calculer la prédiction ici

    # Pour chaque prédiction, on a :
    # (catégorie, [x, y, w, h, probabilité])
    # TODO : Retourner au format JSON

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
