from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance
import pytesseract
import io
import fitz  # PyMuPDF for PDF processing
import openai
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Set up OpenAI API
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("❌ OpenAI API Key is missing! Please check your .env file.")

client = openai.OpenAI(api_key=api_key)

# ✅ Set up Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
CORS(app)

# ✅ Define directories for storing files and results
UPLOAD_FOLDER = "uploads"
RESULTS_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def perform_ocr_on_image(image):
    """Extract text from an image using Tesseract OCR."""
    try:
        if image.mode != 'L':
            image = image.convert('L')
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        text = pytesseract.image_to_string(image, config='--oem 3 --psm 6')
        return text.strip() if text.strip() else None
    except Exception as e:
        print(f"❌ OCR Error: {str(e)}")
        return None

def process_pdf(pdf_path):
    """Extract text and images from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        extracted_data = []

        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text("text").strip()
            if page_text:
                extracted_data.append({"page": page_num, "content": page_text})

            image_list = page.get_images()
            for img_index, image in enumerate(image_list):
                try:
                    xref = image[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    ocr_text = perform_ocr_on_image(image)
                    if ocr_text:
                        extracted_data.append({"page": page_num, "content": f"Image {img_index + 1}: {ocr_text}"})
                except Exception as img_error:
                    print(f"⚠️ Error processing image {img_index + 1} on page {page_num}: {str(img_error)}")

        if not extracted_data:
            extracted_data.append({"page": "N/A", "content": "⚠️ No text found in the PDF."})

        print(f"✅ Extracted Data: {extracted_data}")
        return extracted_data
    except Exception as e:
        return [{"page": "Error", "content": f"❌ Error processing PDF: {str(e)}"}]

def convert_text_to_table(extracted_data):
    """Convert extracted text into an HTML table using OpenAI API."""
    formatted_text = "\n".join([f"Page {item['page']}: {item['content']}" for item in extracted_data])

    print(f"📌 Extracted Text for OpenAI:\n{formatted_text}")

    prompt = f"""
    Analyze the extracted text below and convert it into an HTML table with appropriate columns for better organization.

    **Extracted Text:**  
    {formatted_text}

    **Desired Formatting:**  
    - Convert the data into a well-structured HTML table.
    - Use appropriate columns based on the structure of the data.
    - Ensure the table is responsive and easy to read.

    Return only the HTML table without any additional information.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that converts extracted text into a well-structured HTML table."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        table_html = response.choices[0].message.content.strip()

        print(f"✅ OpenAI Response:\n{table_html}")
        return table_html
    except Exception as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        return "<p>Error generating table</p>"

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        result_path = os.path.join(RESULTS_FOLDER, f"{filename}.json")

        # ✅ Check if the file has been analyzed before
        if os.path.exists(result_path):
            print(f"🔄 Fetching cached result for {filename}")
            with open(result_path, "r", encoding="utf-8") as f:
                cached_result = json.load(f)

            # ✅ Ensure cached data contains "table"
            if isinstance(cached_result, dict) and "table" in cached_result:
                return jsonify({'table': cached_result["table"]})
            else:
                print(f"⚠️ Cached data is corrupted for {filename}, regenerating...")

        # 🚀 Save the new file
        file.save(file_path)
        print(f"📂 Uploaded File: {filename}")

        extracted_data = process_pdf(file_path)

        if not extracted_data:
            return jsonify({'error': 'No text extracted from PDF'}), 400

        formatted_table = convert_text_to_table(extracted_data)

        # ✅ Save the result for future use
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump({"table": formatted_table}, f, ensure_ascii=False, indent=4)

        return jsonify({'table': formatted_table})

    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')  