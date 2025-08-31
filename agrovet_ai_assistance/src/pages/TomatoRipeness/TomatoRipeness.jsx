import React, { useState } from 'react';
import Layout from '../../components/Layout';
import ImageUpload from '../../components/ImageUpload';
import { Cherry, Clock, Star, AlertTriangle, CheckCircle } from 'lucide-react';
import './TomatoRipeness.css';


const TomatoRipeness = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const ripenessStages = [
    {
      stage: 'Tomato Ripe',
      color: 'bg-red-500',
      description: 'These tomatoes have a vibrant red color, a slightly soft but firm texture, and no blemishes. They\'re perfect for salads, sandwiches, or enjoying on their own.'
    },
    {
      stage: 'Tomato Half-Ripe',
      color: 'bg-orange-500',
      description: 'These tomatoes are starting to turn red, but may still have some green patches. They\'re ideal for those who prefer a slightly tart flavor in their tomatoes.'
    },
    {
      stage: 'Tomato Unripe',
      color: 'bg-green-500',
      description: 'These tomatoes are mostly green, with perhaps a hint of red starting to show. They\'re not quite ready for eating yet, but can be used for cooking or pickling.'
    },
    {
      stage: 'Tomato Overripe',
      color: 'bg-red-800',
      description: 'These tomatoes are a deep red color, may be mushy to the touch, and might have some wrinkles or cracks. While still edible, they\'re best suited for sauces, soups, or stews.'
    },
    {
      stage: 'Tomato Rotten',
      color: 'bg-gray-600',
      description: 'These tomatoes should be avoided. They\'ll be very soft, mushy, and may have visible mold or discoloration.'
    }
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
          stage: 'Ripe',
          confidence: 94,
          color: '#DC2626',
          bgColor: 'bg-red-50 border-red-200',
          textColor: 'text-red-800',
          icon: '🍅',
          description: 'Perfect for immediate consumption! This tomato has reached optimal ripeness with excellent color, texture, and flavor development.',
          characteristics: [
            'Vibrant red color throughout',
            'Firm but slightly yielding texture',
            'Sweet and tangy flavor profile',
            'No visible blemishes or soft spots'
          ],
          recommendations: [
            'Consume within 2-3 days for best quality',
            'Store at room temperature if using soon',
            'Perfect for fresh salads and sandwiches',
            'Can be refrigerated to extend shelf life'
          ],
          nutritionalValue: 'High in Vitamin C, Lycopene, and Potassium'
        },
        {
          stage: 'Half-Ripe',
          confidence: 87,
          color: '#EA580C',
          bgColor: 'bg-orange-50 border-orange-200',
          textColor: 'text-orange-800',
          icon: '🟠',
          description: 'Nearly ready! This tomato is in the process of ripening and will be perfect in a few days.',
          characteristics: [
            'Mix of red and green coloration',
            'Firm texture with some give',
            'Developing flavor complexity',
            'Some areas still maturing'
          ],
          recommendations: [
            'Store at room temperature to continue ripening',
            'Will be ready in 2-4 days',
            'Good for cooking applications',
            'Monitor daily for optimal harvest timing'
          ],
          nutritionalValue: 'Good source of Vitamin C and developing Lycopene'
        },
        {
          stage: 'Unripe',
          confidence: 91,
          color: '#16A34A',
          bgColor: 'bg-green-50 border-green-200',
          textColor: 'text-green-800',
          icon: '🟢',
          description: 'Still developing. This tomato needs more time to reach full ripeness and flavor potential.',
          characteristics: [
            'Predominantly green color',
            'Very firm texture',
            'Minimal flavor development',
            'High acidity levels'
          ],
          recommendations: [
            'Leave on plant for continued ripening',
            'If harvested, store in warm area',
            'Can be used for green tomato recipes',
            'Will ripen in 1-2 weeks if stored properly'
          ],
          nutritionalValue: 'High in Vitamin K and developing nutrients'
        }
      ];

      const randomResult = mockResults[Math.floor(Math.random() * mockResults.length)];
      setAnalysisResult(randomResult);
      setIsAnalyzing(false);
    }, 3000);
  };

  return (
    <Layout>
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-4">
              <Cherry className="h-8 w-8 text-red-600" />
              <h1 className="text-3xl font-bold text-gray-900">Know Your Tomatoes</h1>
            </div>
            <h2 className="text-xl text-red-600 font-semibold mb-4">Upload an Image for Ripeness Detection</h2>
            <p className="text-gray-600 leading-relaxed mb-6">
              Ever unsure if the tomato at the store is at its peak ripeness? Wondering if your homegrown tomatoes are 
              ready to be picked? Fear not! Our AI-powered tool takes the mystery out of tomato freshness. Simply 
              upload an image of your tomato, and we'll analyze its color, texture, and other visual cues to determine its 
              ripeness stage.
            </p>
            <p className="text-gray-600 leading-relaxed mb-6">
              Our system identifies tomatoes based on the following categories:
            </p>
          </div>

          {/* Ripeness Stages */}
          <div className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {ripenessStages.map((stage, index) => (
                <div key={index} className="bg-white p-4 rounded-lg border border-gray-200">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`w-4 h-4 ${stage.color} rounded-full`}></div>
                    <span className="font-semibold text-gray-900">{stage.stage}</span>
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed">{stage.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="mb-6 p-4 bg-red-50 rounded-lg border border-red-200">
            <p className="text-red-800 text-center font-medium">
              Let our tool be your guide to enjoying tomatoes at their finest!
            </p>
          </div>

          {/* Upload Section */}
          <div className="mb-8">
            <p className="text-gray-700 mb-4">Or upload your own image</p>
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
                <h3 className="text-xl font-semibold text-gray-900">Tomato Analysis Complete</h3>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Result */}
                <div className="lg:col-span-1">
                  <div className={`p-6 rounded-lg border ${analysisResult.bgColor} text-center`}>
                    <div className="text-4xl mb-3">{analysisResult.icon}</div>
                    <h4 className={`text-xl font-bold ${analysisResult.textColor} mb-2`}>
                      {analysisResult.stage}
                    </h4>
                    <div className={`text-3xl font-bold ${analysisResult.textColor} mb-2`}>
                      {analysisResult.confidence}%
                    </div>
                    <p className="text-sm text-gray-600">Confidence Level</p>
                  </div>

                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <h5 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <Star className="h-4 w-4 mr-2 text-yellow-500" />
                      Nutritional Value
                    </h5>
                    <p className="text-sm text-gray-600">{analysisResult.nutritionalValue}</p>
                  </div>
                </div>

                {/* Detailed Information */}
                <div className="lg:col-span-2 space-y-6">
                  <div>
                    <p className={`text-sm ${analysisResult.textColor} leading-relaxed p-4 rounded-lg ${analysisResult.bgColor}`}>
                      {analysisResult.description}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Characteristics */}
                    <div className="p-4 rounded-lg border border-gray-200">
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <Clock className="h-4 w-4 mr-2" />
                        Key Characteristics
                      </h5>
                      <ul className="space-y-2">
                        {analysisResult.characteristics.map((char, index) => (
                          <li key={index} className="text-sm text-gray-600 flex items-start">
                            <div className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                            {char}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Recommendations */}
                    <div className="p-4 rounded-lg border border-gray-200">
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <AlertTriangle className="h-4 w-4 mr-2" />
                        Recommendations
                      </h5>
                      <ul className="space-y-2">
                        {analysisResult.recommendations.map((rec, index) => (
                          <li key={index} className="text-sm text-gray-600 flex items-start">
                            <div className={`w-2 h-2 rounded-full mt-2 mr-3 flex-shrink-0`} style={{ backgroundColor: analysisResult.color }}></div>
                            {rec}
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

export default TomatoRipeness;