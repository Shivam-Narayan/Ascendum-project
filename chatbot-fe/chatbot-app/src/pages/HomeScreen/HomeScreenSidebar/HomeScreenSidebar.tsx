import type React from "react"
import { useState } from "react"
import {
  FiChevronRight,
  FiLogOut,
  FiUser,
  FiSettings,
  FiHome,
  FiTrash2,
  FiPlus,
} from "react-icons/fi"
import "./HomeScreenSidebar.css"

const NAV_ITEMS = [
  { key: "home", label: "Home", icon: FiHome },
  { key: "profile", label: "Profile", icon: FiUser },
  { key: "settings", label: "Settings", icon: FiSettings },
]

interface HomeScreenSidebarProps {
  isSidebarOpen: boolean
  toggleSidebar: () => void
  activeNav: string
  setActiveNav: (nav: string) => void
}

const HomeScreenSidebar: React.FC<HomeScreenSidebarProps> = ({
  isSidebarOpen,
  toggleSidebar,
  activeNav,
  setActiveNav
}) => {
  const [hsShowLogoutConfirm, setHsShowLogoutConfirm] = useState(false)

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    window.location.href = "/login"
  }

  const clearChat = () => {
    console.log("Clear chat")
  }

  const startNewChat = () => {
    console.log("Starting new chat")
    // Add your new chat logic here
  }

  return (
    <>
      <aside className={`hs-sidebar ${isSidebarOpen ? "open" : "collapsed"}`} aria-label="Sidebar navigation">
        <div className="hs-sidebar__header">
          <button
            className="hs-sidebar-toggle"
            onClick={toggleSidebar}
            aria-label={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            <FiChevronRight className={`hs-toggle-icon ${isSidebarOpen ? "open" : ""}`} />
            {isSidebarOpen && <div className="hs-brand">Assistant</div>}
          </button>
        </div>

        {isSidebarOpen && (
          <div className="hs-new-chat-section">
            <button className="hs-btn hs-btn--primary hs-new-chat-btn" onClick={startNewChat}>
              <FiPlus className="hs-new-chat-icon" />
              <span>New Chat</span>
            </button>
          </div>
        )}

        <nav className="hs-nav">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            const active = activeNav === item.key
            return (
              <button
                key={item.key}
                className={`hs-nav__item ${active ? "active" : ""}`}
                onClick={() => setActiveNav(item.key)}
              >
                <Icon className="hs-nav__icon" />
                {isSidebarOpen && <span className="hs-nav__label">{item.label}</span>}
              </button>
            )
          })}
        </nav>

        <div className="hs-sidebar__spacer" />

        <div className="hs-sidebar__footer">
          {isSidebarOpen && (
            <button className="hs-btn hs-btn--ghost" onClick={clearChat}>
              <FiTrash2 />
              <span className="label">Clear chat</span>
            </button>
          )}
          <button className="hs-btn hs-btn--danger" onClick={() => setHsShowLogoutConfirm(true)}>
            <FiLogOut />
            {isSidebarOpen && <span className="label">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Logout Confirmation Modal */}
      {hsShowLogoutConfirm && (
        <div className="hs-logout-modal-backdrop">
          <div className="hs-logout-modal">
            <h3 className="hs-logout-modal__title">Confirm Logout</h3>
            <p className="hs-logout-modal__text">Are you sure you want to log out?</p>
            <div className="hs-logout-modal__actions">
              <button
                className="hs-btn hs-btn--ghost"
                onClick={() => setHsShowLogoutConfirm(false)}
              >
                Cancel
              </button>
              <button
                className="hs-btn hs-btn--danger"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default HomeScreenSidebar