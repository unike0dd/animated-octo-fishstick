const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

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
    if (!req.file) {
        return res.status(400).json({ message: 'No file uploaded.' });
    }

    const filePath = req.file.path;
    const command = `python file_scanner.py "${filePath}"`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            // Exit code 2 means the file is malicious
            if (error.code === 2) {
                fs.unlink(filePath, (unlinkErr) => {
                    if (unlinkErr) {
                        console.error(`Error deleting malicious file: ${unlinkErr}`);
                        return res.status(500).json({ message: 'Malicious file detected, but failed to delete it.' });
                    }
                    console.log(`Deleted malicious file: ${filePath}`);
                    return res.status(403).json({ message: 'Malicious file detected and rejected.' });
                });
            } else {
                // Other errors (e.g., script not found, python error)
                console.error(`Scanner error: ${stderr}`);
                fs.unlink(filePath, () => {}); // Attempt to delete the file just in case
                return res.status(500).json({ message: 'Error scanning the file.' });
            }
        } else {
            // Exit code 0 means the file is clean
            console.log(`Scan output: ${stdout}`);
            res.json({ message: 'File uploaded and scanned successfully!', filePath: filePath });
        }
    });
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
