import type React from "react";
import { useEffect, useRef, useState } from "react";
import {
  FiPaperclip,
  FiEdit2,
  FiCopy,
  FiDownload,
  FiSend,
  FiX,
  FiLoader,
  FiCheck,
  FiUser,
  FiThumbsUp,
  FiThumbsDown,
} from "react-icons/fi";
import { FiFileText } from "react-icons/fi";
import { FaFilePdf, FaFileWord, FaFileExcel, FaFileCsv } from "react-icons/fa";
import { FaRobot } from "react-icons/fa";
import "./HomeScreenChat.css";
import { uploadFile } from "../../../services/FileUploadApi";
import { askDocument } from "../../../services/QueryApi";
import {
  uploadExcelOrCsv,
  type ExcelUploadResponse,
} from "../../../services/ExcelUploadApi";
import { askDataset } from "../../../services/QueryExcelApi";
import { askGeneral } from "../../../services/GeneralQuery";
import type { ExcelRow } from "../../../services/ExcelUploadApi";
import {
  uploadMultipleFiles,
  type MultipleFileUploadResponse,
} from "../../../services/MultipleUploadApi";
import { askMultipleDocuments } from "../../../services/QueryMultipleApi";

type Role = "user" | "bot";

type Attachment = {
  id: string;
  name: string;
  size: number;
  type: string;
};

type Feedback = "liked" | "disliked" | null;

type Message = {
  id: string;
  role: Role;
  text: string;
  createdAt: number;
  attachments?: Attachment[];
  isEditing?: boolean;
  excelData?: ExcelUploadResponse;
  multipleDocumentsData?: MultipleFileUploadResponse;
  replyTo?: string;
  feedback?: Feedback;
};

const formatTime12Hour = (timestamp: number): string => {
  const date = new Date(timestamp);
  let hours = date.getHours();
  const minutes = date.getMinutes();
  const seconds = date.getSeconds();
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'

  const pad = (num: number) => num.toString().padStart(2, "0");

  return `${pad(hours)}:${pad(minutes)}:${pad(seconds)} ${ampm}`;
};

