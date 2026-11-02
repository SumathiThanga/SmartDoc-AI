
import { useEffect, useRef, useState } from "react";


import {
  LayoutDashboard,
  FileText,
  MessageSquare,
  Upload,
  Settings,
  Bell,
  Sparkles,
  File,
  ArrowUpRight,
  Plus,
  Menu,
  Send,
  Bot,
  User,
  RefreshCw,
  ArrowLeft,
  Trash2,
} from "lucide-react";

const API_URL = "http://localhost:8000";

function App() {
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  const [documents, setDocuments] = useState([]);
  const [totalDocuments, setTotalDocuments] = useState(0);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const [uploadMessage, setUploadMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const [activeView, setActiveView] = useState("dashboard");

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [deletingDocument, setDeletingDocument] = useState("");
  const [refreshing, setRefreshing] = useState(false);

    // Load documents from FastAPI
    async function fetchDocuments() {
    setRefreshing(true);

    try {
      setErrorMessage("");

      const response = await fetch(`${API_URL}/documents`);

      if (!response.ok) {
        throw new Error("Unable to fetch documents.");
      }

      const data = await response.json();

      setDocuments(
        Array.isArray(data.documents) ? data.documents : []
      );

      setTotalDocuments(
        Number(data.total_documents ?? data.documents?.length ?? 0)
      );

    } catch (error) {
      console.error("Document loading error:", error);
      setErrorMessage(error.message);

    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    fetchDocuments();
  }, []);

  // Scroll to the latest chat message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  // Upload PDF to FastAPI
  async function handleFileSelected(event) {
    const file = event.target.files?.[0];

    if (!file) return;

    setUploadMessage("");
    setErrorMessage("");

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMessage("Please select a PDF file.");
      event.target.value = "";
      return;
    }

    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "PDF upload failed.");
      }

      setUploadMessage(
        `${data.filename} uploaded and indexed successfully!`
      );

      await fetchDocuments();
    } catch (error) {
      console.error("Upload error:", error);
      setErrorMessage(error.message);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  function handleRefreshDocuments() {
    setUploadMessage("");
    setErrorMessage("");
    fetchDocuments();
  }

  async function handleDeleteDocument(filename) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?\n\nThis will also remove it from the AI search index.`
    );

    if (!confirmed) return;

    setDeletingDocument(filename);
    setUploadMessage("");
    setErrorMessage("");

    try {
      const response = await fetch(
        `${API_URL}/documents/${encodeURIComponent(filename)}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Document deletion failed.");
      }

      setUploadMessage(`${filename} deleted successfully!`);

      await fetchDocuments();

    } catch (error) {
      console.error("Delete error:", error);
      setErrorMessage(error.message);
    } finally {
      setDeletingDocument("");
    }
  }


  function openFilePicker() {
    if (!uploading) {
      fileInputRef.current?.click();
    }
  }

  // Ask a question using FastAPI /ask
  async function handleAskQuestion(event) {
    event.preventDefault();

    const userQuestion = question.trim();

    if (!userQuestion || asking) return;

    if (totalDocuments === 0) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: "Please upload a PDF document before asking questions.",
        },
      ]);
      return;
    }

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: userQuestion,
      },
    ]);

    setQuestion("");
    setAsking(true);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
          top_k: 5,
        }),
      });

      const contentType = response.headers.get("content-type") || "";

      let result;

      if (contentType.includes("application/json")) {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            typeof data.detail === "string"
              ? data.detail
              : "Unable to get an answer."
          );
        }

        // Swagger shows the successful response as a string.
        result =
          typeof data === "string"
            ? data
            : data.answer ?? data.response ?? JSON.stringify(data);
      } else {
        result = await response.text();

        if (!response.ok) {
          throw new Error(result || "Unable to get an answer.");
        }
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result || "No answer was returned.",
        },
      ]);
    } catch (error) {
      console.error("Question error:", error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: `Sorry, something went wrong: ${error.message}`,
          isError: true,
        },
      ]);
    } finally {
      setAsking(false);
    }
  }

  const colors = [
    "text-blue-600 bg-blue-100",
    "text-purple-600 bg-purple-100",
    "text-orange-600 bg-orange-100",
  ];

  function navigateTo(view) {
    setActiveView(view);
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <div className="flex min-h-screen">

        {/* Sidebar */}
        <aside className="hidden md:flex w-64 bg-slate-950 text-white flex-col p-5 shrink-0">

          <div className="flex items-center gap-3 mb-12">
            <div className="bg-blue-600 p-2 rounded-xl">
              <Sparkles size={23} />
            </div>

            <div>
              <h1 className="font-bold text-xl">
                SmartDoc AI
              </h1>

              <p className="text-xs text-slate-400">
                Intelligent Documents
              </p>
            </div>
          </div>

          <p className="text-xs text-slate-500 mb-4">
            WORKSPACE
          </p>

          <nav className="space-y-2">

            <button
              onClick={() => navigateTo("dashboard")}
              className={`flex items-center gap-3 w-full p-3 rounded-xl ${
                activeView === "dashboard"
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:bg-slate-800"
              }`}
            >
              <LayoutDashboard size={19} />
              Dashboard
            </button>

            <button
              onClick={() => navigateTo("documents")}
              className={`flex items-center gap-3 w-full p-3 rounded-xl ${
                activeView === "documents"
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:bg-slate-800"
              }`}
            >
              <FileText size={19} />
              Documents
            </button>

            <button
              onClick={() => navigateTo("assistant")}
              className={`flex items-center gap-3 w-full p-3 rounded-xl ${
                activeView === "assistant"
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:bg-slate-800"
              }`}
            >
              <MessageSquare size={19} />
              AI Assistant
            </button>

          </nav>

          <div className="mt-auto">

            <button className="flex items-center gap-3 w-full p-3 text-slate-400 hover:bg-slate-800 rounded-xl">
              <Settings size={19} />
              Settings
            </button>

            <div className="border-t border-slate-800 mt-5 pt-5 flex items-center gap-3">

              <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center font-bold">
                S
              </div>

              <div>
                <p className="text-sm font-medium">User</p>

                <p className="text-xs text-slate-400">
                  SmartDoc Workspace
                </p>
              </div>

            </div>
          </div>

        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0">

          {/* Header */}
          <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-5 md:px-8">

            <div className="flex items-center gap-3">
              <Menu className="md:hidden" />

              <div>
                <h2 className="font-bold text-lg">
                  {activeView === "assistant"
                    ? "AI Assistant"
                    : activeView === "documents"
                    ? "Documents"
                    : "Dashboard"}
                </h2>

                <p className="text-xs text-slate-500">
                  Manage and explore your documents
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button className="p-2 rounded-full hover:bg-slate-100">
                <Bell size={20} />
              </button>

              <div className="w-9 h-9 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center font-semibold">
                S
              </div>
            </div>

          </header>

          {/* Dashboard view */}
          {activeView === "dashboard" && (
            <div className="p-5 md:p-8 max-w-7xl mx-auto">

              {/* Welcome */}
              <div className="flex flex-col md:flex-row justify-between gap-4 mb-8">

                <div>
                  <h1 className="text-2xl md:text-3xl font-bold">
                    Welcome to SmartDoc AI 👋
                  </h1>

                  <p className="text-slate-500 mt-2">
                    Your intelligent document workspace.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={openFilePicker}
                  disabled={uploading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl flex items-center justify-center gap-2 font-medium disabled:opacity-50"
                >
                  <Plus size={19} />
                  Upload Document
                </button>

              </div>

              {/* Statistics */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-8">

                <StatCard
                  title="Total Documents"
                  value={loading ? "..." : String(totalDocuments)}
                  icon={<FileText />}
                  color="bg-blue-100 text-blue-600"
                />

                <StatCard
                  title="Processed Documents"
                  value={loading ? "..." : String(totalDocuments)}
                  icon={<Sparkles />}
                  color="bg-green-100 text-green-600"
                />

                <StatCard
                  title="AI Conversations"
                  value={messages.filter((m) => m.role === "user").length}
                  icon={<MessageSquare />}
                  color="bg-purple-100 text-purple-600"
                />

              </div>

              {/* Upload section */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-8">

                <div className="flex items-center gap-2 mb-5">
                  <Upload className="text-blue-600" />

                  <h2 className="font-bold text-lg">
                    Upload your documents
                  </h2>
                </div>

                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  ref={fileInputRef}
                  onChange={handleFileSelected}
                  className="hidden"
                />

                <div className="border-2 border-dashed border-slate-300 rounded-2xl p-10 text-center hover:border-blue-500 transition">

                  <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <FileText size={28} />
                  </div>

                  <h3 className="font-semibold">
                    Select your PDF documents
                  </h3>

                  <p className="text-sm text-slate-500 mt-2">
                    Upload documents to start asking questions.
                  </p>

                  <button
                    type="button"
                    onClick={openFilePicker}
                    disabled={uploading}
                    className="mt-5 bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 rounded-lg disabled:opacity-50"
                  >
                    {uploading
                      ? "Uploading and processing..."
                      : "Browse Files"}
                  </button>

                  {uploading && (
                    <p className="mt-4 text-sm text-blue-600">
                      Please wait. Your PDF is being processed and indexed.
                    </p>
                  )}

                  {uploadMessage && (
                    <p className="mt-4 text-sm text-green-600">
                      {uploadMessage}
                    </p>
                  )}

                  {errorMessage && (
                    <p className="mt-4 text-sm text-red-600">
                      {errorMessage}
                    </p>
                  )}

                </div>
              </div>

              {/* Recent Documents */}
              <DocumentList
                documents={documents}
                loading={loading}
                errorMessage={errorMessage}
                colors={colors}
                onRefresh={handleRefreshDocuments}
                onDelete={handleDeleteDocument}
                deletingDocument={deletingDocument}
                refreshing={refreshing}
              />

              {/* AI Assistant CTA */}
              <div className="mt-8 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-7 text-white">

                <div className="flex items-center gap-3 mb-3">
                  <Sparkles size={25} />

                  <h2 className="text-xl font-bold">
                    Meet your AI Document Assistant
                  </h2>
                </div>

                <p className="text-blue-100 mb-5 max-w-xl">
                  Ask questions about your uploaded PDFs and get
                  intelligent answers.
                </p>

                <button
                  onClick={() => navigateTo("assistant")}
                  className="bg-white text-blue-700 px-5 py-3 rounded-xl font-semibold hover:bg-blue-50"
                >
                  Start asking questions →
                </button>

              </div>

            </div>
          )}

          {/* Documents view */}
          {activeView === "documents" && (
            <div className="p-5 md:p-8 max-w-7xl mx-auto">

              <div className="flex justify-between items-center gap-4 mb-8">
                <div>
                  <h1 className="text-2xl font-bold">
                    Your Documents
                  </h1>
                  <p className="text-slate-500 mt-2">
                    {totalDocuments} documents available
                  </p>
                </div>

                <button
                  onClick={openFilePicker}
                  disabled={uploading}
                  className="bg-blue-600 text-white px-5 py-3 rounded-xl flex items-center gap-2"
                >
                  <Plus size={18} />
                  Upload
                </button>
              </div>

              <input
                type="file"
                accept=".pdf,application/pdf"
                ref={fileInputRef}
                onChange={handleFileSelected}
                className="hidden"
              />

              <DocumentList
                documents={documents}
                loading={loading}
                errorMessage={errorMessage}
                colors={colors}
                onRefresh={handleRefreshDocuments}
                onDelete={handleDeleteDocument}
                deletingDocument={deletingDocument}
                refreshing={refreshing}
              />

              {uploadMessage && (
                <p className="text-green-600 mt-4">{uploadMessage}</p>
              )}

            </div>
          )}

          {/* AI Assistant view */}
          {activeView === "assistant" && (
            <div className="p-4 md:p-8 max-w-5xl mx-auto">

              <div className="mb-6 flex items-center gap-3">
                <div className="bg-blue-100 text-blue-600 p-3 rounded-xl">
                  <Sparkles size={25} />
                </div>

                <div>
                  <h1 className="text-2xl font-bold">
                    AI Document Assistant
                  </h1>

                  <p className="text-sm text-slate-500">
                    Ask questions and get answers from your uploaded PDFs.
                  </p>
                </div>
              </div>

              {/* Chat window */}
              <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">

                {/* Chat header */}
                <div className="p-4 border-b border-slate-200 flex items-center justify-between">

                  <div className="flex items-center gap-3">
                    <div className="bg-blue-600 text-white p-2 rounded-xl">
                      <Bot size={21} />
                    </div>

                    <div>
                      <p className="font-semibold">
                        SmartDoc AI
                      </p>
                      <p className="text-xs text-green-600">
                        Ready to answer
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => setMessages([])}
                    className="text-sm text-slate-500 hover:text-blue-600 flex items-center gap-2"
                    title="Clear conversation"
                  >
                    <RefreshCw size={15} />
                    Clear chat
                  </button>

                </div>

                {/* Messages */}
                <div className="h-[450px] overflow-y-auto p-5 space-y-5 bg-slate-50">

                  {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-center">

                      <div className="bg-blue-100 text-blue-600 p-5 rounded-2xl mb-4">
                        <Bot size={38} />
                      </div>

                      <h2 className="text-lg font-bold">
                        Hello! How can I help you?
                      </h2>

                      <p className="text-sm text-slate-500 mt-2 max-w-md">
                        Ask me anything about your uploaded documents.
                        I'll search your documents and generate an answer.
                      </p>

                      <div className="flex flex-wrap justify-center gap-2 mt-6">
                        <button
                          onClick={() => setQuestion("Summarize the uploaded documents.")}
                          className="text-sm border border-slate-200 bg-white rounded-full px-4 py-2 hover:border-blue-500"
                        >
                          Summarize my documents
                        </button>

                        <button
                          onClick={() => setQuestion("What are the key findings in the documents?")}
                          className="text-sm border border-slate-200 bg-white rounded-full px-4 py-2 hover:border-blue-500"
                        >
                          Find key findings
                        </button>
                      </div>

                    </div>
                  )}

                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex gap-3 ${
                        message.role === "user"
                          ? "justify-end"
                          : "justify-start"
                      }`}
                    >

                      {message.role === "assistant" && (
                        <div className="w-9 h-9 shrink-0 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center">
                          <Bot size={20} />
                        </div>
                      )}

                      <div
                        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-7 whitespace-pre-wrap break-words ${
                          message.role === "user"
                            ? "bg-blue-600 text-white"
                            : message.isError
                            ? "bg-red-50 text-red-700 border border-red-200"
                            : "bg-white text-slate-700 border border-slate-200"
                        }`}
                      >
                        {message.content}
                      </div>

                      {message.role === "user" && (
                        <div className="w-9 h-9 shrink-0 bg-slate-200 text-slate-600 rounded-xl flex items-center justify-center">
                          <User size={19} />
                        </div>
                      )}

                    </div>
                  ))}

                  {asking && (
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center">
                        <Bot size={20} />
                      </div>

                      <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-500">
                        Searching documents and generating an answer...
                      </div>
                    </div>
                  )}

                  <div ref={chatEndRef} />

                </div>

                {/* Question input */}
                <form
                  onSubmit={handleAskQuestion}
                  className="p-4 border-t border-slate-200 bg-white"
                >

                  <div className="flex items-center gap-3">

                    <input
                      type="text"
                      value={question}
                      onChange={(event) => setQuestion(event.target.value)}
                      placeholder="Ask a question about your documents..."
                      disabled={asking}
                      className="flex-1 min-w-0 border border-slate-300 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />

                    <button
                      type="submit"
                      disabled={!question.trim() || asking}
                      className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Send size={20} />
                    </button>

                  </div>

                  <p className="text-xs text-slate-400 mt-3">
                    Answers are generated using your uploaded documents.
                  </p>

                </form>

              </div>

              <button
                onClick={() => navigateTo("dashboard")}
                className="mt-5 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-2"
              >
                <ArrowLeft size={16} />
                Back to Dashboard
              </button>

            </div>
          )}

        </main>

      </div>
    </div>
  );
}


