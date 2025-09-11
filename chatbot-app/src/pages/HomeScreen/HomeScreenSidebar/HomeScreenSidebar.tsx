import type React from "react";
import { useState, useMemo } from "react";
import {
  FiChevronRight,
  FiLogOut,
  FiUser,
  FiSettings,
  FiHome,
  FiTrash2,
  FiPlus,
  FiMessageSquare,
  FiChevronDown,
  FiChevronUp,
  FiDatabase,
} from "react-icons/fi";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import {
  format,
  isToday,
  isYesterday,
  differenceInCalendarDays,
} from "date-fns";
import "./HomeScreenSidebar.css";

interface ChatSession {
  id: string;
  title: string;
  createdAt: number;
  lastMessage?: string;
}

const NAV_ITEMS = [
  { key: "home", label: "Home", icon: FiHome },
  { key: "profile", label: "Profile", icon: FiUser },
  { key: "settings", label: "Settings", icon: FiSettings },
  { key: "database", label: "Database", icon:FiDatabase},
];

interface HomeScreenSidebarProps {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  activeNav: string;
  setActiveNav: (nav: string) => void;
  chatSessions: ChatSession[];
  setActiveChat: (id: string) => void;
  createNewChat: () => void;
  clearChat: () => void;
  activeChatId: string;
}

const HomeScreenSidebar: React.FC<HomeScreenSidebarProps> = ({
  isSidebarOpen,
  toggleSidebar,
  activeNav,
  setActiveNav,
  chatSessions,
  setActiveChat,
  createNewChat,
  clearChat,
  activeChatId,
}) => {
  const [hsShowLogoutConfirm, setHsShowLogoutConfirm] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [isChatHistoryCollapsed, setIsChatHistoryCollapsed] = useState(false);

  const handleLogout = () => {
    setIsLoggingOut(true);
    setTimeout(() => {
      localStorage.clear();
      window.location.href = "/login";
    }, 500);
  };

  // Date group label helper
  const getDateGroupLabel = (date: Date): string => {
    if (isToday(date)) return "Today";
    if (isYesterday(date)) return "Yesterday";

    const diff = differenceInCalendarDays(new Date(), date);
    if (diff < 7) return "This Week";
    if (diff < 14) return "Last Week";

    return format(date, "MMMM d, yyyy");
  };

  // Group chats by date of creation
  const groupedChats = useMemo(() => {
    const withDates = chatSessions.map((chat) => ({
      ...chat,
      createdDate: new Date(chat.createdAt),
    }));

    // Sort by newest first
    withDates.sort(
      (a, b) => b.createdDate.getTime() - a.createdDate.getTime()
    );

    // Group into buckets
    return withDates.reduce(
      (groups: Record<string, typeof withDates>, chat) => {
        const label = getDateGroupLabel(chat.createdDate);
        if (!groups[label]) groups[label] = [];
        groups[label].push(chat);
        return groups;
      },
      {}
    );
  }, [chatSessions]);

  // Truncate preview text
  const truncate = (text: string, length = 30) =>
    text.length > length ? text.slice(0, length) + "..." : text;

  return (
    <>
      <aside
        className={`hs-sidebar ${isSidebarOpen ? "open" : "collapsed"}`}
        aria-label="Sidebar navigation"
      >
        <div className="hs-sidebar__header">
          <div className="hs-brand">
            <img src="/logo.ico" alt="Company Logo" className="hs-brand__logo" />
            {isSidebarOpen && <span>Assistant</span>}
          </div>
          <button
            className="hs-sidebar-toggle"
            onClick={toggleSidebar}
            aria-label={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            <FiChevronRight
              className={`hs-toggle-icon ${isSidebarOpen ? "open" : ""}`}
            />
          </button>
        </div>

        <div className="hs-new-chat-section">
          <button
            className="hs-btn hs-btn--primary hs-new-chat-btn"
            onClick={createNewChat}
          >
            <FiPlus className="hs-new-chat-icon" />
            {isSidebarOpen && (
              <span className="hs-new-chat-label">New Chat</span>
            )}
          </button>
        </div>

        <nav className="hs-nav">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = activeNav === item.key;
            return (
              <button
                key={item.key}
                className={`hs-nav__item ${active ? "active" : ""}`}
                onClick={() => setActiveNav(item.key)}
              >
                <Icon className="hs-nav__icon" />
                {isSidebarOpen && (
                  <span className="hs-nav__label">{item.label}</span>
                )}
              </button>
            );
          })}
        </nav>

        {isSidebarOpen && (
          <div className="hs-chat-history">
            <div className="hs-chat-history__header">
              <h3>Chat History</h3>
              <button
                className="hs-chat-history__toggle"
                onClick={() => setIsChatHistoryCollapsed(!isChatHistoryCollapsed)}
                aria-label={isChatHistoryCollapsed ? "Expand chat history" : "Collapse chat history"}
              >
                {isChatHistoryCollapsed ? <FiChevronDown /> : <FiChevronUp />}
              </button>
            </div>
            {!isChatHistoryCollapsed && (
              <div className="hs-chat-history__list">
                {Object.keys(groupedChats).length === 0 ? (
                  <div className="hs-no-chats">No chats yet</div>
                ) : (
                  Object.entries(groupedChats).map(([label, chats]) => (
                    <div key={label} className="hs-chat-group">
                      <div className="hs-chat-group__label">{label}</div>
                      {chats.map((chat) => (
                        <button
                          key={chat.id}
                          className={`hs-chat-item ${
                            chat.id === activeChatId ? "active" : ""
                          }`}
                          onClick={() => setActiveChat(chat.id)}
                        >
                          <FiMessageSquare className="hs-chat-item__icon" />
                          <div className="hs-chat-item__content">
                            <div className="hs-chat-item__title">{chat.title}</div>
                            {chat.lastMessage && (
                              <div className="hs-chat-item__preview">
                                {truncate(chat.lastMessage)}
                              </div>
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}

        <div className="hs-sidebar__spacer" />

        <div className="hs-sidebar__footer">
          <button
            className="hs-btn hs-btn--ghost"
            onClick={clearChat}
            aria-label="Clear chat"
          >
            <FiTrash2 />
            {isSidebarOpen && <span className="label">Clear chat</span>}
          </button>

          <button
            className="hs-btn hs-btn--danger"
            onClick={() => setHsShowLogoutConfirm(true)}
            aria-label="Logout"
          >
            <FiLogOut />
            {isSidebarOpen && <span className="label">Logout</span>}
          </button>
        </div>
      </aside>

      {hsShowLogoutConfirm && (
        <div className="hs-logout-modal-backdrop">
          <div className="hs-logout-modal">
            <h3 className="hs-logout-modal__title">Confirm Logout</h3>
            <p className="hs-logout-modal__text">
              Are you sure you want to log out?
            </p>
            <div className="hs-logout-modal__actions">
              <button
                className="hs-btn hs-btn--ghost"
                disabled={isLoggingOut}
                onClick={() => setHsShowLogoutConfirm(false)}
              >
                Cancel
              </button>
              <button
                className="hs-btn hs-btn--danger"
                onClick={handleLogout}
                disabled={isLoggingOut}
              >
                {isLoggingOut ? (
                  <>
                    <AiOutlineLoading3Quarters className="spin-icon" />
                    Logging out...
                  </>
                ) : (
                  <>
                    <FiLogOut />
                    Logout
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default HomeScreenSidebar;