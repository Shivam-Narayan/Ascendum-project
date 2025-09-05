import type React from "react";
import { useEffect, useMemo, useState } from "react";
import {
  FiMoon,
  FiSun,
  FiMenu,
  FiUser,
  FiSettings,
  FiEdit2,
  FiShield,
  FiGlobe,
  FiCalendar,
  FiFileText,
  FiChevronRight,
} from "react-icons/fi";
import { FiMail } from "react-icons/fi";
import { Toaster } from "react-hot-toast";
import HomeScreenSidebar from "./HomeScreenSidebar/HomeScreenSidebar";
import HomeScreenChat from "./HomeScreenChatInterface/HomeScreenChat";
import "./HomeScreen.css";
// import type { UserHistoryItem, ChatHistoryItem } from "../../types/chat";
import { getProfile, type Profile } from "../../services/ProfileApi";
import { changePassword } from "../../services/ChangePasswordApi";
import toast from "react-hot-toast";
import { FiEye, FiEyeOff } from "react-icons/fi";
import ReactMarkdown from "react-markdown";

interface ChatSession {
  id: string;
  title: string;
  createdAt: number;
  lastMessage?: string;
  messages: Message[];
  type?: string;
  metadata?: unknown;
}

type Message = {
  id: string;
  role: "user" | "bot";
  text: string;
  createdAt: number;
  attachments?: Attachment[];
  isEditing?: boolean;
};

type Attachment = {
  id: string;
  name: string;
  size: number;
  type: string;
};

