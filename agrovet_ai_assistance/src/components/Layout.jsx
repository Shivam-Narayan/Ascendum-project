// import React from 'react';
// import { useNavigate, useLocation } from 'react-router-dom';
// import { useAuth } from '../contexts/AuthContext';
// import './Layout.css';
// import { 
//   Home, 
//   Sprout, 
//   Bug, 
//   Cherry, 
//   Apple,
//   Grape,
//   TestTube,
//   LogOut,
//   User
// } from 'lucide-react';

// const Layout = ({ children }) => {
//   const navigate = useNavigate();
//   const location = useLocation();
//   const { user, logout } = useAuth();

//   const menuItems = [
//     { path: '/dashboard', label: 'Home', icon: Home },
//     { path: '/soil-nutrition', label: 'Soil Nutrition', icon: TestTube },
//     { path: '/plant-disease', label: 'Plant Disease Identification', icon: Sprout },
//     { path: '/cotton-pests', label: 'Cotton Pests Identification', icon: Bug },
//     { path: '/tomato-ripeness', label: 'Tomato Ripeness Detection', icon: Cherry },
//     { path: '/banana-ripeness', label: 'Banana Ripeness Detection', icon: Apple },
//     { path: '/mango-ripeness', label: 'Mango Ripeness Detection', icon: Grape },
//   ];

//   const handleLogout = () => {
//     logout();
//     navigate('/login');
//   };

//   return (
//     <div className="layout-container">
//       {/* Sidebar */}
//       <div className="sidebar">
//         <div className="sidebar-content">
//           {/* Welcome Message */}
//           <div className="welcome-message">
//             <div className="welcome-text">
//               <User size={18} />
//               <span className="welcome-name">Welcome {user?.name}!</span>
//             </div>
//           </div>

//           {/* Logout Button */}
//           <button
//             onClick={handleLogout}
//             className="logout-button"
//           >
//             <LogOut size={16} />
//             <span>Logout</span>
//           </button>

//           {/* Navigation */}
//           <div className="navigation">
//             <h3 className="navigation-title">Navigation</h3>
            
//             {menuItems.map((item) => {
//               const Icon = item.icon;
//               const isActive = location.pathname === item.path;
              
//               return (
//                 <button
//                   key={item.path}
//                   onClick={() => navigate(item.path)}
//                   className={`nav-item ${isActive ? 'nav-item-active' : ''}`}
//                 >
//                   <Icon size={18} />
//                   <span className="nav-item-label">{item.label}</span>
//                 </button>
//               );
//             })}
//           </div>
//         </div>
//       </div>

//       {/* Main Content */}
//       <div className="main-content">
//         {children}
//       </div>
//     </div>
//   );
// };

// export default Layout;
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Layout.css';
import { 
  Home, 
  Sprout, 
  Bug, 
  Cherry, 
  Apple,
  Grape,
  TestTube,
  LogOut,
  User
} from 'lucide-react';

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { path: '/dashboard', label: 'Home', icon: Home },
    { path: '/soil-nutrition', label: 'Soil Nutrition', icon: TestTube },
    { path: '/plant-disease', label: 'Plant Disease Identification', icon: Sprout },
    { path: '/cotton-pests', label: 'Cotton Pests Identification', icon: Bug },
    { path: '/tomato-ripeness', label: 'Tomato Ripeness Detection', icon: Cherry },
    { path: '/banana-ripeness', label: 'Banana Ripeness Detection', icon: Apple },
    { path: '/mango-ripeness', label: 'Mango Ripeness Detection', icon: Grape },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout-container">
      {/* Sidebar - Fixed */}
      <div className="sidebar">
        <div className="sidebar-content">
          {/* Welcome Message */}
          <div className="welcome-message">
            <div className="welcome-text">
              <User size={18} />
              <span className="welcome-name">Welcome {user?.name}!</span>
            </div>
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="logout-button"
          >
            <LogOut size={16} />
            <span>Logout</span>
          </button>

          {/* Navigation */}
          <div className="navigation">
            <h3 className="navigation-title">Navigation</h3>
            
            <div className="nav-items-container">
              {menuItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <button
                    key={item.path}
                    onClick={() => navigate(item.path)}
                    className={`nav-item ${isActive ? 'nav-item-active' : ''}`}
                  >
                    <Icon size={18} />
                    <span className="nav-item-label">{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Scrollable */}
      <div className="main-content">
        <div className="main-content-inner">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;