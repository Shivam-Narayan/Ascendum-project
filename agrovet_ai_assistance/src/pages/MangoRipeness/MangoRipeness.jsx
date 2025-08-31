import React, { useState } from 'react';
import Layout from '../../components/Layout';
import ImageUpload from '../../components/ImageUpload';
import { Grape, Clock, Star, AlertTriangle, CheckCircle } from 'lucide-react';
import './MangoRipeness.css';

const MangoRipeness = () => {
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
          stage: 'Perfectly Ripe',
          confidence: 93,
          color: '#F97316',
          bgColor: 'bg-orange-50 border-orange-200',
          textColor: 'text-orange-800',
          icon: '🥭',
          description: 'This mango has reached perfect ripeness! Ideal texture and sweetness for immediate consumption.',
          characteristics: [
            'Rich golden-orange color',
            'Slightly soft when gently pressed',
            'Sweet, fragrant aroma',
            'Smooth, unblemished skin'
          ],
          texture: 'Soft and juicy',
          aroma: 'Strong and sweet',
          uses: [
            'Fresh eating and desserts',
            'Smoothies and lassis',
            'Fruit salads and salsas',
            'Premium juice extraction'
          ],
          nutritionalValue: 'Peak vitamin A, C, and antioxidants',
          shelfLife: '2-3 days refrigerated',
          sugarContent: 'High (13-15%)',
          firmness: 'Yields to gentle pressure'
        },
        {
          stage: 'Nearly Ripe',
          confidence: 87,
          color: '#EAB308',
          bgColor: 'bg-yellow-50 border-yellow-200',
          textColor: 'text-yellow-800',
          icon: '🟡',
          description: 'Almost ready! This mango needs 1-2 more days to reach optimal sweetness and texture.',
          characteristics: [
            'Yellow-green with orange patches',
            'Firm with slight give',
            'Mild sweet aroma',
            'Clean, healthy appearance'
          ],
          texture: 'Firm but developing softness',
          aroma: 'Mild and pleasant',
          uses: [
            'Cooking and curry preparations',
            'Chutneys and pickles',
            'Baking applications',
            'Raw mango salads'
          ],
          nutritionalValue: 'Good fiber content and developing sugars',
          shelfLife: '3-5 days to full ripeness',
          sugarContent: 'Medium (8-10%)',
          firmness: 'Firm with minimal give'
        },
        {
          stage: 'Overripe',
          confidence: 91,
          color: '#DC2626',
          bgColor: 'bg-red-50 border-red-200',
          textColor: 'text-red-800',
          icon: '🔴',
          description: 'Past prime for fresh eating but excellent for processing. Very sweet with soft texture.',
          characteristics: [
            'Dark spots and wrinkled skin',
            'Very soft, may be mushy',
            'Intense, fermented aroma',
            'Some discoloration present'
          ],
          texture: 'Very soft to mushy',
          aroma: 'Very strong, slightly fermented',
          uses: [
            'Smoothies and purees',
            'Mango ice cream and sorbets',
            'Jams and preserves',
            'Baked goods and desserts'
          ],
          nutritionalValue: 'Very high in sugars and antioxidants',
          shelfLife: '1 day fresh, freeze for processing',
          sugarContent: 'Very high (16-18%)',
          firmness: 'Very soft, handle carefully'
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
              <Grape className="h-8 w-8 text-orange-600" />
              <h1 className="text-3xl font-bold text-gray-900">Mango Ripeness Detection</h1>
            </div>
            <h2 className="text-xl text-orange-600 font-semibold mb-4">King of Fruits at Perfect Timing</h2>
            <p className="text-gray-600 leading-relaxed mb-6">
              Evaluate mango maturity with precision for optimal harvesting and consumption. Our AI system analyzes 
              color, texture, and visual indicators to determine the perfect ripeness level for your mangoes, 
              ensuring you enjoy them at their peak flavor and nutritional value.
            </p>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
              <p className="text-orange-800 text-sm">
                Mango ripeness is crucial for both taste and texture. Unlike many fruits, mangoes can be picked 
                slightly underripe and will continue to ripen, developing their characteristic sweetness and aroma.
              </p>
            </div>
          </div>

          {/* Ripeness Indicators */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Ripeness Indicators:</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
                <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-yellow-500 rounded-full mx-auto mb-2"></div>
                <span className="text-sm font-medium text-gray-700">Color Change</span>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
                <div className="w-8 h-8 bg-gradient-to-r from-orange-400 to-red-500 rounded-full mx-auto mb-2"></div>
                <span className="text-sm font-medium text-gray-700">Texture</span>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full mx-auto mb-2"></div>
                <span className="text-sm font-medium text-gray-700">Aroma</span>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200 text-center">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full mx-auto mb-2"></div>
                <span className="text-sm font-medium text-gray-700">Firmness</span>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          <div className="mb-8">
            <p className="text-gray-700 mb-4">Upload an image of your mango:</p>
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
                <h3 className="text-xl font-semibold text-gray-900">Mango Analysis Complete</h3>
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
                    <p className="text-sm text-gray-600">Accuracy</p>
                  </div>

                  <div className="mt-4 space-y-3">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-500 uppercase tracking-wider">Texture</div>
                      <div className="font-medium text-sm">{analysisResult.texture}</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-500 uppercase tracking-wider">Aroma</div>
                      <div className="font-medium text-sm">{analysisResult.aroma}</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-500 uppercase tracking-wider">Sugar Content</div>
                      <div className="font-medium text-sm">{analysisResult.sugarContent}</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-500 uppercase tracking-wider">Shelf Life</div>
                      <div className="font-medium text-sm">{analysisResult.shelfLife}</div>
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
                        Physical Characteristics
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
                        Recommended Uses
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
                      Nutritional Profile
                    </h5>
                    <p className="text-sm text-gray-700">{analysisResult.nutritionalValue}</p>
                  </div>
                </div>
              </div>

              {/* Mango Facts */}
              <div className="mt-6 p-4 bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-lg">
                <h5 className="font-semibold text-orange-900 mb-3">🥭 Mango Mastery Tips</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-orange-800">
                  <div>
                    <strong>Ripening:</strong> Store at room temperature, then refrigerate when ripe
                  </div>
                  <div>
                    <strong>Selection:</strong> Choose mangoes that yield slightly to gentle pressure
                  </div>
                  <div>
                    <strong>Varieties:</strong> Different mango varieties ripen to different colors
                  </div>
                  <div>
                    <strong>Cutting:</strong> Score the flesh in a grid pattern for easy serving
                  </div>
                  <div>
                    <strong>Storage:</strong> Ripe mangoes can be frozen for up to 6 months
                  </div>
                  <div>
                    <strong>Health:</strong> Rich in vitamins A, C, and over 20 different vitamins
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

export default MangoRipeness;