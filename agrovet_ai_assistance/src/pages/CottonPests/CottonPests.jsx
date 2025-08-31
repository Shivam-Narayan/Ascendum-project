import React, { useState } from 'react';
import Layout from '../../components/Layout';
import ImageUpload from '../../components/ImageUpload';
import { Bug, Shield, AlertCircle, CheckCircle, Target } from 'lucide-react';
import './CottonPests.css';

const CottonPests = () => {
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
      const mockPests = [
        {
          pest: 'Bollworm',
          scientificName: 'Helicoverpa armigera',
          severity: 'High',
          confidence: 91,
          lifecycle: 'Complete metamorphosis (30-45 days)',
          identification: [
            'Green to brown caterpillars with dark stripes',
            'Length: 35-40mm when fully grown',
            'Feed on cotton bolls, flowers, and leaves',
            'Active during warm evenings'
          ],
          damage: [
            'Holes in cotton bolls and squares',
            'Reduced fiber quality',
            'Secondary fungal infections',
            'Yield losses up to 50-60%'
          ],
          treatment: [
            'Apply Bt (Bacillus thuringiensis) spray',
            'Use pheromone traps for monitoring',
            'Apply neem-based insecticides',
            'Release natural predators (Trichogramma wasps)'
          ],
          prevention: [
            'Plant Bt cotton varieties',
            'Monitor fields regularly',
            'Remove volunteer cotton plants',
            'Maintain field hygiene'
          ],
          color: '#DC2626',
          bgColor: 'bg-red-50 border-red-200',
          textColor: 'text-red-800'
        },
        {
          pest: 'Aphids',
          scientificName: 'Aphis gossypii',
          severity: 'Medium',
          confidence: 87,
          lifecycle: 'Incomplete metamorphosis (7-10 days)',
          identification: [
            'Small, soft-bodied insects (1-2mm)',
            'Green to black coloration',
            'Cluster on young shoots and leaves',
            'Winged and wingless forms present'
          ],
          damage: [
            'Yellowing and curling of leaves',
            'Honeydew secretion attracts ants',
            'Sooty mold development',
            'Stunted plant growth'
          ],
          treatment: [
            'Spray insecticidal soap solution',
            'Apply neem oil or horticultural oil',
            'Use systemic insecticides if severe',
            'Introduce ladybirds as biological control'
          ],
          prevention: [
            'Maintain proper plant spacing',
            'Remove weeds that harbor aphids',
            'Use reflective mulch',
            'Encourage beneficial insects'
          ],
          color: '#F59E0B',
          bgColor: 'bg-yellow-50 border-yellow-200',
          textColor: 'text-yellow-800'
        },
        {
          pest: 'Whitefly',
          scientificName: 'Bemisia tabaci',
          severity: 'Medium',
          confidence: 89,
          lifecycle: 'Complete metamorphosis (21-25 days)',
          identification: [
            'Small white flying insects (1mm)',
            'Found on leaf undersides',
            'Yellow, scale-like nymphs',
            'Flutter when plant is disturbed'
          ],
          damage: [
            'Leaf yellowing and silvering',
            'Honeydew secretion',
            'Virus transmission',
            'Reduced photosynthesis'
          ],
          treatment: [
            'Use yellow sticky traps',
            'Apply systemic insecticides',
            'Spray with horticultural oil',
            'Biological control with Encarsia wasps'
          ],
          prevention: [
            'Use whitefly-resistant varieties',
            'Install fine mesh screens',
            'Remove infected plant debris',
            'Monitor with yellow traps'
          ],
          color: '#10B981',
          bgColor: 'bg-green-50 border-green-200',
          textColor: 'text-green-800'
        }
      ];

      const randomResult = mockPests[Math.floor(Math.random() * mockPests.length)];
      setAnalysisResult(randomResult);
      setIsAnalyzing(false);
    }, 3500);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'Low': return 'text-green-600 bg-green-100';
      case 'Medium': return 'text-yellow-600 bg-yellow-100';
      case 'High': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <Layout>
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center space-x-3 mb-4">
              <Bug className="h-8 w-8 text-red-600" />
              <h1 className="text-3xl font-bold text-gray-900">Cotton Pest Identification</h1>
            </div>
            <h2 className="text-xl text-red-600 font-semibold mb-4">Protect Your Cotton Crop</h2>
            <p className="text-gray-600 leading-relaxed mb-6">
              Identify cotton pests early and implement targeted control measures. Our AI system recognizes common 
              cotton pests, assesses infestation levels, and provides integrated pest management recommendations 
              to protect your crop yield and quality.
            </p>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800 text-sm">
                Early detection and proper identification are essential for effective pest management. Upload clear 
                images of suspected pests or damage symptoms for accurate analysis.
              </p>
            </div>
          </div>

          {/* Common Pests Overview */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Common Cotton Pests We Identify:</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <Bug className="h-8 w-8 text-red-600 mb-2" />
                <h4 className="font-semibold text-gray-900 mb-1">Bollworm</h4>
                <p className="text-sm text-gray-600">Major pest causing significant yield losses</p>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <Target className="h-8 w-8 text-yellow-600 mb-2" />
                <h4 className="font-semibold text-gray-900 mb-1">Aphids</h4>
                <p className="text-sm text-gray-600">Sucking pests affecting plant vigor</p>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <Shield className="h-8 w-8 text-green-600 mb-2" />
                <h4 className="font-semibold text-gray-900 mb-1">Whiteflies</h4>
                <p className="text-sm text-gray-600">Vector for viral diseases</p>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          <div className="mb-8">
            <p className="text-gray-700 mb-4">Upload an image of the pest or damage:</p>
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
                <h3 className="text-xl font-semibold text-gray-900">Pest Identification Complete</h3>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Result */}
                <div className="lg:col-span-1">
                  <div className={`p-6 rounded-lg border ${analysisResult.bgColor} text-center`}>
                    <Bug className={`h-12 w-12 mx-auto mb-4 ${analysisResult.textColor}`} />
                    <h4 className={`text-lg font-bold ${analysisResult.textColor} mb-1`}>
                      {analysisResult.pest}
                    </h4>
                    <p className="text-sm italic text-gray-600 mb-3">{analysisResult.scientificName}</p>
                    
                    <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium mb-3 ${getSeverityColor(analysisResult.severity)}`}>
                      {analysisResult.severity} Risk
                    </div>
                    
                    <div className={`text-2xl font-bold ${analysisResult.textColor} mb-1`}>
                      {analysisResult.confidence}%
                    </div>
                    <p className="text-sm text-gray-600">Confidence</p>
                  </div>

                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <h5 className="font-semibold text-gray-900 mb-2">Life Cycle</h5>
                    <p className="text-sm text-gray-600">{analysisResult.lifecycle}</p>
                  </div>
                </div>

                {/* Detailed Information */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Identification */}
                    <div className="p-4 rounded-lg border border-gray-200">
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <Target className="h-4 w-4 mr-2" />
                        Identification
                      </h5>
                      <ul className="space-y-1">
                        {analysisResult.identification.map((feature, index) => (
                          <li key={index} className="text-sm text-gray-600 flex items-start">
                            <div className="w-1 h-1 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Damage */}
                    <div className="p-4 rounded-lg border border-gray-200">
                      <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                        <AlertCircle className="h-4 w-4 mr-2" />
                        Damage Symptoms
                      </h5>
                      <ul className="space-y-1">
                        {analysisResult.damage.map((symptom, index) => (
                          <li key={index} className="text-sm text-gray-600 flex items-start">
                            <div className="w-1 h-1 bg-red-500 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                            {symptom}
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
                        Treatment Options
                      </h5>
                      <ul className="space-y-2">
                        {analysisResult.treatment.map((option, index) => (
                          <li key={index} className="text-sm text-gray-700 flex items-start">
                            <div className="w-4 h-4 bg-white rounded border-2 border-current mt-0.5 mr-2 flex-shrink-0 flex items-center justify-center">
                              <div className="w-1.5 h-1.5 bg-current rounded-full"></div>
                            </div>
                            {option}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Prevention */}
                    <div className="p-4 rounded-lg border border-green-200 bg-green-50">
                      <h5 className="font-semibold text-green-800 mb-3 flex items-center">
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Prevention Measures
                      </h5>
                      <ul className="space-y-2">
                        {analysisResult.prevention.map((measure, index) => (
                          <li key={index} className="text-sm text-green-700 flex items-start">
                            <div className="w-4 h-4 bg-white rounded border-2 border-green-500 mt-0.5 mr-2 flex-shrink-0 flex items-center justify-center">
                              <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                            </div>
                            {measure}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Additional Tips */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h5 className="font-semibold text-blue-900 mb-2">💡 Pro Tips for Cotton Pest Management</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
                  <div>
                    <strong>Monitoring:</strong> Check fields weekly during growing season
                  </div>
                  <div>
                    <strong>Timing:</strong> Apply treatments based on pest development stages
                  </div>
                  <div>
                    <strong>IPM:</strong> Combine biological, cultural, and chemical controls
                  </div>
                  <div>
                    <strong>Resistance:</strong> Rotate insecticides to prevent resistance
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

export default CottonPests;