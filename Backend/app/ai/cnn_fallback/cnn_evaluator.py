"""
CNN Evaluation Script for Layout Region Classification
Computes detailed metrics, confusion matrix, and per-class performance
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
import numpy as np
import json
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix, 
    classification_report,
    precision_recall_fscore_support
)
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

from app.ai.cnn_fallback.cnn_trainer import LayoutDataset, LayoutClassifier


class CNNEvaluator:
    """Evaluator for layout region classifier"""
    
    def __init__(self, model_path, dataset_dir, device=None):
        self.model_path = Path(model_path)
        self.dataset_dir = Path(dataset_dir)
        
        # Device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
        
        print(f"Using device: {self.device}")
        
        # Load model
        self.model = self._load_model()
        self.classes = ['legend', 'schedule', 'title_block', 'drawing_region']
        
        # Transform
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def _load_model(self):
        """Load trained model"""
        print(f"Loading model from {self.model_path}")
        
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        model = LayoutClassifier(num_classes=4, dropout=0.3)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        model.eval()
        
        print(f"✓ Model loaded (Val Acc: {checkpoint.get('val_acc', 'N/A')}%)")
        
        return model
    
    def evaluate(self, split='test', batch_size=32, save_results=True):
        """
        Evaluate model on test set
        
        Args:
            split: Dataset split to evaluate ('test', 'val', 'train')
            batch_size: Batch size for evaluation
            save_results: Whether to save results to file
            
        Returns:
            Dictionary with evaluation metrics
        """
        print("\n" + "=" * 60)
        print(f"Evaluating on {split} set")
        print("=" * 60)
        
        # Load dataset
        dataset = LayoutDataset(
            self.dataset_dir / split,
            transform=self.transform
        )
        
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )
        
        # Collect predictions
        all_preds = []
        all_labels = []
        all_probs = []
        
        with torch.no_grad():
            for inputs, labels in tqdm(loader, desc="Evaluating"):
                inputs = inputs.to(self.device)
                
                outputs = self.model(inputs)
                probs = torch.softmax(outputs, dim=1)
                _, predicted = torch.max(outputs, 1)
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.numpy())
                all_probs.extend(probs.cpu().numpy())
        
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        all_probs = np.array(all_probs)
        
        # Compute metrics
        results = self._compute_metrics(all_labels, all_preds, all_probs)
        
        # Print results
        self._print_results(results)
        
        # Generate confusion matrix
        self._plot_confusion_matrix(all_labels, all_preds, save=save_results)
        
        # Save results
        if save_results:
            self._save_results(results, split)
        
        return results
    
    def _compute_metrics(self, labels, preds, probs):
        """Compute evaluation metrics"""
        # Overall accuracy
        accuracy = 100 * np.mean(labels == preds)
        
        # Per-class metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            labels, preds, average=None, labels=range(len(self.classes))
        )
        
        # Macro averages
        macro_precision = np.mean(precision)
        macro_recall = np.mean(recall)
        macro_f1 = np.mean(f1)
        
        # Confidence statistics
        max_probs = np.max(probs, axis=1)
        avg_confidence = np.mean(max_probs)
        
        # Confidence by correctness
        correct_mask = labels == preds
        avg_confidence_correct = np.mean(max_probs[correct_mask])
        avg_confidence_incorrect = np.mean(max_probs[~correct_mask]) if np.any(~correct_mask) else 0.0
        
        # Per-class results
        per_class_results = {}
        for i, class_name in enumerate(self.classes):
            per_class_results[class_name] = {
                'precision': float(precision[i]),
                'recall': float(recall[i]),
                'f1_score': float(f1[i]),
                'support': int(support[i])
            }
        
        # Confusion matrix
        cm = confusion_matrix(labels, preds)
        
        results = {
            'overall_accuracy': float(accuracy),
            'macro_precision': float(macro_precision),
            'macro_recall': float(macro_recall),
            'macro_f1': float(macro_f1),
            'avg_confidence': float(avg_confidence),
            'avg_confidence_correct': float(avg_confidence_correct),
            'avg_confidence_incorrect': float(avg_confidence_incorrect),
            'per_class': per_class_results,
            'confusion_matrix': cm.tolist(),
            'total_samples': len(labels)
        }
        
        return results
    
    def _print_results(self, results):
        """Print evaluation results"""
        print("\n" + "=" * 60)
        print("EVALUATION RESULTS")
        print("=" * 60)
        
        print(f"\nOverall Accuracy: {results['overall_accuracy']:.2f}%")
        print(f"Macro Precision: {results['macro_precision']:.4f}")
        print(f"Macro Recall: {results['macro_recall']:.4f}")
        print(f"Macro F1-Score: {results['macro_f1']:.4f}")
        
        print(f"\nAverage Confidence: {results['avg_confidence']:.4f}")
        print(f"  Correct predictions: {results['avg_confidence_correct']:.4f}")
        print(f"  Incorrect predictions: {results['avg_confidence_incorrect']:.4f}")
        
        print("\n" + "-" * 60)
        print("PER-CLASS METRICS")
        print("-" * 60)
        print(f"{'Class':<20} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
        print("-" * 60)
        
        for class_name, metrics in results['per_class'].items():
            print(f"{class_name:<20} "
                  f"{metrics['precision']:<12.4f} "
                  f"{metrics['recall']:<12.4f} "
                  f"{metrics['f1_score']:<12.4f} "
                  f"{metrics['support']:<10}")
        
        print("=" * 60)
    
    def _plot_confusion_matrix(self, labels, preds, save=True):
        """Plot and save confusion matrix"""
        cm = confusion_matrix(labels, preds)
        
        # Normalize
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        # Plot
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm_normalized,
            annot=True,
            fmt='.2f',
            cmap='Blues',
            xticklabels=self.classes,
            yticklabels=self.classes,
            cbar_kws={'label': 'Normalized Count'}
        )
        plt.title('Confusion Matrix (Normalized)', fontsize=14, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        if save:
            save_path = self.model_path.parent / 'confusion_matrix.png'
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"\n✓ Confusion matrix saved to {save_path}")
        
        plt.close()
    
    def _save_results(self, results, split):
        """Save evaluation results to JSON"""
        save_path = self.model_path.parent / f'evaluation_{split}.json'
        
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Evaluation results saved to {save_path}")
    
    def test_confidence_threshold(self, split='test', thresholds=[0.5, 0.6, 0.7, 0.75, 0.8, 0.9]):
        """
        Test different confidence thresholds
        
        Args:
            split: Dataset split to test on
            thresholds: List of confidence thresholds to test
            
        Returns:
            Dictionary with threshold analysis
        """
        print("\n" + "=" * 60)
        print("Testing Confidence Thresholds")
        print("=" * 60)
        
        # Load dataset
        dataset = LayoutDataset(
            self.dataset_dir / split,
            transform=self.transform
        )
        
        loader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=0)
        
        # Collect predictions
        all_preds = []
        all_labels = []
        all_probs = []
        
        with torch.no_grad():
            for inputs, labels in tqdm(loader, desc="Collecting predictions"):
                inputs = inputs.to(self.device)
                outputs = self.model(inputs)
                probs = torch.softmax(outputs, dim=1)
                _, predicted = torch.max(outputs, 1)
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.numpy())
                all_probs.extend(probs.cpu().numpy())
        
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        all_probs = np.array(all_probs)
        max_probs = np.max(all_probs, axis=1)
        
        # Test thresholds
        threshold_results = {}
        
        print(f"\n{'Threshold':<12} {'Accepted':<12} {'Accuracy':<12} {'Avg Conf':<12}")
        print("-" * 60)
        
        for threshold in thresholds:
            mask = max_probs >= threshold
            
            if np.sum(mask) == 0:
                continue
            
            accepted_preds = all_preds[mask]
            accepted_labels = all_labels[mask]
            accepted_probs = max_probs[mask]
            
            accuracy = 100 * np.mean(accepted_preds == accepted_labels)
            avg_conf = np.mean(accepted_probs)
            acceptance_rate = 100 * np.sum(mask) / len(all_labels)
            
            threshold_results[threshold] = {
                'acceptance_rate': float(acceptance_rate),
                'accuracy': float(accuracy),
                'avg_confidence': float(avg_conf),
                'num_accepted': int(np.sum(mask)),
                'num_total': len(all_labels)
            }
            
            print(f"{threshold:<12.2f} "
                  f"{acceptance_rate:<12.1f}% "
                  f"{accuracy:<12.2f}% "
                  f"{avg_conf:<12.4f}")
        
        print("=" * 60)
        
        # Save results
        save_path = self.model_path.parent / 'threshold_analysis.json'
        with open(save_path, 'w') as f:
            json.dump(threshold_results, f, indent=2)
        
        print(f"\n✓ Threshold analysis saved to {save_path}")
        
        return threshold_results


if __name__ == "__main__":
    # Evaluate model
    evaluator = CNNEvaluator(
        model_path='models/best_model.pth',
        dataset_dir='cnn_dataset'
    )
    
    # Run evaluation
    results = evaluator.evaluate(split='test')
    
    # Test confidence thresholds
    threshold_results = evaluator.test_confidence_threshold(split='test')
    
    print("\n✓ Evaluation complete!")
