import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react"
import {
  ArrowUpRight,
  Check,
  ChevronRight,
  Copy,
  FileText,
  Menu,
  MessageSquare,
  MoreHorizontal,
  Paperclip,
  Plus,
  Search,
  Settings,
  Sparkles,
  Trash2,
  X
} from "lucide-react"

type Role = "user" | "assistant"

type Message = {
  role: Role
  content: string
}

type Conversation = {
  id: string
  title: string
  messages: Message[]
}

type Engine = {
  provider: string
  model: string
  status: "online" | "demo"
  isCloud: boolean
}

type WorkspaceState = {
  conversations: Conversation[]
  engine: Engine
  activeId: string
  voiceDraft?: string | null
}

const starterConversations: Conversation[] = [
  { id: "launch", title: "Quarterly launch strategy", messages: [] },
  { id: "architecture", title: "React architecture review", messages: [] },
  { id: "research", title: "Research paper notes", messages: [] },
  { id: "portfolio", title: "Portfolio copy ideas", messages: [] },
  { id: "learning", title: "Learning plan for Spanish", messages: [] }
]

const prompts = [
  { label: "STRATEGY", text: "Turn these launch notes into a decisive one-page plan" },
  { label: "CODE REVIEW", text: "Read this architecture and challenge the weak decisions" },
  { label: "DEEP WORK", text: "Help me understand this without oversimplifying it" }
]

const API_BASE = window.location.port === "5173" ? "http://127.0.0.1:8765" : ""
const apiPath = (path: string) => `${API_BASE}${path}`

