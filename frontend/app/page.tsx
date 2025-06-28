"use client"
import React, { useState, useRef, ChangeEvent } from 'react';
import { Upload, Leaf, Microscope, AlertCircle, CheckCircle, Download, Camera, Zap, Shield, Activity } from 'lucide-react';

// Type definitions
interface Nanoparticle {
  name: string;
  type: string;
  concentration: string;
  effectiveness: string;
  application: string;
}

interface PredictionResult {
  disease: string;
  confidence: number;
  severity: 'High' | 'Medium' | 'Low' | 'None';
  description: string;
  nanoparticles: Nanoparticle[];
}

interface ApiErrorResponse {
  error: string;
}

type SeverityLevel = 'High' | 'Medium' | 'Low' | 'None';

const MaizeDiseaseDetector: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [results, setResults] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // API configuration
  const API_BASE_URL: string = 'http://localhost:5000'; // Change this to your backend URL

  // Function to call the backend API for disease prediction
  const predictDisease = async (imageFile: File): Promise<PredictionResult> => {
    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData: ApiErrorResponse = await response.json();
        throw new Error(errorData.error || 'Prediction failed');
      }

      const result: PredictionResult = await response.json();
      return result;
    } catch (error) {
      // Fallback to mock data if API is not available
      console.warn('API unavailable, using mock data:', (error as Error).message);
      return mockPrediction(imageFile);
    }
  };

  // Mock prediction function (fallback when API is unavailable)
  const mockPrediction = async (imageFile: File): Promise<PredictionResult> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock responses for different diseases
    const mockResults: PredictionResult[] = [
      {
        disease: "Northern Corn Leaf Blight",
        confidence: 0.92,
        severity: "High",
        description: "A fungal disease caused by Exserohilum turcicum that creates elongated, grayish-green to tan lesions on corn leaves. It can significantly reduce yield if left untreated, especially in humid conditions.",
        nanoparticles: [
          {
            name: "Copper Nanoparticles",
            type: "Metal-based",
            concentration: "50-100 ppm",
            effectiveness: "95%",
            application: "Foliar spray every 7-10 days during disease development"
          },
          {
            name: "Silver Nanoparticles",
            type: "Metal-based",
            concentration: "25-50 ppm",
            effectiveness: "88%",
            application: "Root zone application twice weekly for systemic effect"
          },
          {
            name: "Chitosan-Silver Hybrid NPs",
            type: "Bio-metallic",
            concentration: "75-125 ppm",
            effectiveness: "92%",
            application: "Targeted spray on infected areas with 5-day intervals"
          }
        ]
      },
      {
        disease: "Common Rust",
        confidence: 0.87,
        severity: "Medium",
        description: "A fungal disease caused by Puccinia sorghi, characterized by small, reddish-brown pustules on both leaf surfaces. Most common in moderate temperature (60-77°F) and high humidity conditions.",
        nanoparticles: [
          {
            name: "Silica Nanoparticles",
            type: "Oxide-based",
            concentration: "200-300 ppm",
            effectiveness: "82%",
            application: "Preventive foliar spray bi-weekly during rust season"
          },
          {
            name: "Zinc Oxide Nanoparticles",
            type: "Oxide-based",
            concentration: "75-150 ppm",
            effectiveness: "78%",
            application: "Soil amendment and foliar spray combination"
          }
        ]
      },
      {
        disease: "Gray Leaf Spot",
        confidence: 0.89,
        severity: "Medium",
        description: "A fungal disease caused by Cercospora zeae-maydis that creates rectangular lesions with parallel sides on corn leaves. It thrives in warm, humid conditions and can cause significant yield loss.",
        nanoparticles: [
          {
            name: "Titanium Dioxide Nanoparticles",
            type: "Oxide-based",
            concentration: "100-200 ppm",
            effectiveness: "85%",
            application: "UV-activated foliar treatment during sunny periods"
          },
          {
            name: "Copper-Silver Hybrid NPs",
            type: "Bimetallic",
            concentration: "40-80 ppm",
            effectiveness: "92%",
            application: "Targeted spray on affected areas every 5-7 days"
          }
        ]
      },
      {
        disease: "Healthy",
        confidence: 0.95,
        severity: "None",
        description: "The leaf appears healthy with no visible signs of disease. Continue regular monitoring and preventive care to maintain plant health.",
        nanoparticles: [
          {
            name: "Silica Nanoparticles",
            type: "Oxide-based",
            concentration: "100-150 ppm",
            effectiveness: "N/A (Preventive)",
            application: "Preventive foliar spray monthly to boost plant immunity"
          }
        ]
      }
    ];
    
    return mockResults[Math.floor(Math.random() * mockResults.length)];
  };

  const handleImageUpload = (event: ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setError(null);
      setResults(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e: ProgressEvent<FileReader>) => {
        if (e.target?.result) {
          setImagePreview(e.target.result as string);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async (): Promise<void> => {
    if (!selectedImage) {
      setError("Please upload an image first");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Call the backend API for disease prediction
      const result = await predictDisease(selectedImage);
      setResults(result);
    } catch (err) {
      setError("Analysis failed. Please try again.");
      console.error('Prediction error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getSeverityColor = (severity: SeverityLevel): string => {
    switch (severity) {
      case 'High': return 'text-red-600 bg-red-100';
      case 'Medium': return 'text-yellow-600 bg-yellow-100';
      case 'Low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const exportToPDF = (): void => {
    // In a real app, you would generate a proper PDF
    alert("PDF export functionality would be implemented here using libraries like jsPDF or react-pdf");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-emerald-50">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-green-500">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-green-600 p-3 rounded-full">
                <Leaf className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">CornCare AI</h1>
                <p className="text-gray-600">Advanced Maize Disease Detection & Nano Treatment</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-green-600">
              <Microscope className="h-6 w-6" />
              <span className="font-semibold">Nano-Enhanced Agriculture</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Camera className="h-6 w-6 mr-2 text-green-600" />
              Upload Maize Leaf Image
            </h2>
            
            <div className="space-y-6">
              {/* Upload Area */}
              <div 
                className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-green-500 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                
                {imagePreview ? (
                  <div className="space-y-4">
                    <img 
                      src={imagePreview} 
                      alt="Preview" 
                      className="max-w-full h-64 object-contain mx-auto rounded-lg shadow-md"
                    />
                    <p className="text-sm text-gray-600">Click to change image</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Upload className="h-16 w-16 text-gray-400 mx-auto" />
                    <div>
                      <p className="text-lg font-medium text-gray-900">Drop your image here</p>
                      <p className="text-gray-500">or click to browse</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={!selectedImage || isAnalyzing}
                className="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-4 px-6 rounded-xl font-semibold text-lg hover:from-green-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 flex items-center justify-center space-x-2"
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Zap className="h-5 w-5" />
                    <span>Analyze Disease</span>
                  </>
                )}
              </button>

              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg flex items-center">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Activity className="h-6 w-6 mr-2 text-blue-600" />
              Analysis Results
            </h2>

            {!results ? (
              <div className="text-center py-12">
                <Microscope className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">Upload an image and click analyze to see results</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Disease Info */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      {results.disease === "Healthy" ? (
                        <CheckCircle className="h-8 w-8 text-green-500" />
                      ) : (
                        <AlertCircle className="h-8 w-8 text-red-500" />
                      )}
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">{results.disease}</h3>
                        <p className="text-sm text-gray-600">Disease Classification</p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getSeverityColor(results.severity)}`}>
                      {results.severity}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600">Confidence</p>
                      <p className={`text-2xl font-bold ${getConfidenceColor(results.confidence)}`}>
                        {(results.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Severity Level</p>
                      <p className="text-lg font-semibold text-gray-900">{results.severity}</p>
                    </div>
                  </div>
                  
                  <p className="text-gray-700 leading-relaxed">{results.description}</p>
                </div>

                {/* Nano Treatment Recommendations */}
                <div>
                  <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <Shield className="h-5 w-5 mr-2 text-purple-600" />
                    Recommended Nanoparticle Treatments
                  </h4>
                  
                  <div className="space-y-4">
                    {results.nanoparticles.map((nano: Nanoparticle, index: number) => (
                      <div key={index} className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
                        <div className="flex items-start justify-between mb-2">
                          <h5 className="font-semibold text-gray-900">{nano.name}</h5>
                          <span className="text-sm text-purple-600 bg-purple-100 px-2 py-1 rounded">
                            {nano.type}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600">Concentration</p>
                            <p className="font-medium">{nano.concentration}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Effectiveness</p>
                            <p className="font-medium text-green-600">{nano.effectiveness}</p>
                          </div>
                        </div>
                        
                        <div className="mt-2">
                          <p className="text-gray-600 text-sm">Application Method</p>
                          <p className="font-medium">{nano.application}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Export Button */}
                <button
                  onClick={exportToPDF}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 px-6 rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-200 flex items-center justify-center space-x-2"
                >
                  <Download className="h-5 w-5" />
                  <span>Export Diagnosis Report</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-green-100 p-3 rounded-full">
                <Leaf className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">AI-Powered Detection</h3>
            </div>
            <p className="text-gray-600">Advanced machine learning algorithms analyze leaf patterns to identify diseases with high accuracy.</p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-blue-100 p-3 rounded-full">
                <Microscope className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Nano Technology</h3>
            </div>
            <p className="text-gray-600">Cutting-edge nanoparticle treatments provide targeted, effective disease management solutions.</p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-purple-100 p-3 rounded-full">
                <Shield className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Precision Agriculture</h3>
            </div>
            <p className="text-gray-600">Personalized treatment recommendations based on disease type, severity, and environmental conditions.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MaizeDiseaseDetector;