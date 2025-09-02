import React, { useEffect, useState } from 'react';
import './SplashScreen.css';

const SplashScreen = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Start animations after a brief delay
    setTimeout(() => {
      setIsVisible(true);
    }, 300);

    // Navigate to the login screen after 5 seconds
    const timer = setTimeout(() => {
      // Add fade out effect before navigation
      setIsVisible(false);
      setTimeout(() => {
        window.location.href = "/login";
      }, 800);
    }, 5000);

    return () => clearTimeout(timer); // Cleanup the timer on component unmount
  }, []);

  return (
    <div className="splash-container">
      <div className={`splash-content ${isVisible ? 'visible' : ''}`}>
        <h2 className="project-name">AI Thumbnail Generator</h2>
        <div className="logo-container">
          <h1 className="company-name">Ascendum Solution</h1>
          <p className="tagline">Rise Together</p>
        </div>
      </div>
    </div>
  );
};

export default SplashScreen;