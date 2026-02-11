const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const session = require('express-session');
const bcrypt = require('bcrypt');

const app = express();
const port = 3000;
const saltRounds = 10; // for bcrypt

// --- User Store ---
const USERS_FILE = 'users.json';
let users = {};

// Load users from file, or create an empty file
if (fs.existsSync(USERS_FILE)) {
    const data = fs.readFileSync(USERS_FILE);
    users = JSON.parse(data);
} else {
    fs.writeFileSync(USERS_FILE, JSON.stringify({}));
}

const saveUsers = () => {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
};

// --- Middleware ---
app.use(express.static(__dirname));
app.use(express.json());

// Trust the proxy to get the correct protocol (https)
app.set('trust proxy', 1);

app.use(session({
    secret: 'a-very-secret-key-that-should-be-in-an-env-file',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: true } // Set to true for HTTPS
}));

// Middleware to check if a user is authenticated
const isAuthenticated = (req, res, next) => {
    if (req.session.user) {
        next();
    } else {
        res.status(401).json({ message: 'You must be logged in to perform this action.' });
    }
};

// --- File Uploads ---
const uploadsDir = 'uploads';
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir);
}
const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, 'uploads/'),
    filename: (req, file, cb) => cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname))
});
const upload = multer({ storage: storage });

// --- Routes ---
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// --- Authentication Routes ---
app.post('/register', async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) {
        return res.status(400).json({ message: 'Username and password are required.' });
    }
    if (users[username]) {
        return res.status(409).json({ message: 'User already exists.' });
    }

    const hashedPassword = await bcrypt.hash(password, saltRounds);
    users[username] = { password: hashedPassword };
    saveUsers();

    res.status(201).json({ message: 'User registered successfully.' });
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    const user = users[username];

    if (user && await bcrypt.compare(password, user.password)) {
        req.session.user = { username: username };
        res.json({ message: 'Logged in successfully.' });
    } else {
        res.status(401).json({ message: 'Invalid username or password.' });
    }
});

app.post('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            return res.status(500).json({ message: 'Could not log out.' });
        }
        res.json({ message: 'Logged out successfully.' });
    });
});

// Route to check current session status
app.get('/session', (req, res) => {
    if (req.session.user) {
        res.json({ loggedIn: true, user: req.session.user });
    } else {
        res.json({ loggedIn: false });
    }
});


// --- Protected Routes ---
app.post('/chat', isAuthenticated, (req, res) => {
    const userMessage = req.body.message;
    // Sanitize the user message to prevent XSS
    const sanitizedMessage = userMessage.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const botResponse = `You said: ${sanitizedMessage}`;
    res.json({ message: botResponse });
});

app.post('/upload', isAuthenticated, upload.single('media'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ message: 'No file uploaded.' });
    }

    const filePath = req.file.path;
    const command = `python file_scanner.py "${filePath}"`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            if (error.code === 2) { // Malicious file
                fs.unlink(filePath, () => {});
                return res.status(403).json({ message: 'Malicious file detected and rejected.' });
            } else { // Other scanner error
                console.error(`Scanner error: ${stderr}`);
                fs.unlink(filePath, () => {}); 
                return res.status(500).json({ message: 'Error scanning the file.' });
            }
        } else {
            console.log(`Scan output: ${stdout}`);
            res.json({ message: 'File uploaded and scanned successfully!', filePath: filePath });
        }
    });
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
