"""
Synthetic Schedule Generator for CNN Training
Generates 224x224 grayscale patches simulating construction schedules/tables
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import os


class SyntheticScheduleGenerator:
    """Generates synthetic schedule/table images for training"""
    
    def __init__(self, image_size=224):
        self.image_size = image_size
        
    def generate_schedule(self, num_rows=None, num_cols=None, output_path=None):
        """
        Generate a single synthetic schedule image with imperfections
        
        Args:
            num_rows: Number of table rows (5-10 if None)
            num_cols: Number of columns (3-5 if None)
            output_path: Path to save image (optional)
            
        Returns:
            PIL Image object
        """
        if num_rows is None:
            num_rows = random.randint(5, 10)
        if num_cols is None:
            num_cols = random.randint(3, 5)
        
        # Create white background
        img = Image.new('L', (self.image_size, self.image_size), color=255)
        draw = ImageDraw.Draw(img)
        
        # Calculate grid dimensions with random padding
        margin = 10 + random.randint(-3, 3)
        table_width = self.image_size - 2 * margin
        table_height = self.image_size - 2 * margin
        row_height = table_height // num_rows
        
        # Random column widths
        col_widths = self._generate_column_widths(num_cols, table_width)
        
        # Draw grid lines with breaks and misalignments
        self._draw_grid_with_imperfections(draw, margin, num_rows, num_cols, row_height, col_widths)
        
        # Fill cells with content (skip some rows for missing data)
        self._fill_cells_with_imperfections(draw, margin, num_rows, num_cols, row_height, col_widths)
        
        # Make slightly irregular (class boundary confusion)
        if random.random() < 0.1:
            # Add some non-grid elements
            x = random.randint(margin, self.image_size - margin - 30)
            y = random.randint(margin, self.image_size - margin - 10)
            draw.text((x, y), random.choice(['NOTE:', 'REF:', '*']), fill=0)
        
        # Apply augmentations
        img = self._apply_augmentations(img)
        
        if output_path:
            img.save(output_path)
        
        return img
    
    def _generate_column_widths(self, num_cols, total_width):
        """Generate random column widths that sum to total_width"""
        # Random proportions
        proportions = [random.uniform(0.5, 2.0) for _ in range(num_cols)]
        total = sum(proportions)
        widths = [int(total_width * p / total) for p in proportions]
        
        # Adjust last column to match exactly
        widths[-1] = total_width - sum(widths[:-1])
        return widths
    
    def _draw_grid_with_imperfections(self, draw, margin, num_rows, num_cols, row_height, col_widths):
        """Draw grid lines with broken segments and misalignments"""
        # Horizontal lines with breaks
        for i in range(num_rows + 1):
            y = margin + i * row_height + random.randint(-2, 2)  # Misalignment
            line_width = 2 if i == 0 else 1
            
            # Randomly remove 10-20% of line segments
            if random.random() < 0.15 and i > 0:
                # Draw broken line
                segments = 4
                seg_len = (self.image_size - 2 * margin) // segments
                for j in range(segments):
                    if random.random() < 0.8:  # 20% chance to skip segment
                        x_start = margin + j * seg_len
                        x_end = margin + (j + 1) * seg_len
                        draw.line([x_start, y, x_end, y], fill=0, width=line_width)
            else:
                draw.line([margin, y, self.image_size - margin, y], fill=0, width=line_width)
        
        # Vertical lines with breaks
        x = margin
        for i in range(num_cols + 1):
            line_width = 2 if i == 0 or i == num_cols else 1
            x_offset = random.randint(-2, 2)  # Misalignment
            
            # Randomly remove segments
            if random.random() < 0.15 and i > 0 and i < num_cols:
                # Draw broken line
                segments = 3
                seg_len = (self.image_size - 2 * margin) // segments
                for j in range(segments):
                    if random.random() < 0.8:
                        y_start = margin + j * seg_len
                        y_end = margin + (j + 1) * seg_len
                        draw.line([x + x_offset, y_start, x + x_offset, y_end], 
                                 fill=0, width=line_width)
            else:
                draw.line([x + x_offset, margin, x + x_offset, self.image_size - margin], 
                         fill=0, width=line_width)
            
            if i < num_cols:
                x += col_widths[i]
    
    def _fill_cells_with_imperfections(self, draw, margin, num_rows, num_cols, row_height, col_widths):
        """Fill cells with text content, skip some rows"""
        for row in range(num_rows):
            # Skip entire row (missing data)
            if random.random() < 0.05 and row > 0:
                continue
            
            # Add extra blank row occasionally
            if random.random() < 0.03:
                continue
            
            x = margin
            for col in range(num_cols):
                # Cell position with random shifts
                cell_x = x + 5 + random.randint(-2, 2)
                cell_y = margin + row * row_height + 5 + random.randint(-3, 3)
                
                # Generate content
                if row == 0:
                    content = self._generate_header(col)
                else:
                    content = self._generate_cell_data(col)
                
                # Random font size changes (imperfect typography)
                # Note: PIL default font doesn't support size, but we simulate with spacing
                if random.random() < 0.1:
                    content = content[:len(content)//2]  # Truncated text
                
                # Draw text
                draw.text((cell_x, cell_y), content, fill=0)
                
                x += col_widths[col]
    
    def _generate_header(self, col_index):
        """Generate header text"""
        headers = [
            ['Item', 'Description', 'Qty', 'Unit', 'Rate'],
            ['Activity', 'Start', 'End', 'Duration', 'Status'],
            ['Material', 'Spec', 'Quantity', 'Cost', 'Supplier'],
            ['Task', 'Date', 'Hours', 'Progress', 'Notes']
        ]
        header_set = random.choice(headers)
        return header_set[col_index % len(header_set)]
    
    def _generate_cell_data(self, col_index):
        """Generate cell data based on column type"""
        data_types = [
            # Numeric
            lambda: str(random.randint(1, 999)),
            # Dates
            lambda: f"{random.randint(1,28)}/{random.randint(1,12)}/24",
            # Codes
            lambda: f"{random.choice(['A', 'B', 'C'])}-{random.randint(100,999)}",
            # Short text
            lambda: random.choice(['Concrete', 'Steel', 'Brick', 'Wood', 'Glass']),
            # Measurements
            lambda: f"{random.randint(10,500)}m",
        ]
        
        return random.choice(data_types)()
    
    def _apply_augmentations(self, img):
        """Apply random augmentations with real-world imperfections"""
        img_array = np.array(img)
        
        # Random rotation (±4°)
        angle = random.uniform(-4, 4)
        img = img.rotate(angle, fillcolor=255)
        img_array = np.array(img)
        
        # Add noise
        noise = np.random.normal(0, 6, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        # Random contrast variation
        contrast_factor = random.uniform(0.75, 1.25)
        mean = img_array.mean()
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
        
        # Random erasing
        if random.random() < 0.15:
            h, w = img_array.shape
            erase_h = int(h * random.uniform(0.05, 0.1))
            erase_w = int(w * random.uniform(0.05, 0.1))
            y = random.randint(0, h - erase_h)
            x = random.randint(0, w - erase_w)
            img_array[y:y+erase_h, x:x+erase_w] = 255
        
        # Random line thickness variation (simulate scan quality)
        if random.random() < 0.3:
            from scipy.ndimage import maximum_filter
            kernel_size = random.choice([1, 2])
            img_array = 255 - maximum_filter(255 - img_array, size=kernel_size)
        
        # Background texture
        if random.random() < 0.2:
            texture = np.random.normal(250, 3, img_array.shape)
            mask = img_array > 240
            img_array[mask] = np.clip(texture[mask], 0, 255).astype(np.uint8)
        
        return Image.fromarray(img_array)
    
    def generate_batch(self, num_samples, output_dir):
        """
        Generate multiple schedule images
        
        Args:
            num_samples: Number of images to generate
            output_dir: Directory to save images
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for i in range(num_samples):
            output_path = os.path.join(output_dir, f'schedule_{i:04d}.png')
            self.generate_schedule(output_path=output_path)
            
            if (i + 1) % 50 == 0:
                print(f"Generated {i + 1}/{num_samples} schedule images")
        
        print(f"✓ Generated {num_samples} schedule images in {output_dir}")


if __name__ == "__main__":
    # Test generation
    generator = SyntheticScheduleGenerator()
    
    # Generate single sample
    img = generator.generate_schedule()
    img.save('test_schedule.png')
    print("✓ Test schedule saved as test_schedule.png")
    
    # Generate batch
    generator.generate_batch(10, 'test_schedules')