// Reusable statistics card
function StatCard({ title, value, icon, color }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6">

      <div className="flex items-center justify-between mb-5">
        <div className={`p-3 rounded-xl ${color}`}>
          {icon}
        </div>

        <span className="text-xs text-slate-400">
          Overview
        </span>
      </div>

      <h2 className="text-3xl font-bold">
        {value}
      </h2>

      <p className="text-sm text-slate-500 mt-1">
        {title}
      </p>

    </div>
  );
}


// Reusable document list
function DocumentList({
  documents,
  loading,
  errorMessage,
  colors,
  onRefresh,
  onDelete,
  deletingDocument,
  refreshing,
}) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6">

      <div className="flex items-center justify-between mb-6">

        <div>
          <h2 className="font-bold text-lg">
            Recent Documents
          </h2>

          <p className="text-sm text-slate-500 mt-1">
            Your recently uploaded files
          </p>
        </div>

        <button
          type="button"
          onClick={onRefresh}
          disabled={refreshing}
          className="text-blue-600 text-sm font-medium hover:text-blue-800 disabled:opacity-50 flex items-center gap-2"
        >
          <RefreshCw
            size={15}
            className={refreshing ? "animate-spin" : ""}
          />
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>

      </div>

      <div className="space-y-4">

        {loading && (
          <p className="text-sm text-slate-500">
            Loading documents...
          </p>
        )}

        {!loading && errorMessage && (
          <p className="text-sm text-red-600">
            {errorMessage}
          </p>
        )}

        {!loading && !errorMessage && documents.length === 0 && (
          <p className="text-sm text-slate-500 text-center py-8">
            No documents yet. Upload your first PDF to get started.
          </p>
        )}

        {!loading && documents.map((doc, index) => (
          <div
            key={doc}
            className="flex items-center justify-between gap-3 p-4 border border-slate-100 rounded-xl hover:bg-slate-50"
          >

            <div className="flex items-center gap-3 min-w-0">

              <div className={`p-3 rounded-xl ${colors[index % colors.length]}`}>
                <File size={22} />
              </div>

              <div className="min-w-0">
                <p className="font-semibold text-sm truncate">
                  {doc}
                </p>

                <p className="text-xs text-slate-500 mt-1">
                  PDF document
                </p>
              </div>

            </div>

            
          <div className="flex items-center gap-3 shrink-0">

            <span className="text-xs text-green-600 bg-green-50 px-3 py-1.5 rounded-full">
              Available
            </span>

            <button
              type="button"
              onClick={() => onDelete(doc)}
              disabled={!!deletingDocument}
              title={`Delete ${doc}`}
              className="p-2 rounded-lg text-red-500 hover:bg-red-50 hover:text-red-700 disabled:opacity-40"
            >
              {deletingDocument === doc ? (
                <span className="text-xs">Deleting...</span>
              ) : (
                <Trash2 size={18} />
              )}
            </button>

          </div>


          </div>
        ))}

      </div>

    </div>
  );
}

export default App;
