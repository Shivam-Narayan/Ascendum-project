import type React from "react";
import { useEffect, useMemo, useState } from "react";
import {
  FiMoon,
  FiSun,
  FiMenu,
  FiUser,
  FiSettings,
  FiEdit2,
  FiBell,
  FiShield,
  FiGlobe,
} from "react-icons/fi";
import { FiMail, FiCalendar, FiHash } from "react-icons/fi";
import { Toaster } from "react-hot-toast";
import HomeScreenSidebar from "./HomeScreenSidebar/HomeScreenSidebar";
import HomeScreenChat from "./HomeScreenChatInterface/HomeScreenChat";
import "./HomeScreen.css";

const HomeScreen: React.FC = () => {
  const [isSidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [activeNav, setActiveNav] = useState<string>("home");
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    // Check if user has a theme preference in localStorage
    const savedTheme = localStorage.getItem("theme");
    return (
      savedTheme === "dark" ||
      (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches)
    );
  });

  // Simulated user info
  const userName = useMemo(() => {
    try {
      const user = localStorage.getItem("user");
      if (user) {
        const u = JSON.parse(user);
        return u.full_name || u.email || "User";
      }
    } catch (error) {
      console.error("Failed to parse user from localStorage:", error);
    }
    return "User";
  }, []);

  useEffect(() => {
    // Smooth theme transition
    document.body.style.transition =
      "background-color 0.3s ease, color 0.3s ease";

    if (isDarkMode) {
      document.body.classList.add("dark-theme");
      localStorage.setItem("theme", "dark");
    } else {
      document.body.classList.remove("dark-theme");
      localStorage.setItem("theme", "light");
    }

    // Clean up transition after apply
    const timer = setTimeout(() => {
      document.body.style.transition = "";
    }, 300);

    return () => clearTimeout(timer);
  }, [isDarkMode]);

  const toggleSidebar = () => setSidebarOpen((s) => !s);
  const toggleTheme = () => setIsDarkMode((prev) => !prev);

  const handleNavChange = (nav: string) => {
    setActiveNav(nav);
  };

  // Render different content based on activeNav
  const renderContent = () => {
    switch (activeNav) {
      case "home":
        return <HomeScreenChat />;
      case "profile":
        return <ProfileCard userName={userName} />;
      case "settings":
        return (
          <SettingsCard toggleTheme={toggleTheme} isDarkMode={isDarkMode} />
        );
      default:
        return <HomeScreenChat />;
    }
  };

  return (
    <div
      className={`hs-app ${
        isSidebarOpen ? "sidebar-open" : "sidebar-collapsed"
      }`}
    >
      <Toaster
        position="top-right"
        toastOptions={{
          className: "hs-toast",
          duration: 3000,
          style: {
            background: isDarkMode ? "var(--hs-surface)" : "#fff",
            color: isDarkMode ? "var(--hs-ink)" : "#333",
            border: isDarkMode ? "1px solid var(--hs-border)" : "none",
            boxShadow: "var(--hs-shadow-2)",
          },
        }}
      />

      <HomeScreenSidebar
        isSidebarOpen={isSidebarOpen}
        toggleSidebar={toggleSidebar}
        activeNav={activeNav}
        setActiveNav={handleNavChange}
      />

      <main className="hs-main">
        <header className="hs-topbar">
          <div className="hs-left">
            <button
              className="hs-icon-btn hs-icon-btn--ghost show-mobile"
              onClick={toggleSidebar}
              aria-label="Toggle sidebar"
            >
              <FiMenu />
            </button>
            <h1 className="hs-title">Welcome, {userName}</h1>
          </div>
          <div className="hs-right">
            <button
              className="hs-icon-btn"
              onClick={toggleTheme}
              aria-label="Toggle theme"
            >
              {isDarkMode ? <FiSun /> : <FiMoon />}
            </button>
          </div>
        </header>

        {renderContent()}
      </main>
    </div>
  );
};

// Profile Card Component
const ProfileCard: React.FC<{ userName: string }> = ({ userName }) => {
  const userEmail = useMemo(() => {
    try {
      const user = localStorage.getItem("user");
      if (user) {
        const u = JSON.parse(user);
        return u.email || "No email found";
      }
    } catch (error) {
      console.error("Failed to parse user from localStorage:", error);
    }
    return "No email found";
  }, []);

  return (
    <div className="hs-content-card profile-card">
      <div className="hs-card-header">
        <div className="hs-card-icon">
          <FiUser size={20} />
        </div>
        <h2>Profile Information</h2>
      </div>
      <div className="hs-card-content">
        <div className="hs-info-grid">
          <div className="hs-info-item">
            <div className="hs-info-label">
              <FiUser size={18} />
              <span>Full Name</span>
            </div>
            <div className="hs-info-value">{userName}</div>
          </div>

          <div className="hs-info-item">
            <div className="hs-info-label">
              <FiMail size={18} />
              <span>Email</span>
            </div>
            <div className="hs-info-value">{userEmail}</div>
          </div>

          <div className="hs-info-item">
            <div className="hs-info-label">
              <FiCalendar size={18} />
              <span>Member Since</span>
            </div>
            <div className="hs-info-value">January 2024</div>
          </div>

          <div className="hs-info-item">
            <div className="hs-info-label">
              <FiHash size={18} />
              <span>User ID</span>
            </div>
            <div className="hs-info-value">
              #USR-{Math.random().toString(36).substr(2, 9).toUpperCase()}
            </div>
          </div>
        </div>

        <div className="hs-card-actions">
          <button className="hs-btn hs-btn--primary hs-btn--with-icon">
            <FiEdit2 size={16} />
            <span>Edit Profile</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// Settings Card Component
const SettingsCard: React.FC<{
  toggleTheme: () => void;
  isDarkMode: boolean;
}> = ({ toggleTheme, isDarkMode }) => {
  return (
    <div className="hs-content-card settings-card">
      <div className="hs-card-header">
        <div className="hs-card-icon">
          <FiSettings size={20} />
        </div>
        <h2>Settings & Preferences</h2>
      </div>
      <div className="hs-card-content">
        <div className="hs-settings-grid">
          <div className="hs-setting-card">
            <div className="hs-setting-icon">
              <FiMoon size={20} />
            </div>
            <div className="hs-setting-content">
              <h3>Theme Preference</h3>
              <p>Choose between light and dark mode</p>
            </div>
            <button
              className="hs-btn hs-btn--outline hs-btn--small"
              onClick={toggleTheme}
            >
              {isDarkMode ? "Light Mode" : "Dark Mode"}
            </button>
          </div>

          <div className="hs-setting-card">
            <div className="hs-setting-icon">
              <FiBell size={20} />
            </div>
            <div className="hs-setting-content">
              <h3>Notifications</h3>
              <p>Manage your alert preferences</p>
            </div>
            <button className="hs-btn hs-btn--outline hs-btn--small">
              Configure
            </button>
          </div>

          <div className="hs-setting-card">
            <div className="hs-setting-icon">
              <FiShield size={20} />
            </div>
            <div className="hs-setting-content">
              <h3>Privacy & Security</h3>
              <p>Control your data and privacy settings</p>
            </div>
            <button className="hs-btn hs-btn--outline hs-btn--small">
              Manage
            </button>
          </div>

          <div className="hs-setting-card">
            <div className="hs-setting-icon">
              <FiGlobe size={20} />
            </div>
            <div className="hs-setting-content">
              <h3>Language & Region</h3>
              <p>Set your preferred language</p>
            </div>
            <select className="hs-select hs-select--small">
              <option>English</option>
              <option>Spanish</option>
              <option>French</option>
              <option>German</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;
