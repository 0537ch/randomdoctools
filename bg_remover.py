from rembg import remove
from PIL import Image
import io
import os

class BackgroundRemover:
    def __init__(self):
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.webp'}

    def is_supported(self, filename):
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)

    def remove_background(self, input_path, output_path=None):
        """
        Remove background from an image
        Args:
            input_path: Path to input image
            output_path: Path to save output image (optional)
        Returns:
            Path to output image
        """
        try:
            # If no output path specified, create one
            if output_path is None:
                filename = os.path.basename(input_path)
                name, _ = os.path.splitext(filename)
                output_path = os.path.join('output', f'{name}_nobg.png')  # Always save as PNG

            # Read input image
            with Image.open(input_path) as input_image:
                # Convert to RGB if necessary
                if input_image.mode in ('RGBA', 'LA'):
                    # Keep alpha channel
                    input_image = input_image.convert('RGBA')
                else:
                    # Convert to RGB for non-alpha images
                    input_image = input_image.convert('RGB')
                
                # Remove background
                output_image = remove(input_image)
                
                # Save output image
                output_image.save(output_path, 'PNG')
                
                return output_path
            
        except Exception as e:
            raise Exception(f"Error removing background: {str(e)}")