const HomeScreen: React.FC = () => {
  const [isSidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [activeNav, setActiveNav] = useState<string>("home");
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    const savedTheme = localStorage.getItem("theme");
    return savedTheme === "dark";
  });

  // Initialize chat sessions state with proper check
  const [chatSessions, setChatSessions] = useState<ChatSession[]>(() => {
    try {
      const saved = localStorage.getItem("chatSessions");
      if (saved) {
        const parsed = JSON.parse(saved);
        return Array.isArray(parsed) && parsed.length > 0 ? parsed : [];
      }
    } catch {
      // If there's an error parsing, return empty array
    }
    return [];
  });

  const [activeChatId, setActiveChatId] = useState<string>(() => {
    return localStorage.getItem("activeChatId") || "";
  });

  // Only migrate non-blank chats from userHistory (NEW LOGIC)
  useEffect(() => {
  try {
    const savedUserHistory = localStorage.getItem("userHistory");
    const savedChatSessions = localStorage.getItem("chatSessions");

    let sessions: ChatSession[] = [];

    // First: restore from chatSessions (most recent user data)
    if (savedChatSessions) {
      const parsed = JSON.parse(savedChatSessions);
      if (Array.isArray(parsed) && parsed.length > 0) {
        sessions = parsed;
      }
    }

    // Second: import userHistory only if no chatSessions exist
    if (sessions.length === 0 && savedUserHistory) {
      const userHistory: { role: string; message: string; timestamp: string }[] =
        JSON.parse(savedUserHistory);

      // Convert userHistory into a single ChatSession
      const messages: Message[] = userHistory
        .map((item) => ({
          id: crypto.randomUUID(),
          role: (item.role === "user" ? "user" : "bot") as "user" | "bot",
          text: item.message || "",
          createdAt: item.timestamp
            ? new Date(item.timestamp).getTime()
            : Date.now(),
        }))
        .filter((msg) => msg.text && msg.text.trim() !== "");

      if (messages.length > 0) {
        const firstUserMessage = messages.find((msg) => msg.role === "user");
        const title = firstUserMessage
          ? firstUserMessage.text.slice(0, 30) +
            (firstUserMessage.text.length > 30 ? "..." : "")
          : "Imported Chat";

        const importedChat: ChatSession = {
          id: crypto.randomUUID(),
          title,
          createdAt: Date.now(),
          messages,
        };
        sessions = [importedChat];
      }
    }

    // Last resort: create a new empty chat
    if (sessions.length === 0) {
      const newChat: ChatSession = {
        id: crypto.randomUUID(),
        title: "New Chat",
        createdAt: Date.now(),
        messages: [],
      };
      sessions = [newChat];
    }

    setChatSessions(sessions);
    setActiveChatId(sessions[0].id);
  } catch (error) {
    console.error("Error initializing chat sessions:", error);
    // Fallback to a new chat if something goes wrong
    const newChat: ChatSession = {
      id: crypto.randomUUID(),
      title: "New Chat",
      createdAt: Date.now(),
      messages: [],
    };
    setChatSessions([newChat]);
    setActiveChatId(newChat.id);
  }
}, []);

  // Get active chat
  const activeChat = useMemo(() => {
    return chatSessions.find((chat) => chat.id === activeChatId) || null;
  }, [chatSessions, activeChatId]);

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
    // Save chat sessions to localStorage whenever they change
    localStorage.setItem("chatSessions", JSON.stringify(chatSessions));
  }, [chatSessions]);

  useEffect(() => {
    // Save active chat ID to localStorage
    if (activeChatId) {
      localStorage.setItem("activeChatId", activeChatId);
    }
  }, [activeChatId]);

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

  // Create a new chat session
  const createNewChat = () => {
    // Check if the active chat is already new chat (empty or titled "New Chat")
    const activeChat = chatSessions.find((chat) => chat.id === activeChatId);
    if (
      activeChat &&
      (activeChat.title === "New Chat" || activeChat.messages.length === 0)
    ) {
      // Optionally show a toast or just do nothing
      toast("You are already on a new chat.");
      return;
    }

    // Otherwise, create new chat as before
    const newChat: ChatSession = {
      id: crypto.randomUUID(),
      title: "New Chat",
      createdAt: Date.now(),
      messages: [],
    };

    setChatSessions((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
    setActiveNav("home");
  };

  // Set active chat
  const setActiveChat = (id: string) => {
    setChatSessions((prev) =>
      prev.map((chat) =>
        chat.id === id ? { ...chat, createdAt: Date.now() } : chat
      )
    );
    setActiveChatId(id);
    setActiveNav("home");
  };

  // Update chat with new messages
  const updateChatMessages = (chatId: string, messages: Message[]) => {
    setChatSessions((prev) =>
      prev.map((chat) => {
        if (chat.id === chatId) {
          const lastMessage =
            messages.length > 0
              ? messages[messages.length - 1].text
              : undefined;

          return {
            ...chat,
            messages,
            lastMessage,
            title:
              messages.length > 0
                ? messages[0].text.slice(0, 30) +
                  (messages[0].text.length > 30 ? "..." : "")
                : "New Chat",
          };
        }
        return chat;
      })
    );
  };

  // Clear current chat
  const clearChat = () => {
    if (activeChatId) {
      setChatSessions((prev) =>
        prev.map((chat) =>
          chat.id === activeChatId
            ? {
                ...chat,
                messages: [],
                lastMessage: undefined,
                title: "New Chat",
              }
            : chat
        )
      );
    }
  };

  // Render different content based on activeNav
  const renderContent = () => {
    switch (activeNav) {
      case "home":
        return (
          <HomeScreenChat
            messages={activeChat?.messages || []}
            updateMessages={(messages) => {
              if (activeChatId) {
                updateChatMessages(activeChatId, messages);
              }
            }}
            isNewChat={!activeChatId}
          />
        );
      case "profile":
        return <ProfileCard />;
      case "settings":
        return (
          <SettingsCard toggleTheme={toggleTheme} isDarkMode={isDarkMode} />
        );
      default:
        return (
          <HomeScreenChat
            messages={activeChat?.messages || []}
            updateMessages={(messages) => {
              if (activeChatId) {
                updateChatMessages(activeChatId, messages);
              }
            }}
            isNewChat={!activeChatId}
          />
        );
    }
  };

  // Updated greeting function to include color
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return { text: "Good Morning,", color: "#f59e0b" }; // orange
    if (hour < 17) return { text: "Good Afternoon,", color: "#22c55e" }; // green
    if (hour < 21) return { text: "Good Evening,", color: "#0ea5e9" }; // blue
    return { text: "Good Night,", color: "#8b5cf6" }; // purple
  };

  const greeting = getGreeting();

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
        chatSessions={chatSessions}
        setActiveChat={setActiveChat}
        createNewChat={createNewChat}
        clearChat={clearChat}
        activeChatId={activeChatId}
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
            <h1 className="hs-title">{activeChat?.title || "New Chat"}</h1>
          </div>

          <div
            className="hs-right"
            style={{ display: "flex", alignItems: "center", gap: "8px" }}
          >
            {/* Greeting Text (not clickable) */}
            <span
              className="hs-greeting"
              style={{
                color: greeting.color,
                fontWeight: 500,
                cursor: "default",
              }}
            >
              {greeting.text}
            </span>

            {/* Username (clickable) */}
            <button
              className="hs-username"
              onClick={() => handleNavChange("profile")}
            >
              {userName}
            </button>

            {/* Theme Toggle */}
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

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = date.getFullYear();
  return `${day}-${month}-${year}`;
};

