from pdf2image import convert_from_path
from PIL import Image
import os
import logging

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
