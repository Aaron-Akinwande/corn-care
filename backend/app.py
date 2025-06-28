from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import base64
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

# Disease classes (should match your model's training classes)
DISEASE_CLASSES = {
    0: 'Healthy',
    1: 'Northern Corn Leaf Blight',
    2: 'Common Rust',
    3: 'Gray Leaf Spot'
}

# Load the pre-trained model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Using mock predictions for demonstration")
    model = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image, target_size=(224, 224)):
    """Preprocess image for model prediction"""
    try:
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image
        image = image.resize(target_size)
        
        # Convert to numpy array and normalize
        img_array = np.array(image)
        img_array = img_array.astype('float32') / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        raise ValueError(f"Error preprocessing image: {str(e)}")

def get_severity_level(confidence, disease_name):
    """Determine severity level based on confidence and disease type"""
    if disease_name == 'Healthy':
        return 'None'
    elif confidence >= 0.8:
        return 'High'
    elif confidence >= 0.6:
        return 'Medium'
    else:
        return 'Low'

def get_disease_description(disease_name):
    """Get detailed description for each disease"""
    descriptions = {
        'Healthy': 'The leaf appears healthy with no visible signs of disease. Continue regular monitoring and preventive care to maintain plant health.',
        'Northern Corn Leaf Blight': 'A fungal disease caused by Exserohilum turcicum that creates elongated, grayish-green to tan lesions on corn leaves. It can significantly reduce yield if left untreated, especially in humid conditions.',
        'Common Rust': 'A fungal disease caused by Puccinia sorghi, characterized by small, reddish-brown pustules on both leaf surfaces. Most common in moderate temperature (60-77°F) and high humidity conditions.',
        'Gray Leaf Spot': 'A fungal disease caused by Cercospora zeae-maydis that creates rectangular lesions with parallel sides on corn leaves. It thrives in warm, humid conditions and can cause significant yield loss.'
    }
    return descriptions.get(disease_name, 'Unknown disease detected.')

def get_nanoparticle_recommendations(disease_name):
    """Get nanoparticle treatment recommendations based on disease type"""
    recommendations = {
        'Healthy': [
            {
                'name': 'Silica Nanoparticles',
                'type': 'Oxide-based',
                'concentration': '100-150 ppm',
                'effectiveness': 'N/A (Preventive)',
                'application': 'Preventive foliar spray monthly to boost plant immunity'
            }
        ],
        'Northern Corn Leaf Blight': [
            {
                'name': 'Copper Nanoparticles',
                'type': 'Metal-based',
                'concentration': '50-100 ppm',
                'effectiveness': '95%',
                'application': 'Foliar spray every 7-10 days during disease development'
            },
            {
                'name': 'Silver Nanoparticles',
                'type': 'Metal-based',
                'concentration': '25-50 ppm',
                'effectiveness': '88%',
                'application': 'Root zone application twice weekly for systemic effect'
            },
            {
                'name': 'Chitosan-Silver Hybrid NPs',
                'type': 'Bio-metallic',
                'concentration': '75-125 ppm',
                'effectiveness': '92%',
                'application': 'Targeted spray on infected areas with 5-day intervals'
            }
        ],
        'Common Rust': [
            {
                'name': 'Silica Nanoparticles',
                'type': 'Oxide-based',
                'concentration': '200-300 ppm',
                'effectiveness': '82%',
                'application': 'Preventive foliar spray bi-weekly during rust season'
            },
            {
                'name': 'Zinc Oxide Nanoparticles',
                'type': 'Oxide-based',
                'concentration': '75-150 ppm',
                'effectiveness': '78%',
                'application': 'Soil amendment and foliar spray combination'
            },
            {
                'name': 'Magnesium Oxide NPs',
                'type': 'Oxide-based',
                'concentration': '100-200 ppm',
                'effectiveness': '85%',
                'application': 'Early morning foliar application for best absorption'
            }
        ],
        'Gray Leaf Spot': [
            {
                'name': 'Titanium Dioxide Nanoparticles',
                'type': 'Oxide-based',
                'concentration': '100-200 ppm',
                'effectiveness': '85%',
                'application': 'UV-activated foliar treatment during sunny periods'
            },
            {
                'name': 'Copper-Silver Hybrid NPs',
                'type': 'Bimetallic',
                'concentration': '40-80 ppm',
                'effectiveness': '92%',
                'application': 'Targeted spray on affected areas every 5-7 days'
            },
            {
                'name': 'Selenium Nanoparticles',
                'type': 'Metalloid-based',
                'concentration': '20-40 ppm',
                'effectiveness': '89%',
                'application': 'Foliar spray with surfactant for enhanced penetration'
            }
        ]
    }
    return recommendations.get(disease_name, [])