// Profile Card Component
const ProfileCard: React.FC = () => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  const [showChangePassword, setShowChangePassword] = useState(false);
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getProfile();
        setProfile(data);
      } catch (err) {
        console.error("Failed to load profile:", err);
        toast.error("Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleChangePassword = async () => {
    if (!oldPassword || !newPassword || !confirmPassword) {
      toast.error("All fields are required");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await changePassword({
        old_password: oldPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      if (result.error) {
        toast.error(result.error);
      } else {
        toast.success("Password changed successfully");
        setShowChangePassword(false);
        setOldPassword("");
        setNewPassword("");
        setConfirmPassword("");
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error(err.message);
      } else {
        toast.error("Something went wrong");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="hs-content-card profile-card">
        <div className="hs-card-header">
          <div className="hs-card-icon">
            <FiUser size={20} />
          </div>
          <h2>Profile Information</h2>
        </div>
        <div className="hs-card-content">Loading...</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="hs-content-card profile-card">
        <div className="hs-card-header">
          <div className="hs-card-icon">
            <FiUser size={20} />
          </div>
          <h2>Profile Information</h2>
        </div>
        <div className="hs-card-content">Failed to load profile.</div>
      </div>
    );
  }

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
            <div className="hs-info-value">{profile.full_name}</div>
          </div>

          <div className="hs-info-item">
            <div className="hs-info-label">
              <FiMail size={18} />
              <span>Email</span>
            </div>
            <div className="hs-info-value">{profile.email}</div>
          </div>
        </div>

        <div className="hs-info-item">
          <div className="hs-info-label">
            <FiCalendar size={18} />
            <span>Registered At</span>
          </div>
          <div className="hs-info-value">
            {formatDate(profile.registered_at)}
          </div>
        </div>

        <div className="hs-card-actions">
          <button
            className="hs-btn hs-btn--primary hs-btn--with-icon"
            onClick={() => setShowChangePassword(true)}
          >
            <FiEdit2 size={16} />
            <span>Change Password</span>
          </button>
        </div>

        {/* Change Password Modal */}
        {showChangePassword && (
          <div className="hs-logout-modal-backdrop">
            <div className="hs-logout-modal">
              <h3 className="hs-logout-modal__title">Change Password</h3>

              <div className="hs-logout-modal__content hs-password-form">
                {/* Old Password */}
                <div className="hs-input-wrapper">
                  <input
                    type={showOldPassword ? "text" : "password"}
                    placeholder="Old Password"
                    value={oldPassword}
                    onChange={(e) => setOldPassword(e.target.value)}
                    className="hs-input"
                  />
                  <button
                    type="button"
                    className="hs-eye-btn"
                    onClick={() => setShowOldPassword((prev) => !prev)}
                  >
                    {showOldPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>

                {/* New Password */}
                <div className="hs-input-wrapper">
                  <input
                    type={showNewPassword ? "text" : "password"}
                    placeholder="New Password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="hs-input"
                  />
                  <button
                    type="button"
                    className="hs-eye-btn"
                    onClick={() => setShowNewPassword((prev) => !prev)}
                  >
                    {showNewPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>

                {/* Confirm Password */}
                <div className="hs-input-wrapper">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Confirm Password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="hs-input"
                  />
                  <button
                    type="button"
                    className="hs-eye-btn"
                    onClick={() => setShowConfirmPassword((prev) => !prev)}
                  >
                    {showConfirmPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>
              </div>

              <div className="hs-logout-modal__actions">
                <button
                  className="hs-btn hs-btn--ghost"
                  onClick={() => setShowChangePassword(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  className="hs-btn hs-btn--primary"
                  onClick={handleChangePassword}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Changing..." : "Change Password"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Settings Card Component (Mobile-Friendly Version)
const SettingsCard: React.FC<{
  toggleTheme: () => void;
  isDarkMode: boolean;
}> = ({ toggleTheme, isDarkMode }) => {
  const [agreementText, setAgreementText] = useState<string>("");
  const [showAgreement, setShowAgreement] = useState(false);
  const [showPrivacy, setShowPrivacy] = useState(false);

  // Load agreement text from assets
  const loadAgreement = async () => {
    try {
      const response = await fetch("../../../src/assets/agreement.md");
      const text = await response.text();
      setAgreementText(text);
      setShowAgreement(true);
      document.body.style.overflow = "hidden";
    } catch {
      toast.error("Failed to load agreement");
    }
  };

  // Close modal and restore scrolling
  const closeModal = () => {
    setShowAgreement(false);
    setShowPrivacy(false);
    document.body.style.overflow = "auto";
  };

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
          {/* Theme Toggle */}
          <div className="hs-setting-card">
            <div className="hs-setting-icon">
              <FiMoon size={20} />
            </div>
            <div className="hs-setting-content">
              <h3>Dark Mode</h3>
              <p>Switch between light and dark theme</p>
            </div>
            <label className="hs-toggle-switch">
              <input
                type="checkbox"
                checked={isDarkMode}
                onChange={toggleTheme}
              />
              <span className="hs-toggle-slider"></span>
            </label>
          </div>

          {/* Agreement Button */}
          <div className="hs-setting-card" onClick={loadAgreement}>
            <div className="hs-setting-icon">
              <FiFileText size={20} />
            </div>
            <div className="hs-setting-content">
              <h3>User Agreement</h3>
              <p>View terms and conditions</p>
            </div>
            <div className="hs-setting-action">
              <FiChevronRight size={20} />
            </div>
          </div>

          {/* Privacy Button */}
          <div
            className="hs-setting-card"
            onClick={() => {
              setShowPrivacy(true);
              document.body.style.overflow = "hidden";
            }}
          >
            <div className="hs-setting-icon">
              <FiShield size={20} />
            </div>
            <div className="hs-setting-content">
              <h3>Privacy & Security</h3>
              <p>Manage your data settings</p>
            </div>
            <div className="hs-setting-action">
              <FiChevronRight size={20} />
            </div>
          </div>

          {/* Language Selector */}
          <div
            className="hs-setting-card opacity-60 cursor-not-allowed"
            onClick={() =>
              toast("This feature will be available in production", {
                icon: "⚠️",
              })
            }
          >
            <div className="hs-setting-icon">
              <FiGlobe size={20} />
            </div>
            <div className="hs-setting-content">
              <h3>Language</h3>
              <p>Select preferred language</p>
            </div>
            <div className="hs-dropdown-wrapper">
              <select
                className="hs-dropdown bg-gray-200 text-gray-500"
                disabled
              >
                <option value="en">English</option>
                <option value="es">Español</option>
                <option value="fr">Français</option>
                <option value="de">Deutsch</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Privacy & Security Modal */}
      {showPrivacy && (
        <div className="hs-modal-backdrop" onClick={closeModal}>
          <div
            className={`hs-modal-card ${
              isDarkMode ? "hs-dark-bg" : "hs-light-bg"
            }`}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="hs-modal-title">Privacy & Security</h2>
            <div className="hs-modal-content">
              <p>
                This chatbot application ensures complete confidentiality of the
                documents you upload. All your files are securely processed
                within the system and no external parties, including developers
                or administrators, can access or read your documents.
              </p>
              <p>
                Our security measures include encryption of data at rest and in
                transit, strict access control, and adherence to data protection
                standards. Your privacy is fully respected and protected at all
                times.
              </p>
            </div>
            <div className="hs-modal-actions">
              <button className="hs-btn hs-btn--primary" onClick={closeModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Agreement Modal */}
      {showAgreement && (
        <div className="hs-modal-backdrop" onClick={closeModal}>
          <div
            className={`hs-modal-card ${
              isDarkMode ? "hs-dark-bg" : "hs-light-bg"
            }`}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="hs-modal-title">
              END USER LICENSE AGREEMENT (EULA)
            </h2>

            <div className="hs-modal-content">
              <ReactMarkdown>{agreementText}</ReactMarkdown>
            </div>

            <div className="hs-modal-actions">
              <button className="hs-btn hs-btn--primary" onClick={closeModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomeScreen;
