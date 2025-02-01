import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import fetch from 'node-fetch';
import FormData from 'form-data';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const FLASK_API_URL = "http://127.0.0.1:5000/analyze";

const uploadsDir = path.join(process.cwd(), 'uploads');
fs.mkdirSync(uploadsDir, { recursive: true });

app.use(express.static(path.join(process.cwd(), 'public')));
app.use('/uploads', express.static(uploadsDir));

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadsDir),
    filename: (req, file, cb) => cb(null, file.originalname),
});

const upload = multer({ storage });

app.post('/upload', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ message: '❌ No file uploaded!' });
    }

    console.log(`📂 Uploaded file: ${req.file.filename}`);

    try {
        const formData = new FormData();
        formData.append('file', fs.createReadStream(req.file.path));

        const response = await fetch(FLASK_API_URL, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error(`Flask API error! Status: ${response.status}`);

        const result = await response.json();
        fs.writeFileSync(path.join(uploadsDir, `${req.file.filename}.html`), result.table, 'utf8');
        
        res.status(201).json({ message: '✅ File processed successfully!', fileName: req.file.filename });
    } catch (error) {
        console.error('❌ Error processing file:', error);
        res.status(500).json({ message: '❌ Error processing file.', error: error.message });
    }
});

app.get('/result/:filename', (req, res) => {
    const filename = req.params.filename;
    const resultPath = path.join(uploadsDir, `${filename}.html`);

    if (fs.existsSync(resultPath)) {
        res.sendFile(resultPath);
    } else {
        res.status(404).send('<p>❌ No results found for this file.</p>');
    }
});

app.listen(PORT, () => console.log(`🚀 Server running on http://localhost:${PORT}`));
