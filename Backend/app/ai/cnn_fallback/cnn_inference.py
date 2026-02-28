"""
CNN Inference Module for Layout Region Classification
Provides isolated, pluggable inference for Layer 2 integration
"""

import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import numpy as np
from pathlib import Path
import warnings

from app.ai.cnn_fallback.cnn_trainer import LayoutClassifier


class CNNLayoutClassifier:
    """
    Isolated CNN classifier for layout regions
    Accepts cropped numpy images and returns class + confidence
    """
    
    def __init__(self, model_path, device=None, confidence_threshold=0.75):
        """
        Initialize CNN classifier
        
        Args:
            model_path: Path to trained model checkpoint
            device: torch device (None for auto-detect)
            confidence_threshold: Minimum confidence to accept prediction
        """
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        
        # Device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
        
        # Classes
        self.classes = ['legend', 'schedule', 'title_block', 'drawing_region']
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        # Load model
        self.model = self._load_model()
        
        # Transform
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        print(f"✓ CNN Layout Classifier initialized (device: {self.device})")
    
    def _load_model(self):
        """Load trained model"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        # Load checkpoint
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        # Initialize model
        model = LayoutClassifier(num_classes=4, dropout=0.3)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        model.eval()
        
        return model
    
    def predict(self, image):
        """
        Predict layout region class
        
        Args:
            image: Input image as:
                   - numpy array (H, W) or (H, W, 3)
                   - PIL Image
                   - torch Tensor
        
        Returns:
            dict: {
                "class": str,           # Predicted class name
                "confidence": float,    # Confidence score (0-1)
                "all_probs": dict,      # All class probabilities
                "accepted": bool        # Whether confidence >= threshold
            }
        """
        # Convert to PIL Image
        pil_image = self._to_pil_image(image)
        
        # Transform
        input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]
        
        # Get prediction
        pred_idx = np.argmax(probs)
        pred_class = self.classes[pred_idx]
        confidence = float(probs[pred_idx])
        
        # All probabilities
        all_probs = {cls: float(probs[i]) for i, cls in enumerate(self.classes)}
        
        # Check threshold
        accepted = confidence >= self.confidence_threshold
        
        return {
            "class": pred_class,
            "confidence": confidence,
            "all_probs": all_probs,
            "accepted": accepted
        }
    
    def predict_batch(self, images):
        """
        Predict multiple images in batch
        
        Args:
            images: List of images (numpy arrays or PIL Images)
        
        Returns:
            List of prediction dictionaries
        """
        # Convert all to PIL
        pil_images = [self._to_pil_image(img) for img in images]
        
        # Transform batch
        batch_tensor = torch.stack([self.transform(img) for img in pil_images])
        batch_tensor = batch_tensor.to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(batch_tensor)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()
        
        # Process results
        results = []
        for i in range(len(images)):
            pred_idx = np.argmax(probs[i])
            pred_class = self.classes[pred_idx]
            confidence = float(probs[i][pred_idx])
            
            all_probs = {cls: float(probs[i][j]) for j, cls in enumerate(self.classes)}
            accepted = confidence >= self.confidence_threshold
            
            results.append({
                "class": pred_class,
                "confidence": confidence,
                "all_probs": all_probs,
                "accepted": accepted
            })
        
        return results
    
    def _to_pil_image(self, image):
        """Convert various image formats to PIL Image"""
        if isinstance(image, Image.Image):
            # Already PIL Image
            return image.convert('RGB')
        
        elif isinstance(image, np.ndarray):
            # Numpy array
            if image.ndim == 2:
                # Grayscale
                return Image.fromarray(image).convert('RGB')
            elif image.ndim == 3:
                if image.shape[2] == 1:
                    # Grayscale with channel
                    return Image.fromarray(image[:, :, 0]).convert('RGB')
                elif image.shape[2] == 3:
                    # RGB
                    return Image.fromarray(image.astype(np.uint8)).convert('RGB')
                elif image.shape[2] == 4:
                    # RGBA
                    return Image.fromarray(image.astype(np.uint8)).convert('RGB')
            
            raise ValueError(f"Unsupported numpy array shape: {image.shape}")
        
        elif isinstance(image, torch.Tensor):
            # Torch tensor
            image_np = image.cpu().numpy()
            if image_np.ndim == 3:
                # (C, H, W) -> (H, W, C)
                image_np = np.transpose(image_np, (1, 2, 0))
            return self._to_pil_image(image_np)
        
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
    
    def set_confidence_threshold(self, threshold):
        """Update confidence threshold"""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0 and 1")
        self.confidence_threshold = threshold
        print(f"✓ Confidence threshold updated to {threshold}")


class CNNFallbackIntegration:
    """
    Integration wrapper for Layer 2 pipeline
    Combines heuristic and CNN predictions with confidence fusion
    """
    
    def __init__(self, model_path, heuristic_threshold=0.65, cnn_threshold=0.75):
        """
        Initialize fallback integration
        
        Args:
            model_path: Path to trained CNN model
            heuristic_threshold: Confidence below which CNN activates
            cnn_threshold: Minimum CNN confidence to accept
        """
        self.heuristic_threshold = heuristic_threshold
        self.cnn_threshold = cnn_threshold
        
        # Initialize CNN classifier
        self.cnn_classifier = CNNLayoutClassifier(
            model_path=model_path,
            confidence_threshold=cnn_threshold
        )
        
        print(f"✓ CNN Fallback Integration initialized")
        print(f"  Heuristic threshold: {heuristic_threshold}")
        print(f"  CNN threshold: {cnn_threshold}")
    
    def classify_region(self, cropped_image, heuristic_result=None):
        """
        Classify region with CNN fallback logic
        
        Args:
            cropped_image: Cropped region image (numpy array or PIL)
            heuristic_result: Optional dict with:
                {
                    "class": str,
                    "confidence": float
                }
        
        Returns:
            dict: {
                "class": str,
                "confidence": float,
                "source": str,          # "heuristic", "cnn", or "uncertain"
                "heuristic_used": bool,
                "cnn_used": bool,
                "final_confidence": float
            }
        """
        # Check if heuristic is confident
        if heuristic_result and heuristic_result.get('confidence', 0) >= self.heuristic_threshold:
            # Use heuristic result
            return {
                "class": heuristic_result['class'],
                "confidence": heuristic_result['confidence'],
                "source": "heuristic",
                "heuristic_used": True,
                "cnn_used": False,
                "final_confidence": heuristic_result['confidence']
            }
        
        # Heuristic not confident, use CNN
        cnn_result = self.cnn_classifier.predict(cropped_image)
        
        if cnn_result['accepted']:
            # CNN is confident
            if heuristic_result:
                # Fuse confidences
                final_confidence = (
                    0.7 * heuristic_result.get('confidence', 0) + 
                    0.3 * cnn_result['confidence']
                )
            else:
                final_confidence = cnn_result['confidence']
            
            return {
                "class": cnn_result['class'],
                "confidence": cnn_result['confidence'],
                "source": "cnn",
                "heuristic_used": bool(heuristic_result),
                "cnn_used": True,
                "final_confidence": final_confidence,
                "all_probs": cnn_result['all_probs']
            }
        
        # Both uncertain
        return {
            "class": "uncertain",
            "confidence": cnn_result['confidence'],
            "source": "uncertain",
            "heuristic_used": bool(heuristic_result),
            "cnn_used": True,
            "final_confidence": 0.0,
            "all_probs": cnn_result['all_probs']
        }


# Convenience function for quick inference
def quick_predict(image, model_path='models/best_model.pth'):
    """
    Quick prediction without initialization overhead
    
    Args:
        image: Input image (numpy array or PIL)
        model_path: Path to model checkpoint
    
    Returns:
        Prediction dictionary
    """
    classifier = CNNLayoutClassifier(model_path)
    return classifier.predict(image)


if __name__ == "__main__":
    # Example usage
    print("CNN Inference Module")
    print("=" * 60)
    
    # Initialize classifier
    classifier = CNNLayoutClassifier(
        model_path='models/best_model.pth',
        confidence_threshold=0.75
    )
    
    # Example: Predict from numpy array
    dummy_image = np.random.randint(0, 255, (224, 224), dtype=np.uint8)
    result = classifier.predict(dummy_image)
    
    print("\nPrediction Result:")
    print(f"  Class: {result['class']}")
    print(f"  Confidence: {result['confidence']:.4f}")
    print(f"  Accepted: {result['accepted']}")
    print(f"  All Probabilities: {result['all_probs']}")
    
    # Example: Integration with heuristic
    print("\n" + "=" * 60)
    print("CNN Fallback Integration Example")
    print("=" * 60)
    
    integration = CNNFallbackIntegration(
        model_path='models/best_model.pth',
        heuristic_threshold=0.65,
        cnn_threshold=0.75
    )
    
    # Scenario 1: High heuristic confidence
    heuristic_high = {"class": "legend", "confidence": 0.85}
    result1 = integration.classify_region(dummy_image, heuristic_high)
    print("\nScenario 1 (High heuristic confidence):")
    print(f"  Source: {result1['source']}")
    print(f"  Class: {result1['class']}")
    
    # Scenario 2: Low heuristic confidence
    heuristic_low = {"class": "schedule", "confidence": 0.45}
    result2 = integration.classify_region(dummy_image, heuristic_low)
    print("\nScenario 2 (Low heuristic confidence):")
    print(f"  Source: {result2['source']}")
    print(f"  CNN Used: {result2['cnn_used']}")
