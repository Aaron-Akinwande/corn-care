# 🌽 Maize Disease Detection & Nano Treatment System

## Complete Full-Stack Setup Guide

### 📋 System Overview
This is a comprehensive AI-powered web application that detects maize diseases from leaf images and recommends nano-based treatments. The system consists of:
- **Frontend**: Modern React application with responsive UI
- **Backend**: Python Flask API with TensorFlow/Keras CNN model
- **AI Model**: Deep learning model for disease classification
- **Treatment Database**: Nano-particle treatment recommendations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- npm or yarn
- Git

### Backend Setup (Flask API)

1. **Clone and Setup Environment**
```bash
# Create project directory
mkdir maize-disease-detection
cd maize-disease-detection

# Create backend directory
mkdir backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. **Install Dependencies**
```bash
# Install required packages
pip install -r requirements.txt
```

3. **Create Directory Structure**
```bash
# Create necessary directories
mkdir models uploads static templates

# Your backend structure should look like:
backend/
├── app.py
├── requirements.txt
├── models/
│   └── maize_disease_model.h5  # Your trained model
├── uploads/
└── static/
```

4. **Prepare the AI Model**

You have two options:

**Option A: Use Mock Predictions (for immediate testing)**
- The app will work with mock predictions if no model is found
- Perfect for testing the complete system

**Option B: Add Your Trained Model**
```bash
# Place your trained model in the models directory
cp your_trained_model.h5 models/maize_disease_model.h5
```

**Option C: Train a New Model**
```python
# Example training script (create train_model.py)
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

# Simple CNN model for demonstration
def create_maize_disease_model():
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(4, activation='softmax')  # 4 classes: Healthy, Blight, Rust, Gray Spot
    ])
    
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model

# Create and save model
model = create_maize_disease_model()
model.save('models/maize_disease_model.h5')
```

5. **Run the Backend**
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup (React App)

1. **Create React Application**
```bash
# Navigate back to project root
cd ..

# Create React app
npx create-react-app frontend
cd frontend

# Install additional dependencies
npm install lucide-react
```

2. **Replace App.js with the Provided Code**
- Copy the React component code from the artifact
- Replace the contents of `src/App.js`

3. **Update Package.json**
```json
{
  "name": "maize-disease-frontend",
  "version": "0.1.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.263.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

4. **Setup Tailwind CSS**
```bash
# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Configure tailwind.config.js
```

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

5. **Run the Frontend**
```bash
npm start
```

The frontend will start on `http://localhost:3000`

---

## 🧪 Testing the Application

### 1. Test Backend API
```bash
# Test health check
curl http://localhost:5000/

# Test with a sample image
curl -X POST -F "image=@sample_leaf.jpg" http://localhost:5000/predict
```

### 2. Test Frontend
1. Open `http://localhost:3000`
2. Upload a maize leaf image
3. Click "Analyze Disease"
4. View the results and recommendations

---

## 📊 Model Training Data Structure

If you want to train your own model, organize your data like this:

```
dataset/
├── train/
│   ├── healthy/
│   ├── blight/
│   ├── rust/
│   └── gray_leaf_spot/
├── validation/
│   ├── healthy/
│   ├── blight/
│   ├── rust/
│   └── gray_leaf_spot/
└── test/
    ├── healthy/
    ├── blight/
    ├── rust/
    └── gray_leaf_spot/
```

### Model Training Script Example

```python
# train_model.py
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# Data generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

# Load data
train_generator = train_datagen.flow_from_directory(
    'dataset/train',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

validation_generator = train_datagen.flow_from_directory(
    'dataset/train',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

# Create model
model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    alpha=1.0,
    include_top=False,
    weights='imagenet'
)

model.trainable = False

# Add custom layers
global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
prediction_layer = tf.keras.layers.Dense(4, activation='softmax')

model = tf.keras.Sequential([
    model,
    global_average_layer,
    prediction_layer
])

# Compile
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train
history = model.fit(
    train_generator,
    epochs=10,
    validation_data=validation_generator
)

# Save model
model.save('models/maize_disease_model.h5')
```

---

## 🚀 Production Deployment

### Backend Deployment (using Gunicorn)

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Create WSGI Entry Point**
```python
# wsgi.py
from app import app

if __name__ == "__main__":
    app.run()
```

3. **Run with Gunicorn**
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### Frontend Deployment

1. **Build for Production**
```bash
npm run build
```

2. **Serve Static Files**
```bash
# Using serve
npm install -g serve
serve -s build -l 3000
```

### Docker Deployment

**Backend Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

**Frontend Dockerfile**
```dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/models:/app/models

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in backend directory:
```env
FLASK_ENV=production
FLASK_DEBUG=False
MODEL_PATH=models/maize_disease_model.h5
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB max file size
```

### Frontend Configuration

Update API_BASE_URL in the React component:
```javascript
// For production
const API_BASE_URL = 'https://your-backend-domain.com';

// For development
const API_BASE_URL = 'http://localhost:5000';
```

---

## 🧪 API Documentation

### Endpoints

#### GET /
- **Description**: Health check
- **Response**: JSON with status and model info

#### POST /predict
- **Description**: Predict disease from image
- **Request**: multipart/form-data with 'image' file
- **Response**: JSON with disease, confidence, severity, description, and nanoparticles

#### GET /diseases
- **Description**: Get information about all detectable diseases
- **Response**: JSON with disease details and treatments

#### GET /nanoparticles
- **Description**: Get comprehensive nanoparticle treatment information
- **Response**: JSON with nanoparticle types and safety info

### Example API Response

```json
{
  "disease": "Northern Corn Leaf Blight",
  "confidence": 0.92,
  "severity": "High",
  "description": "A fungal disease caused by Exserohilum turcicum...",
  "nanoparticles": [
    {
      "name": "Copper Nanoparticles",
      "type": "Metal-based",
      "concentration": "50-100 ppm",
      "effectiveness": "95%",
      "application": "Foliar spray every 7-10 days"
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Common Issues

1. **CORS Error**: Make sure Flask-CORS is installed and configured
2. **Model Loading Error**: Check if model file exists and is valid
3. **Image Upload Error**: Verify file size and format restrictions
4. **API Connection Error**: Check if backend is running on correct port

### Debug Mode

Run backend in debug mode:
```bash
export FLASK_DEBUG=1
python app.py
```

### Logging

Add logging to your Flask app:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📈 Performance Optimization

### Backend Optimizations
- Use model caching
- Implement image preprocessing optimization
- Add request rate limiting
- Use Redis for caching results

### Frontend Optimizations
- Implement image compression before upload
- Add loading states and progress indicators
- Use React.memo for expensive components
- Implement lazy loading

---

## 🔐 Security Considerations

1. **File Upload Security**
   - Validate file types and sizes
   - Scan uploaded files for malware
   - Use secure file storage

2. **API Security**
   - Implement rate limiting
   - Add authentication for production
   - Validate all inputs

3. **Model Security**
   - Protect model files
   - Implement model versioning
   - Monitor for adversarial attacks

---

## 📚 Additional Resources

- [TensorFlow Documentation](https://www.tensorflow.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Support

For questions and support, please contact:
- Email: support@corncareai.com
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)

---

**Happy Farming! 🌽🚀**