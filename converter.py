from pdf2image import convert_from_path
from PIL import Image
import os
import logging
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import subprocess

class FileConverter:
    def __init__(self):
        self.poppler_path = os.path.join(os.path.dirname(__file__), 'poppler', 'poppler-23.08.0', 'Library', 'bin')

    def convert_pdf_to_png(self, pdf_path):
        """Convert PDF to PNG"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, poppler_path=self.poppler_path)
            
            # Save path
            output_path = os.path.join('output', os.path.splitext(os.path.basename(pdf_path))[0] + '.png')
            
            # Save the first page as PNG
            images[0].save(output_path, 'PNG')
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error converting PDF to PNG: {str(e)}")

    def png_to_pdf(self, png_path, output_path):
        """Convert PNG to PDF"""
        try:
            image = Image.open(png_path)
            rgb_image = image.convert('RGB')
            rgb_image.save(output_path, 'PDF')
            return True
        except Exception as e:
            logging.error(f"Error converting PNG to PDF: {str(e)}")
            return False

    def combine_pdfs(self, pdf_paths, output_path):
        """Combine multiple PDFs into one"""
        try:
            from PyPDF2 import PdfMerger
            merger = PdfMerger()
            
            # Add each PDF to the merger
            for pdf_path in pdf_paths:
                merger.append(pdf_path)
            
            # Write the combined PDF to output path
            merger.write(output_path)
            merger.close()
            return True
        except Exception as e:
            logging.error(f"Error combining PDFs: {str(e)}")
            return False

    def split_pdf(self, input_path, output_dir, start_page, end_page):
        """Split PDF file into range of pages"""
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()

            # Validate page range
            if start_page < 1 or end_page > len(reader.pages) or start_page > end_page:
                raise ValueError("Invalid page range")

            # Add specified pages to writer
            for page_num in range(start_page - 1, end_page):
                writer.add_page(reader.pages[page_num])

            # Generate output filename with page range
            output_path = os.path.join(output_dir, f'split_{start_page}-{end_page}.pdf')
            
            # Write the output file
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
        except Exception as e:
            logging.error(f"Error splitting PDF: {str(e)}")
            return None

    def rotate_pdf(self, input_path, output_path, rotation):
        """Rotate PDF pages"""
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()

            # Process each page
            for page in reader.pages:
                page.rotate(rotation)
                writer.add_page(page)

            # Write the rotated PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
        except Exception as e:
            logging.error(f"Error rotating PDF: {str(e)}")
            return False

    def add_watermark(self, input_path, output_path, watermark_text):
        """Add text watermark to PDF"""
        try:
            # Create watermark
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            
            # Configure watermark text
            can.setFont("Helvetica", 60)
            can.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)  # Gray, 30% opacity
            can.saveState()
            can.translate(300, 400)
            can.rotate(45)
            can.drawString(0, 0, watermark_text)
            can.restoreState()
            can.save()
            
            # Move to the beginning of the BytesIO buffer
            packet.seek(0)
            watermark = PdfReader(packet)
            
            # Get the first page of the watermark
            watermark_page = watermark.pages[0]
            
            # Read the input PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Add watermark to each page
            for page in reader.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)
            
            # Write the watermarked PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
        except Exception as e:
            logging.error(f"Error adding watermark: {str(e)}")
            return False

    # Image Processing Functions
    def resize_image(self, input_path, output_path, width, height, maintain_aspect=True):
        """Resize image to specified dimensions"""
        try:
            with Image.open(input_path) as img:
                if maintain_aspect:
                    # Calculate new dimensions maintaining aspect ratio
                    img_width, img_height = img.size
                    aspect = img_width / img_height
                    if width:
                        height = int(width / aspect)
                    else:
                        width = int(height * aspect)
                
                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                resized_img.save(output_path, quality=95, optimize=True)
            return True
        except Exception as e:
            logging.error(f"Error resizing image: {str(e)}")
            return False

    def crop_image(self, input_path, output_path, left, top, right, bottom):
        """Crop image to specified coordinates"""
        try:
            with Image.open(input_path) as img:
                cropped_img = img.crop((left, top, right, bottom))
                cropped_img.save(output_path, quality=95, optimize=True)
            return True
        except Exception as e:
            logging.error(f"Error cropping image: {str(e)}")
            return False

    def convert_image_format(self, input_path, output_path):
        """Convert image to different format based on output extension"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if saving as JPEG
                if output_path.lower().endswith(('.jpg', '.jpeg')) and img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(output_path, quality=95, optimize=True)
            return True
        except Exception as e:
            logging.error(f"Error converting image: {str(e)}")
            return False

    def compress_image(self, input_path, output_path, quality):
        """Compress image with specified quality (1-100)"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if saving as JPEG
                if output_path.lower().endswith(('.jpg', '.jpeg')) and img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(output_path, quality=quality, optimize=True)
            return True
        except Exception as e:
            logging.error(f"Error compressing image: {str(e)}")
            return False
