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

@app.route('/split-pdf', methods=['POST'])
def split_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        start_page = int(request.form.get('start_page', 1))
        end_page = int(request.form.get('end_page', 1))
        
        if file and allowed_file(file.filename, {'pdf'}):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            output_path = converter.split_pdf(input_path, app.config['OUTPUT_FOLDER'], start_page, end_page)
            if output_path:
                return send_file(output_path, as_attachment=True)
            else:
                return jsonify({'error': 'Failed to split PDF'}), 500
        else:
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
            
    except Exception as e:
        logger.error(f"Error in split_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/rotate-pdf', methods=['POST'])
def rotate_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        rotation = int(request.form.get('rotation', 90))  # Default to 90 degrees
        
        # Validate rotation
        if rotation not in [90, 180, 270]:
            return jsonify({'error': 'Invalid rotation. Must be 90, 180, or 270 degrees'}), 400
        
        if file and allowed_file(file.filename, {'pdf'}):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Generate output filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'rotated_{timestamp}.pdf')
            
            if converter.rotate_pdf(input_path, output_path, rotation):
                return send_file(output_path, as_attachment=True)
            else:
                return jsonify({'error': 'Failed to rotate PDF'}), 500
        else:
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
            
    except Exception as e:
        logger.error(f"Error in rotate_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/add-watermark', methods=['POST'])
def add_watermark():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        watermark_text = request.form.get('watermark_text', '')
        
        if not watermark_text:
            return jsonify({'error': 'No watermark text provided'}), 400
        
        if file and allowed_file(file.filename, {'pdf'}):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'watermarked_{timestamp}.pdf')
            
            if converter.add_watermark(input_path, output_path, watermark_text):
                return send_file(output_path, as_attachment=True)
            else:
                return jsonify({'error': 'Failed to add watermark'}), 500
        else:
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
            
    except Exception as e:
        logger.error(f"Error in add_watermark: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Image Processing Routes
@app.route('/resize-image', methods=['POST'])
def resize_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        width = request.form.get('width', type=int)
        height = request.form.get('height', type=int)
        maintain_aspect = request.form.get('maintain_aspect', 'true').lower() == 'true'
        
        if not (width or height):
            return jsonify({'error': 'Width or height must be specified'}), 400
        
        if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'webp'}):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'resized_{timestamp}_{filename}')
            
            if converter.resize_image(input_path, output_path, width, height, maintain_aspect):
                return send_file(output_path, as_attachment=True)
            else:
                return jsonify({'error': 'Failed to resize image'}), 500
        else:
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, and WEBP files are allowed'}), 400
            
    except Exception as e:
        logger.error(f"Error in resize_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/crop-image', methods=['POST'])
def crop_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        left = request.form.get('left', type=int)
        top = request.form.get('top', type=int)
        right = request.form.get('right', type=int)
        bottom = request.form.get('bottom', type=int)
        
        if None in [left, top, right, bottom]:
            return jsonify({'error': 'All crop coordinates must be specified'}), 400
        
        if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'webp'}):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'cropped_{timestamp}_{filename}')
            
            if converter.crop_image(input_path, output_path, left, top, right, bottom):
                return send_file(output_path, as_attachment=True)
            else:
                return jsonify({'error': 'Failed to crop image'}), 500
        else:
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, and WEBP files are allowed'}), 400
            
    except Exception as e:
        logger.error(f"Error in crop_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/convert-image', methods=['POST'])
def convert_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        target_format = request.form.get('format', '').lower()
        
        if not target_format:
            return jsonify({'error': 'Target format must be specified'}), 400
        
        if target_format not in ['png', 'jpg', 'jpeg', 'webp']:
            return jsonify({'error': 'Invalid target format. Must be PNG, JPG, JPEG, or WEBP'}), 400
        
        if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'webp'}):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f'{os.path.splitext(filename)[0]}_{timestamp}.{target_format}'
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            if converter.convert_image_format(input_path, output_path):
                return send_file(output_path, as_attachment=True)
            else:
                return jsonify({'error': 'Failed to convert image'}), 500
        else:
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, and WEBP files are allowed'}), 400
            
    except Exception as e:
        logger.error(f"Error in convert_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/compress-image', methods=['POST'])
def compress_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        quality = request.form.get('quality', type=int, default=80)
        
        if not 1 <= quality <= 100:
            return jsonify({'error': 'Quality must be between 1 and 100'}), 400
        
        if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'webp'}):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'compressed_{timestamp}_{filename}')
            
            if converter.compress_image(input_path, output_path, quality):
                return send_file(output_path, as_attachment=True)
            else:
                return jsonify({'error': 'Failed to compress image'}), 500
        else:
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, and WEBP files are allowed'}), 400
            
    except Exception as e:
        logger.error(f"Error in compress_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create required directories
    logger.info("Creating required directories...")
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Start server
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