function App() {
  const [conversations, setConversations] = useState<Conversation[]>(starterConversations)
  const [activeId, setActiveId] = useState("launch")
  const [query, setQuery] = useState("")
  const [draft, setDraft] = useState("")
  const [busy, setBusy] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [copied, setCopied] = useState<string | null>(null)
  const composerRef = useRef<HTMLTextAreaElement>(null)
  const lastVoiceDraft = useRef<string | null>(null)

  const activeConversation = conversations.find((conversation) => conversation.id === activeId) ?? conversations[0]
  const visibleConversations = useMemo(
    () => conversations.filter((conversation) => conversation.title.toLowerCase().includes(query.toLowerCase())),
    [conversations, query]
  )
  const [engine, setEngine] = useState<Engine>({
    provider: "ollama",
    model: "gemma4:cloud",
    status: "online",
    isCloud: true
  })

  useEffect(() => {
    const syncState = async () => {
      try {
        const response = await fetch(apiPath("/api/state"))
        if (!response.ok) return
        const state = (await response.json()) as WorkspaceState
        if (state.conversations.length) setConversations(state.conversations)
        if (state.activeId) setActiveId(state.activeId)
        setEngine(state.engine)
        if (state.voiceDraft && state.voiceDraft !== lastVoiceDraft.current) {
          lastVoiceDraft.current = state.voiceDraft
          setDraft(state.voiceDraft)
          window.setTimeout(() => composerRef.current?.focus(), 80)
        }
      } catch {
        return
      }
    }
    void syncState()
    const timer = window.setInterval(() => void syncState(), 900)
    return () => window.clearInterval(timer)
  }, [])

  const createConversation = async () => {
    if (busy) return
    const localConversation: Conversation = {
      id: crypto.randomUUID(),
      title: "New conversation",
      messages: []
    }
    try {
      const response = await fetch(apiPath("/api/conversations"), { method: "POST" })
      if (response.ok) {
        const remoteConversation = (await response.json()) as Conversation
        localConversation.id = remoteConversation.id
      }
    } catch {
      localConversation.id = `local-${Date.now()}`
    }
    setConversations((current) => [localConversation, ...current])
    setActiveId(localConversation.id)
    setSidebarOpen(false)
    window.setTimeout(() => composerRef.current?.focus(), 80)
  }

  const selectConversation = (id: string) => {
    setActiveId(id)
    setSidebarOpen(false)
    void fetch(apiPath("/api/active"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: id })
    })
  }

  const updateActiveConversation = (messages: Message[], title?: string) => {
    setConversations((current) =>
      current.map((conversation) =>
        conversation.id === activeId
          ? { ...conversation, messages, title: title ?? conversation.title }
          : conversation
      )
    )
  }

  const sendMessage = async (event?: FormEvent) => {
    event?.preventDefault()
    const text = draft.trim()
    if (!text || busy || !activeConversation) return
    const nextMessages = [...activeConversation.messages, { role: "user" as Role, content: text }]
    const title = activeConversation.messages.length ? activeConversation.title : text.slice(0, 42) + (text.length > 42 ? "..." : "")
    updateActiveConversation(nextMessages, title)
    setDraft("")
    setBusy(true)
    try {
      const response = await fetch(apiPath(`/api/conversations/${activeConversation.id}/messages`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text })
      })
      if (!response.ok) throw new Error("Bolt could not reach the engine")
      const result = (await response.json()) as { message: Message; conversation?: Conversation }
      const responseMessages = result.conversation?.messages ?? [...nextMessages, result.message]
      updateActiveConversation(responseMessages, result.conversation?.title ?? title)
    } catch (error) {
      updateActiveConversation([
        ...nextMessages,
        { role: "assistant", content: error instanceof Error ? error.message : "Bolt could not reach the engine." }
      ], title)
    } finally {
      setBusy(false)
      window.setTimeout(() => composerRef.current?.focus(), 80)
    }
  }

  const handleComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      void sendMessage()
    }
  }

  const copyMessage = async (content: string) => {
    await navigator.clipboard.writeText(content)
    setCopied(content)
    window.setTimeout(() => setCopied(null), 1400)
  }

  const deleteConversation = async (id: string) => {
    setConversations((current) => current.filter((conversation) => conversation.id !== id))
    if (activeId === id) setActiveId(conversations.find((conversation) => conversation.id !== id)?.id ?? "")
    try {
      await fetch(apiPath(`/api/conversations/${id}`), { method: "DELETE" })
    } catch {
      return
    }
  }

  const usePrompt = (text: string) => {
    setDraft(text)
    composerRef.current?.focus()
  }

  const hasMessages = Boolean(activeConversation?.messages.length)

  return (
    <div className="app-shell">
      <div className={`mobile-scrim ${sidebarOpen ? "visible" : ""}`} onClick={() => setSidebarOpen(false)} />
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="brand-lockup">
          <div className="brand-mark"><span>ϟ</span><i /></div>
          <div>
            <div className="brand-name">Bolt AI</div>
            <div className="brand-caption">PRIVATE INTELLIGENCE</div>
          </div>
        </div>

        <button className="new-thread" onClick={() => void createConversation()}>
          <Plus size={18} strokeWidth={1.8} />
          <span>New thread</span>
          <kbd>Ctrl N</kbd>
        </button>

        <label className="search-field">
          <Search size={17} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find a thread" />
          <kbd>⌘K</kbd>
        </label>

        <div className="archive-heading"><span>ARCHIVE</span><MoreHorizontal size={16} /></div>
        <nav className="thread-list">
          {visibleConversations.map((conversation, index) => (
            <div className={`thread-item ${conversation.id === activeId ? "active" : ""}`} key={conversation.id}>
              <button onClick={() => selectConversation(conversation.id)}>
                <MessageSquare size={16} strokeWidth={1.5} />
                <span>{conversation.title}</span>
              </button>
              <span className="thread-time">{index === 0 ? "Now" : `${index}d`}</span>
              {conversation.id === activeId && conversation.id !== "launch" ? (
                <button className="thread-delete" onClick={() => void deleteConversation(conversation.id)} aria-label="Delete thread">
                  <Trash2 size={14} />
                </button>
              ) : null}
            </div>
          ))}
          {!visibleConversations.length ? <div className="no-results">No threads found</div> : null}
        </nav>

        <div className="sidebar-bottom">
          <div className="engine-card">
            <div className="engine-card-top"><span className="status-dot" /><strong>Bolt Engine</strong><Check size={15} /></div>
            <div className="engine-meta">Encrypted&nbsp; · &nbsp;{engine.isCloud ? "Ollama cloud" : "Local device"}</div>
          </div>
          <button className="settings-link" onClick={() => setSettingsOpen(true)}><Settings size={17} /><span>Settings</span><ChevronRight size={16} /></button>
          <div className="permission-note"><Sparkles size={12} /> No tools without permission</div>
        </div>
      </aside>

      <main className="main-stage">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={20} /></button>
          <div className="page-heading">
            <div className="eyebrow">PERSONAL ARCHIVE <ChevronRight size={12} /></div>
            <h1>{activeConversation?.title ?? "New conversation"}</h1>
          </div>
          <button className="engine-pill" onClick={() => setSettingsOpen(true)}>
            <span className="status-dot" />
            <span className="pill-label">ENGINE</span>
            <span className="pill-divider" />
            <strong>{engine.status === "online" ? "ONLINE" : "DEMO"}</strong>
            <ChevronRight size={14} />
          </button>
        </header>

        <section className={`conversation-canvas ${hasMessages ? "has-messages" : "empty"}`}>
          {hasMessages ? (
            <div className="message-stack">
              {activeConversation.messages.map((message, index) => (
                <article className={`message-row ${message.role}`} key={`${message.role}-${index}`}>
                  {message.role === "assistant" ? <div className="bolt-avatar">ϟ<i /></div> : null}
                  <div className={`message-card ${message.role}`}>
                    <div className="message-meta"><span>{message.role === "assistant" ? "BOLT AI" : "YOU"}</span>{message.role === "assistant" ? <button onClick={() => void copyMessage(message.content)}>{copied === message.content ? <Check size={13} /> : <Copy size={13} />} {copied === message.content ? "Copied" : "Copy"}</button> : null}</div>
                    <div className="message-content">{message.content}</div>
                  </div>
                </article>
              ))}
              {busy ? <div className="thinking-row"><div className="bolt-avatar">ϟ<i /></div><div className="thinking-card"><span /><span /><span /></div></div> : null}
            </div>
          ) : (
            <div className="empty-state">
              <div className="hero-symbol">ϟ<i /></div>
              <div className="eyebrow centered">PRIVATE WORKSPACE</div>
              <h2>Begin with a thought.</h2>
              <p>Write it as it is. Bolt will help you make it clear.</p>
              <div className="prompt-list">
                {prompts.map((prompt, index) => (
                  <button className="prompt-row" key={prompt.label} onClick={() => usePrompt(prompt.text)}>
                    <span className="prompt-index">0{index + 1} <b>/</b> {prompt.label}</span>
                    <span className="prompt-text">{prompt.text}</span>
                    <ArrowUpRight size={17} />
                  </button>
                ))}
              </div>
            </div>
          )}
        </section>

        <div className="composer-wrap">
          <form className={`composer ${busy ? "busy" : ""}`} onSubmit={sendMessage}>
            <textarea ref={composerRef} value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={handleComposerKeyDown} placeholder="Write what you’re thinking..." rows={2} disabled={busy} />
            <div className="composer-toolbar">
              <div className="composer-tools"><button type="button" disabled aria-label="Attach a file"><Paperclip size={19} /></button><button type="button" disabled aria-label="Add a document"><FileText size={18} /></button></div>
              <div className="composer-status">{busy ? "Bolt is thinking · your session stays private" : engine.isCloud ? "Private session · Ollama cloud engine" : "Private session · stored on this device"}</div>
              <div className="composer-shortcuts">Enter send&nbsp; · &nbsp;Shift Enter new line</div>
              <button className="send-button" type="submit" disabled={busy || !draft.trim()} aria-label="Send message"><ArrowUpRight size={20} /></button>
            </div>
          </form>
          <div className="composer-footer"><span>LOCAL CONTROL</span><span className="footer-separator" /><span>Conversations stay with Bolt</span><span className="footer-grow" /><span>{engine.model}</span></div>
        </div>
      </main>

      {settingsOpen ? <div className="modal-layer" onClick={() => setSettingsOpen(false)}><section className="settings-modal" onClick={(event) => event.stopPropagation()}><div className="modal-header"><div><div className="eyebrow">BOLT ENGINE</div><h2>Workspace settings</h2></div><button onClick={() => setSettingsOpen(false)} aria-label="Close settings"><X size={19} /></button></div><p>Control how Bolt connects to your AI engine. Your conversation archive remains local.</p><div className="settings-grid"><div><span>Provider</span><strong>{engine.provider === "ollama" ? "Ollama" : engine.provider}</strong></div><div><span>Model</span><strong>{engine.model}</strong></div><div><span>Status</span><strong className="online-text"><i /> {engine.status === "online" ? "Connected" : "Demo mode"}</strong></div><div><span>Privacy</span><strong>Local control</strong></div></div><button className="close-settings" onClick={() => setSettingsOpen(false)}>Done <Check size={16} /></button></section></div> : null}
    </div>
  )
}

export default App
