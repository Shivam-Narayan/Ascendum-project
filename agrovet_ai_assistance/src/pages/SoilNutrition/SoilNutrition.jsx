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
      case 'High': return 'nutrient-high';
      case 'Medium': return 'nutrient-medium';
      case 'Low': return 'nutrient-low';
      default: return 'nutrient-default';
    }
  };

  const getPhColor = (ph) => {
    if (ph < 6.0) return 'ph-acidic';
    if (ph > 7.5) return 'ph-alkaline';
    return 'ph-neutral';
  };

  return React.createElement(
    Layout,
    null,
    React.createElement(
      'div',
      { className: 'soil-nutrition-container' },
      React.createElement(
        'div',
        { className: 'soil-nutrition-content' },
        React.createElement(
          'div',
          { className: 'soil-nutrition-header' },
          React.createElement(
            'div',
            { className: 'header-title' },
            React.createElement(TestTube, { className: 'header-icon' }),
            React.createElement(
              'h1',
              { className: 'main-title' },
              'Know Your Soil\'s Secrets: Unlock the Key to Plant Health'
            )
          ),
          React.createElement(
            'h2',
            { className: 'sub-title' },
            'Analyze Your Soil Today!'
          ),
          React.createElement(
            'p',
            { className: 'description-text' },
            'Having healthy soil is the foundation of a thriving garden. But understanding complex soil test kits can be challenging. Our app simplifies the process!'
          ),
          React.createElement(
            'p',
            { className: 'description-text' },
            'Our "Soil pH Analysis" feature uses image recognition to analyze the color of your soil from a simple picture.'
          ),
          React.createElement(
            'div',
            { className: 'info-box' },
            React.createElement(
              'p',
              { className: 'info-text' },
              'Soil pH refers to how acidic or alkaline your soil is. It directly affects the nutrients available to your plants. By knowing your soil\'s pH, you can make informed decisions about amending your soil to create the perfect environment for your plants to flourish.'
            )
          )
        ),
        React.createElement(
          'div',
          { className: 'soil-types-section' },
          React.createElement(
            'h3',
            { className: 'section-title' },
            'Here are the soil types we can identify:'
          ),
          React.createElement(
            'div',
            { className: 'soil-types-grid' },
            soilTypes.map((type, index) =>
              React.createElement(
                'div',
                { key: index, className: 'soil-type-card' },
                React.createElement('div', { className: 'soil-type-icon' }),
                React.createElement('span', { className: 'soil-type-name' }, type)
              )
            )
          )
        ),
        React.createElement(
          'div',
          { className: 'upload-section' },
          React.createElement(
            'p',
            { className: 'upload-instruction' },
            'Choose an image...'
          ),
          React.createElement(ImageUpload, {
            onImageSelect: handleImageSelect,
            onAnalyze: handleAnalyze,
            isAnalyzing: isAnalyzing
          })
        ),
        analysisResult && React.createElement(
          'div',
          { className: 'analysis-results' },
          React.createElement(
            'div',
            { className: 'results-header' },
            React.createElement(CheckCircle, { className: 'results-icon' }),
            React.createElement(
              'h3',
              { className: 'results-title' },
              'Soil Analysis Complete'
            )
          ),
          React.createElement(
            'div',
            { className: 'results-grid' },
            React.createElement(
              'div',
              { className: 'results-left' },
              React.createElement(
                'div',
                { className: 'soil-type-result' },
                React.createElement('div', {
                  className: 'soil-color-sample',
                  style: { backgroundColor: analysisResult.color }
                }),
                React.createElement(
                  'h4',
                  { className: 'detected-soil-type' },
                  analysisResult.soilType
                ),
                React.createElement(
                  'p',
                  { className: 'detection-note' },
                  'Detected soil type based on color analysis'
                )
              ),
              React.createElement(
                'div',
                { className: 'ph-analysis' },
                React.createElement(
                  'div',
                  { className: 'ph-header' },
                  React.createElement('span', { className: 'ph-label' }, 'pH Level'),
                  React.createElement(
                    'span',
                    { className: `ph-status ${getPhColor(analysisResult.ph)}` },
                    analysisResult.phStatus
                  )
                ),
                React.createElement(
                  'div',
                  { className: 'ph-value' },
                  analysisResult.ph
                ),
                React.createElement(
                  'div',
                  { className: 'ph-scale' },
                  React.createElement('div', {
                    className: 'ph-indicator',
                    style: { width: `${((analysisResult.ph - 4) / 6) * 100}%` }
                  })
                ),
                React.createElement(
                  'div',
                  { className: 'ph-scale-labels' },
                  React.createElement('span', null, '4.0'),
                  React.createElement('span', null, '7.0'),
                  React.createElement('span', null, '10.0')
                )
              )
            ),
            React.createElement(
              'div',
              { className: 'results-right' },
              React.createElement(
                'div',
                { className: 'nutrients-section' },
                React.createElement(
                  'h5',
                  { className: 'section-header' },
                  React.createElement(Droplets, { className: 'section-icon' }),
                  'Nutrient Levels'
                ),
                React.createElement(
                  'div',
                  { className: 'nutrients-list' },
                  Object.entries(analysisResult.nutrients).map(([nutrient, level]) =>
                    React.createElement(
                      'div',
                      { key: nutrient, className: 'nutrient-item' },
                      React.createElement(
                        'span',
                        { className: 'nutrient-name' },
                        `${nutrient.charAt(0).toUpperCase() + nutrient.slice(1)} (N)`
                      ),
                      React.createElement(
                        'span',
                        { className: `nutrient-level ${getNutrientColor(level)}` },
                        level
                      )
                    )
                  )
                )
              ),
              React.createElement(
                'div',
                { className: 'metrics-section' },
                React.createElement(
                  'h5',
                  { className: 'section-header' },
                  React.createElement(TrendingUp, { className: 'section-icon' }),
                  'Additional Metrics'
                ),
                React.createElement(
                  'div',
                  { className: 'metrics-list' },
                  React.createElement(
                    'div',
                    { className: 'metric-item' },
                    React.createElement('span', { className: 'metric-name' }, 'Moisture Content'),
                    React.createElement('span', { className: 'metric-value' }, `${analysisResult.moisture}%`)
                  ),
                  React.createElement(
                    'div',
                    { className: 'metric-item' },
                    React.createElement('span', { className: 'metric-name' }, 'Organic Matter'),
                    React.createElement('span', { className: 'metric-value' }, `${analysisResult.organicMatter}%`)
                  )
                )
              )
            )
          ),
          React.createElement(
            'div',
            { className: 'recommendations-section' },
            React.createElement(
              'h5',
              { className: 'recommendations-header' },
              React.createElement(AlertTriangle, { className: 'section-icon' }),
              'Expert Recommendations'
            ),
            React.createElement(
              'ul',
              { className: 'recommendations-list' },
              analysisResult.recommendations.map((rec, index) =>
                React.createElement(
                  'li',
                  { key: index, className: 'recommendation-item' },
                  React.createElement('div', { className: 'recommendation-bullet' }),
                  rec
                )
              )
            )
          )
        )
      )
    )
  );
};

export default SoilNutrition;