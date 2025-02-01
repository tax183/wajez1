# Wajez

Wajez is a web application that extracts text from documents and images using OCR technology, summarizes content, and displays it in a structured format.

## Features

- Extract text from **PDF** and image files (**PNG, JPEG, GIF, WEBP**)
- **OCR processing** for text extraction from images
- **Content summarization** using GPT-4-Turbo
- Display results in a **structured format**
- Option to **download extracted text as a JSON file**
- **Upload and analyze new files** easily

## Technologies Used

## Technologies Used

### Back-End
- **Node.js (Express.js)** - Manages API requests and file handling.
- **Flask (Python)** - Handles file processing, OCR, and AI summarization.
- **Tesseract OCR** - Extracts text from images.
- **PyMuPDF (Fitz)** - Extracts text from PDF files.
- **OpenAI API** - Summarizes extracted content.
- **Multer** - Handles file uploads in Node.js.
- **node-fetch** - Sends HTTP requests to Flask API.
- **FormData** - Manages file transfer between Node.js and Flask.
- **fs (File System)** - Reads, writes, and processes local files.
- **child_process (exec)** - Runs Python script from Node.js.
- **dotenv** - Loads environment variables.

### Front-End
- **HTML, CSS, JavaScript** - User interface.
- **Fetch API** - Communicates with the back-end.

### File Processing & Storage
- **Multer (Node.js)** - Manages file uploads.
- **Express.js** - Handles API requests for file management.
- **Flask-CORS** - Enables communication between front-end and back-end.
- **File System (fs)** - Manages file storage and processing in Node.js.

## Installation

### 1. Install Dependencies

#### Flask (Python)
```bash
pip install -r requirements.txt
