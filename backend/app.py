from flask import Flask, json, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MODEL_PATH = 'models/maize_disease_model.h5'

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('models', exist_ok=True)


with open("class_indices.json") as f:
    class_indices = json.load(f)

    DISEASE_CLASSES = {v: k for k, v in class_indices.items()}


DISEASE_NAME_MAP = {
    'Blight': 'Northern Corn Leaf Blight',
    'Common_Rust': 'Common Rust',
    'Gray_Leaf_Spot': 'Gray Leaf Spot',
    'Healthy': 'Healthy'
}


# Load model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"✅ Model loaded from {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image, target_size=(224, 224)):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = image.resize(target_size)
    img_array = np.array(image).astype('float32') / 255.0
    return np.expand_dims(img_array, axis=0)

def get_severity_level(confidence, disease_name):
    if disease_name == 'Healthy':
        return 'None'
    elif confidence >= 0.8:
        return 'High'
    elif confidence >= 0.6:
        return 'Medium'
    else:
        return 'Low'

def get_disease_description(disease_name):
    descriptions = {
        'Healthy': 'The leaf appears healthy with no visible signs of disease. Continue regular monitoring and preventive care.',
        'Northern Corn Leaf Blight': 'A fungal disease caused by *Exserohilum turcicum*. Elongated, tan lesions reduce yield significantly in humid climates.',
        'Common Rust': 'Caused by *Puccinia sorghi*. It creates reddish-brown pustules and spreads in humid, moderate temperatures.',
        'Gray Leaf Spot': 'Caused by *Cercospora zeae-maydis*. It forms rectangular lesions and thrives in hot, humid environments.'
    }
    return descriptions.get(disease_name, 'Unknown disease.')

def get_nanoparticle_recommendations(disease_name):
    recommendations = {
        'Healthy': [
            {
                'name': 'Silica Nanoparticles',
                'type': 'Oxide-based',
                'concentration': '100-150 ppm',
                'effectiveness': 'N/A (Preventive)',
                'application': 'Monthly foliar spray to boost plant immunity'
            }
        ],
        'Northern Corn Leaf Blight': [
            {
                'name': 'Copper Nanoparticles',
                'type': 'Metal-based',
                'concentration': '50-100 ppm',
                'effectiveness': '95%',
                'application': 'Spray every 7-10 days during infection'
            },
            {
                'name': 'Silver Nanoparticles',
                'type': 'Metal-based',
                'concentration': '25-50 ppm',
                'effectiveness': '88%',
                'application': 'Root zone application twice weekly'
            },
            {
                'name': 'Chitosan-Silver Hybrid NPs',
                'type': 'Bio-metallic',
                'concentration': '75-125 ppm',
                'effectiveness': '92%',
                'application': 'Targeted spray every 5 days'
            }
        ],
        'Common Rust': [
            {
                'name': 'Silica Nanoparticles',
                'type': 'Oxide-based',
                'concentration': '200-300 ppm',
                'effectiveness': '82%',
                'application': 'Bi-weekly spray during rust season'
            },
            {
                'name': 'Zinc Oxide Nanoparticles',
                'type': 'Oxide-based',
                'concentration': '75-150 ppm',
                'effectiveness': '78%',
                'application': 'Soil + foliar combo'
            },
            {
                'name': 'Magnesium Oxide NPs',
                'type': 'Oxide-based',
                'concentration': '100-200 ppm',
                'effectiveness': '85%',
                'application': 'Apply early morning for best results'
            }
        ],
        'Gray Leaf Spot': [
            {
                'name': 'Titanium Dioxide Nanoparticles',
                'type': 'Oxide-based',
                'concentration': '100-200 ppm',
                'effectiveness': '85%',
                'application': 'UV-activated foliar spray during sunny days'
            },
            {
                'name': 'Copper-Silver Hybrid NPs',
                'type': 'Bimetallic',
                'concentration': '40-80 ppm',
                'effectiveness': '92%',
                'application': 'Spray every 5-7 days on affected areas'
            },
            {
                'name': 'Selenium Nanoparticles',
                'type': 'Metalloid-based',
                'concentration': '20-40 ppm',
                'effectiveness': '89%',
                'application': 'Foliar spray with surfactant'
            }
        ]
    }
    return recommendations.get(disease_name, [])

# Routes
@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'message': 'Maize Disease Detection API',
        'model_loaded': model is not None
    })

@app.route('/predict', methods=['POST'])
def predict_disease():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid or missing file'}), 400

        image = Image.open(io.BytesIO(file.read()))
        processed = preprocess_image(image)

        if model:
            predictions = model.predict(processed)
        else:
            return jsonify({'error': 'Model not available'}), 500

        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        raw_disease_name = DISEASE_CLASSES[predicted_class_idx]
        disease_name = DISEASE_NAME_MAP.get(raw_disease_name, raw_disease_name)

        severity = get_severity_level(confidence, disease_name)
        description = get_disease_description(disease_name)
        nanoparticles = get_nanoparticle_recommendations(disease_name)

        return jsonify({
            'disease': disease_name,
            'confidence': round(confidence, 3),
            'severity': severity,
            'description': description,
            'nanoparticles': nanoparticles,
            'all_predictions': {
                DISEASE_NAME_MAP.get(DISEASE_CLASSES[i], DISEASE_CLASSES[i]): round(float(predictions[0][i]), 3)
                for i in range(len(predictions[0]))
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/diseases', methods=['GET'])
def get_diseases():
    data = []
    for idx, raw_name in DISEASE_CLASSES.items():
        name = DISEASE_NAME_MAP.get(raw_name, raw_name)
        data.append({
            'id': idx,
            'name': name,
            'description': get_disease_description(name),
            'nanoparticle_treatments': get_nanoparticle_recommendations(name)
        })
    return jsonify({'diseases': data})

@app.route('/nanoparticles', methods=['GET'])
def get_nanoparticle_info():
    return jsonify({
        'nanoparticle_types': {
            'Metal-based': {
                'description': 'Antimicrobial metal particles like Cu, Ag, Au',
                'examples': ['Copper NPs', 'Silver NPs', 'Gold NPs']
            },
            'Oxide-based': {
                'description': 'Photocatalytic oxides',
                'examples': ['ZnO NPs', 'TiO2 NPs', 'SiO2 NPs']
            },
            'Bimetallic': {
                'description': 'Dual-metal nanoparticles',
                'examples': ['Cu-Ag', 'Au-Pt']
            },
            'Bio-metallic': {
                'description': 'Biocompatible organic-metal hybrids',
                'examples': ['Chitosan-Ag', 'Alginate-Cu']
            }
        },
        'application_methods': [
            'Foliar spray', 'Root zone', 'Soil amendment', 'Seed treatment', 'Hydroponics'
        ],
        'safety_considerations': [
            'Avoid phytotoxicity by using correct ppm',
            'Apply during cool hours',
            'Observe plant response after treatment',
            'Follow local regulations'
        ]
    })

if __name__ == '__main__':
    print("🌽 Starting Maize Disease Detection API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
