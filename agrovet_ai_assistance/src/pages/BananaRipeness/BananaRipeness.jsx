import React, { useState } from 'react';
import Layout from '../../components/Layout';
import ImageUpload from '../../components/ImageUpload';
import { Apple, Clock, Star, AlertTriangle, CheckCircle } from 'lucide-react';
import './BananaRipeness.css';

const BananaRipeness = () => {
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
      const mockResults = [
        {
          stage: 'Perfect Ripe',
          confidence: 92,
          color: '#FCD34D',
          bgColor: 'bg-yellow-50 border-yellow-200',
          textColor: 'text-yellow-800',
          icon: '🍌',
          description: 'Ideal for immediate consumption! This banana has reached perfect ripeness with optimal sweetness and texture.',
          characteristics: [
            'Bright yellow peel with few brown spots',
            'Soft, creamy texture',
            'Sweet flavor with balanced acidity',
            'Easy to digest'
          ],
          uses: [
            'Fresh eating and snacking',
            'Smoothies and shakes',
            'Breakfast bowls and cereals',
            'Fruit salads'
          ],
          nutritionalValue: 'Peak potassium, vitamin B6, and natural sugars',
          shelfLife: '2-3 days at room temperature',
          sugarContent: 'High (14-16%)',
          firmness: 'Soft but not mushy'
        },
        {
          stage: 'Slightly Underripe',
          confidence: 88,
          color: '#84CC16',
          bgColor: 'bg-lime-50 border-lime-200',
          textColor: 'text-lime-800',
          icon: '🟢',
          description: 'Still developing sweetness. This banana will be perfect in 1-2 days with proper storage.',
          characteristics: [
            'Green-yellow coloration',
            'Firm texture',
            'Slightly tart flavor',
            'Higher starch content'
          ],
          uses: [
            'Cooking and baking applications',
            'Green banana curry',
            'Chips and fries',
            'Plantain-style preparations'
          ],
          nutritionalValue: 'High in resistant starch and fiber',
          shelfLife: '3-5 days to reach full ripeness',
          sugarContent: 'Medium (10-12%)',
          firmness: 'Very firm'
        },
        {
          stage: 'Overripe',
          confidence: 94,
          color: '#A16207',
          bgColor: 'bg-amber-50 border-amber-200',
          textColor: 'text-amber-800',
          icon: '🟤',
          description: 'Very sweet but soft. Perfect for baking and smoothies, though past prime for fresh eating.',
          characteristics: [
            'Brown spots covering most of peel',
            'Very soft, almost mushy texture',
            'Very sweet flavor',
            'Strong banana aroma'
          ],
          uses: [
            'Banana bread and muffins',
            'Smoothies and milkshakes',
            'Ice cream and desserts',
            'Pancakes and waffles'
          ],
          nutritionalValue: 'Very high in antioxidants and sugars',
          shelfLife: '1-2 days, freeze for longer storage',
          sugarContent: 'Very high (18-20%)',
          firmness: 'Very soft/mushy'
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
              <Apple className="h-8 w-8 text-yellow-600" />
              <h1 className="text-3xl font-bold text-gray-900">Banana Ripeness Detection</h1>
            </div>
            <h2 className="text-xl text-yellow-600 font-semibold mb-4">Perfect Timing for Perfect Bananas</h2>
            <p className="text-gray-600 leading-relaxed mb-6">
              Determine the perfect ripeness level of your bananas for different uses. Our AI analyzes color, 
              texture, and visual cues to help you choose bananas at their optimal stage for eating fresh, 
              cooking, or baking.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <p className="text-yellow-800 text-sm">
                Banana ripeness affects taste, texture, and nutritional content. Each stage has its perfect use - 
                from cooking with green bananas to making smoothies with overripe ones!
              </p>
            </div>
          </div>

          {/* Ripeness Scale */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Banana Ripeness Scale:</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                  <span className="font-semibold text-green-800">Underripe</span>
                </div>
                <p className="text-sm text-green-700">Firm, starchy, great for cooking</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
                  <span className="font-semibold text-yellow-800">Perfect Ripe</span>
                </div>
                <p className="text-sm text-yellow-700">Sweet, soft, ideal for eating fresh</p>
              </div>
              <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-4 h-4 bg-amber-600 rounded-full"></div>
                  <span className="font-semibold text-amber-800">Overripe</span>
                </div>
                <p className="text-sm text-amber-700">Very sweet, perfect for baking</p>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          <div className="mb-8">
            <p className="text-gray-700 mb-4">Upload an image of your banana:</p>
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
                <h3 className="text-xl font-semibold text-gray-900">Banana Analysis Complete</h3>
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

                  <div className="mt-4 space-y-3">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Sugar Content:</span>
                        <span className="font-medium">{analysisResult.sugarContent}</span>
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Firmness:</span>
                        <span className="font-medium">{analysisResult.firmness}</span>
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Shelf Life:</span>
                        <span className="font-medium">{analysisResult.shelfLife}</span>
                      </div>
                    </div>
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

                    {/* Best Uses */}
                    <div className="p-4 rounded-lg border border-gray-200">
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <Star className="h-4 w-4 mr-2" />
                        Best Uses
                      </h5>
                      <ul className="space-y-2">
                        {analysisResult.uses.map((use, index) => (
                          <li key={index} className="text-sm text-gray-600 flex items-start">
                            <div className={`w-2 h-2 rounded-full mt-2 mr-3 flex-shrink-0`} style={{ backgroundColor: analysisResult.color }}></div>
                            {use}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Nutritional Information */}
                  <div className={`p-4 rounded-lg border ${analysisResult.bgColor}`}>
                    <h5 className={`font-semibold ${analysisResult.textColor} mb-2 flex items-center`}>
                      <AlertTriangle className="h-4 w-4 mr-2" />
                      Nutritional Highlights
                    </h5>
                    <p className="text-sm text-gray-700">{analysisResult.nutritionalValue}</p>
                  </div>
                </div>
              </div>

              {/* Fun Facts */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h5 className="font-semibold text-blue-900 mb-2">🍌 Did You Know?</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
                  <div>
                    <strong>Ripening:</strong> Bananas continue ripening after harvest due to ethylene gas production
                  </div>
                  <div>
                    <strong>Storage:</strong> Keep bananas separate from other fruits to control ripening speed
                  </div>
                  <div>
                    <strong>Freezing:</strong> Overripe bananas freeze well for smoothies and baking
                  </div>
                  <div>
                    <strong>Nutrition:</strong> Banana ripeness affects the ratio of starch to sugar content
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

export default BananaRipeness;