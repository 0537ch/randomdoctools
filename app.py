from flask import Flask, request, render_template, send_file, jsonify
import os
from pathlib import Path
from converter import FileConverter
from bg_remover import BackgroundRemover
from werkzeug.utils import secure_filename
import traceback
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'input'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

converter = FileConverter()
bg_remover = BackgroundRemover()

def allowed_file(filename, formats):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in formats

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        logger.info("Starting file conversion...")
        if 'file' not in request.files:
            logger.error("No file provided in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, {'pdf', 'png'}):
            logger.error(f"Unsupported file type: {file.filename}")
            return jsonify({'error': 'File type not supported'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Saving file to: {filepath}")
        file.save(filepath)
        
        logger.info(f"Converting file: {filepath}")
        output_path = converter.convert_pdf_to_png(filepath) if filename.endswith('.pdf') else converter.convert_png_to_pdf(filepath)
        logger.info(f"Conversion complete. Output path: {output_path}")
        
        output_filename = os.path.basename(output_path)
        logger.info(f"Sending file: {output_filename}")
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/remove-background', methods=['POST'])
def remove_background():
    try:
        logger.info("Starting background removal...")
        if 'file' not in request.files:
            logger.error("No file provided in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        if not bg_remover.is_supported(file.filename):
            logger.error(f"Unsupported file type: {file.filename}")
            return jsonify({'error': 'File type not supported. Please upload PNG, JPG, or WEBP'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Saving file to: {filepath}")
        file.save(filepath)
        
        logger.info(f"Removing background from: {filepath}")
        output_path = bg_remover.remove_background(filepath)
        logger.info(f"Background removal complete. Output path: {output_path}")
        
        output_filename = os.path.basename(output_path)
        logger.info(f"Sending file: {output_filename}")
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        logger.error(f"Error during background removal: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/combine-pdf', methods=['POST'])
def combine_pdf():
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        
        # Validate files
        if len(files) < 2:
            return jsonify({'error': 'At least 2 PDF files are required'}), 400
        
        pdf_paths = []
        for file in files:
            if file and allowed_file(file.filename, {'pdf'}):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                pdf_paths.append(filepath)
            else:
                return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'combined_{timestamp}.pdf')
        
        # Combine PDFs
        if converter.combine_pdfs(pdf_paths, output_path):
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({'error': 'Failed to combine PDFs'}), 500
            
    except Exception as e:
        logger.error(f"Error in combine_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create required directories
    logger.info("Creating required directories...")
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Start server
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
