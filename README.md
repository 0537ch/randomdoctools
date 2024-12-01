# File Converter Service

A robust microservice for document and image processing, offering various conversion and manipulation capabilities. Built with Flask and containerized with Docker for easy deployment.

## 🚀 Features

- **PDF Operations**
  - PDF to PNG conversion
  - PNG to PDF conversion
  - PDF merging/splitting
  - PDF watermarking
  
- **Image Processing**
  - Format conversion
  - Background removal
  - Image compression
  - Basic transformations

## 🛠️ Tech Stack

- Python 3.x
- Flask
- Docker
- PyPDF2
- pdf2image
- Pillow (PIL)
- rembg
- Werkzeug

## 🔧 Prerequisites

- Docker (recommended)
- Python 3.x (for local development)
- poppler-utils (for PDF processing)

## 🚀 Quick Start

### Using Docker (Recommended)

1. Build the Docker image:
```bash
docker build -t file-converter-service .
```

2. Run the container:
```bash
docker run -p 5001:5001 file-converter-service
```

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/0537ch/randomdoctools.git
cd randomdoctools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

Access the web interface at `http://localhost:5001`

## 🔍 API Usage

### PDF to PNG Conversion
- **Endpoint**: `/convert/pdf-to-png`
- **Method**: POST
- **Input**: PDF file
- **Output**: ZIP file containing PNG images

### PNG to PDF Conversion
- **Endpoint**: `/convert/png-to-pdf`
- **Method**: POST
- **Input**: PNG file
- **Output**: PDF file

### Background Removal
- **Endpoint**: `/process/remove-background`
- **Method**: POST
- **Input**: Image file (PNG, JPG, JPEG, WEBP)
- **Output**: Processed image with background removed

### PDF Combination
- **Endpoint**: `/process/combine-pdf`
- **Method**: POST
- **Input**: Multiple PDF files
- **Output**: Single combined PDF file

## ⚙️ Configuration

- **Maximum file size**: 16MB
- **Supported formats**:
  - PDF files (`.pdf`)
  - Image files (`.png`, `.jpg`, `.jpeg`, `.webp`)
  - Other formats may be supported based on the conversion type

## 🔒 Security Considerations

- Input validation implemented
- Temporary file cleanup
- Rate limiting (coming soon)
- File size restrictions

## 🌟 Deployment

The service is configured for deployment on Railway platform with the following files:
- `Dockerfile` - Container configuration
- `railway.toml` - Railway platform settings
- `Procfile` - Process configuration

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request to the [repository](https://github.com/0537ch/randomdoctools).
