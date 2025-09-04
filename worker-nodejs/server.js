const express = require('express');
const multer = require('multer');
const Jimp = require('jimp');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

app.post('/process', upload.single('image'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No image file provided' });
  }

  try {
    const image = await Jimp.read(req.file.buffer);
    image.invert(); // Apply the invert filter

    const processedImageBuffer = await image.getBufferAsync(Jimp.MIME_PNG);

    res.writeHead(200, {
      'Content-Type': 'image/png',
      'Content-Length': processedImageBuffer.length
    });
    res.end(processedImageBuffer);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to process image.' });
  }
});

const PORT = 5002;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Node.js worker listening on port ${PORT}`);
});
