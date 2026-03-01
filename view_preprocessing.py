import cv2
import numpy as np
import matplotlib.pyplot as plt
from Backend.app.ai.raster_pipeline import preprocess_scanned_blueprint

# Load and preprocess the image
image_path = "images/img2.png"
result = preprocess_scanned_blueprint(image_path)

# Display results
fig, axes = plt.subplots(1, 2, figsize=(15, 7))

# Original cleaned image
axes[0].imshow(result['clean_image'], cmap='gray')
axes[0].set_title('Denoised Image')
axes[0].axis('off')

# Binary preprocessed image
axes[1].imshow(result['binary_image'], cmap='gray')
axes[1].set_title('Binary Preprocessed Image')
axes[1].axis('off')

plt.suptitle(f"Deskew Angle: {result['deskew_angle']:.2f}°", fontsize=14)
plt.tight_layout()
plt.show()

print("Preprocessing complete")
print(f"  Deskew angle: {result['deskew_angle']:.2f}°")
print(f"  Scale factor: {result['scale_factor']}")
