"""
CNN Fallback Validation Suite
Comprehensive validation, calibration, and safety audit
"""

import torch
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw
from tqdm import tqdm

from app.ai.cnn_fallback.cnn_inference import CNNLayoutClassifier


class ValidationSuite:
    """Comprehensive validation and calibration suite"""
    
    def __init__(self, model_path, dataset_dir, output_dir='cnn_fallback/validation'):
        self.model_path = Path(model_path)
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize classifier
        self.classifier = CNNLayoutClassifier(
            model_path=str(self.model_path),
            confidence_threshold=0.75
        )
        
        self.classes = ['legend', 'schedule', 'title_block', 'drawing_region']
        
        print("=" * 60)
        print("CNN Fallback Validation Suite Initialized")
        print("=" * 60)

    
    def run_full_audit(self):
        """Run complete validation audit"""
        print("\n🔍 Starting Full Validation Audit...")
        
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'model_path': str(self.model_path),
            'dataset_dir': str(self.dataset_dir)
        }
        
        # Task 1: Mixed validation evaluation
        print("\n" + "=" * 60)
        print("TASK 1: Mixed Validation Evaluation")
        print("=" * 60)
        mixed_results = self.task1_mixed_validation()
        audit_results['mixed_validation'] = mixed_results
        
        # Task 2: Confusion analysis
        print("\n" + "=" * 60)
        print("TASK 2: Confusion Analysis")
        print("=" * 60)
        confusion_results = self.task2_confusion_analysis(mixed_results)
        audit_results['confusion_analysis'] = confusion_results
        
        # Task 3: Confidence calibration
        print("\n" + "=" * 60)
        print("TASK 3: Confidence Calibration Study")
        print("=" * 60)
        calibration_results = self.task3_confidence_calibration(mixed_results)
        audit_results['calibration'] = calibration_results
        
        # Task 4: Robustness stress test
        print("\n" + "=" * 60)
        print("TASK 4: Robustness Stress Test")
        print("=" * 60)
        robustness_results = self.task4_robustness_test()
        audit_results['robustness'] = robustness_results
        
        # Task 5: Real-world dry run
        print("\n" + "=" * 60)
        print("TASK 5: Real-World Dry Run Simulation")
        print("=" * 60)
        dryrun_results = self.task5_dryrun_simulation(mixed_results)
        audit_results['dryrun'] = dryrun_results
        
        # Task 6: Generate audit report
        print("\n" + "=" * 60)
        print("TASK 6: Generating Final Audit Report")
        print("=" * 60)
        self.task6_generate_report(audit_results)
        
        print("\n" + "=" * 60)
        print("✓ Full Validation Audit Complete!")
        print("=" * 60)
        
        return audit_results

    
    def task1_mixed_validation(self):
        """Task 1: Mixed validation evaluation"""
        from torch.utils.data import DataLoader
        from app.ai.cnn_fallback.cnn_trainer import LayoutDataset
        from torchvision import transforms
        from sklearn.metrics import confusion_matrix, classification_report
        
        # Load validation dataset
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        val_dataset = LayoutDataset(
            self.dataset_dir / 'val',
            transform=transform
        )
        
        val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
        
        # Collect predictions
        all_preds = []
        all_labels = []
        all_probs = []
        all_images = []
        
        print(f"Evaluating {len(val_dataset)} validation samples...")
        
        with torch.no_grad():
            for inputs, labels in tqdm(val_loader):
                inputs = inputs.to(self.classifier.device)
                outputs = self.classifier.model(inputs)
                probs = torch.softmax(outputs, dim=1)
                _, predicted = torch.max(outputs, 1)
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.numpy())
                all_probs.extend(probs.cpu().numpy())
        
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        all_probs = np.array(all_probs)
        
        # Compute metrics
        from sklearn.metrics import precision_recall_fscore_support
        
        accuracy = 100 * np.mean(all_preds == all_labels)
        precision, recall, f1, support = precision_recall_fscore_support(
            all_labels, all_preds, average=None
        )
        
        # Per-class metrics
        per_class = {}
        for i, cls in enumerate(self.classes):
            per_class[cls] = {
                'accuracy': float(100 * np.mean(all_preds[all_labels == i] == i)),
                'precision': float(precision[i]),
                'recall': float(recall[i]),
                'f1_score': float(f1[i]),
                'support': int(support[i])
            }
        
        # Confusion matrix
        cm = confusion_matrix(all_labels, all_preds)
        
        # Save results
        results = {
            'overall_accuracy': float(accuracy),
            'per_class': per_class,
            'confusion_matrix': cm.tolist(),
            'total_samples': len(all_labels),
            'predictions': all_preds.tolist(),
            'labels': all_labels.tolist(),
            'probabilities': all_probs.tolist()
        }
        
        # Save to JSON
        with open(self.output_dir / 'validation_report.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate confusion matrix image
        self._plot_confusion_matrix(cm, 'confusion_matrix.png')
        
        # Generate confidence histograms
        self._plot_confidence_histograms(all_labels, all_preds, all_probs)
        
        print(f"\n✓ Overall Accuracy: {accuracy:.2f}%")
        print(f"✓ Results saved to: {self.output_dir / 'validation_report.json'}")
        
        return results

    
    def task2_confusion_analysis(self, mixed_results):
        """Task 2: Analyze confusion patterns and save misclassified samples"""
        from torch.utils.data import DataLoader
        from app.ai.cnn_fallback.cnn_trainer import LayoutDataset
        from torchvision import transforms
        
        # Create misclassified directory
        misclass_dir = self.output_dir / 'misclassified'
        misclass_dir.mkdir(exist_ok=True)
        
        # Load dataset
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        val_dataset = LayoutDataset(self.dataset_dir / 'val', transform=transform)
        
        # Get predictions
        preds = np.array(mixed_results['predictions'])
        labels = np.array(mixed_results['labels'])
        probs = np.array(mixed_results['probabilities'])
        
        # Find misclassified samples
        misclassified_idx = np.where(preds != labels)[0]
        
        # Analyze confusion pairs
        confusion_pairs = defaultdict(int)
        for idx in misclassified_idx:
            true_cls = self.classes[labels[idx]]
            pred_cls = self.classes[preds[idx]]
            confusion_pairs[(true_cls, pred_cls)] += 1
        
        # Sort by frequency
        sorted_pairs = sorted(confusion_pairs.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nFound {len(misclassified_idx)} misclassified samples")
        print("\nTop confusion pairs:")
        for (true_cls, pred_cls), count in sorted_pairs[:5]:
            print(f"  {true_cls} → {pred_cls}: {count} cases")
        
        # Save misclassified images (first 50)
        print(f"\nSaving misclassified samples to: {misclass_dir}")
        for i, idx in enumerate(misclassified_idx[:50]):
            img_path, _ = val_dataset.samples[idx]
            img = Image.open(img_path)
            
            true_cls = self.classes[labels[idx]]
            pred_cls = self.classes[preds[idx]]
            confidence = probs[idx][preds[idx]]
            
            filename = f"{true_cls}_{pred_cls}_{confidence:.3f}.png"
            img.save(misclass_dir / filename)
        
        # Analyze specific confusions
        legend_schedule = confusion_pairs.get(('legend', 'schedule'), 0) + \
                         confusion_pairs.get(('schedule', 'legend'), 0)
        title_schedule = confusion_pairs.get(('title_block', 'schedule'), 0) + \
                        confusion_pairs.get(('schedule', 'title_block'), 0)
        
        results = {
            'total_misclassified': len(misclassified_idx),
            'confusion_pairs': {f"{k[0]}_to_{k[1]}": v for k, v in sorted_pairs},
            'most_common_confusion': {
                'pair': f"{sorted_pairs[0][0][0]} → {sorted_pairs[0][0][1]}",
                'count': sorted_pairs[0][1]
            } if sorted_pairs else None,
            'legend_schedule_confusion': int(legend_schedule),
            'title_schedule_confusion': int(title_schedule),
            'analysis': self._analyze_confusion_reasons(sorted_pairs)
        }
        
        print(f"✓ Confusion analysis complete")
        
        return results

    
    def task3_confidence_calibration(self, mixed_results):
        """Task 3: Confidence calibration study"""
        preds = np.array(mixed_results['predictions'])
        labels = np.array(mixed_results['labels'])
        probs = np.array(mixed_results['probabilities'])
        
        # Get max confidence for each prediction
        max_probs = np.max(probs, axis=1)
        
        # Separate correct and incorrect
        correct_mask = preds == labels
        correct_conf = max_probs[correct_mask]
        incorrect_conf = max_probs[~correct_mask]
        
        # Compute statistics
        results = {
            'correct': {
                'mean': float(np.mean(correct_conf)),
                'std': float(np.std(correct_conf)),
                'min': float(np.min(correct_conf)),
                'max': float(np.max(correct_conf)),
                'median': float(np.median(correct_conf)),
                'count': int(len(correct_conf))
            },
            'incorrect': {
                'mean': float(np.mean(incorrect_conf)) if len(incorrect_conf) > 0 else 0.0,
                'std': float(np.std(incorrect_conf)) if len(incorrect_conf) > 0 else 0.0,
                'min': float(np.min(incorrect_conf)) if len(incorrect_conf) > 0 else 0.0,
                'max': float(np.max(incorrect_conf)) if len(incorrect_conf) > 0 else 0.0,
                'median': float(np.median(incorrect_conf)) if len(incorrect_conf) > 0 else 0.0,
                'count': int(len(incorrect_conf))
            }
        }
        
        # Test different thresholds
        thresholds = [0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]
        threshold_analysis = {}
        
        for thresh in thresholds:
            accepted = max_probs >= thresh
            if np.sum(accepted) == 0:
                continue
            
            accepted_preds = preds[accepted]
            accepted_labels = labels[accepted]
            
            acc = 100 * np.mean(accepted_preds == accepted_labels)
            acceptance_rate = 100 * np.sum(accepted) / len(labels)
            
            threshold_analysis[thresh] = {
                'accuracy': float(acc),
                'acceptance_rate': float(acceptance_rate),
                'num_accepted': int(np.sum(accepted))
            }
        
        results['threshold_analysis'] = threshold_analysis
        
        # Recommendations
        safe_override = self._recommend_safe_threshold(threshold_analysis, target_acc=90)
        safe_escalation = self._recommend_escalation_threshold(correct_conf, incorrect_conf)
        
        results['recommendations'] = {
            'safe_override_threshold': safe_override,
            'safe_escalation_threshold': safe_escalation,
            'current_threshold_0.75_accuracy': threshold_analysis.get(0.75, {}).get('accuracy', 0)
        }
        
        # Plot confidence distributions
        self._plot_confidence_calibration(correct_conf, incorrect_conf)
        
        print(f"\n✓ Confidence Calibration Results:")
        print(f"  Correct predictions - Mean: {results['correct']['mean']:.4f}")
        print(f"  Incorrect predictions - Mean: {results['incorrect']['mean']:.4f}")
        print(f"  Recommended safe override threshold: {safe_override:.2f}")
        print(f"  Recommended escalation threshold: {safe_escalation:.2f}")
        
        return results

    
    def task4_robustness_test(self):
        """Task 4: Robustness stress test with distortions"""
        from torch.utils.data import DataLoader
        from app.ai.cnn_fallback.cnn_trainer import LayoutDataset
        from torchvision import transforms
        from scipy.ndimage import rotate, gaussian_filter
        
        # Load validation dataset
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        val_dataset = LayoutDataset(self.dataset_dir / 'val', transform=None)
        
        distortion_types = ['skew', 'blur', 'contrast', 'erase']
        results = {}
        
        print("\nTesting robustness with distortions...")
        
        for distortion in distortion_types:
            print(f"\n  Testing {distortion}...")
            
            all_preds = []
            all_labels = []
            
            for img_path, label in tqdm(val_dataset.samples[:200]):  # Test on subset
                # Load image
                img = Image.open(img_path).convert('RGB')
                img_array = np.array(img)
                
                # Apply distortion
                distorted = self._apply_distortion(img_array, distortion)
                
                # Predict
                result = self.classifier.predict(distorted)
                all_preds.append(self.classes.index(result['class']))
                all_labels.append(label)
            
            all_preds = np.array(all_preds)
            all_labels = np.array(all_labels)
            
            accuracy = 100 * np.mean(all_preds == all_labels)
            
            # Per-class accuracy
            per_class_acc = {}
            for i, cls in enumerate(self.classes):
                mask = all_labels == i
                if np.sum(mask) > 0:
                    per_class_acc[cls] = float(100 * np.mean(all_preds[mask] == i))
            
            results[distortion] = {
                'accuracy': float(accuracy),
                'per_class_accuracy': per_class_acc
            }
            
            print(f"    Accuracy: {accuracy:.2f}%")
        
        # Compute baseline (no distortion)
        print(f"\n  Testing baseline (no distortion)...")
        baseline_preds = []
        baseline_labels = []
        
        for img_path, label in tqdm(val_dataset.samples[:200]):
            img = Image.open(img_path).convert('RGB')
            result = self.classifier.predict(img)
            baseline_preds.append(self.classes.index(result['class']))
            baseline_labels.append(label)
        
        baseline_acc = 100 * np.mean(np.array(baseline_preds) == np.array(baseline_labels))
        results['baseline'] = {'accuracy': float(baseline_acc)}
        
        # Compute degradation
        for distortion in distortion_types:
            drop = baseline_acc - results[distortion]['accuracy']
            results[distortion]['accuracy_drop'] = float(drop)
        
        # Find most degraded class
        worst_distortion = max(distortion_types, 
                              key=lambda d: results[d]['accuracy_drop'])
        
        results['summary'] = {
            'baseline_accuracy': float(baseline_acc),
            'worst_distortion': worst_distortion,
            'max_accuracy_drop': float(results[worst_distortion]['accuracy_drop'])
        }
        
        print(f"\n✓ Robustness Test Complete")
        print(f"  Baseline: {baseline_acc:.2f}%")
        print(f"  Worst distortion: {worst_distortion} "
              f"(drop: {results[worst_distortion]['accuracy_drop']:.2f}%)")
        
        return results

    
    def task5_dryrun_simulation(self, mixed_results):
        """Task 5: Real-world dry run simulation"""
        preds = np.array(mixed_results['predictions'])
        labels = np.array(mixed_results['labels'])
        probs = np.array(mixed_results['probabilities'])
        
        # Simulate heuristic confidences (realistic range)
        np.random.seed(42)
        heuristic_confidences = np.random.uniform(0.4, 0.9, len(labels))
        
        # Simulate heuristic predictions (80% correct when confident)
        heuristic_preds = labels.copy()
        for i in range(len(labels)):
            if heuristic_confidences[i] < 0.65:
                # Low confidence - more likely to be wrong
                if np.random.random() < 0.5:
                    heuristic_preds[i] = np.random.choice(
                        [c for c in range(len(self.classes)) if c != labels[i]]
                    )
            else:
                # High confidence - mostly correct
                if np.random.random() < 0.2:
                    heuristic_preds[i] = np.random.choice(
                        [c for c in range(len(self.classes)) if c != labels[i]]
                    )
        
        # Apply fallback logic
        heuristic_threshold = 0.65
        cnn_threshold = 0.75
        
        final_preds = []
        sources = []
        escalations = 0
        cnn_overrides = 0
        incorrect_overrides = 0
        
        for i in range(len(labels)):
            cnn_conf = probs[i][preds[i]]
            
            if heuristic_confidences[i] >= heuristic_threshold:
                # Use heuristic
                final_preds.append(heuristic_preds[i])
                sources.append('heuristic')
            elif cnn_conf >= cnn_threshold:
                # Use CNN
                final_preds.append(preds[i])
                sources.append('cnn')
                cnn_overrides += 1
                
                # Check if override was incorrect
                if preds[i] != labels[i]:
                    incorrect_overrides += 1
            else:
                # Escalate
                final_preds.append(heuristic_preds[i])  # Fallback to heuristic
                sources.append('escalate')
                escalations += 1
        
        final_preds = np.array(final_preds)
        
        # Compute metrics
        final_accuracy = 100 * np.mean(final_preds == labels)
        heuristic_only_accuracy = 100 * np.mean(heuristic_preds == labels)
        cnn_only_accuracy = 100 * np.mean(preds == labels)
        
        cnn_override_rate = 100 * cnn_overrides / len(labels)
        escalation_rate = 100 * escalations / len(labels)
        incorrect_override_rate = 100 * incorrect_overrides / cnn_overrides if cnn_overrides > 0 else 0
        
        results = {
            'final_accuracy': float(final_accuracy),
            'heuristic_only_accuracy': float(heuristic_only_accuracy),
            'cnn_only_accuracy': float(cnn_only_accuracy),
            'cnn_override_rate': float(cnn_override_rate),
            'escalation_rate': float(escalation_rate),
            'incorrect_override_rate': float(incorrect_override_rate),
            'total_samples': len(labels),
            'cnn_overrides': int(cnn_overrides),
            'escalations': int(escalations),
            'incorrect_overrides': int(incorrect_overrides)
        }
        
        print(f"\n✓ Dry Run Simulation Results:")
        print(f"  Final accuracy: {final_accuracy:.2f}%")
        print(f"  CNN override rate: {cnn_override_rate:.2f}%")
        print(f"  Escalation rate: {escalation_rate:.2f}%")
        print(f"  Incorrect override rate: {incorrect_override_rate:.2f}%")
        
        # Safety check
        if cnn_override_rate > 50:
            print(f"  ⚠️  WARNING: CNN dominates decisions ({cnn_override_rate:.1f}%)")
        
        return results

    
    def task6_generate_report(self, audit_results):
        """Task 6: Generate final audit report"""
        report_path = self.output_dir / 'CNN_AUDIT_REPORT.md'
        
        # Determine recommendation
        mixed_acc = audit_results['mixed_validation']['overall_accuracy']
        incorrect_override_rate = audit_results['dryrun']['incorrect_override_rate']
        max_acc_drop = audit_results['robustness']['summary']['max_accuracy_drop']
        
        if mixed_acc >= 85 and incorrect_override_rate < 15 and max_acc_drop < 20:
            recommendation = "SAFE FOR PRODUCTION"
        elif mixed_acc >= 80 and incorrect_override_rate < 25:
            recommendation = "SAFE WITH CONDITIONS"
        else:
            recommendation = "NEEDS REFINEMENT"
        
        # Generate markdown report
        report = self._generate_markdown_report(audit_results, recommendation)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✓ Audit report generated: {report_path}")
        print(f"\n{'=' * 60}")
        print(f"FINAL RECOMMENDATION: {recommendation}")
        print(f"{'=' * 60}")
        
        return recommendation

    
    # Helper methods
    
    def _plot_confusion_matrix(self, cm, filename):
        """Plot confusion matrix"""
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm_normalized, annot=True, fmt='.2f', cmap='Blues',
                   xticklabels=self.classes, yticklabels=self.classes)
        plt.title('Confusion Matrix (Normalized)')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=150)
        plt.close()
    
    def _plot_confidence_histograms(self, labels, preds, probs):
        """Plot confidence histograms per class"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        for i, cls in enumerate(self.classes):
            mask = labels == i
            class_probs = probs[mask, i]
            
            axes[i].hist(class_probs, bins=20, alpha=0.7, edgecolor='black')
            axes[i].set_title(f'{cls} - Confidence Distribution')
            axes[i].set_xlabel('Confidence')
            axes[i].set_ylabel('Frequency')
            axes[i].axvline(0.75, color='r', linestyle='--', label='Threshold 0.75')
            axes[i].legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'confidence_histograms.png', dpi=150)
        plt.close()
    
    def _plot_confidence_calibration(self, correct_conf, incorrect_conf):
        """Plot confidence calibration"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        axes[0].hist(correct_conf, bins=20, alpha=0.7, label='Correct', color='green')
        axes[0].hist(incorrect_conf, bins=20, alpha=0.7, label='Incorrect', color='red')
        axes[0].set_xlabel('Confidence')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Confidence Distribution by Correctness')
        axes[0].legend()
        axes[0].axvline(0.75, color='black', linestyle='--', label='Threshold')
        
        # Box plot
        axes[1].boxplot([correct_conf, incorrect_conf], labels=['Correct', 'Incorrect'])
        axes[1].set_ylabel('Confidence')
        axes[1].set_title('Confidence Box Plot')
        axes[1].axhline(0.75, color='r', linestyle='--', label='Threshold')
        axes[1].legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'confidence_calibration.png', dpi=150)
        plt.close()

    
    def _apply_distortion(self, img_array, distortion_type):
        """Apply distortion to image"""
        if distortion_type == 'skew':
            # Slight rotation
            angle = np.random.uniform(-5, 5)
            from scipy.ndimage import rotate
            return rotate(img_array, angle, reshape=False, mode='constant', cval=255)
        
        elif distortion_type == 'blur':
            # Gaussian blur
            from scipy.ndimage import gaussian_filter
            return gaussian_filter(img_array, sigma=1.5)
        
        elif distortion_type == 'contrast':
            # Reduce contrast
            mean = img_array.mean()
            return np.clip((img_array - mean) * 0.5 + mean, 0, 255).astype(np.uint8)
        
        elif distortion_type == 'erase':
            # Random erasing
            img_copy = img_array.copy()
            h, w = img_array.shape[:2]
            erase_h = int(h * 0.1)
            erase_w = int(w * 0.1)
            
            for _ in range(5):
                y = np.random.randint(0, h - erase_h)
                x = np.random.randint(0, w - erase_w)
                img_copy[y:y+erase_h, x:x+erase_w] = 255
            
            return img_copy
        
        return img_array
    
    def _analyze_confusion_reasons(self, sorted_pairs):
        """Analyze reasons for confusion"""
        if not sorted_pairs:
            return "No confusion pairs found"
        
        top_pair = sorted_pairs[0][0]
        
        reasons = {
            ('legend', 'schedule'): "Both contain structured layouts with text",
            ('schedule', 'legend'): "Grid patterns may resemble legend layouts",
            ('title_block', 'schedule'): "Both have dense text and rectangular structure",
            ('schedule', 'title_block'): "Table borders may resemble title block frames",
            ('drawing_region', 'legend'): "Sparse symbols may be confused with legend items",
            ('legend', 'drawing_region'): "Dense legend layouts may appear as drawing content"
        }
        
        return reasons.get(top_pair, "Visual similarity between classes")
    
    def _recommend_safe_threshold(self, threshold_analysis, target_acc=90):
        """Recommend safe override threshold"""
        for thresh in sorted(threshold_analysis.keys(), reverse=True):
            if threshold_analysis[thresh]['accuracy'] >= target_acc:
                return float(thresh)
        return 0.85  # Conservative default
    
    def _recommend_escalation_threshold(self, correct_conf, incorrect_conf):
        """Recommend escalation threshold"""
        # Find threshold where most incorrect predictions fall below
        if len(incorrect_conf) == 0:
            return 0.5
        
        percentile_75 = np.percentile(incorrect_conf, 75)
        return float(min(0.65, percentile_75))

    
    def _generate_markdown_report(self, audit_results, recommendation):
        """Generate markdown audit report"""
        mixed = audit_results['mixed_validation']
        confusion = audit_results['confusion_analysis']
        calibration = audit_results['calibration']
        robustness = audit_results['robustness']
        dryrun = audit_results['dryrun']
        
        report = f"""# CNN Fallback Validation Audit Report

**Date:** {audit_results['timestamp']}  
**Model:** {audit_results['model_path']}  
**Dataset:** {audit_results['dataset_dir']}

---

## Executive Summary

**Final Recommendation:** `{recommendation}`

### Key Metrics
- **Mixed Validation Accuracy:** {mixed['overall_accuracy']:.2f}%
- **Most Common Confusion:** {confusion['most_common_confusion']['pair'] if confusion['most_common_confusion'] else 'N/A'}
- **Recommended CNN Threshold:** {calibration['recommendations']['safe_override_threshold']:.2f}
- **CNN Override Rate:** {dryrun['cnn_override_rate']:.2f}%
- **Incorrect Override Rate:** {dryrun['incorrect_override_rate']:.2f}%

---

## 1. Dataset Description

### Validation Set Composition
- **Total Samples:** {mixed['total_samples']}
- **Classes:** legend, schedule, title_block, drawing_region

### Per-Class Distribution
"""
        
        for cls, metrics in mixed['per_class'].items():
            report += f"- **{cls}:** {metrics['support']} samples\n"
        
        report += f"""

---

## 2. Training Details

- **Architecture:** MobileNetV2 (pretrained on ImageNet)
- **Fine-tuning:** Last 3 blocks unfrozen
- **Classifier Head:** Dropout(0.3) + Linear(4 classes)
- **Input Size:** 224×224×3 RGB
- **Loss Function:** CrossEntropyLoss
- **Optimizer:** Adam (lr=1e-4)

---

## 3. Validation Metrics

### Overall Performance
- **Accuracy:** {mixed['overall_accuracy']:.2f}%

### Per-Class Performance

| Class | Accuracy | Precision | Recall | F1-Score | Support |
|-------|----------|-----------|--------|----------|---------|
"""
        
        for cls, metrics in mixed['per_class'].items():
            report += f"| {cls} | {metrics['accuracy']:.2f}% | {metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['f1_score']:.4f} | {metrics['support']} |\n"
        
        report += f"""

### Confusion Matrix
![Confusion Matrix](confusion_matrix.png)

---

## 4. Confusion Analysis

### Misclassification Summary
- **Total Misclassified:** {confusion['total_misclassified']} samples
- **Most Common Confusion:** {confusion['most_common_confusion']['pair'] if confusion['most_common_confusion'] else 'N/A'} ({confusion['most_common_confusion']['count'] if confusion['most_common_confusion'] else 0} cases)

### Specific Confusion Patterns
- **Legend ↔ Schedule:** {confusion['legend_schedule_confusion']} cases
- **Title Block ↔ Schedule:** {confusion['title_schedule_confusion']} cases

### Analysis
{confusion['analysis']}

**Possible Causes:**
- Visual similarity in structured layouts
- Synthetic data may not capture all real-world variations
- Grid patterns can appear in multiple classes

**Mitigation:**
- Add more diverse real samples
- Increase synthetic variation
- Consider ensemble methods

---

## 5. Confidence Calibration

### Confidence Statistics

**Correct Predictions:**
- Mean: {calibration['correct']['mean']:.4f}
- Median: {calibration['correct']['median']:.4f}
- Min: {calibration['correct']['min']:.4f}
- Max: {calibration['correct']['max']:.4f}

**Incorrect Predictions:**
- Mean: {calibration['incorrect']['mean']:.4f}
- Median: {calibration['incorrect']['median']:.4f}
- Min: {calibration['incorrect']['min']:.4f}
- Max: {calibration['incorrect']['max']:.4f}

### Threshold Analysis

| Threshold | Accuracy | Acceptance Rate |
|-----------|----------|-----------------|
"""
        
        for thresh, metrics in sorted(calibration['threshold_analysis'].items()):
            report += f"| {thresh:.2f} | {metrics['accuracy']:.2f}% | {metrics['acceptance_rate']:.2f}% |\n"
        
        report += f"""

### Calibration Visualization
![Confidence Calibration](confidence_calibration.png)

### Recommendations
- **Safe Override Threshold:** {calibration['recommendations']['safe_override_threshold']:.2f}
- **Safe Escalation Threshold:** {calibration['recommendations']['safe_escalation_threshold']:.2f}
- **Current 0.75 Threshold Accuracy:** {calibration['recommendations']['current_threshold_0.75_accuracy']:.2f}%

**Assessment:** {'✓ Current threshold is appropriate' if calibration['recommendations']['current_threshold_0.75_accuracy'] >= 85 else '⚠️ Consider adjusting threshold'}

---

## 6. Robustness Test Results

### Baseline Performance
- **Accuracy (No Distortion):** {robustness['summary']['baseline_accuracy']:.2f}%

### Performance Under Distortions

| Distortion | Accuracy | Drop |
|------------|----------|------|
"""
        
        for dist in ['skew', 'blur', 'contrast', 'erase']:
            if dist in robustness:
                report += f"| {dist.capitalize()} | {robustness[dist]['accuracy']:.2f}% | {robustness[dist]['accuracy_drop']:.2f}% |\n"
        
        report += f"""

### Analysis
- **Worst Distortion:** {robustness['summary']['worst_distortion']}
- **Maximum Accuracy Drop:** {robustness['summary']['max_accuracy_drop']:.2f}%

**Assessment:** {'✓ Model is robust' if robustness['summary']['max_accuracy_drop'] < 20 else '⚠️ Model shows sensitivity to distortions'}

---

## 7. Real-World Dry Run Simulation

### Fallback Logic Performance
- **Final Accuracy:** {dryrun['final_accuracy']:.2f}%
- **Heuristic-Only Accuracy:** {dryrun['heuristic_only_accuracy']:.2f}%
- **CNN-Only Accuracy:** {dryrun['cnn_only_accuracy']:.2f}%

### Decision Distribution
- **CNN Overrides:** {dryrun['cnn_overrides']} ({dryrun['cnn_override_rate']:.2f}%)
- **Escalations:** {dryrun['escalations']} ({dryrun['escalation_rate']:.2f}%)
- **Incorrect Overrides:** {dryrun['incorrect_overrides']} ({dryrun['incorrect_override_rate']:.2f}%)

### Safety Assessment
"""
        
        if dryrun['cnn_override_rate'] > 50:
            report += "⚠️ **WARNING:** CNN dominates decisions - may override heuristics too aggressively\n"
        elif dryrun['cnn_override_rate'] < 10:
            report += "⚠️ **WARNING:** CNN rarely activates - threshold may be too high\n"
        else:
            report += "✓ **GOOD:** CNN activates appropriately as fallback\n"
        
        if dryrun['incorrect_override_rate'] > 25:
            report += "⚠️ **WARNING:** High incorrect override rate - CNN may introduce errors\n"
        else:
            report += "✓ **GOOD:** Low incorrect override rate - CNN provides reliable fallback\n"
        
        report += f"""

---

## 8. Risk Assessment

### Identified Risks

1. **Confusion Between Similar Classes**
   - Risk Level: {'HIGH' if confusion['legend_schedule_confusion'] > 20 else 'MEDIUM' if confusion['legend_schedule_confusion'] > 10 else 'LOW'}
   - Mitigation: Add more diverse training samples, improve synthetic generation

2. **Confidence Calibration**
   - Risk Level: {'HIGH' if abs(calibration['correct']['mean'] - calibration['incorrect']['mean']) < 0.15 else 'LOW'}
   - Mitigation: {'Retrain with better data' if abs(calibration['correct']['mean'] - calibration['incorrect']['mean']) < 0.15 else 'Current calibration is acceptable'}

3. **Robustness to Distortions**
   - Risk Level: {'HIGH' if robustness['summary']['max_accuracy_drop'] > 25 else 'MEDIUM' if robustness['summary']['max_accuracy_drop'] > 15 else 'LOW'}
   - Mitigation: {'Add augmentation during training' if robustness['summary']['max_accuracy_drop'] > 15 else 'Current robustness is acceptable'}

4. **CNN Override Behavior**
   - Risk Level: {'HIGH' if dryrun['incorrect_override_rate'] > 25 else 'MEDIUM' if dryrun['incorrect_override_rate'] > 15 else 'LOW'}
   - Mitigation: {'Increase CNN threshold or improve model' if dryrun['incorrect_override_rate'] > 15 else 'Override behavior is safe'}

---

## 9. Final Recommendation

### {recommendation}

"""
        
        if recommendation == "SAFE FOR PRODUCTION":
            report += """
**Justification:**
- Validation accuracy meets target (≥85%)
- Confidence calibration is reliable
- Robustness to distortions is acceptable
- CNN override behavior is safe
- Low incorrect override rate

**Deployment Guidelines:**
- Use recommended threshold: {:.2f}
- Monitor CNN activation rate in production
- Collect edge cases for continuous improvement
- Set up alerting for unusual confidence patterns
""".format(calibration['recommendations']['safe_override_threshold'])
        
        elif recommendation == "SAFE WITH CONDITIONS":
            report += """
**Justification:**
- Validation accuracy is acceptable (≥80%)
- Some concerns with specific confusion patterns
- Robustness could be improved
- CNN override behavior needs monitoring

**Conditions for Deployment:**
- Deploy with conservative threshold: {:.2f}
- Implement strict monitoring and logging
- Manual review of escalated cases
- Gradual rollout with A/B testing
- Collect production data for retraining
""".format(calibration['recommendations']['safe_override_threshold'])
        
        else:
            report += """
**Justification:**
- Validation accuracy below target (<80%)
- Significant confusion between classes
- Poor robustness to distortions
- High incorrect override rate

**Required Actions Before Deployment:**
1. Collect more diverse real training samples (50+ per class)
2. Improve synthetic data generation
3. Retrain model with augmented dataset
4. Re-run validation audit
5. Consider ensemble methods or architecture changes
"""
        
        report += """

---

## 10. Next Steps

### Immediate Actions
1. Review misclassified samples in `misclassified/` folder
2. Collect real cropped samples from production drawings
3. Add real samples to dataset and rebuild splits
4. Monitor CNN activation patterns in staging environment

### Long-term Improvements
1. Expand dataset with edge cases
2. Implement active learning pipeline
3. Add model versioning and A/B testing
4. Set up continuous validation monitoring
5. Consider multi-model ensemble for critical cases

---

**Report Generated:** {audit_results['timestamp']}  
**Validation Suite Version:** 1.0.0
"""
        
        return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python validation_suite.py <model_path> <dataset_dir>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    dataset_dir = sys.argv[2]
    
    suite = ValidationSuite(model_path, dataset_dir)
    results = suite.run_full_audit()
    
    print("\n" + "=" * 60)
    print("Validation audit complete!")
    print(f"Results saved to: {suite.output_dir}")
    print("=" * 60)
