"""
Synthetic Title Block Generator for CNN Training
Generates 224x224 grayscale patches simulating drawing title blocks
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import os


class SyntheticTitleBlockGenerator:
    """Generates synthetic title block images for training"""
    
    def __init__(self, image_size=224):
        self.image_size = image_size
        
    def generate_titleblock(self, output_path=None):
        """
        Generate a single synthetic title block image with imperfections
        
        Args:
            output_path: Path to save image (optional)
            
        Returns:
            PIL Image object
        """
        # Create white background
        img = Image.new('L', (self.image_size, self.image_size), color=255)
        draw = ImageDraw.Draw(img)
        
        # Draw rectangular border with breaks
        margin = 10 + random.randint(-2, 2)
        border_width = 3
        
        # Sometimes make sparse (class boundary confusion)
        if random.random() < 0.1:
            # Draw only partial border
            draw.line([margin, margin, self.image_size - margin, margin], fill=0, width=border_width)
            draw.line([margin, self.image_size - margin, self.image_size - margin, self.image_size - margin], 
                     fill=0, width=border_width)
        else:
            # Draw full border with possible breaks
            if random.random() < 0.15:
                # Broken border
                segments = [(margin, margin, self.image_size - margin, margin),
                           (self.image_size - margin, margin, self.image_size - margin, self.image_size - margin),
                           (self.image_size - margin, self.image_size - margin, margin, self.image_size - margin)]
                for seg in segments:
                    if random.random() < 0.85:
                        draw.line(seg, fill=0, width=border_width)
            else:
                draw.rectangle([margin, margin, self.image_size - margin, self.image_size - margin],
                              outline=0, width=border_width)
        
        # Add inner dividing lines with breaks
        self._draw_divisions_with_imperfections(draw, margin)
        
        # Fill with metadata text
        self._fill_metadata_with_imperfections(draw, margin)
        
        # Apply augmentations
        img = self._apply_augmentations(img)
        
        if output_path:
            img.save(output_path)
        
        return img
    
    def _draw_divisions_with_imperfections(self, draw, margin):
        """Draw internal division lines with breaks"""
        # Horizontal divisions
        num_h_divisions = random.randint(3, 6)
        section_height = (self.image_size - 2 * margin) // num_h_divisions
        
        for i in range(1, num_h_divisions):
            y = margin + i * section_height + random.randint(-3, 3)  # Misalignment
            
            # Broken lines (10-20% discontinuity)
            if random.random() < 0.15:
                segments = 3
                seg_len = (self.image_size - 2 * margin) // segments
                for j in range(segments):
                    if random.random() < 0.8:
                        x_start = margin + j * seg_len
                        x_end = margin + (j + 1) * seg_len
                        draw.line([x_start, y, x_end, y], fill=0, width=1)
            else:
                draw.line([margin, y, self.image_size - margin, y], fill=0, width=1)
        
        # Vertical divisions (fewer)
        num_v_divisions = random.randint(1, 3)
        section_width = (self.image_size - 2 * margin) // (num_v_divisions + 1)
        
        for i in range(1, num_v_divisions + 1):
            x = margin + i * section_width + random.randint(-3, 3)
            
            # Only draw in certain sections
            if random.random() < 0.7:
                y_start = margin + random.randint(0, 2) * section_height
                y_end = self.image_size - margin
                
                # Broken lines
                if random.random() < 0.15:
                    segments = 2
                    seg_len = (y_end - y_start) // segments
                    for j in range(segments):
                        if random.random() < 0.8:
                            draw.line([x, y_start + j * seg_len, x, y_start + (j + 1) * seg_len], 
                                     fill=0, width=1)
                else:
                    draw.line([x, y_start, x, y_end], fill=0, width=1)
    
    def _fill_metadata_with_imperfections(self, draw, margin):
        """Fill title block with dense metadata text with imperfections"""
        # Define metadata fields
        fields = [
            ('PROJECT:', self._generate_project_name()),
            ('DRAWING NO:', self._generate_drawing_number()),
            ('SCALE:', self._generate_scale()),
            ('DATE:', self._generate_date()),
            ('REV:', self._generate_revision()),
            ('DRAWN BY:', self._generate_name()),
            ('CHECKED BY:', self._generate_name()),
            ('APPROVED:', self._generate_name()),
            ('SHEET:', f"{random.randint(1, 50)} OF {random.randint(50, 100)}"),
            ('TITLE:', self._generate_title()),
        ]
        
        # Randomly select 6-10 fields
        num_fields = random.randint(6, 10)
        selected_fields = random.sample(fields, num_fields)
        
        # Compact spacing with random shifts
        y_offset = margin + 15
        line_spacing = (self.image_size - 2 * margin - 20) // num_fields
        
        for label, value in selected_fields:
            # Skip some fields (missing data)
            if random.random() < 0.05:
                continue
            
            x_label = margin + 15 + random.randint(-3, 3)
            x_value = margin + 80 + random.randint(-5, 5)
            
            # Random vertical shifts
            y_pos = y_offset + random.randint(-2, 2)
            
            # Draw label
            draw.text((x_label, y_pos), label, fill=0)
            
            # Draw value (slightly offset)
            # Overlapping text (low probability)
            if random.random() < 0.05:
                y_pos -= random.randint(3, 8)
            
            # Truncated text occasionally
            if random.random() < 0.1:
                value = value[:len(value)//2]
            
            draw.text((x_value, y_pos), value, fill=0)
            
            y_offset += line_spacing
    
    def _generate_project_name(self):
        """Generate project name"""
        projects = [
            'RESIDENTIAL COMPLEX',
            'COMMERCIAL TOWER',
            'BRIDGE CONSTRUCTION',
            'HIGHWAY EXPANSION',
            'METRO STATION',
            'INDUSTRIAL FACILITY'
        ]
        return random.choice(projects)
    
    def _generate_drawing_number(self):
        """Generate drawing number"""
        prefix = random.choice(['A', 'S', 'M', 'E', 'C'])
        number = random.randint(100, 999)
        return f"{prefix}-{number}"
    
    def _generate_scale(self):
        """Generate scale"""
        scales = ['1:50', '1:100', '1:200', '1:500', '1:1000', 'NTS']
        return random.choice(scales)
    
    def _generate_date(self):
        """Generate date"""
        day = random.randint(1, 28)
        month = random.randint(1, 12)
        year = random.randint(2020, 2024)
        return f"{day:02d}/{month:02d}/{year}"
    
    def _generate_revision(self):
        """Generate revision number"""
        return random.choice(['00', '01', '02', '03', 'A', 'B', 'C', 'FINAL'])
    
    def _generate_name(self):
        """Generate person name/initials"""
        if random.random() < 0.5:
            # Initials
            return f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}.{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}."
        else:
            # Short name
            names = ['SMITH', 'JONES', 'BROWN', 'DAVIS', 'WILSON', 'TAYLOR']
            return random.choice(names)
    
    def _generate_title(self):
        """Generate drawing title"""
        titles = [
            'FOUNDATION PLAN',
            'FLOOR PLAN',
            'ELEVATION VIEW',
            'SECTION DETAIL',
            'SITE LAYOUT',
            'STRUCTURAL DETAIL'
        ]
        return random.choice(titles)
    
    def _apply_augmentations(self, img):
        """Apply random augmentations with real-world imperfections"""
        img_array = np.array(img)
        
        # Random rotation (±4°)
        angle = random.uniform(-4, 4)
        img = img.rotate(angle, fillcolor=255)
        img_array = np.array(img)
        
        # Add noise
        noise = np.random.normal(0, 7, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        # Random brightness
        brightness_factor = random.uniform(0.82, 1.18)
        img_array = np.clip(img_array * brightness_factor, 0, 255).astype(np.uint8)
        
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
        
        # Random erasing
        if random.random() < 0.15:
            h, w = img_array.shape
            erase_h = int(h * random.uniform(0.05, 0.1))
            erase_w = int(w * random.uniform(0.05, 0.1))
            y = random.randint(0, h - erase_h)
            x = random.randint(0, w - erase_w)
            img_array[y:y+erase_h, x:x+erase_w] = 255
        
        # Simulate scan artifacts (occasional)
        if random.random() < 0.2:
            # Add horizontal line artifact
            artifact_y = random.randint(0, self.image_size - 1)
            img_array[artifact_y, :] = np.clip(img_array[artifact_y, :] + random.randint(-20, 20), 0, 255)
        
        # Faded lines (some lines lighter)
        if random.random() < 0.2:
            mask = img_array < 100
            img_array[mask] = np.clip(img_array[mask] + random.randint(30, 60), 0, 255).astype(np.uint8)
        
        # Background texture
        if random.random() < 0.2:
            texture = np.random.normal(250, 3, img_array.shape)
            mask = img_array > 240
            img_array[mask] = np.clip(texture[mask], 0, 255).astype(np.uint8)
        
        return Image.fromarray(img_array)
    
    def generate_batch(self, num_samples, output_dir):
        """
        Generate multiple title block images
        
        Args:
            num_samples: Number of images to generate
            output_dir: Directory to save images
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for i in range(num_samples):
            output_path = os.path.join(output_dir, f'titleblock_{i:04d}.png')
            self.generate_titleblock(output_path=output_path)
            
            if (i + 1) % 50 == 0:
                print(f"Generated {i + 1}/{num_samples} title block images")
        
        print(f"✓ Generated {num_samples} title block images in {output_dir}")


if __name__ == "__main__":
    # Test generation
    generator = SyntheticTitleBlockGenerator()
    
    # Generate single sample
    img = generator.generate_titleblock()
    img.save('test_titleblock.png')
    print("✓ Test title block saved as test_titleblock.png")
    
    # Generate batch
    generator.generate_batch(10, 'test_titleblocks')
