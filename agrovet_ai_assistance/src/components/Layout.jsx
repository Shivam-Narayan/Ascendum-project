import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
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
    <div className="flex min-h-screen bg-gradient-to-br from-green-50 via-white to-amber-50">
      {/* Sidebar */}
      <div className="w-80 bg-white shadow-xl border-r border-green-100">
        <div className="p-6">
          {/* Welcome Message */}
          <div className="mb-6 p-4 bg-green-100 rounded-lg border border-green-200">
            <div className="flex items-center space-x-2 text-green-800">
              <User size={18} />
              <span className="text-sm font-medium">Welcome {user?.name}!</span>
            </div>
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="mb-6 px-4 py-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200 flex items-center space-x-2"
          >
            <LogOut size={16} />
            <span>Logout</span>
          </button>

          {/* Navigation */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Navigation</h3>
            
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 flex items-center space-x-3 ${
                    isActive 
                      ? 'bg-green-100 text-green-800 border border-green-200 shadow-sm' 
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
                  }`}
                >
                  <Icon size={18} />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
};

export default Layout;