function formatBytes(bytes: number) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${
    sizes[i]
  }`;
}

function downloadText(text: string, filename = "response.txt") {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ---------- RESPONSE CLEANERS ----------
function formatDatasetAnswer(raw: string): string {
  let formatted = raw.replace(/^Answer:\s*/i, "").trim();
  formatted = formatted.replace(/Confidence:.*\n?/gi, "");
  formatted = formatted.replace(/Method:.*\n?/gi, "");
  const sentences = formatted
    .split(/[.\n]/)
    .map((s) => s.trim())
    .filter(Boolean);
  if (sentences.length > 1) {
    return sentences[0] + "...";
  }
  return formatted;
}

const ACCEPTED_MIME = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "text/csv",
];

const ACCEPTED_EXT = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv"];

interface HomeScreenChatProps {
  messages: Message[];
  updateMessages: (messages: Message[]) => void;
  isNewChat: boolean;
}

const HomeScreenChat: React.FC<HomeScreenChatProps> = ({
  messages,
  updateMessages,
  isNewChat,
}) => {
  const [input, setInput] = useState<string>("");
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [sending, setSending] = useState<boolean>(false);
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "info";
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const typingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const shouldSendFilesRef = useRef<boolean>(false);
  const getFileIcon = (type: string, name: string) => {
    if (type === "application/pdf" || name.endsWith(".pdf"))
      return <FaFilePdf className="hs-attachment__icon pdf" />;
    if (
      type === "application/msword" ||
      type ===
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
      name.endsWith(".doc") ||
      name.endsWith(".docx")
    )
      return <FaFileWord className="hs-attachment__icon word" />;
    if (
      type === "application/vnd.ms-excel" ||
      type ===
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
      name.endsWith(".xls") ||
      name.endsWith(".xlsx")
    )
      return <FaFileExcel className="hs-attachment__icon excel" />;
    if (type === "text/csv" || name.endsWith(".csv"))
      return <FaFileCsv className="hs-attachment__icon csv" />;
    return <FiFileText className="hs-attachment__icon" />;
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    return () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }
    };
  }, []);

  // New useEffect to handle automatic sending when files are selected
  useEffect(() => {
    if (shouldSendFilesRef.current && pendingFiles.length > 0) {
      sendMessage();
      shouldSendFilesRef.current = false;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingFiles]);

  const showToast = (message: string, type: "success" | "info" = "info") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleFeedback = (messageId: string, feedback: Feedback) => {
    const updatedMessages = messages.map((m) =>
      m.id === messageId ? { ...m, feedback } : m
    );
    updateMessages(updatedMessages);

    // Show toast notification
    if (feedback === "liked") {
      showToast("Thanks for your feedback! 👍", "success");
    } else {
      showToast("Thanks for your feedback! We'll try to improve. 👎", "info");
    }
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const handleFilesSelected: React.ChangeEventHandler<HTMLInputElement> = (
    e
  ) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    const filtered = files.filter(
      (f) =>
        ACCEPTED_MIME.includes(f.type) ||
        ACCEPTED_EXT.some((ext) => f.name.toLowerCase().endsWith(ext))
    );

    if (filtered.length === 0) return;

    // Set files and mark that we should send them
    setPendingFiles(filtered);
    shouldSendFilesRef.current = true;

    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removePendingFile = (name: string) => {
    setPendingFiles((prev) => prev.filter((f) => f.name !== name));
  };

  const sendMessage = async () => {
    if (isTyping || sending) return;

    const text = input.trim();
    if (!text && pendingFiles.length === 0) return;
    setSending(true);

    const attachments: Attachment[] = pendingFiles.map((f) => ({
      id: `${f.name}-${f.size}-${f.lastModified}`,
      name: f.name,
      size: f.size,
      type: f.type,
    }));

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      text,
      createdAt: Date.now(),
      attachments: attachments.length ? attachments : undefined,
    };

    const updatedMessages = [...messages, userMsg];
    updateMessages(updatedMessages);
    setInput("");
    autoResize(true);

    const botId = crypto.randomUUID();
    const botMsg: Message = {
      id: botId,
      role: "bot",
      text: "",
      createdAt: Date.now(),
    };

    updateMessages([...updatedMessages, botMsg]);

    let responseText = "";
    let excelData: ExcelUploadResponse | undefined;
    let multipleDocumentsData: MultipleFileUploadResponse | undefined;

    try {
      if (pendingFiles.length > 0) {
        // Check if we're uploading multiple files (more than 1)
        if (pendingFiles.length > 1) {
          const token = localStorage.getItem("token") || "";
          if (!token) {
            throw new Error("Please login to upload multiple files");
          }

          const response = await uploadMultipleFiles(pendingFiles, token);
          if (response.documents_id) {
            localStorage.setItem(
              "multiple_documents_id",
              response.documents_id
            );
            localStorage.removeItem("batch_id");
            localStorage.removeItem("dataset_id");
            multipleDocumentsData = response;

            // Format success message with file details
            const successFiles = response.details.filter(
              (d) => d.status === "success"
            );
            const errorFiles = response.details.filter(
              (d) => d.status === "error"
            );

            responseText = `📚 ${successFiles.length} file(s) uploaded successfully!\n\n`;

            if (successFiles.length > 0) {
              responseText += "Uploaded files:\n";
              successFiles.forEach((file) => {
                responseText += `• ${file.filename} (${file.file_type})\n`;
              });
            }

            if (errorFiles.length > 0) {
              responseText += `\n❌ ${errorFiles.length} file(s) failed to upload:\n`;
              errorFiles.forEach((file) => {
                responseText += `• ${file.filename}: ${
                  file.error_message || "Unknown error"
                }\n`;
              });
            }

            responseText += `\nYou can now ask questions about these documents.`;
          }
        } else {
          // Single file upload (existing logic)
          for (const file of pendingFiles) {
            if (
              file.type === "application/pdf" ||
              file.name.endsWith(".pdf") ||
              file.name.endsWith(".doc") ||
              file.name.endsWith(".docx")
            ) {
              const response = await uploadFile(file);
              if (response.pdf_id) {
                localStorage.setItem("batch_id", response.pdf_id);
                localStorage.removeItem("dataset_id");
                localStorage.removeItem("multiple_documents_id");
                responseText =
                  `📄 Your document was uploaded successfully!\n\nNow you can ask things like:\n` +
                  `• What is the main topic of this document?\n` +
                  `• Summarize the key findings.\n` +
                  `• What information is in the tables?\n` +
                  `• What are the main conclusions?`;
              }
            } else if (
              file.type === "text/csv" ||
              file.type === "application/vnd.ms-excel" ||
              file.type ===
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
              file.name.endsWith(".csv") ||
              file.name.endsWith(".xls") ||
              file.name.endsWith(".xlsx")
            ) {
              const token = localStorage.getItem("token") || "";
              const response = await uploadExcelOrCsv(file, token);
              if (response.dataset_id) {
                localStorage.setItem("dataset_id", response.dataset_id);
                localStorage.removeItem("batch_id");
                localStorage.removeItem("multiple_documents_id");
                excelData = response;
                responseText = "Your dataset was uploaded successfully!";
              }
            }
          }
        }
        setPendingFiles([]);
      } else if (text) {
        const datasetId = localStorage.getItem("dataset_id");
        const batchId = localStorage.getItem("batch_id");
        const multipleDocumentsId = localStorage.getItem(
          "multiple_documents_id"
        );

        // Check multiple documents first, then others
        if (multipleDocumentsId) {
          const token = localStorage.getItem("token") || "";
          if (!token) {
            throw new Error("Please login to query multiple documents");
          }
          const answer = await askMultipleDocuments(
            multipleDocumentsId,
            text,
            token
          );
          responseText = answer.answer || "No answer found.";
        } else if (datasetId) {
          const answer = await askDataset(datasetId, text);
          responseText = formatDatasetAnswer(answer.answer);
        } else if (batchId) {
          const answer = await askDocument(batchId, text);
          responseText = answer.answer || "No answer found.";
        } else {
          // General chat
          const token = localStorage.getItem("token") || "";
          if (token) {
            const answer = await askGeneral(text, token);
            responseText = answer.answer || "No response.";
          } else {
            responseText = "⚠️ Please login to continue.";
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        responseText = `Error: ${err.message}`;
      } else {
        responseText = "Error: Unknown error occurred";
      }
    }

    // start typing animation
    setIsTyping(true);
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
    }

    let index = 0;
    typingIntervalRef.current = setInterval(() => {
      index++;
      const updatedBotMessage = {
        ...botMsg,
        text: responseText.slice(0, index),
        createdAt:
          index === responseText.length ? Date.now() : botMsg.createdAt,
        excelData: excelData,
        multipleDocumentsData: multipleDocumentsData,
      };
      updateMessages([...updatedMessages, updatedBotMessage]);

      if (scrollRef.current) {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      }

      if (index >= responseText.length) {
        if (typingIntervalRef.current) {
          clearInterval(typingIntervalRef.current);
          typingIntervalRef.current = null;
        }
        setSending(false);
        setIsTyping(false);
      }
    }, 20);
  };

  const onKeyDownComposer: React.KeyboardEventHandler<HTMLTextAreaElement> = (
    e
  ) => {
    if (isTyping || sending) {
      e.preventDefault();
      return;
    }
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyMessage = async (id: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleEditMessage = (id: string) => {
    const updatedMessages = messages.map((m) =>
      m.id === id && m.role === "user" ? { ...m, isEditing: !m.isEditing } : m
    );
    updateMessages(updatedMessages);
  };

  const reAskAssistant = async (
    userId: string,
    text: string,
    baseMessages: Message[]
  ) => {
    if (!text.trim()) return;

    const botId = crypto.randomUUID();
    const botMsg: Message = {
      id: botId,
      role: "bot",
      text: "",
      createdAt: Date.now(),
      replyTo: userId,
    };
    updateMessages([...baseMessages, botMsg]);

    let responseText = "";

    try {
      const datasetId = localStorage.getItem("dataset_id");
      const batchId = localStorage.getItem("batch_id");
      const multipleDocumentsId = localStorage.getItem("multiple_documents_id");

      // Check multiple documents first, then others
      if (multipleDocumentsId) {
        const token = localStorage.getItem("token") || "";
        if (!token) {
          throw new Error("Please login to query multiple documents");
        }
        const answer = await askMultipleDocuments(
          multipleDocumentsId,
          text,
          token
        );
        responseText = answer.answer || "No answer found.";
      } else if (datasetId) {
        const answer = await askDataset(datasetId, text);
        responseText = formatDatasetAnswer(answer.answer);
      } else if (batchId) {
        const answer = await askDocument(batchId, text);
        responseText = answer.answer || "No answer found.";
      } else {
        const token = localStorage.getItem("token") || "";
        if (token) {
          const answer = await askGeneral(text, token);
          responseText = answer.answer || "No response.";
        } else {
          responseText = "⚠️ Please login to continue.";
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        responseText = `Error fetching answer: ${err.message}`;
      } else {
        responseText = "Error fetching answer: Unknown error";
      }
    }

    // Typing animation (same as your sendMessage)
    setIsTyping(true);
    let index = 0;
    const interval = setInterval(() => {
      index++;
      const updatedBotMessage = {
        ...botMsg,
        text: responseText.slice(0, index),
        createdAt:
          index === responseText.length ? Date.now() : botMsg.createdAt,
      };
      updateMessages([...baseMessages, updatedBotMessage]);

      if (index >= responseText.length) {
        clearInterval(interval);
        setIsTyping(false);
        setSending(false);
      }
    }, 20);
  };

  const commitEditMessage = async (id: string, newText: string) => {
    // 1. Update the user message text
    const updatedMessages = messages.map((m) =>
      m.id === id ? { ...m, text: newText, isEditing: false } : m
    );
    updateMessages(updatedMessages);

    // 2. Remove old bot reply after this message (if any)
    const userIndex = updatedMessages.findIndex((m) => m.id === id);
    const filteredMessages = updatedMessages.filter(
      (m, i) => !(i === userIndex + 1 && m.role === "bot")
    );
    updateMessages(filteredMessages);

    // 3. Trigger assistant again with edited text
    // (reuse sendMessage logic but adapt it to take custom text)
    reAskAssistant(id, newText, filteredMessages);

    setSending(true);
  };

  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const autoResize = (reset = false) => {
    if (textareaRef.current) {
      if (reset) {
        textareaRef.current.style.height = "auto";
      } else {
        textareaRef.current.style.height = "auto"; // reset
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`; // adjust
      }
    }
  };

  const renderBotMessage = (message: Message) => {
    const { text, excelData, multipleDocumentsData } = message;
    const tableRegex = /\|(.+)\|/g;

    // If we have multiple documents data, render the upload summary
    if (multipleDocumentsData) {
      const successFiles = multipleDocumentsData.details.filter(
        (d) => d.status === "success"
      );
      const errorFiles = multipleDocumentsData.details.filter(
        (d) => d.status === "error"
      );

      return (
        <div className="hs-multiple-docs-card">
          <div className="hs-multiple-docs-card__header">
            <span role="img" aria-label="documents">
              📚
            </span>
            <h4>{successFiles.length} file(s) uploaded successfully!</h4>
          </div>

          {successFiles.length > 0 && (
            <>
              <p>
                <strong>Uploaded files:</strong>
              </p>
              <ul className="hs-multiple-docs-list">
                {successFiles.map((file, index) => (
                  <li key={index} className="hs-multiple-docs-item">
                    <span className="hs-multiple-docs-filename">
                      {file.filename}
                    </span>
                    <span className="hs-multiple-docs-type">
                      ({file.file_type})
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}

          {errorFiles.length > 0 && (
            <>
              <p className="hs-multiple-docs-error">
                <strong>❌ {errorFiles.length} file(s) failed:</strong>
              </p>
              <ul className="hs-multiple-docs-error-list">
                {errorFiles.map((file, index) => (
                  <li key={index} className="hs-multiple-docs-error-item">
                    {file.filename}: {file.error_message || "Unknown error"}
                  </li>
                ))}
              </ul>
            </>
          )}

          <p className="hs-multiple-docs-help">
            You can now ask questions about these documents.
          </p>
        </div>
      );
    }

    // If we have Excel data, render the dataset table
    if (excelData) {
      return (
        <div className="hs-dataset-card">
          <h4>Dataset uploaded successfully!</h4>
          <p>
            Rows: {excelData.rows} | Columns: {excelData.columns}
          </p>
          <p>
            <strong>Columns:</strong> {excelData.columns_list.join(", ")}
          </p>

          <div className="hs-table-wrapper">
            <table className="hs-table">
              <thead>
                <tr>
                  {excelData.columns_list.map((col, i) => (
                    <th key={i}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {excelData.sample_data.map((row: ExcelRow, i: number) => (
                  <tr key={i}>
                    {excelData.columns_list.map((col, j) => (
                      <td key={j} data-fulltext={String(row[col] || "")}>
                        {row[col]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    if (text.includes("📄 Your document was uploaded successfully!")) {
      const suggestions = [
        "What is the main topic of this document?",
        "Summarize the key findings.",
        "What information is in the tables?",
        "What are the main conclusions?",
      ];

      return (
        <div className="hs-doc-card">
          <div className="hs-doc-card__header">
            <span role="img" aria-label="document">
              📄
            </span>
            <h4>Document uploaded successfully!</h4>
          </div>
          <p className="hs-doc-card__subtitle">You can ask questions like:</p>

          <div className="hs-doc-card__grid">
            {suggestions.map((q) => (
              <button
                key={q}
                type="button"
                className="hs-doc-card__grid-btn"
                onClick={() => setInput(q)}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      );
    }

    // ✅ If bot response contains a Markdown table, render it properly
    if (tableRegex.test(text)) {
      const lines = text.split("\n").filter((line) => line.startsWith("|"));
      const headers = lines[0]
        .split("|")
        .map((h) => h.trim())
        .filter(Boolean);
      const rows = lines.slice(2).map((line) =>
        line
          .split("|")
          .map((cell) => cell.trim())
          .filter(Boolean)
      );

      return (
        <div className="hs-table-wrapper">
          <table className="hs-table">
            <thead>
              <tr>
                {headers.map((h, i) => (
                  <th key={i}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j} data-fulltext={cell}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // Default: normal text
    return <pre className="hs-text">{text}</pre>;
  };

  return (
    <section className="hs-chat">
      {isNewChat && messages.length === 0 ? (
        <div className="hs-empty">
          <h2 className="hs-empty__title">Welcome to Chat Assistant</h2>
          <p className="hs-empty__subtitle">
            Ask a question or attach a file to get started.
          </p>
        </div>
      ) : (
        <>
          <div ref={scrollRef} className="hs-chat__messages">
            {messages.map((m) => (
              <article
                key={m.id}
                className={`hs-message ${
                  m.role === "user" ? "from-user" : "from-bot"
                }`}
              >
                <div className="hs-avatar">
                  {m.role === "user" ? (
                    <div className="hs-avatar__circle user">
                      <FiUser />
                    </div>
                  ) : (
                    <div className="hs-avatar__circle bot">
                      <FaRobot />
                    </div>
                  )}
                </div>
                <div className="hs-bubble">
                  {m.isEditing ? (
                    <MessageEditor
                      initial={m.text}
                      onCancel={() => toggleEditMessage(m.id)}
                      onSave={(val) => commitEditMessage(m.id, val)}
                    />
                  ) : (
                    <>
                      {m.role === "bot" && !m.text ? (
                        <div className="hs-typing">
                          <span>.</span>
                          <span>.</span>
                          <span>.</span>
                        </div>
                      ) : m.role === "bot" ? (
                        renderBotMessage(m)
                      ) : (
                        <pre className="hs-text">{m.text}</pre>
                      )}
                      {!!m.attachments?.length && (
                        <ul className="hs-attachments">
                          {m.attachments.map((a) => (
                            <li key={a.id} className="hs-attachment">
                              {getFileIcon(a.type, a.name)}
                              <span className="name">{a.name}</span>
                              <span className="size">
                                {formatBytes(a.size)}
                              </span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </>
                  )}
                </div>

                <div className="hs-meta">
                  <span className="hs-meta__who">
                    {m.role === "user" ? "You" : "Assistant"}
                  </span>
                  <span className="hs-meta__time">
                    {formatTime12Hour(m.createdAt)}
                  </span>
                </div>

                <div className="hs-actions">
                  {m.role === "bot" ? (
                    <>
                      <button
                        className="hs-icon-btn"
                        title="Copy"
                        onClick={() => copyMessage(m.id, m.text)}
                        aria-label="Copy response"
                      >
                        {copiedId === m.id ? <FiCheck /> : <FiCopy />}
                      </button>
                      {copiedId === m.id && (
                        <span className="hs-copied-label">Copied!</span>
                      )}
                      <button
                        className="hs-icon-btn"
                        title="Download"
                        onClick={() => downloadText(m.text)}
                        aria-label="Download response"
                      >
                        <FiDownload />
                      </button>
                      {/* Add feedback buttons for bot messages */}
                      <button
                        className={`hs-icon-btn hs-feedback-btn ${
                          m.feedback === "liked" ? "active" : ""
                        }`}
                        title="Helpful"
                        onClick={() => handleFeedback(m.id, "liked")}
                        aria-label="Mark as helpful"
                      >
                        <FiThumbsUp />
                      </button>
                      <button
                        className={`hs-icon-btn hs-feedback-btn ${
                          m.feedback === "disliked" ? "active" : ""
                        }`}
                        title="Not helpful"
                        onClick={() => handleFeedback(m.id, "disliked")}
                        aria-label="Mark as not helpful"
                      >
                        <FiThumbsDown />
                      </button>
                    </>
                  ) : !m.isEditing ? (
                    <button
                      className="hs-icon-btn"
                      title="Edit"
                      onClick={() => toggleEditMessage(m.id)}
                      aria-label="Edit message"
                    >
                      <FiEdit2 />
                    </button>
                  ) : null}
                </div>
              </article>
            ))}
          </div>

          {!!pendingFiles.length && (
            <div className="hs-pending-files" role="status" aria-live="polite">
              {pendingFiles.map((f) => (
                <span className="hs-chip" key={`${f.name}-${f.size}`}>
                  <span className="name" title={f.name}>
                    {f.name}
                  </span>
                  <span className="size">{formatBytes(f.size)}</span>
                  <button
                    className="remove"
                    onClick={() => removePendingFile(f.name)}
                    aria-label={`Remove ${f.name}`}
                  >
                    <FiX />
                  </button>
                </span>
              ))}
            </div>
          )}

          <footer className="hs-composer" aria-label="Message composer">
            <input
              ref={fileInputRef}
              type="file"
              className="hs-hidden-input"
              onChange={handleFilesSelected}
              multiple
              accept={[...ACCEPTED_EXT, ...ACCEPTED_MIME].join(",")}
              aria-hidden
              tabIndex={-1}
            />

            <button
              className="hs-icon-btn"
              onClick={handleAttachClick}
              title="Attach file"
              aria-label="Attach file"
              disabled={isTyping || sending}
            >
              <FiPaperclip />
            </button>

            <textarea
              ref={textareaRef}
              className="hs-input"
              placeholder={
                isTyping || sending
                  ? "Assistant is typing..."
                  : "Type your message"
              }
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                autoResize();
              }}
              onKeyDown={onKeyDownComposer}
              rows={1}
              disabled={isTyping || sending}
            />

            <button
              className="hs-icon-btn hs-btn--primary"
              onClick={sendMessage}
              disabled={
                sending ||
                isTyping ||
                (!input.trim() && pendingFiles.length === 0)
              }
              aria-disabled={
                sending ||
                isTyping ||
                (!input.trim() && pendingFiles.length === 0)
              }
            >
              {sending ? (
                <span className="hs-spinner">
                  <FiLoader />
                </span>
              ) : (
                <FiSend />
              )}
            </button>
          </footer>
        </>
      )}
      {toast && (
        <div className={`hs-toast-feedback hs-toast-feedback--${toast.type}`}>
          {toast.message}
        </div>
      )}
    </section>
  );
};

function MessageEditor({
  initial,
  onCancel,
  onSave,
}: {
  initial: string;
  onCancel: () => void;
  onSave: (val: string) => void;
}) {
  const [val, setVal] = useState(initial);
  return (
    <div className="hs-editor">
      <textarea
        className="hs-editor__input"
        value={val}
        onChange={(e) => setVal(e.target.value)}
        rows={4}
      />
      <div className="hs-editor__actions">
        <button className="hs-btn hs-btn--ghost" onClick={onCancel}>
          Cancel
        </button>
        <button className="hs-btn hs-btn--primary" onClick={() => onSave(val)}>
          Save
        </button>
      </div>
    </div>
  );
}

export default HomeScreenChat;
