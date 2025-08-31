import React, { useState } from 'react';
import Layout from '../../components/Layout';
import ImageUpload from '../../components/ImageUpload';
import { TestTube, Droplets, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import './SoilNutrition.css';

const SoilNutrition = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const soilTypes = [
    'Alluvial soil',
    'Black soil',
    'Clay soil',
    'Red soil'
  ];

  const handleImageSelect = (file) => {
    setSelectedImage(file);
    setAnalysisResult(null);
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);

    // Simulate AI analysis
    setTimeout(() => {
      const mockResults = [
        {
          soilType: 'Clay soil',
          ph: 6.8,
          phStatus: 'Slightly Acidic',
          moisture: 65,
          organicMatter: 4.2,
          nutrients: {
            nitrogen: 'High',
            phosphorus: 'Medium',
            potassium: 'Low'
          },
          recommendations: [
            'Add potassium-rich fertilizer to improve K levels',
            'Consider adding lime to increase pH slightly',
            'Maintain current organic matter levels with compost'
          ],
          color: '#8B4513'
        },
        {
          soilType: 'Black soil',
          ph: 7.2,
          phStatus: 'Neutral',
          moisture: 55,
          organicMatter: 5.8,
          nutrients: {
            nitrogen: 'High',
            phosphorus: 'High',
            potassium: 'Medium'
          },
          recommendations: [
            'Excellent soil quality for most crops',
            'Monitor water drainage during monsoon',
            'Continue current nutrient management practices'
          ],
          color: '#2F4F4F'
        },
        {
          soilType: 'Red soil',
          ph: 5.5,
          phStatus: 'Acidic',
          moisture: 45,
          organicMatter: 2.9,
          nutrients: {
            nitrogen: 'Low',
            phosphorus: 'Low',
            potassium: 'Medium'
          },
          recommendations: [
            'Apply lime to reduce acidity and improve pH',
            'Add nitrogen and phosphorus fertilizers',
            'Increase organic matter with compost or manure'
          ],
          color: '#CD5C5C'
        }
      ];

      const randomResult = mockResults[Math.floor(Math.random() * mockResults.length)];
      setAnalysisResult(randomResult);
      setIsAnalyzing(false);
    }, 3000);
  };

  const getNutrientColor = (level) => {
    switch (level) {
      case 'High': return 'text-green-600 bg-green-100';
      case 'Medium': return 'text-yellow-600 bg-yellow-100';
      case 'Low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPhColor = (ph) => {
    if (ph < 6.0) return 'text-red-600 bg-red-100';
    if (ph > 7.5) return 'text-blue-600 bg-blue-100';
    return 'text-green-600 bg-green-100';
  };

  return (
    <Layout>
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-4">
              <TestTube className="h-8 w-8 text-amber-600" />
              <h1 className="text-3xl font-bold text-gray-900">
                Know Your Soil's Secrets: Unlock the Key to Plant Health
              </h1>
            </div>
            <h2 className="text-xl text-amber-600 font-semibold mb-4">Analyze Your Soil Today!</h2>
            <p className="text-gray-600 leading-relaxed mb-4">
              Having healthy soil is the foundation of a thriving garden. But understanding complex soil test kits can be 
              challenging. Our app simplifies the process!
            </p>
            <p className="text-gray-600 leading-relaxed mb-6">
              Our "Soil pH Analysis" feature uses image recognition to analyze the color of your soil from a simple picture.
            </p>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
              <p className="text-amber-800 text-sm">
                Soil pH refers to how acidic or alkaline your soil is. It directly affects the nutrients available to your plants. 
                By knowing your soil's pH, you can make informed decisions about amending your soil to create the 
                perfect environment for your plants to flourish.
              </p>
            </div>
          </div>

          {/* Soil Types */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Here are the soil types we can identify:</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {soilTypes.map((type, index) => (
                <div key={index} className="bg-white p-4 rounded-lg border border-gray-200 text-center">
                  <div className="w-8 h-8 bg-gradient-to-r from-amber-500 to-yellow-500 rounded-full mx-auto mb-2"></div>
                  <span className="text-sm font-medium text-gray-700">{type}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Upload Section */}
          <div className="mb-8">
            <p className="text-gray-700 mb-4">Choose an image...</p>
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
                <h3 className="text-xl font-semibold text-gray-900">Soil Analysis Complete</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Soil Type and Visual */}
                <div className="space-y-4">
                  <div className="text-center p-6 rounded-lg border border-gray-200">
                    <div 
                      className="w-20 h-20 rounded-full mx-auto mb-4 shadow-md"
                      style={{ backgroundColor: analysisResult.color }}
                    ></div>
                    <h4 className="text-lg font-semibold text-gray-900">{analysisResult.soilType}</h4>
                    <p className="text-sm text-gray-600 mt-2">Detected soil type based on color analysis</p>
                  </div>

                  {/* pH Analysis */}
                  <div className="p-4 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">pH Level</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPhColor(analysisResult.ph)}`}>
                        {analysisResult.phStatus}
                      </span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900 mb-1">{analysisResult.ph}</div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-red-500 via-green-500 to-blue-500 h-2 rounded-full"
                        style={{ width: `${((analysisResult.ph - 4) / 6) * 100}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>4.0</span>
                      <span>7.0</span>
                      <span>10.0</span>
                    </div>
                  </div>
                </div>

                {/* Detailed Analysis */}
                <div className="space-y-4">
                  {/* Nutrients */}
                  <div className="p-4 rounded-lg border border-gray-200">
                    <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                      <Droplets className="h-4 w-4 mr-2" />
                      Nutrient Levels
                    </h5>
                    <div className="space-y-2">
                      {Object.entries(analysisResult.nutrients).map(([nutrient, level]) => (
                        <div key={nutrient} className="flex justify-between items-center">
                          <span className="text-sm text-gray-600 capitalize">{nutrient} (N)</span>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getNutrientColor(level)}`}>
                            {level}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Additional Metrics */}
                  <div className="p-4 rounded-lg border border-gray-200">
                    <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Additional Metrics
                    </h5>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Moisture Content</span>
                        <span className="text-sm font-medium text-gray-900">{analysisResult.moisture}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Organic Matter</span>
                        <span className="text-sm font-medium text-gray-900">{analysisResult.organicMatter}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                <h5 className="font-semibold text-green-900 mb-3 flex items-center">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Expert Recommendations
                </h5>
                <ul className="space-y-2">
                  {analysisResult.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm text-green-800 flex items-start">
                      <div className="w-2 h-2 bg-green-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default SoilNutrition;
