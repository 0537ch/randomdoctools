# Random Doc Tools

A versatile document processing tool that provides various functionalities:

## Features
1. PDF to PNG Conversion
2. PNG to PDF Conversion
3. Image Background Removal
4. PDF Combination (Merge multiple PDFs)

## Setup
1. Clone the repository
```bash
git clone https://github.com/0537ch/randomdoctools.git
cd randomdoctools
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python app.py
```

4. Access the web interface at `http://localhost:5001`

## Usage
### PDF to PNG Conversion
- Upload a PDF file
- Get the converted PNG file(s)

### PNG to PDF Conversion
- Upload a PNG file
- Get the converted PDF file

### Background Removal
- Upload an image (PNG, JPG, JPEG, WEBP)
- Get the image with background removed

### Combine PDFs
- Select multiple PDF files (2 or more)
- Get a single combined PDF file

## Dependencies
- Flask
- PyPDF2
- pdf2image
- Pillow
- rembg
- Werkzeug

## Note
- Maximum file size: 16MB
- Supported formats:
  - PDF to PNG conversion: PDF files
  - PNG to PDF conversion: PNG files
  - Background removal: PNG, JPG, JPEG, WEBP
  - PDF combination: PDF files
