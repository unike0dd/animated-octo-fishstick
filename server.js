const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000;

const uploadsDir = 'uploads';
if (!fs.existsSync(uploadsDir)){
    fs.mkdirSync(uploadsDir);
}

// Set up multer for file uploads
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/')
    },
    filename: function (req, file, cb) {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname))
    }
});

const upload = multer({ storage: storage });

app.use(express.static(__dirname));
app.use(express.json());

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/chat', (req, res) => {
    const userMessage = req.body.message;
    // TODO: Add chatbot logic here
    const botResponse = `You said: ${userMessage}`;
    res.json({ message: botResponse });
});

app.post('/upload', upload.single('media'), (req, res) => {
    if (req.file) {
        res.json({ message: 'File uploaded successfully!', filePath: req.file.path });
    } else {
        res.status(400).json({ message: 'File upload failed.' });
    }
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
