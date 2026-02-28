"""
Synthetic Legend Generator for CNN Training
Generates 224x224 grayscale patches simulating drawing legends
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import os


class SyntheticLegendGenerator:
    """Generates synthetic legend images for training"""
    
    def __init__(self, image_size=224):
        self.image_size = image_size
        self.shapes = ['circle', 'square', 'triangle', 'line', 'dashed_line']
        
    def generate_legend(self, num_items=None, output_path=None):
        """
        Generate a single synthetic legend image with imperfections
        
        Args:
            num_items: Number of legend items (8-12 if None)
            output_path: Path to save image (optional)
            
        Returns:
            PIL Image object
        """
        if num_items is None:
            num_items = random.randint(8, 12)
        
        # Create white background
        img = Image.new('L', (self.image_size, self.image_size), color=255)
        draw = ImageDraw.Draw(img)
        
        # 2-column layout with random padding shifts
        col_width = self.image_size // 2
        item_height = self.image_size // (num_items // 2 + 2)
        symbol_size = min(20, item_height - 10)
        
        # Add slight grid-like structure (class boundary confusion)
        if random.random() < 0.15:
            # Draw faint grid lines
            for i in range(2, num_items // 2):
                y = i * item_height + random.randint(-5, 5)
                draw.line([10, y, self.image_size - 10, y], fill=220, width=1)
        
        # Generate legend items with imperfections
        for i in range(num_items):
            col = i % 2
            row = i // 2
            
            # Random padding shifts
            x_base = col * col_width + 20 + random.randint(-5, 5)
            y_base = row * item_height + 20 + random.randint(-8, 8)
            
            # Skip some items randomly (missing rows)
            if random.random() < 0.05:
                continue
            
            # Draw shape symbol with broken lines
            shape = random.choice(self.shapes)
            self._draw_shape(draw, shape, x_base, y_base, symbol_size)
            
            # Draw text label with imperfect typography
            text_x = x_base + symbol_size + 10 + random.randint(-3, 3)
            text_y = y_base + random.randint(-2, 2)
            label = self._generate_label()
            
            # Overlapping text (low probability)
            if random.random() < 0.05:
                text_y -= random.randint(5, 10)
            
            draw.text((text_x, text_y), label, fill=0)
        
        # Apply augmentations
        img = self._apply_augmentations(img)
        
        if output_path:
            img.save(output_path)
        
        return img
    
    def _draw_shape(self, draw, shape, x, y, size):
        """Draw a geometric shape with broken lines"""
        # Randomly break lines (10-20% discontinuity)
        broken = random.random() < 0.15
        
        if shape == 'circle':
            if broken:
                # Draw arc instead of full circle
                start_angle = random.randint(0, 90)
                end_angle = start_angle + random.randint(200, 340)
                draw.arc([x, y, x + size, y + size], start_angle, end_angle, fill=0, width=2)
            else:
                draw.ellipse([x, y, x + size, y + size], outline=0, width=2)
        elif shape == 'square':
            if broken:
                # Draw 3 sides only
                sides = random.sample([(x, y, x + size, y), 
                                      (x + size, y, x + size, y + size),
                                      (x + size, y + size, x, y + size),
                                      (x, y + size, x, y)], 3)
                for side in sides:
                    draw.line(side, fill=0, width=2)
            else:
                draw.rectangle([x, y, x + size, y + size], outline=0, width=2)
        elif shape == 'triangle':
            points = [(x, y + size), (x + size//2, y), (x + size, y + size)]
            if broken:
                # Draw 2 sides only
                draw.line([points[0], points[1]], fill=0, width=2)
                draw.line([points[1], points[2]], fill=0, width=2)
            else:
                draw.polygon(points, outline=0)
        elif shape == 'line':
            if broken:
                # Draw segmented line
                segments = 3
                seg_len = size // segments
                for i in range(0, size, seg_len * 2):
                    draw.line([x + i, y + size//2, x + min(i + seg_len, size), y + size//2], 
                             fill=0, width=2)
            else:
                draw.line([x, y + size//2, x + size, y + size//2], fill=0, width=2)
        elif shape == 'dashed_line':
            dash_length = size // 4
            for i in range(0, size, dash_length * 2):
                # Random discontinuities
                if random.random() < 0.8:
                    draw.line([x + i, y + size//2, x + i + dash_length, y + size//2], 
                             fill=0, width=2)
    
    def _generate_label(self):
        """Generate random text label"""
        prefixes = ['Wall', 'Door', 'Window', 'Beam', 'Column', 'Slab', 'Foundation']
        suffixes = ['Type A', 'Type B', '300mm', '450mm', 'Existing', 'New']
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"
    
    def _apply_augmentations(self, img):
        """Apply random augmentations with real-world imperfections"""
        img_array = np.array(img)
        
        # Random rotation (±4° for perspective skew)
        angle = random.uniform(-4, 4)
        img = img.rotate(angle, fillcolor=255)
        img_array = np.array(img)
        
        # Add Gaussian noise
        noise = np.random.normal(0, 8, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        # Random brightness jitter
        brightness_factor = random.uniform(0.85, 1.15)
        img_array = np.clip(img_array * brightness_factor, 0, 255).astype(np.uint8)
        
        # Random contrast jitter
        if random.random() < 0.3:
            mean = img_array.mean()
            contrast_factor = random.uniform(0.7, 1.3)
            img_array = np.clip((img_array - mean) * contrast_factor + mean, 0, 255).astype(np.uint8)
        
        # Gaussian blur (10% probability)
        if random.random() < 0.1:
            from scipy.ndimage import gaussian_filter
            img_array = gaussian_filter(img_array, sigma=random.uniform(0.5, 1.5))
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        # Motion blur (5% probability)
        if random.random() < 0.05:
            kernel_size = random.randint(3, 7)
            kernel = np.zeros((kernel_size, kernel_size))
            kernel[kernel_size // 2, :] = 1.0 / kernel_size
            from scipy.ndimage import convolve
            img_array = convolve(img_array, kernel, mode='constant', cval=255)
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        # Random erasing (5-10% area)
        if random.random() < 0.15:
            h, w = img_array.shape
            erase_h = int(h * random.uniform(0.05, 0.1))
            erase_w = int(w * random.uniform(0.05, 0.1))
            y = random.randint(0, h - erase_h)
            x = random.randint(0, w - erase_w)
            img_array[y:y+erase_h, x:x+erase_w] = 255
        
        # Slight background texture
        if random.random() < 0.2:
            texture = np.random.normal(250, 3, img_array.shape)
            mask = img_array > 240
            img_array[mask] = np.clip(texture[mask], 0, 255).astype(np.uint8)
        
        return Image.fromarray(img_array)
    
    def generate_batch(self, num_samples, output_dir):
        """
        Generate multiple legend images
        
        Args:
            num_samples: Number of images to generate
            output_dir: Directory to save images
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for i in range(num_samples):
            output_path = os.path.join(output_dir, f'legend_{i:04d}.png')
            self.generate_legend(output_path=output_path)
            
            if (i + 1) % 50 == 0:
                print(f"Generated {i + 1}/{num_samples} legend images")
        
        print(f"✓ Generated {num_samples} legend images in {output_dir}")


if __name__ == "__main__":
    # Test generation
    generator = SyntheticLegendGenerator()
    
    # Generate single sample
    img = generator.generate_legend()
    img.save('test_legend.png')
    print("✓ Test legend saved as test_legend.png")
    
    # Generate batch
    generator.generate_batch(10, 'test_legends')
