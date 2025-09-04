const express = require('express');
const multer = require('multer');
const Jimp = require('jimp');
const path = require('path');
const fs = require('fs');

const app = express();
const upload = multer({ dest: 'uploads/' });
const OUTPUT_FOLDER = path.join(__dirname, 'output');
if (!fs.existsSync(OUTPUT_FOLDER)) {
  fs.mkdirSync(OUTPUT_FOLDER);
}

app.post('/process', upload.single('image'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No image file provided' });
  }
  try {
    const imagePath = req.file.path;
    const outputPath = path.join(OUTPUT_FOLDER, 'processed.png');
    const image = await Jimp.read(imagePath);
    image.sepia().write(outputPath, () => {
      fs.unlinkSync(imagePath); // Clean up temp file
      res.status(200).json({ message: 'Success! Sepia filter applied.' });
    });
  } catch (err) {
    res.status(500).json({ error: 'Failed to process image.' });
  }
});

const PORT = 5002;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Node.js worker listening on port ${PORT}`);
});