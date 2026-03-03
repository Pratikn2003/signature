"""
Signature Feature Extraction
------------------------------
Extracts multiple features from preprocessed signature images:

1. HOG (Histogram of Oriented Gradients) - captures stroke direction patterns
2. Pixel Density Ratio - ink-to-background ratio
3. Aspect Ratio - width/height of signature
4. Horizontal & Vertical Projections - stroke distribution
5. Contour Features - number of contours, total contour area
6. Grid-based density - divide image into grid, compute density per cell
7. Centroid location - center of mass of signature strokes
"""

import cv2
import numpy as np
from skimage.feature import hog


def extract_hog_features(normalized_img):
    """
    Extract HOG (Histogram of Oriented Gradients) features.
    Captures the direction and magnitude of signature strokes.
    """
    features = hog(
        normalized_img,
        orientations=9,
        pixels_per_cell=(15, 15),
        cells_per_block=(2, 2),
        block_norm='L2-Hys',
        feature_vector=True
    )
    return features


def extract_pixel_density(binary_img):
    """
    Calculate the ratio of signature pixels to total pixels.
    Genuine signatures tend to have consistent ink density.
    """
    total_pixels = binary_img.shape[0] * binary_img.shape[1]
    ink_pixels = np.count_nonzero(binary_img)
    density = ink_pixels / total_pixels if total_pixels > 0 else 0
    return np.array([density])


def extract_aspect_ratio(binary_img):
    """
    Calculate aspect ratio of the signature bounding box.
    """
    img_uint8 = binary_img.astype(np.uint8) if binary_img.dtype != np.uint8 else binary_img
    # If image is float 0-1, scale to 0-255 first
    if binary_img.max() <= 1.0 and binary_img.dtype in [np.float32, np.float64]:
        img_uint8 = (binary_img * 255).astype(np.uint8)

    coords = cv2.findNonZero(img_uint8)
    if coords is None:
        return np.array([1.0])

    _, _, w, h = cv2.boundingRect(coords)
    ratio = w / h if h > 0 else 1.0
    return np.array([ratio])


def extract_projections(binary_img, bins=20):
    """
    Compute horizontal and vertical projection profiles.
    Shows how the signature strokes are distributed.
    """
    if binary_img.size == 0:
        return np.zeros(bins * 2)

    img = binary_img.astype(np.float64)
    if img.max() > 1:
        img = img / 255.0

    # Horizontal projection (sum along rows)
    h_proj = np.sum(img, axis=1)
    # Vertical projection (sum along columns)
    v_proj = np.sum(img, axis=0)

    # Safety: handle single-pixel images
    if len(h_proj) < 2:
        h_proj_resized = np.zeros(bins)
    else:
        h_proj_resized = np.interp(
            np.linspace(0, len(h_proj) - 1, bins),
            np.arange(len(h_proj)),
            h_proj
        )

    if len(v_proj) < 2:
        v_proj_resized = np.zeros(bins)
    else:
        v_proj_resized = np.interp(
            np.linspace(0, len(v_proj) - 1, bins),
            np.arange(len(v_proj)),
            v_proj
        )

    # Normalize
    h_max = h_proj_resized.max()
    v_max = v_proj_resized.max()
    if h_max > 0:
        h_proj_resized /= h_max
    if v_max > 0:
        v_proj_resized /= v_max

    return np.concatenate([h_proj_resized, v_proj_resized])


