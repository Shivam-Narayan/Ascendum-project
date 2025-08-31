import React, { useState } from 'react';
import Layout from '../../components/Layout';
import ImageUpload from '../../components/ImageUpload';
import { Sprout, AlertTriangle, CheckCircle, Shield, Zap } from 'lucide-react';
import './PlantDisease.css';

const PlantDisease = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleImageSelect = (file) => {
    setSelectedImage(file);
    setAnalysisResult(null);
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);

    // Simulate AI analysis
    setTimeout(() => {
      const mockDiseases = [
        {
          disease: 'Bacterial Leaf Spot',
          severity: 'Medium',
          confidence: 89,
          plant: 'Tomato',
          symptoms: [
            'Small dark spots on leaves',
            'Yellow halos around spots',
            'Leaf yellowing and drop',
            'Fruit cracking in severe cases'
          ],
          causes: [
            'Warm, humid conditions',
            'Overhead watering',
            'Poor air circulation',
            'Contaminated seeds or tools'
          ],
          treatment: [
            'Apply copper-based fungicide',
            'Improve air circulation',
            'Water at soil level, not leaves',
            'Remove affected plant debris'
          ],
          prevention: [
            'Use drip irrigation instead of overhead watering',
            'Ensure proper plant spacing',
            'Rotate crops annually',
            'Disinfect gardening tools regularly'
          ],
          color: '#F59E0B',
          bgColor: 'bg-yellow-50 border-yellow-200',
          textColor: 'text-yellow-800'
        },
        {
          disease: 'Powdery Mildew',
          severity: 'Low',
          confidence: 94,
          plant: 'Various Plants',
          symptoms: [
            'White powdery coating on leaves',
            'Leaf distortion and yellowing',
            'Stunted growth',
            'Reduced fruit production'
          ],
          causes: [
            'High humidity with dry conditions',
            'Poor air circulation',
            'Overcrowded plants',
            'Shade and cool temperatures'
          ],
          treatment: [
            'Apply neem oil or baking soda spray',
            'Increase air circulation',
            'Remove affected leaves',
            'Use sulfur-based fungicides if severe'
          ],
          prevention: [
            'Plant in full sun locations',
            'Ensure adequate spacing between plants',
            'Water at soil level',
            'Choose resistant plant varieties'
          ],
          color: '#10B981',
          bgColor: 'bg-green-50 border-green-200',
          textColor: 'text-green-800'
        },
        {
          disease: 'Late Blight',
          severity: 'High',
          confidence: 92,
          plant: 'Tomato/Potato',
          symptoms: [
            'Dark lesions on leaves and stems',
            'White fuzzy growth on leaf undersides',
            'Rapid plant collapse',
            'Brown rot on fruits'
          ],
          causes: [
            'Cool, wet weather conditions',
            'High humidity (>90%)',
            'Poor drainage',
            'Infected plant material'
          ],
          treatment: [
            'Remove and destroy affected plants immediately',
            'Apply preventive fungicide to healthy plants',
            'Improve drainage and air circulation',
            'Stop overhead watering'
          ],
          prevention: [
            'Choose blight-resistant varieties',
            'Ensure good drainage and spacing',
            'Apply preventive fungicide sprays',
            'Remove plant debris at season end'
          ],
          color: '#DC2626',
          bgColor: 'bg-red-50 border-red-200',
          textColor: 'text-red-800'
        }
      ];

      const randomResult = mockDiseases[Math.floor(Math.random() * mockDiseases.length)];
      setAnalysisResult(randomResult);
      setIsAnalyzing(false);
    }, 3500);
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'Low': return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'Medium': return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'High': return <Zap className="h-5 w-5 text-red-600" />;
      default: return <AlertTriangle className="h-5 w-5 text-gray-600" />;
    }
  };

  return (
    <Layout>
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-4">
              <Sprout className="h-8 w-8 text-green-600" />
              <h1 className="text-3xl font-bold text-gray-900">Plant Disease Identification</h1>
            </div>
            <h2 className="text-xl text-green-600 font-semibold mb-4">Early Detection for Healthy Plants</h2>
            <p className="text-gray-600 leading-relaxed mb-6">
              Identify plant diseases early and get expert treatment recommendations. Our AI-powered system analyzes 
              plant images to detect common diseases, assess severity, and provide actionable guidance to keep your 
              plants healthy and thriving.
            </p>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <p className="text-green-800 text-sm">
                Early detection is crucial for effective disease management. Upload a clear image of the affected 
                plant parts (leaves, stems, or fruits) for the most accurate analysis.
              </p>
            </div>
          </div>

          {/* Key Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
              <Sprout className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900 mb-1">Disease Detection</h3>
              <p className="text-sm text-gray-600">Identify 50+ common plant diseases</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
              <Shield className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900 mb-1">Treatment Plans</h3>
              <p className="text-sm text-gray-600">Get specific treatment recommendations</p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
              <AlertTriangle className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900 mb-1">Prevention Tips</h3>
              <p className="text-sm text-gray-600">Learn how to prevent future issues</p>
            </div>
          </div>

          {/* Upload Section */}
          <div className="mb-8">
            <p className="text-gray-700 mb-4">Upload an image of the affected plant:</p>
            <ImageUpload
              onImageSelect={handleImageSelect}
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
            />
          </div>

          {/* Analysis Results */}
          {analysisResult && (
            <div className="bg-white rounded-lg border border-gray-200 shadow-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <h3 className="text-xl font-semibold text-gray-900">Disease Analysis Complete</h3>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Result */}
                <div className="lg:col-span-1">
                  <div className={`p-6 rounded-lg border ${analysisResult.bgColor} text-center`}>
                    <Sprout className={`h-12 w-12 mx-auto mb-4 ${analysisResult.textColor}`} />
                    <h4 className={`text-lg font-bold ${analysisResult.textColor} mb-2`}>
                      {analysisResult.disease}
                    </h4>
                    <p className="text-sm text-gray-600 mb-3">Detected in: {analysisResult.plant}</p>
                    
                    <div className="flex items-center justify-center space-x-2 mb-3">
                      {getSeverityIcon(analysisResult.severity)}
                      <span className="font-medium">{analysisResult.severity} Severity</span>
                    </div>
                    
                    <div className={`text-2xl font-bold ${analysisResult.textColor}`}>
                      {analysisResult.confidence}%
                    </div>
                    <p className="text-sm text-gray-600">Confidence</p>
                  </div>
                </div>

                {/* Detailed Information */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Symptoms */}
                    <div className="p-4 rounded-lg border border-gray-200">
                      <h5 className="font-semibold text-gray-900 mb-3">Symptoms</h5>
                      <ul className="space-y-1">
                        {analysisResult.symptoms.map((symptom, index) => (
                          <li key={index} className="text-sm text-gray-600 flex items-start">
                            <div className="w-1 h-1 bg-red-500 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                            {symptom}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Causes */}
                    <div className="p-4 rounded-lg border border-gray-200">
                      <h5 className="font-semibold text-gray-900 mb-3">Common Causes</h5>
                      <ul className="space-y-1">
                        {analysisResult.causes.map((cause, index) => (
                          <li key={index} className="text-sm text-gray-600 flex items-start">
                            <div className="w-1 h-1 bg-yellow-500 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                            {cause}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Treatment */}
                    <div className={`p-4 rounded-lg border ${analysisResult.bgColor}`}>
                      <h5 className={`font-semibold ${analysisResult.textColor} mb-3 flex items-center`}>
                        <Shield className="h-4 w-4 mr-2" />
                        Treatment Steps
                      </h5>
                      <ul className="space-y-2">
                        {analysisResult.treatment.map((step, index) => (
                          <li key={index} className="text-sm text-gray-700 flex items-start">
                            <div className="w-4 h-4 bg-white rounded-full border-2 border-current mt-0.5 mr-2 flex-shrink-0 flex items-center justify-center">
                              <div className="w-1 h-1 bg-current rounded-full"></div>
                            </div>
                            {step}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Prevention */}
                    <div className="p-4 rounded-lg border border-blue-200 bg-blue-50">
                      <h5 className="font-semibold text-blue-800 mb-3 flex items-center">
                        <AlertTriangle className="h-4 w-4 mr-2" />
                        Prevention Tips
                      </h5>
                      <ul className="space-y-2">
                        {analysisResult.prevention.map((tip, index) => (
                          <li key={index} className="text-sm text-blue-700 flex items-start">
                            <div className="w-4 h-4 bg-white rounded-full border-2 border-blue-500 mt-0.5 mr-2 flex-shrink-0 flex items-center justify-center">
                              <div className="w-1 h-1 bg-blue-500 rounded-full"></div>
                            </div>
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default PlantDisease;