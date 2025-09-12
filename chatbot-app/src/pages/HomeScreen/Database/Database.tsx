import React, { useState, useEffect, useCallback } from "react";
import type { ReactElement } from "react";
import {
  FiDatabase,
  FiUpload,
  FiSend,
  FiUser,
  FiMessageSquare,
  FiChevronDown,
  FiChevronUp,
  FiRefreshCw,
  FiTrash2,
  FiCopy,
  FiDownload,
  FiThumbsUp,
  FiThumbsDown,
} from "react-icons/fi";
import toast from "react-hot-toast";
import "./Database.css";
import { uploadDatabaseFile } from "../../../services/DatabaseUpload";
import type { UploadError } from "../../../services/DatabaseUpload";
import { queryDocument } from "../../../services/DatabaseQueryApi";
import type {
  QueryResponse,
  QueryError,
} from "../../../services/DatabaseQueryApi";
import type { QueryResult } from "../../../services/DatabaseQueryApi";
import {
  getUploadedDocuments,
  type UploadedDocument,
} from "../../../services/DatabaseDocuments";

interface ChatMessage {
  role: string;
  content: string;
  timestamp: Date;
  results?: QueryResult[];
}

interface DatabaseFile {
  id: string;
  name: string;
  type: string;
  uploadedAt: string;
  size: string;
  documentId?: string;
}

// Helper function to serialize Date objects for localStorage
const serializeMessage = (message: ChatMessage) => ({
  ...message,
  timestamp: message.timestamp.toISOString(),
});

// Helper function to deserialize Date objects from localStorage
const deserializeMessage = (message: {
  role: string;
  content: string;
  timestamp: string;
  results?: QueryResult[];
}): ChatMessage => ({
  ...message,
  timestamp: new Date(message.timestamp),
  results: message.results || undefined,
});

