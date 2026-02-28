"""
Synthetic Drawing Region Generator for CNN Training
Generates 224x224 grayscale patches simulating actual drawing regions
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import os
import math


class SyntheticDrawingGenerator:
    """Generates synthetic drawing region images for training"""
    
    def __init__(self, image_size=224):
        self.image_size = image_size
        
    def generate_drawing(self, output_path=None):
        """
        Generate a single synthetic drawing region image
        
        Args:
            output_path: Path to save image (optional)
            
        Returns:
            PIL Image object
        """
        # Create white background
        img = Image.new('L', (self.image_size, self.image_size), color=255)
        draw = ImageDraw.Draw(img)
        
        # Draw sparse long lines (main feature)
        self._draw_sparse_lines(draw)
        
        # Draw angled lines
        self._draw_angled_lines(draw)
        
        # Add few dimension texts
        self._add_dimension_texts(draw)
        
        # Apply augmentations
        img = self._apply_augmentations(img)
        
        if output_path:
            img.save(output_path)
        
        return img
    
    def _draw_sparse_lines(self, draw):
        """Draw sparse long lines (walls, structural elements)"""
        num_lines = random.randint(3, 8)
        
        for _ in range(num_lines):
            # Random orientation: horizontal, vertical, or diagonal
            orientation = random.choice(['horizontal', 'vertical', 'diagonal'])
            
            if orientation == 'horizontal':
                y = random.randint(20, self.image_size - 20)
                x1 = random.randint(10, 50)
                x2 = random.randint(self.image_size - 50, self.image_size - 10)
                draw.line([x1, y, x2, y], fill=0, width=random.choice([1, 2]))
                
                # Occasionally add parallel line (double wall)
                if random.random() < 0.3:
                    offset = random.randint(5, 15)
                    draw.line([x1, y + offset, x2, y + offset], fill=0, width=1)
            
            elif orientation == 'vertical':
                x = random.randint(20, self.image_size - 20)
                y1 = random.randint(10, 50)
                y2 = random.randint(self.image_size - 50, self.image_size - 10)
                draw.line([x, y1, x, y2], fill=0, width=random.choice([1, 2]))
                
                # Occasionally add parallel line
                if random.random() < 0.3:
                    offset = random.randint(5, 15)
                    draw.line([x + offset, y1, x + offset, y2], fill=0, width=1)
            
            else:  # diagonal
                x1 = random.randint(10, self.image_size // 2)
                y1 = random.randint(10, self.image_size // 2)
                x2 = random.randint(self.image_size // 2, self.image_size - 10)
                y2 = random.randint(self.image_size // 2, self.image_size - 10)
                draw.line([x1, y1, x2, y2], fill=0, width=1)
    
    def _draw_angled_lines(self, draw):
        """Draw angled lines (beams, connections)"""
        num_angled = random.randint(2, 5)
        
        for _ in range(num_angled):
            # Random angle
            angle = random.uniform(15, 75)
            
            # Random start point
            x1 = random.randint(30, self.image_size - 30)
            y1 = random.randint(30, self.image_size - 30)
            
            # Calculate end point based on angle
            length = random.randint(40, 100)
            x2 = int(x1 + length * math.cos(math.radians(angle)))
            y2 = int(y1 + length * math.sin(math.radians(angle)))
            
            # Ensure within bounds
            x2 = max(10, min(self.image_size - 10, x2))
            y2 = max(10, min(self.image_size - 10, y2))
            
            draw.line([x1, y1, x2, y2], fill=0, width=1)
            
            # Occasionally add arrow or endpoint marker
            if random.random() < 0.4:
                self._draw_arrow_head(draw, x1, y1, x2, y2)
    
    def _draw_arrow_head(self, draw, x1, y1, x2, y2):
        """Draw small arrow head at line end"""
        arrow_size = 5
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Arrow points
        left_x = x2 - arrow_size * math.cos(angle - math.pi / 6)
        left_y = y2 - arrow_size * math.sin(angle - math.pi / 6)
        right_x = x2 - arrow_size * math.cos(angle + math.pi / 6)
        right_y = y2 - arrow_size * math.sin(angle + math.pi / 6)
        
        draw.line([x2, y2, left_x, left_y], fill=0, width=1)
        draw.line([x2, y2, right_x, right_y], fill=0, width=1)
    
    def _add_dimension_texts(self, draw):
        """Add few dimension texts (sparse)"""
        num_texts = random.randint(2, 5)
        
        for _ in range(num_texts):
            x = random.randint(20, self.image_size - 60)
            y = random.randint(20, self.image_size - 20)
            
            # Generate dimension text
            text = self._generate_dimension()
            draw.text((x, y), text, fill=0)
            
            # Occasionally add dimension line
            if random.random() < 0.5:
                line_length = random.randint(30, 80)
                draw.line([x - 5, y + 10, x + line_length, y + 10], fill=0, width=1)
                # End ticks
                draw.line([x - 5, y + 7, x - 5, y + 13], fill=0, width=1)
                draw.line([x + line_length, y + 7, x + line_length, y + 13], fill=0, width=1)
    
    def _generate_dimension(self):
        """Generate dimension text"""
        dimension_types = [
            lambda: f"{random.randint(100, 9999)}",
            lambda: f"{random.randint(10, 999)}mm",
            lambda: f"{random.randint(1, 50)}m",
            lambda: f"{random.randint(1, 20)}.{random.randint(0, 99)}m",
            lambda: f"R{random.randint(50, 500)}",  # Radius
            lambda: f"Ø{random.randint(10, 200)}",  # Diameter
        ]
        return random.choice(dimension_types)()
    
    def _apply_augmentations(self, img):
        """Apply random augmentations with real-world imperfections"""
        img_array = np.array(img)
        
        # Random rotation (±6°)
        angle = random.uniform(-6, 6)
        img = img.rotate(angle, fillcolor=255)
        img_array = np.array(img)
        
        # Add noise
        noise = np.random.normal(0, 6, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        # Random brightness
        brightness_factor = random.uniform(0.85, 1.15)
        img_array = np.clip(img_array * brightness_factor, 0, 255).astype(np.uint8)
        
        # Gaussian blur (10% probability)
        if random.random() < 0.1:
            from scipy.ndimage import gaussian_filter
            sigma = random.uniform(0.5, 1.5)
            img_array = gaussian_filter(img_array, sigma=sigma)
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        # Motion blur (5% probability)
        if random.random() < 0.05:
            kernel_size = random.randint(3, 7)
            kernel = np.zeros((kernel_size, kernel_size))
            kernel[kernel_size // 2, :] = 1.0 / kernel_size
            from scipy.ndimage import convolve
            img_array = convolve(img_array, kernel, mode='constant', cval=255)
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        # Random erasing
        if random.random() < 0.15:
            h, w = img_array.shape
            erase_h = int(h * random.uniform(0.05, 0.1))
            erase_w = int(w * random.uniform(0.05, 0.1))
            y = random.randint(0, h - erase_h)
            x = random.randint(0, w - erase_w)
            img_array[y:y+erase_h, x:x+erase_w] = 255
        
        # Simulate line thickness variation
        if random.random() < 0.3:
            from scipy.ndimage import maximum_filter
            kernel_size = random.choice([1, 2])
            img_array = 255 - maximum_filter(255 - img_array, size=kernel_size)
        
        # Add occasional smudge/blur
        if random.random() < 0.2:
            from scipy.ndimage import gaussian_filter
            sigma = random.uniform(0.3, 0.8)
            img_array = gaussian_filter(img_array, sigma=sigma)
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        # Background texture
        if random.random() < 0.2:
            texture = np.random.normal(250, 3, img_array.shape)
            mask = img_array > 240
            img_array[mask] = np.clip(texture[mask], 0, 255).astype(np.uint8)
        
        return Image.fromarray(img_array)
    
    def generate_batch(self, num_samples, output_dir):
        """
        Generate multiple drawing region images
        
        Args:
            num_samples: Number of images to generate
            output_dir: Directory to save images
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for i in range(num_samples):
            output_path = os.path.join(output_dir, f'drawing_{i:04d}.png')
            self.generate_drawing(output_path=output_path)
            
            if (i + 1) % 50 == 0:
                print(f"Generated {i + 1}/{num_samples} drawing images")
        
        print(f"✓ Generated {num_samples} drawing images in {output_dir}")


if __name__ == "__main__":
    # Test generation
    generator = SyntheticDrawingGenerator()
    
    # Generate single sample
    img = generator.generate_drawing()
    img.save('test_drawing.png')
    print("✓ Test drawing saved as test_drawing.png")
    
    # Generate batch
    generator.generate_batch(10, 'test_drawings')
