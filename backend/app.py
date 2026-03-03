"""
Signify - Signature Verification API
--------------------------------------
Endpoints:
  POST /add-customer     → Upload 6-12 signatures with name & ID
  POST /verify-signature → Upload 1 signature + customer ID to verify
  GET  /customer/<id>    → Check if customer exists
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import numpy as np

from preprocessing import preprocess_signature
from feature_extraction import extract_all_features, verify_signature

app = Flask(__name__)
CORS(app, origins=[
    "https://pratikn2003.github.io",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
])

# Folders
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_customer_data_path(customer_id):
    return os.path.join(DATA_FOLDER, f"{customer_id}.json")


def save_customer_data(customer_id, customer_name, features_list):
    """Save customer name and feature vectors to JSON."""
    data = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "num_signatures": len(features_list),
        "features": [feat.tolist() for feat in features_list]
    }
    filepath = get_customer_data_path(customer_id)
    with open(filepath, 'w') as f:
        json.dump(data, f)


def load_customer_data(customer_id):
    """Load customer data from JSON."""
    filepath = get_customer_data_path(customer_id)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        data = json.load(f)
    # Convert features back to numpy arrays
    data['features'] = [np.array(feat) for feat in data['features']]
    return data


@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Signify - Signature Verification API"})


@app.route('/add-customer', methods=['POST'])
def add_customer():
    """
    Add a new customer with their signature dataset.

    Expects multipart/form-data:
        - customerName: string
        - customerId: string
        - signatures: 6-12 image files
    
    Pipeline:
        1. Receive images
        2. Preprocess each image (grayscale → blur → binarize → clean → crop → resize → normalize)
        3. Extract features (HOG + density + projections + contours + grid + centroid)
        4. Store features with customer ID
    """
    try:
        customer_name = request.form.get('customerName', '').strip()
        customer_id = request.form.get('customerId', '').strip()

        if not customer_name:
            return jsonify({"success": False, "error": "Customer name is required."}), 400

        if not customer_id:
            return jsonify({"success": False, "error": "Customer ID is required."}), 400

        # Check if customer already exists
        if os.path.exists(get_customer_data_path(customer_id)):
            return jsonify({"success": False, "error": f"Customer ID '{customer_id}' already exists."}), 400

        # Get uploaded files
        files = request.files.getlist('signatures')

        if len(files) < 6:
            return jsonify({"success": False, "error": "Minimum 6 signature images required."}), 400

        if len(files) > 12:
            return jsonify({"success": False, "error": "Maximum 12 signature images allowed."}), 400

        # Validate file types
        for f in files:
            if not allowed_file(f.filename):
                return jsonify({"success": False, "error": f"Invalid file type: {f.filename}. Only PNG, JPG, JPEG allowed."}), 400

        # Create customer upload folder
        customer_folder = os.path.join(UPLOAD_FOLDER, customer_id)
        os.makedirs(customer_folder, exist_ok=True)

        # Process each signature through the pipeline
        features_list = []
        for i, file in enumerate(files):
            # Read file bytes
            file_bytes = file.read()

            # Save original image
            ext = file.filename.rsplit('.', 1)[1].lower()
            save_path = os.path.join(customer_folder, f"sig_{i+1}.{ext}")
            with open(save_path, 'wb') as out_f:
                out_f.write(file_bytes)

            # === PREPROCESSING PIPELINE ===
            # grayscale → blur → binarize → morphological cleanup → crop → resize → normalize
            normalized_img, binary_img = preprocess_signature(file_bytes, from_bytes=True)

            # === FEATURE EXTRACTION ===
            # HOG + pixel density + aspect ratio + projections + contours + grid density + centroid
            feature_vector = extract_all_features(normalized_img, binary_img)
            features_list.append(feature_vector)

        # Save customer data (name + features)
        save_customer_data(customer_id, customer_name, features_list)

        return jsonify({
            "success": True,
            "message": f"Customer '{customer_name}' saved with {len(files)} signatures.",
            "customerId": customer_id,
            "signaturesProcessed": len(files),
            "featureVectorSize": len(features_list[0])
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/verify-signature', methods=['POST'])
def verify_signature_endpoint():
    """
    Verify a signature against stored customer signatures.

    Expects multipart/form-data:
        - customerId: string
        - signature: single image file

    Pipeline:
        1. Load stored features for the customer ID
        2. Preprocess the uploaded signature
        3. Extract features
        4. Compare using cosine similarity
        5. Return genuine/forged result with confidence score
    """
    try:
        customer_id = request.form.get('customerId', '').strip()

        if not customer_id:
            return jsonify({"success": False, "error": "Customer ID is required."}), 400

        # Load stored customer data
        customer_data = load_customer_data(customer_id)
        if customer_data is None:
            return jsonify({"success": False, "error": f"Customer ID '{customer_id}' not found."}), 404

        # Get uploaded signature
        file = request.files.get('signature')
        if not file:
            return jsonify({"success": False, "error": "Signature image is required."}), 400

        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "Invalid file type. Only PNG, JPG, JPEG allowed."}), 400

        # Read file
        file_bytes = file.read()

        # === PREPROCESSING PIPELINE ===
        normalized_img, binary_img = preprocess_signature(file_bytes, from_bytes=True)

        # === FEATURE EXTRACTION ===
        test_features = extract_all_features(normalized_img, binary_img)

        # === VERIFICATION (Cosine Similarity) ===
        stored_features = customer_data['features']
        is_genuine, avg_similarity, max_similarity = verify_signature(
            test_features, stored_features, threshold=0.75
        )

        # Convert similarity to percentage
        confidence = round(avg_similarity * 100, 2)

        return jsonify({
            "success": True,
            "customerId": customer_id,
            "customerName": customer_data['customer_name'],
            "isGenuine": is_genuine,
            "result": "✅ GENUINE" if is_genuine else "❌ FORGED",
            "confidence": confidence,
            "avgSimilarity": round(avg_similarity, 4),
            "maxSimilarity": round(max_similarity, 4),
            "storedSignatures": customer_data['num_signatures']
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Check if a customer exists and return basic info."""
    customer_data = load_customer_data(customer_id)
    if customer_data is None:
        return jsonify({"exists": False}), 404

    return jsonify({
        "exists": True,
        "customerId": customer_data['customer_id'],
        "customerName": customer_data['customer_name'],
        "numSignatures": customer_data['num_signatures']
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)

