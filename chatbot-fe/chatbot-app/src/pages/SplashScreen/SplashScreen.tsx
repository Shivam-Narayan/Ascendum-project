import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./SplashScreen.css";

const SplashScreen: React.FC = () => {
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const navigate = useNavigate();

  useEffect(() => {
    const animationTimer = setTimeout(() => {
      setIsVisible(true);
    }, 300);

    const redirectTimer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => {
        navigate("/login");
      }, 800);
    }, 5000);

    return () => {
      clearTimeout(animationTimer);
      clearTimeout(redirectTimer);
    };
  }, [navigate]);

  return (
    <div className="splash-container">
      <div className={`splash-content ${isVisible ? "visible" : ""}`}>
        <h2 className="project-name">Ascend AI Chatbot India</h2>
        <div className="logo-container">
          <h1 className="company-name">Ascendum Solution</h1>
          <p className="tagline">Rise Together</p>
        </div>
      </div>
    </div>
  );
};

export default SplashScreen;
