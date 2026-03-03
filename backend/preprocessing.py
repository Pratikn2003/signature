"""
Signature Preprocessing Pipeline
---------------------------------
Steps:
1. Load image
2. Convert to grayscale
3. Gaussian blur (noise removal)
4. Adaptive thresholding (binarization)
5. Morphological operations (clean up)
6. Invert if needed (signature = white on black → black on white)
7. Crop to signature bounding box
8. Resize to standard size (150x150)
9. Normalize pixel values (0-1)
"""

import cv2
import numpy as np


# Standard size for all processed signatures
STANDARD_SIZE = (150, 150)


def load_image(image_path):
    """Load image from file path."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    return img


def load_image_from_bytes(file_bytes):
    """Load image from bytes (for uploaded files)."""
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image from bytes")
    return img


def to_grayscale(img):
    """Step 1: Convert to grayscale."""
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def remove_noise(gray_img):
    """Step 2: Apply Gaussian blur to remove noise."""
    return cv2.GaussianBlur(gray_img, (5, 5), 0)


def binarize(blurred_img):
    """Step 3: Adaptive thresholding for binarization."""
    binary = cv2.adaptiveThreshold(
        blurred_img, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=21,
        C=10
    )
    return binary


def morphological_cleanup(binary_img):
    """Step 4: Morphological operations to clean small noise."""
    # Remove small noise with opening
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    cleaned = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, kernel_small)

    # Fill small gaps with closing
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_close)

    return cleaned


def crop_to_signature(binary_img, padding=10):
    """Step 5: Crop image to the bounding box of the signature."""
    coords = cv2.findNonZero(binary_img)
    if coords is None:
        # No signature found — return original image
        return binary_img

    x, y, w, h = cv2.boundingRect(coords)

    # Add padding
    rows, cols = binary_img.shape
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(cols, x + w + padding)
    y2 = min(rows, y + h + padding)

    cropped = binary_img[y1:y2, x1:x2]

    # Safety: ensure minimum size
    if cropped.shape[0] < 5 or cropped.shape[1] < 5:
        return binary_img

    return cropped


def resize_signature(cropped_img, size=STANDARD_SIZE):
    """Step 6: Resize to standard size while maintaining aspect ratio."""
    h, w = cropped_img.shape[:2]
    target_w, target_h = size

    # Safety: handle edge case of zero-dimension image
    if h == 0 or w == 0:
        return np.zeros((target_h, target_w), dtype=np.uint8)

    # Calculate scale to fit within target size
    scale = min(target_w / w, target_h / h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    resized = cv2.resize(cropped_img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Center on a blank canvas
    canvas = np.zeros((target_h, target_w), dtype=np.uint8)
    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

    return canvas


def normalize(img):
    """Step 7: Normalize pixel values to 0-1 range."""
    return img.astype(np.float32) / 255.0


def thin_signature(binary_img):
    """Step 5b (optional): Skeletonize/thin the signature strokes."""
    # Use morphological thinning
    thinned = cv2.ximgproc.thinning(binary_img) if hasattr(cv2, 'ximgproc') else binary_img
    return thinned


def preprocess_signature(image_input, from_bytes=False):
    """
    Full preprocessing pipeline.

    Args:
        image_input: file path (str) or bytes
        from_bytes: True if image_input is bytes

    Returns:
        processed: normalized numpy array (150x150), values 0-1
        binary: binary image before normalization (for feature extraction)
    """
    # Load
    if from_bytes:
        img = load_image_from_bytes(image_input)
    else:
        img = load_image(image_input)

    # Pipeline
    gray = to_grayscale(img)
    blurred = remove_noise(gray)
    binary = binarize(blurred)
    cleaned = morphological_cleanup(binary)
    cropped = crop_to_signature(cleaned)
    resized = resize_signature(cropped)
    normalized = normalize(resized)

    return normalized, resized
