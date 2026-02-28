"""
CNN Training Script for Layout Region Classification
Uses MobileNetV2 with custom head for 4-class classification
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import json
import os
from pathlib import Path
import time
from tqdm import tqdm


class LayoutDataset(Dataset):
    """Dataset loader for layout region images"""
    
    def __init__(self, data_dir, transform=None):
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.classes = ['legend', 'schedule', 'title_block', 'drawing_region']
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        # Load all image paths and labels
        self.samples = []
        for class_name in self.classes:
            class_dir = self.data_dir / class_name
            if not class_dir.exists():
                continue
            
            for img_path in class_dir.glob('*.png'):
                self.samples.append((str(img_path), self.class_to_idx[class_name]))
        
        print(f"Loaded {len(self.samples)} samples from {data_dir}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


class LayoutClassifier(nn.Module):
    """MobileNetV2-based layout classifier"""
    
    def __init__(self, num_classes=4, dropout=0.3):
        super(LayoutClassifier, self).__init__()
        
        # Load pretrained MobileNetV2
        self.backbone = models.mobilenet_v2(pretrained=True)
        
        # Freeze backbone except last block
        for param in self.backbone.features[:-3].parameters():
            param.requires_grad = False
        
        # Replace classifier head
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


class CNNTrainer:
    """Trainer for layout region classifier"""
    
    def __init__(self, dataset_dir, model_save_dir='models', device=None):
        self.dataset_dir = Path(dataset_dir)
        self.model_save_dir = Path(model_save_dir)
        self.model_save_dir.mkdir(exist_ok=True)
        
        # Device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
        
        print(f"Using device: {self.device}")
        
        # Data transforms
        self.train_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomRotation(10),
            transforms.RandomHorizontalFlip(0.3),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        self.val_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Load datasets
        self.train_dataset = LayoutDataset(
            self.dataset_dir / 'train',
            transform=self.train_transform
        )
        self.val_dataset = LayoutDataset(
            self.dataset_dir / 'val',
            transform=self.val_transform
        )
        
        # Model
        self.model = LayoutClassifier(num_classes=4, dropout=0.3)
        self.model.to(self.device)
        
        # Training history
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
    
    def train(self, epochs=15, batch_size=32, lr=1e-4):
        """
        Train the model
        
        Args:
            epochs: Number of training epochs
            batch_size: Batch size
            lr: Learning rate
        """
        print("\n" + "=" * 60)
        print("Starting Training")
        print("=" * 60)
        
        # Data loaders
        train_loader = DataLoader(
            self.train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0
        )
        val_loader = DataLoader(
            self.val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )
        
        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='max', factor=0.5, patience=2
        )
        
        best_val_acc = 0.0
        
        for epoch in range(epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")
            print("-" * 60)
            
            # Train phase
            train_loss, train_acc = self._train_epoch(train_loader, criterion, optimizer)
            
            # Validation phase
            val_loss, val_acc = self._validate_epoch(val_loader, criterion)
            
            # Update history
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            # Print metrics
            print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
            
            # Learning rate scheduling
            scheduler.step(val_acc)
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self._save_model('best_model.pth', epoch, val_acc)
                print(f"✓ Saved best model (Val Acc: {val_acc:.2f}%)")
        
        print("\n" + "=" * 60)
        print(f"Training Complete! Best Val Acc: {best_val_acc:.2f}%")
        print("=" * 60)
        
        # Save final model
        self._save_model('final_model.pth', epochs, val_acc)
        
        # Save training history
        self._save_history()
        
        return self.history
    
    def _train_epoch(self, loader, criterion, optimizer):
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(loader, desc="Training")
        for inputs, labels in pbar:
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            
            # Forward
            optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward
            loss.backward()
            optimizer.step()
            
            # Metrics
            running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({'loss': loss.item(), 'acc': 100 * correct / total})
        
        epoch_loss = running_loss / total
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def _validate_epoch(self, loader, criterion):
        """Validate for one epoch"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            pbar = tqdm(loader, desc="Validation")
            for inputs, labels in pbar:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                # Forward
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)
                
                # Metrics
                running_loss += loss.item() * inputs.size(0)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
                # Update progress bar
                pbar.set_postfix({'loss': loss.item(), 'acc': 100 * correct / total})
        
        epoch_loss = running_loss / total
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def _save_model(self, filename, epoch, val_acc):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'val_acc': val_acc,
            'classes': self.train_dataset.classes
        }
        
        save_path = self.model_save_dir / filename
        torch.save(checkpoint, save_path)
    
    def _save_history(self):
        """Save training history"""
        history_path = self.model_save_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        print(f"✓ Saved training history to {history_path}")


if __name__ == "__main__":
    # Train model
    trainer = CNNTrainer(dataset_dir='cnn_dataset')
    
    history = trainer.train(
        epochs=15,
        batch_size=32,
        lr=1e-4
    )
    
    print("\n✓ Model saved to: models/best_model.pth")
    print("✓ Ready for inference!")
