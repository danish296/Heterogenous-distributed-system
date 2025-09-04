import os
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)
OUTPUT_FOLDER = '/app/output'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    try:
        image = Image.open(file.stream).convert('L') # Grayscale
        image.save(os.path.join(OUTPUT_FOLDER, 'processed.png'))
        return jsonify({"message": "Success! Image is now grayscale."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)