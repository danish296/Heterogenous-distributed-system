from flask import Flask, request, send_file
from PIL import Image
from io import BytesIO

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return "No image file provided", 400

    file = request.files['image']
    try:
        image = Image.open(file.stream).convert('L') # Grayscale

        # Save image to an in-memory buffer
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Send the image file back in the response
        return send_file(buffer, mimetype='image/png')

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
