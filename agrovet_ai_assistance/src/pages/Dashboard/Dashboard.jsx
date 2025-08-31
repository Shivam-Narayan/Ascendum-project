import React from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { 
  TestTube, 
  Sprout, 
  Bug, 
  Cherry, 
  Apple, 
  Grape, 
  ArrowRight,
  Leaf
} from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Soil Nutrition Analysis',
      description: 'Analyze soil health and pH levels using advanced AI image recognition technology.',
      icon: TestTube,
      path: '/soil-nutrition',
      colorClass: 'amber',
      cardClass: 'amber'
    },
    {
      title: 'Plant Disease Detection',
      description: 'Identify plant diseases early and get treatment recommendations.',
      icon: Sprout,
      path: '/plant-disease',
      colorClass: 'green',
      cardClass: 'green'
    },
    {
      title: 'Cotton Pest Identification',
      description: 'Detect and identify common cotton pests for better crop protection.',
      icon: Bug,
      path: '/cotton-pests',
      colorClass: 'red',
      cardClass: 'red'
    },
    {
      title: 'Tomato Ripeness Detection',
      description: 'Determine optimal harvest time for tomatoes using visual analysis.',
      icon: Cherry,
      path: '/tomato-ripeness',
      colorClass: 'red-orange',
      cardClass: 'red'
    },
    {
      title: 'Banana Ripeness Detection',
      description: 'Assess banana ripeness levels for perfect timing and quality control.',
      icon: Apple,
      path: '/banana-ripeness',
      colorClass: 'yellow-amber',
      cardClass: 'yellow'
    },
    {
      title: 'Mango Ripeness Detection',
      description: 'Evaluate mango maturity with precision for optimal harvesting.',
      icon: Grape,
      path: '/mango-ripeness',
      colorClass: 'orange-red',
      cardClass: 'orange'
    }
  ];

  return (
    <Layout>
      <div className="dashboard-container">
        {/* Hero Section */}
        <div className="hero-section">
          <div className="hero-card">
            <div className="hero-content">
              <div className="hero-text">
                <div className="hero-title-container">
                  <Leaf className="leaf-icon" />
                  <h1 className="hero-main-title">
                    Grow with Confidence
                  </h1>
                </div>
                <h2 className="hero-subtitle">
                  Introducing AI Personal Assistant for Plant and Soil
                </h2>
                <p className="hero-description">
                  Ever looked at your garden and wondered, "Is my soil healthy?" or "What's that spot on my tomato plant?" 
                  Well, wonder no more! We're excited to introduce a revolutionary tool that empowers you to become 
                  an expert in your own backyard.
                </p>
              </div>
              <div className="hero-image-container">
                <img
                  src="https://images.pexels.com/photos/1482101/pexels-photo-1482101.jpeg?auto=compress&cs=tinysrgb&w=400"
                  alt="Plant Analysis"
                  className="hero-image"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="features-grid">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                onClick={() => navigate(feature.path)}
                className={`feature-card ${feature.cardClass}`}
              >
                <div className="feature-card-header">
                  <div className={`feature-icon-container ${feature.colorClass}`}>
                    <Icon className="feature-icon" />
                  </div>
                  <ArrowRight className="arrow-icon" />
                </div>
                <h3 className="feature-title">
                  {feature.title}
                </h3>
                <p className="feature-description">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>

        {/* Additional Info */}
        <div className="cta-section">
          <div className="cta-content">
            <h3 className="cta-title">Ready to Transform Your Agriculture Experience?</h3>
            <p className="cta-description">
              Our AI-powered tools provide instant analysis and expert recommendations to help you make informed decisions about your plants and soil.
            </p>
            <div className="stats-container">
              <div className="stat-item">
                <div className="stat-number">6</div>
                <div className="stat-label">AI Tools</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">∞</div>
                <div className="stat-label">Possibilities</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">24/7</div>
                <div className="stat-label">Available</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;