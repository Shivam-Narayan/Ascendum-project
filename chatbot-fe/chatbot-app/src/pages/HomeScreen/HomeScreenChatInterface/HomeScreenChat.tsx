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
} from "react-icons/fi";
import "./HomeScreenChat.css";
import { uploadFile } from "../../../services/FileUploadApi";
import { askDocument } from "../../../services/QueryApi";
import { uploadExcelOrCsv } from "../../../services/ExcelUploadApi";
import { askDataset } from "../../../services/QueryExcelApi";

type Role = "user" | "bot";

type Attachment = {
  id: string;
  name: string;
  size: number;
  type: string;
};

type Message = {
  id: string;
  role: Role;
  text: string;
  createdAt: number;
  attachments?: Attachment[];
  isEditing?: boolean;
};

function formatBytes(bytes: number) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
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
  // Remove "Answer:" prefix if present
  let formatted = raw.replace(/^Answer:\s*/i, "").trim();

  // Remove confidence/method lines
  formatted = formatted.replace(/Confidence:.*\n?/gi, "");
  formatted = formatted.replace(/Method:.*\n?/gi, "");

  // Optional summarization: keep only first sentence
  const sentences = formatted.split(/[.\n]/).map((s) => s.trim()).filter(Boolean);
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

const HomeScreenChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [sending, setSending] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const handleFilesSelected: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    const filtered = files.filter(
      (f) =>
        ACCEPTED_MIME.includes(f.type) ||
        ACCEPTED_EXT.some((ext) => f.name.toLowerCase().endsWith(ext))
    );
    setPendingFiles((prev) => [...prev, ...filtered]);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removePendingFile = (name: string) => {
    setPendingFiles((prev) => prev.filter((f) => f.name !== name));
  };

  const sendMessage = async () => {
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

    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    // placeholder bot message
    const botId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      { id: botId, role: "bot", text: "", createdAt: Date.now() },
    ]);

    let responseText = "";

    try {
      if (pendingFiles.length > 0) {
        for (const file of pendingFiles) {
          // Handle PDF/Doc
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
              responseText =
                `📄 Your document was uploaded successfully!\n\nNow you can ask things like:\n` +
                `• What is the main topic of this document?\n` +
                `• Summarize the key findings.\n` +
                `• What information is in the tables?\n` +
                `• What are the main conclusions?`;
            }
          }
          // Handle Excel/CSV
          else if (
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
              responseText =
                `Your dataset was uploaded successfully!\n\n` +
                `Rows: ${response.rows}\n` +
                `Columns: ${response.columns}\n\n` +
                `Columns: ${response.columns_list.join(", ")}`;
            }
          }
        }
        setPendingFiles([]);
      } else if (text) {
        const datasetId = localStorage.getItem("dataset_id");
        const batchId = localStorage.getItem("batch_id");

        if (datasetId) {
          const answer = await askDataset(datasetId, text);
          responseText = formatDatasetAnswer(answer.answer);
        } else if (batchId) {
          const answer = await askDocument(batchId, text);
          responseText = answer.answer || "No answer found.";
        } else {
          responseText =
            "⚠️ No document or dataset uploaded yet. Please upload a file before asking questions.";
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        responseText = `Error fetching answer: ${err.message}`;
      } else {
        responseText = "Error fetching answer: Unknown error";
      }
    }

    // typing animation
    let index = 0;
    const typingInterval = setInterval(() => {
      index++;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === botId ? { ...m, text: responseText.slice(0, index), createdAt: index === 1 ? Date.now() : m.createdAt, } : m
        )
      );
      if (index >= responseText.length) {
        clearInterval(typingInterval);
        setSending(false);
      }
    }, 20);
  };

  const onKeyDownComposer: React.KeyboardEventHandler<HTMLTextAreaElement> = (
    e
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyMessage = async (text: string) => {
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
  };

  const toggleEditMessage = (id: string) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === id && m.role === "user" ? { ...m, isEditing: !m.isEditing } : m
      )
    );
  };

  const commitEditMessage = (id: string, newText: string) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === id ? { ...m, text: newText, isEditing: false } : m
      )
    );
  };

  return (
    <section className="hs-chat">
      <div ref={scrollRef} className="hs-chat__messages">
        {messages.length === 0 ? (
          <div className="hs-empty">
            <h2 className="hs-empty__title">Welcome to Chat Assistant</h2>
            <p className="hs-empty__subtitle">
              Ask a question or attach a file to get started.
            </p>
          </div>
        ) : (
          messages.map((m) => (
            <article
              key={m.id}
              className={`hs-message ${
                m.role === "user" ? "from-user" : "from-bot"
              }`}
            >
              <div className="hs-bubble">
                {m.isEditing ? (
                  <MessageEditor
                    initial={m.text}
                    onCancel={() => toggleEditMessage(m.id)}
                    onSave={(val) => commitEditMessage(m.id, val)}
                  />
                ) : (
                  <>
                    <pre className="hs-text">
                      {m.role === "bot" && !m.text ? (
                        <div className="hs-typing">
                          <span>.</span>
                          <span>.</span>
                          <span>.</span>
                        </div>
                      ) : (
                        <pre className="hs-text">{m.text}</pre>
                      )}
                    </pre>
                    {!!m.attachments?.length && (
                      <ul className="hs-attachments">
                        {m.attachments.map((a) => (
                          <li key={a.id} className="hs-attachment">
                            <span className="name">{a.name}</span>
                            <span className="size">{formatBytes(a.size)}</span>
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
                  {new Date(m.createdAt).toLocaleTimeString()}
                </span>
              </div>

              <div className="hs-actions">
                {m.role === "bot" ? (
                  <>
                    <button
                      className="hs-icon-btn"
                      title="Copy"
                      onClick={() => copyMessage(m.text)}
                      aria-label="Copy response"
                    >
                      <FiCopy />
                    </button>
                    <button
                      className="hs-icon-btn"
                      title="Download"
                      onClick={() => downloadText(m.text)}
                      aria-label="Download response"
                    >
                      <FiDownload />
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
          ))
        )}
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
        >
          <FiPaperclip />
        </button>

        <textarea
          className="hs-input"
          placeholder="Type your message... (Shift+Enter for new line)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDownComposer}
          rows={1}
        />

        <button
          className="hs-icon-btn hs-btn--primary"
          onClick={sendMessage}
          disabled={sending || (!input.trim() && pendingFiles.length === 0)}
          aria-disabled={sending || (!input.trim() && pendingFiles.length === 0)}
        >
          {sending ? <FiLoader className="hs-spin" /> : <FiSend />}
        </button>
      </footer>
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