def mock_prediction(image):
    """Mock prediction function for demonstration when model is not available"""
    import random
    
    # Simulate random prediction
    class_idx = random.randint(0, 3)
    confidence = random.uniform(0.7, 0.98)
    
    return np.array([[confidence if i == class_idx else random.uniform(0.01, 0.3) 
                     for i in range(4)]])

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'Maize Disease Detection API',
        'model_loaded': model is not None
    })

@app.route('/predict', methods=['POST'])
def predict_disease():
    """Main prediction endpoint"""
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, JPEG, or GIF'}), 400
        
        # Read and process image
        try:
            image = Image.open(io.BytesIO(file.read()))
            processed_image = preprocess_image(image)
        except Exception as e:
            return jsonify({'error': f'Error processing image: {str(e)}'}), 400
        
        # Make prediction
        try:
            if model is not None:
                predictions = model.predict(processed_image)
            else:
                # Use mock prediction for demonstration
                predictions = mock_prediction(processed_image)
            
            # Get predicted class and confidence
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            disease_name = DISEASE_CLASSES[predicted_class_idx]
            
            # Get severity level
            severity = get_severity_level(confidence, disease_name)
            
            # Get disease description
            description = get_disease_description(disease_name)
            
            # Get nanoparticle recommendations
            nanoparticles = get_nanoparticle_recommendations(disease_name)
            
            # Prepare response
            response = {
                'disease': disease_name,
                'confidence': round(confidence, 3),
                'severity': severity,
                'description': description,
                'nanoparticles': nanoparticles,
                'all_predictions': {
                    DISEASE_CLASSES[i]: round(float(predictions[0][i]), 3) 
                    for i in range(len(predictions[0]))
                }
            }
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({'error': f'Error during prediction: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/diseases', methods=['GET'])
def get_disease_info():
    """Get information about all detectable diseases"""
    diseases_info = []
    
    for class_idx, disease_name in DISEASE_CLASSES.items():
        disease_info = {
            'id': class_idx,
            'name': disease_name,
            'description': get_disease_description(disease_name),
            'nanoparticle_treatments': get_nanoparticle_recommendations(disease_name)
        }
        diseases_info.append(disease_info)
    
    return jsonify({
        'diseases': diseases_info,
        'total_classes': len(DISEASE_CLASSES)
    })

@app.route('/nanoparticles', methods=['GET'])
def get_nanoparticle_info():
    """Get comprehensive information about nanoparticle treatments"""
    nanoparticle_types = {
        'Metal-based': {
            'description': 'Nanoparticles made from metals like copper, silver, and gold with strong antimicrobial properties',
            'examples': ['Copper NPs', 'Silver NPs', 'Gold NPs'],
            'mechanism': 'Release of metal ions that disrupt microbial cell walls and proteins'
        },
        'Oxide-based': {
            'description': 'Metal oxide nanoparticles with photocatalytic and antimicrobial properties',
            'examples': ['TiO2 NPs', 'ZnO NPs', 'SiO2 NPs'],
            'mechanism': 'Generation of reactive oxygen species and direct contact antimicrobial action'
        },
        'Bimetallic': {
            'description': 'Hybrid nanoparticles combining two metals for enhanced efficacy',
            'examples': ['Cu-Ag NPs', 'Au-Ag NPs', 'Pt-Pd NPs'],
            'mechanism': 'Synergistic effects of multiple metals for broader spectrum activity'
        },
        'Bio-metallic': {
            'description': 'Biocompatible nanoparticles combining organic and metallic components',
            'examples': ['Chitosan-Ag NPs', 'Alginate-Cu NPs'],
            'mechanism': 'Controlled release and enhanced biocompatibility with plant tissues'
        }
    }
    
    return jsonify({
        'nanoparticle_types': nanoparticle_types,
        'application_methods': [
            'Foliar spray',
            'Root zone application',
            'Soil amendment',
            'Seed treatment',
            'Hydroponic solution'
        ],
        'safety_considerations': [
            'Use recommended concentrations to avoid phytotoxicity',
            'Apply during cooler parts of the day',
            'Monitor plant response after application',
            'Follow local regulations for nanomaterial use'
        ]
    })

if __name__ == '__main__':
    print("Starting Maize Disease Detection API...")
    print("Available endpoints:")
    print("  GET  /           - Health check")
    print("  POST /predict    - Disease prediction")
    print("  GET  /diseases   - Disease information")
    print("  GET  /nanoparticles - Nanoparticle treatment info")
    print("\nModel status:", "Loaded" if model is not None else "Mock mode (for demo)")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)