def extract_contour_features(binary_img):
    """
    Extract contour-based features:
    - Number of contours (connected components)
    - Total contour area
    - Average contour area
    """
    img_uint8 = binary_img.astype(np.uint8)
    if img_uint8.max() <= 1:
        img_uint8 = (img_uint8 * 255).astype(np.uint8)

    contours, _ = cv2.findContours(img_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    num_contours = len(contours)
    total_area = sum(cv2.contourArea(c) for c in contours) if contours else 0
    avg_area = total_area / num_contours if num_contours > 0 else 0

    # Normalize
    img_area = binary_img.shape[0] * binary_img.shape[1]
    return np.array([
        num_contours / 100.0,  # normalized count
        total_area / img_area if img_area > 0 else 0,
        avg_area / img_area if img_area > 0 else 0
    ])


def extract_grid_density(binary_img, grid_size=5):
    """
    Divide the image into a grid and compute ink density per cell.
    Captures spatial distribution of the signature.
    """
    if binary_img.size == 0:
        return np.zeros(grid_size * grid_size)

    img = binary_img.astype(np.float64)
    if img.max() > 1:
        img = img / 255.0

    h, w = img.shape
    cell_h = max(1, h // grid_size)
    cell_w = max(1, w // grid_size)

    densities = []
    for i in range(grid_size):
        for j in range(grid_size):
            r_start = i * cell_h
            r_end = min((i + 1) * cell_h, h)
            c_start = j * cell_w
            c_end = min((j + 1) * cell_w, w)
            cell = img[r_start:r_end, c_start:c_end]
            cell_density = np.mean(cell) if cell.size > 0 else 0.0
            densities.append(cell_density)

    return np.array(densities)


def extract_centroid(binary_img):
    """
    Find the centroid (center of mass) of the signature.
    Normalized to 0-1 range.
    """
    img_uint8 = binary_img.astype(np.uint8)
    if img_uint8.max() <= 1:
        img_uint8 = (img_uint8 * 255).astype(np.uint8)

    moments = cv2.moments(img_uint8)
    h, w = binary_img.shape

    if moments["m00"] != 0:
        cx = moments["m10"] / moments["m00"] / w
        cy = moments["m01"] / moments["m00"] / h
    else:
        cx, cy = 0.5, 0.5

    return np.array([cx, cy])


def extract_all_features(normalized_img, binary_img):
    """
    Extract all features and concatenate into a single feature vector.

    Args:
        normalized_img: preprocessed image (0-1 float, 150x150)
        binary_img: binary image (uint8, 150x150)

    Returns:
        feature_vector: 1D numpy array with all features
    """
    features = []

    # 1. HOG features (main feature - captures stroke patterns)
    hog_feat = extract_hog_features(normalized_img)
    features.append(hog_feat)

    # 2. Pixel density
    density = extract_pixel_density(binary_img)
    features.append(density)

    # 3. Aspect ratio
    aspect = extract_aspect_ratio(binary_img)
    features.append(aspect)

    # 4. Projection profiles
    projections = extract_projections(binary_img)
    features.append(projections)

    # 5. Contour features
    contour_feat = extract_contour_features(binary_img)
    features.append(contour_feat)

    # 6. Grid density
    grid = extract_grid_density(binary_img)
    features.append(grid)

    # 7. Centroid
    centroid = extract_centroid(binary_img)
    features.append(centroid)

    # Concatenate all features
    feature_vector = np.concatenate(features)

    return feature_vector


def compute_similarity(feature_vec1, feature_vec2):
    """
    Compute cosine similarity between two feature vectors.
    Returns a value between -1 and 1 (1 = identical).
    """
    norm1 = np.linalg.norm(feature_vec1)
    norm2 = np.linalg.norm(feature_vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(np.dot(feature_vec1, feature_vec2) / (norm1 * norm2))


def verify_signature(test_features, stored_features_list, threshold=0.75):
    """
    Compare a test signature against all stored signatures.

    Args:
        test_features: feature vector of the signature to verify
        stored_features_list: list of feature vectors of stored signatures
        threshold: similarity threshold (above = genuine, below = forged)

    Returns:
        is_genuine: True if signature matches
        avg_similarity: average similarity score (0-1)
        max_similarity: highest similarity score
    """
    if not stored_features_list:
        return False, 0.0, 0.0

    similarities = []
    for stored_feat in stored_features_list:
        sim = compute_similarity(test_features, stored_feat)
        similarities.append(sim)

    avg_similarity = float(np.mean(similarities))
    max_similarity = float(np.max(similarities))

    # Use average similarity for decision
    is_genuine = avg_similarity >= threshold

    return is_genuine, avg_similarity, max_similarity
