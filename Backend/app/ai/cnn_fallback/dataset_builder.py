"""
Dataset Builder for CNN Training
Combines all synthetic generators and organizes dataset structure
"""

import os
import json
import random
from pathlib import Path
import shutil

from app.ai.cnn_fallback.synthetic_legend_generator import SyntheticLegendGenerator
from app.ai.cnn_fallback.synthetic_schedule_generator import SyntheticScheduleGenerator
from app.ai.cnn_fallback.synthetic_titleblock_generator import SyntheticTitleBlockGenerator
from app.ai.cnn_fallback.synthetic_drawing_generator import SyntheticDrawingGenerator


class DatasetBuilder:
    """Builds complete training dataset with train/val/test splits"""
    
    def __init__(self, base_dir='dataset'):
        self.base_dir = Path(base_dir)
        self.classes = ['legend', 'schedule', 'title_block', 'drawing_region']
        
        # Initialize generators
        self.generators = {
            'legend': SyntheticLegendGenerator(),
            'schedule': SyntheticScheduleGenerator(),
            'title_block': SyntheticTitleBlockGenerator(),
            'drawing_region': SyntheticDrawingGenerator()
        }
    
    def build_dataset(self, 
                     synthetic_per_class=500,
                     train_ratio=0.7,
                     val_ratio=0.15,
                     test_ratio=0.15):
        """
        Build complete dataset with train/val/test splits
        
        Args:
            synthetic_per_class: Number of synthetic samples per class
            train_ratio: Proportion for training set
            val_ratio: Proportion for validation set
            test_ratio: Proportion for test set
        """
        print("=" * 60)
        print("Building CNN Training Dataset")
        print("=" * 60)
        
        # Create directory structure
        self._create_directory_structure()
        
        # Generate synthetic data for each class
        for class_name in self.classes:
            print(f"\n📦 Generating {class_name} samples...")
            self._generate_class_samples(class_name, synthetic_per_class)
        
        # Split into train/val/test
        print("\n📊 Splitting dataset...")
        self._split_dataset(train_ratio, val_ratio, test_ratio)
        
        # Generate metadata
        print("\n📝 Generating metadata...")
        metadata = self._generate_metadata()
        
        # Save metadata
        metadata_path = self.base_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, indent=2, fp=f)
        
        print("\n" + "=" * 60)
        print("✓ Dataset build complete!")
        print(f"✓ Location: {self.base_dir.absolute()}")
        print(f"✓ Total samples: {metadata['total_samples']}")
        print(f"✓ Train: {metadata['train_samples']}")
        print(f"✓ Val: {metadata['val_samples']}")
        print(f"✓ Test: {metadata['test_samples']}")
        print("=" * 60)
        
        return metadata
    
    def _create_directory_structure(self):
        """Create dataset directory structure"""
        # Main splits
        splits = ['train', 'val', 'test', 'raw']
        
        for split in splits:
            for class_name in self.classes:
                dir_path = self.base_dir / split / class_name
                dir_path.mkdir(parents=True, exist_ok=True)
        
        # Real data directory (for manual addition)
        real_dir = self.base_dir / 'real'
        for class_name in self.classes:
            (real_dir / class_name).mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Created directory structure at {self.base_dir}")
    
    def _generate_class_samples(self, class_name, num_samples):
        """Generate samples for a specific class"""
        generator = self.generators[class_name]
        output_dir = self.base_dir / 'raw' / class_name
        
        # Generate based on class type
        if class_name == 'legend':
            generator.generate_batch(num_samples, str(output_dir))
        elif class_name == 'schedule':
            generator.generate_batch(num_samples, str(output_dir))
        elif class_name == 'title_block':
            generator.generate_batch(num_samples, str(output_dir))
        elif class_name == 'drawing_region':
            generator.generate_batch(num_samples, str(output_dir))
    
    def _split_dataset(self, train_ratio, val_ratio, test_ratio):
        """Split raw data into train/val/test sets"""
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.01, \
            "Ratios must sum to 1.0"
        
        for class_name in self.classes:
            raw_dir = self.base_dir / 'raw' / class_name
            files = list(raw_dir.glob('*.png'))
            
            # Shuffle files
            random.shuffle(files)
            
            # Calculate split indices
            total = len(files)
            train_end = int(total * train_ratio)
            val_end = train_end + int(total * val_ratio)
            
            # Split files
            train_files = files[:train_end]
            val_files = files[train_end:val_end]
            test_files = files[val_end:]
            
            # Copy to respective directories
            self._copy_files(train_files, self.base_dir / 'train' / class_name)
            self._copy_files(val_files, self.base_dir / 'val' / class_name)
            self._copy_files(test_files, self.base_dir / 'test' / class_name)
            
            print(f"  {class_name}: {len(train_files)} train, "
                  f"{len(val_files)} val, {len(test_files)} test")
    
    def _copy_files(self, files, dest_dir):
        """Copy files to destination directory"""
        for file in files:
            shutil.copy2(file, dest_dir / file.name)
    
    def _generate_metadata(self):
        """Generate dataset metadata"""
        metadata = {
            'classes': self.classes,
            'num_classes': len(self.classes),
            'image_size': 224,
            'splits': {}
        }
        
        total_samples = 0
        
        for split in ['train', 'val', 'test']:
            split_data = {}
            split_total = 0
            
            for class_name in self.classes:
                class_dir = self.base_dir / split / class_name
                num_samples = len(list(class_dir.glob('*.png')))
                split_data[class_name] = num_samples
                split_total += num_samples
            
            metadata['splits'][split] = split_data
            metadata[f'{split}_samples'] = split_total
            total_samples += split_total
        
        metadata['total_samples'] = total_samples
        
        return metadata
    
    def add_real_samples(self, class_name, source_dir):
        """
        Add real cropped samples to dataset
        
        Args:
            class_name: Target class name
            source_dir: Directory containing real samples
        """
        if class_name not in self.classes:
            raise ValueError(f"Invalid class: {class_name}")
        
        source_path = Path(source_dir)
        if not source_path.exists():
            raise ValueError(f"Source directory not found: {source_dir}")
        
        # Copy to real directory
        real_dir = self.base_dir / 'real' / class_name
        
        files = list(source_path.glob('*.png')) + list(source_path.glob('*.jpg'))
        
        for file in files:
            shutil.copy2(file, real_dir / file.name)
        
        print(f"✓ Added {len(files)} real samples to {class_name}")
        print(f"  Note: Run rebuild_splits() to include in train/val/test")
    
    def rebuild_splits(self, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
        """
        Rebuild train/val/test splits including real samples
        
        Args:
            train_ratio: Proportion for training set
            val_ratio: Proportion for validation set
            test_ratio: Proportion for test set
        """
        print("Rebuilding dataset splits with real samples...")
        
        # Clear existing splits
        for split in ['train', 'val', 'test']:
            for class_name in self.classes:
                split_dir = self.base_dir / split / class_name
                for file in split_dir.glob('*.png'):
                    file.unlink()
        
        # Combine raw and real samples
        for class_name in self.classes:
            raw_dir = self.base_dir / 'raw' / class_name
            real_dir = self.base_dir / 'real' / class_name
            
            all_files = list(raw_dir.glob('*.png')) + list(real_dir.glob('*.png'))
            
            if not all_files:
                continue
            
            # Shuffle
            random.shuffle(all_files)
            
            # Split
            total = len(all_files)
            train_end = int(total * train_ratio)
            val_end = train_end + int(total * val_ratio)
            
            train_files = all_files[:train_end]
            val_files = all_files[train_end:val_end]
            test_files = all_files[val_end:]
            
            # Copy
            self._copy_files(train_files, self.base_dir / 'train' / class_name)
            self._copy_files(val_files, self.base_dir / 'val' / class_name)
            self._copy_files(test_files, self.base_dir / 'test' / class_name)
            
            print(f"  {class_name}: {len(train_files)} train, "
                  f"{len(val_files)} val, {len(test_files)} test")
        
        # Update metadata
        metadata = self._generate_metadata()
        with open(self.base_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, indent=2, fp=f)
        
        print("✓ Splits rebuilt successfully")


if __name__ == "__main__":
    # Build dataset
    builder = DatasetBuilder(base_dir='cnn_dataset')
    
    # Generate 500 synthetic samples per class
    metadata = builder.build_dataset(
        synthetic_per_class=500,
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15
    )
    
    print("\n📋 Dataset ready for training!")
    print("   Add real samples to: cnn_dataset/real/<class_name>/")
    print("   Then run: builder.rebuild_splits()")