const Database: React.FC = () => {
  const [files, setFiles] = useState<DatabaseFile[]>([]);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isFetchingDocuments, setIsFetchingDocuments] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const savedMessages = localStorage.getItem("databaseMessages");
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        return parsedMessages.map(deserializeMessage);
      } catch (error) {
        console.error("Failed to parse saved messages:", error);
        return [];
      }
    }
    return [];
  });

  const [isFilesCollapsed, setIsFilesCollapsed] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [showClearChatConfirm, setShowClearChatConfirm] = useState(false);
  const [showClearFilesConfirm, setShowClearFilesConfirm] = useState(false);

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success("Copied to clipboard!");
    } catch (err) {
      console.error("Failed to copy: ", err);
      toast.error("Failed to copy to clipboard");
    }
  };

  const downloadAsTxt = (content: string, filename: string) => {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${filename}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Downloaded as text file!");
  };

  const handleFeedback = (isPositive: boolean) => {
    if (isPositive) {
      toast.success("Thanks for your positive feedback! 👍");
    } else {
      toast("Thanks for your feedback! We'll improve. 👎");
    }
  };

  // Convert uploaded document to DatabaseFile format
  const convertToDatabaseFile = useCallback(
    (doc: UploadedDocument): DatabaseFile => {
      return {
        id: doc.document_id,
        name: doc.filename,
        type: doc.file_type.toUpperCase(),
        uploadedAt: new Date(doc.uploaded_at).toLocaleDateString(),
        size: "Unknown size",
        documentId: doc.document_id,
      };
    },
    []
  );

  // Fetch uploaded documents from backend
  const fetchUploadedDocuments = useCallback(
    async (showToast: boolean = true) => {
      setIsFetchingDocuments(true);
      try {
        const response = await getUploadedDocuments();
        const databaseFiles = response.documents.map(convertToDatabaseFile);
        setFiles(databaseFiles);

        localStorage.setItem("databaseFiles", JSON.stringify(databaseFiles));

        if (showToast && databaseFiles.length > 0) {
          toast.success(
            `Loaded ${databaseFiles.length} document(s) from database`
          );
        }
      } catch (error) {
        console.error("Failed to fetch uploaded documents:", error);
        if (showToast) toast.error("Failed to load documents from database");
      } finally {
        setIsFetchingDocuments(false);
      }
    },
    [convertToDatabaseFile]
  );

  // Load persisted state and fetch latest docs on mount
  useEffect(() => {
    const savedFiles = localStorage.getItem("databaseFiles");
    if (savedFiles) {
      try {
        setFiles(JSON.parse(savedFiles));
      } catch (error) {
        console.error("Failed to parse saved files:", error);
      }
    }

    const savedMessages = localStorage.getItem("databaseMessages");
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        setMessages(parsedMessages.map(deserializeMessage));
      } catch (error) {
        console.error("Failed to parse saved messages:", error);
      }
    }

    const savedUIConfig = localStorage.getItem("databaseUIConfig");
    if (savedUIConfig) {
      try {
        const uiConfig = JSON.parse(savedUIConfig);
        setIsFilesCollapsed(uiConfig.isFilesCollapsed || false);
        setSelectedFile(uiConfig.selectedFile || null);
      } catch (error) {
        console.error("Failed to parse saved UI config:", error);
      }
    }

    // 👇 disable toast on initial mount
    fetchUploadedDocuments(false);
  }, [fetchUploadedDocuments]);

  // Save all state to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem("databaseFiles", JSON.stringify(files));
  }, [files]);

  useEffect(() => {
    localStorage.setItem(
      "databaseMessages",
      JSON.stringify(messages.map(serializeMessage))
    );
  }, [messages]);

  useEffect(() => {
    const uiConfig = {
      isFilesCollapsed,
      selectedFile,
    };
    localStorage.setItem("databaseUIConfig", JSON.stringify(uiConfig));
  }, [isFilesCollapsed, selectedFile]);

  // Helper functions for rendering content with tables
  const renderTextLines = (lines: string[]): ReactElement[] => {
    return lines.map((line, index) => <p key={`text-${index}`}>{line}</p>);
  };

  // Helper function to render a table from markdown lines
  const renderTable = (tableLines: string[]): ReactElement => {
    // Clean up the table lines
    const cleanedLines = tableLines.map((line) =>
      line
        .trim()
        .replace(/^\||\|$/g, "")
        .trim()
    );

    // Check if we have a separator row (usually the second row with ---)
    const hasSeparator =
      cleanedLines.length > 1 &&
      cleanedLines[1]
        .split("|")
        .some((cell) => cell.trim().replace(/[-:]/g, "").trim() === "");

    const headerRowIndex = hasSeparator ? 0 : -1;
    const dataStartIndex = hasSeparator ? 2 : 0;

    // Parse headers
    const headers = cleanedLines[headerRowIndex >= 0 ? headerRowIndex : 0]
      .split("|")
      .map((cell) => cell.trim())
      .filter((cell) => cell !== "");

    // Parse data rows
    const rows = cleanedLines
      .slice(dataStartIndex)
      .filter((row) => row.split("|").some((cell) => cell.trim() !== ""))
      .map((row) =>
        row
          .split("|")
          .map((cell) => cell.trim())
          .filter((cell) => cell !== "")
      )
      .filter((row) => row.length > 0);

    return (
      <div
        key={`table-${Date.now()}-${Math.random()}`}
        className="Database-markdownTable"
      >
        <table>
          {hasSeparator && (
            <thead>
              <tr>
                {headers.map((header, index) => (
                  <th key={index}>{header}</th>
                ))}
              </tr>
            </thead>
          )}
          <tbody>
            {(!hasSeparator ? [headers, ...rows] : rows).map(
              (row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => {
                    // For tables without separators, treat the first row as header
                    if (!hasSeparator && rowIndex === 0) {
                      return <th key={cellIndex}>{cell}</th>;
                    }
                    return <td key={cellIndex}>{cell}</td>;
                  })}
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>
    );
  };

  const renderContentWithTables = (content: string): ReactElement => {
    const lines = content.split("\n");
    const elements: ReactElement[] = [];
    let currentTable: string[] = [];
    let inTable = false;
    let currentText: string[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Check if this line looks like a table row (contains multiple pipes)
      if (line.includes("|") && line.split("|").length > 2) {
        if (!inTable) {
          // If we have accumulated text, add it as paragraphs
          if (currentText.length > 0) {
            elements.push(...renderTextLines(currentText));
            currentText = [];
          }
          inTable = true;
        }
        currentTable.push(line);
      } else {
        if (inTable) {
          // We were in a table, now we're not - render the table
          if (currentTable.length > 0) {
            elements.push(renderTable(currentTable));
            currentTable = [];
          }
          inTable = false;
        }

        // Accumulate text lines
        if (line.trim()) {
          currentText.push(line);
        } else if (currentText.length > 0) {
          // Empty line - flush the accumulated text
          elements.push(...renderTextLines(currentText));
          currentText = [];
        }
      }
    }

    // Handle any remaining content after the loop
    if (inTable && currentTable.length > 0) {
      elements.push(renderTable(currentTable));
    }

    if (currentText.length > 0) {
      elements.push(...renderTextLines(currentText));
    }

    return elements.length > 0 ? <>{elements}</> : <p>{content}</p>;
  };

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const fileList = event.target.files;
    if (!fileList || fileList.length === 0) return;

    const validExtensions = [".pdf", ".doc", ".docx", ".csv", ".xlsx"];
    const validFiles: File[] = [];
    const invalidFiles: string[] = [];

    // Validate all files first
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      const fileExtension = file.name
        .toLowerCase()
        .substring(file.name.lastIndexOf("."));

      if (!validExtensions.includes(fileExtension)) {
        invalidFiles.push(file.name);
      } else {
        validFiles.push(file);
      }
    }

    // Show error for invalid files
    if (invalidFiles.length > 0) {
      toast.error(
        `Invalid file type(s): ${invalidFiles.join(
          ", "
        )}. Please upload valid database files (PDF, Word, Excel, CSV)`
      );
    }

    if (validFiles.length === 0) return;

    setIsUploading(true);

    try {
      // Process all valid files
      for (const file of validFiles) {
        try {
          const response = await uploadDatabaseFile(file);
          const fileExtension = file.name
            .toLowerCase()
            .substring(file.name.lastIndexOf("."));

          if (response.status === "ok" && response.documents.length > 0) {
            const uploadedDocument = response.documents[0];

            const newFile: DatabaseFile = {
              id:
                Date.now().toString() + Math.random().toString(36).substr(2, 9),
              name: file.name,
              type: fileExtension.replace(".", "").toUpperCase(),
              uploadedAt: new Date().toLocaleDateString(),
              size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
              documentId: uploadedDocument.document_id,
            };

            setFiles((prev) => [newFile, ...prev]);

            const successMessage: ChatMessage = {
              role: "assistant",
              content: `Database file "${file.name}" has been uploaded successfully! You can now ask questions about this database.`,
              timestamp: new Date(),
            };
            setMessages((prev) => [...prev, successMessage]);
          } else {
            throw new Error("Upload failed: Invalid response from server");
          }
        } catch (error: unknown) {
          console.error(`Upload error for ${file.name}:`, error);

          let uploadError: UploadError = {
            error: "Upload failed",
            details: "Please try again.",
          };

          if (typeof error === "object" && error !== null && "error" in error) {
            uploadError = error as UploadError;
          } else if (error instanceof Error) {
            uploadError = { error: error.message };
          }

          const errorMessage: ChatMessage = {
            role: "assistant",
            content: `Failed to upload file ${file.name}: ${
              uploadError.error
            }. ${uploadError.details || "Please try again."}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
        }
      }

      if (validFiles.length > 0) {
        toast.success(`Uploaded ${validFiles.length} file(s) successfully`);

        // Refresh the document list from backend after upload
        fetchUploadedDocuments();
      }
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  };

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);

    const userMessage: ChatMessage = {
      role: "user",
      content: query,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response: QueryResponse = await queryDocument(
        query,
        selectedFile || undefined
      );

      const aiResponse: ChatMessage = {
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
        results: response.results,
      };

      setMessages((prev) => [...prev, aiResponse]);
      toast.success("Query processed successfully");
    } catch (error: unknown) {
      console.error("Query error:", error);

      let queryError: QueryError = {
        error: "Query failed",
        details: "Please try again.",
      };

      if (typeof error === "object" && error !== null && "error" in error) {
        queryError = error as QueryError;
      } else if (error instanceof Error) {
        queryError = { error: error.message };
      }

      toast.error(queryError.error || "Failed to process query");

      const errorMessage: ChatMessage = {
        role: "assistant",
        content: `Failed to process query: ${queryError.error}. ${
          queryError.details || "Please try again."
        }`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setQuery("");
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const clearFiles = () => {
    setShowClearFilesConfirm(true);
  };

  const confirmClearFiles = () => {
    setFiles([]);
    setSelectedFile(null);
    localStorage.removeItem("databaseFiles");
    setShowClearFilesConfirm(false);
    toast.success("All files cleared from view");
  };

  const clearChat = () => {
    setShowClearChatConfirm(true);
  };

  const confirmClearChat = () => {
    setMessages([]);
    localStorage.removeItem("databaseMessages");
    setShowClearChatConfirm(false);
    toast.success("Chat history cleared");
  };

  const refreshFiles = () => {
    fetchUploadedDocuments();
  };

  const formatResults = (results: QueryResult[]) => {
    if (!results || results.length === 0) return null;

    return (
      <div className="Database-results">
        <h5>Search Results ({results.length} found):</h5>
        {results.slice(0, 3).map((result, index) => (
          <div key={index} className="Database-resultItem">
            <div className="Database-resultContent">
              <strong>{result.metadata.filename}</strong> (Page{" "}
              {result.page + 1})<p>{result.content}</p>
              <small>Score: {(result.score * 100).toFixed(1)}% match</small>
            </div>
          </div>
        ))}
        {results.length > 3 && (
          <div className="Database-resultMore">
            <small>...and {results.length - 3} more results</small>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="Database-card">
      <div className="Database-header">
        <div className="Database-headerIcon">
          <FiDatabase size={20} />
        </div>
        <h2>Database Query</h2>
        <div className="Database-actions">
          <button
            className={`Database-refreshBtn ${
              isFetchingDocuments ? "Database-refreshBtn--loading" : ""
            }`}
            onClick={refreshFiles}
            title="Refresh documents from database"
            disabled={isFetchingDocuments}
          >
            {isFetchingDocuments ? (
              <div className="Database-refreshSpinner"></div>
            ) : (
              <FiRefreshCw size={16} />
            )}
          </button>
          <label
            className={`Database-uploadBtn ${
              isUploading ? "Database-uploadBtn--loading" : ""
            }`}
            title="Upload database file"
            htmlFor="database-file-input"
          >
            {isUploading ? (
              <div className="Database-uploadSpinner"></div>
            ) : (
              <FiUpload size={16} />
            )}
            <input
              id="database-file-input"
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.csv,.xlsx"
              onChange={handleFileUpload}
              className="Database-fileInput"
              disabled={isUploading}
            />
          </label>
        </div>
      </div>

      <div className="Database-content">
        {/* File list - Collapsible */}
        {files.length > 0 && (
          <div className="Database-files">
            <div className="Database-filesHeader">
              <h4>Available Documents ({files.length})</h4>
              <div className="Database-filesActions">
                <button
                  className="Database-collapseBtn"
                  onClick={() => setIsFilesCollapsed(!isFilesCollapsed)}
                  title={isFilesCollapsed ? "Expand files" : "Collapse files"}
                >
                  {isFilesCollapsed ? <FiChevronDown /> : <FiChevronUp />}
                </button>
                <button
                  className="Database-clearFilesBtn"
                  onClick={clearFiles}
                  title="Clear all files from view"
                >
                  Clear
                </button>
              </div>
            </div>
            {!isFilesCollapsed && (
              <div className="Database-filesList">
                {files.map((file) => (
                  <div
                    key={file.id}
                    className={`Database-fileItem ${
                      selectedFile === file.name
                        ? "Database-fileItem--selected"
                        : ""
                    }`}
                    onClick={() =>
                      setSelectedFile(
                        selectedFile === file.name ? null : file.name
                      )
                    }
                  >
                    <div className="Database-fileInfo">
                      <div className="Database-fileName">
                        {file.name}
                        {selectedFile === file.name && (
                          <span className="Database-fileSelectedBadge">
                            Selected
                          </span>
                        )}
                      </div>
                      <div className="Database-fileMeta">
                        <span className="Database-fileType">{file.type}</span>
                        <span className="Database-fileSize">{file.size}</span>
                        <span className="Database-fileDate">
                          {file.uploadedAt}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* File selection info */}
        {selectedFile && (
          <div className="Database-selectionInfo">
            <small>
              Querying only: <strong>{selectedFile}</strong>
            </small>
            <button
              onClick={() => setSelectedFile(null)}
              className="Database-clearSelectionBtn"
            >
              Clear selection
            </button>
          </div>
        )}

        {/* Chat interface container */}
        <div className="Database-chatContainer">
          <div className="Database-chat">
            <div className="Database-chatHeader">
              <h4>Chat</h4>
              {messages.length > 0 && (
                <button
                  className="Database-clearChatBtn"
                  onClick={clearChat}
                  title="Clear chat history"
                >
                  <FiTrash2 size={14} />
                  Clear Chat
                </button>
              )}
            </div>
            <div className="Database-messages">
              {messages.length === 0 ? (
                <div className="Database-emptyChat">
                  <FiDatabase size={48} />
                  <p>Query documents from the database</p>
                  <small>Supported formats: PDF, Word, Excel, CSV</small>
                  {files.length > 0 && (
                    <small>Click on a file to query specific documents</small>
                  )}
                </div>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={index}
                    className={`Database-message Database-message--${message.role}`}
                  >
                    <div className="Database-messageHeader">
                      <div className="Database-messageIcon">
                        {message.role === "user" ? (
                          <FiUser size={14} />
                        ) : (
                          <FiMessageSquare size={14} />
                        )}
                      </div>
                      <span className="Database-messageRole">
                        {message.role === "user" ? "You" : "Assistant"}
                      </span>
                      <span className="Database-messageTime">
                        {formatTime(message.timestamp)}
                      </span>
                    </div>
                    <div className="Database-messageContent">
                      {renderContentWithTables(message.content)}
                      {message.results && formatResults(message.results)}

                      {/* Add action buttons for assistant messages */}
                      {message.role === "assistant" && (
                        <div className="Database-messageActions">
                          <button
                            className="Database-actionBtn"
                            onClick={() => copyToClipboard(message.content)}
                            title="Copy response"
                          >
                            <FiCopy size={12} />
                          </button>
                          <button
                            className="Database-actionBtn"
                            onClick={() =>
                              downloadAsTxt(
                                message.content,
                                `response-${index + 1}`
                              )
                            }
                            title="Download as text file"
                          >
                            <FiDownload size={12} />
                          </button>
                          <button
                            className="Database-feedbackBtn thumbsUp"
                            onClick={() => handleFeedback(true)}
                            title="Helpful response"
                          >
                            <FiThumbsUp size={12} />
                          </button>
                          <button
                            className="Database-feedbackBtn thumbsDown"
                            onClick={() => handleFeedback(false)}
                            title="Not helpful"
                          >
                            <FiThumbsDown size={12} />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="Database-message Database-message--assistant">
                  <div className="Database-messageHeader">
                    <div className="Database-messageIcon">
                      <FiMessageSquare size={14} />
                    </div>
                    <span className="Database-messageRole">Assistant</span>
                    <span className="Database-messageTime">
                      {formatTime(new Date())}
                    </span>
                  </div>
                  <div className="Database-messageContent Database-messageContent--loading">
                    <div className="Database-typingIndicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Query input */}
            <form className="Database-queryForm" onSubmit={handleQuerySubmit}>
              <div className="Database-inputContainer">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && e.shiftKey) {
                      e.preventDefault();
                      setQuery(query + "\n");
                    } else if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleQuerySubmit(e);
                    }
                  }}
                  placeholder={
                    selectedFile
                      ? `Ask about ${selectedFile}...`
                      : "Ask a question about your database..."
                  }
                  disabled={isLoading || isUploading || files.length === 0}
                  className="Database-queryInput"
                  rows={1}
                  style={{ resize: "vertical" }}
                />
                <button
                  type="submit"
                  disabled={
                    isLoading ||
                    isUploading ||
                    !query.trim() ||
                    files.length === 0
                  }
                  className="Database-sendButton"
                >
                  <FiSend size={18} />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      {showClearChatConfirm && (
        <div className="Database-confirmModal">
          <div className="Database-confirmModalContent">
            <h3>Clear Chat History</h3>
            <p>Are you sure you want to clear the chat history?</p>
            <div className="Database-confirmModalActions">
              <button
                className="Database-confirmModalBtn Database-confirmModalBtn--cancel"
                onClick={() => setShowClearChatConfirm(false)}
              >
                Cancel
              </button>
              <button
                className="Database-confirmModalBtn Database-confirmModalBtn--confirm"
                onClick={confirmClearChat}
              >
                Clear Chat
              </button>
            </div>
          </div>
        </div>
      )}

      {showClearFilesConfirm && (
        <div className="Database-confirmModal">
          <div className="Database-confirmModalContent">
            <h3>Clear Files</h3>
            <p>
              Are you sure you want to clear all uploaded files from this view?
              This will not delete them from the database.
            </p>
            <div className="Database-confirmModalActions">
              <button
                className="Database-confirmModalBtn Database-confirmModalBtn--cancel"
                onClick={() => setShowClearFilesConfirm(false)}
              >
                Cancel
              </button>
              <button
                className="Database-confirmModalBtn Database-confirmModalBtn--confirm"
                onClick={confirmClearFiles}
              >
                Clear Files
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Database;
