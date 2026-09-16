import { useEffect, useRef, useState } from "react"
import type { useChat } from "../../hooks/useChat"
import { ApprovalCard } from "./ApprovalCard"

export function ChatPanel({
  chat,
  onClose,
  onMutated,
}: {
  chat: ReturnType<typeof useChat>
  onClose: () => void
  onMutated: () => void
}) {
  const { messages, pendingInterrupt, streaming, error, sendMessage, resolveInterrupt } = chat
  const [input, setInput] = useState("")
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
  }, [messages, pendingInterrupt, streaming])

  async function submit() {
    const text = input.trim()
    if (!text || streaming) return
    setInput("")
    await sendMessage(text)
    onMutated()
  }

  async function resolve(approve: boolean, reason?: string) {
    await resolveInterrupt(approve, reason)
    onMutated()
  }

  return (
    <aside className="fixed bottom-0 right-0 top-14 z-30 flex w-full max-w-sm flex-col border-l border-border bg-canvas sm:top-14">
      <div className="flex items-center justify-between border-b border-border p-3">
        <p className="label text-text">Job tracker assistant</p>
        <button onClick={onClose} className="label text-muted hover:text-text" aria-label="Close assistant">
          Close
        </button>
      </div>

      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-3">
        {messages.length === 0 && !pendingInterrupt && (
          <p className="text-sm text-faint">
            Ask me to save, list, update, or delete applications — or paste a job description and I'll extract it.
            Deleting always asks for your approval first.
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[90%] border p-2 text-sm ${
              m.role === "human"
                ? "ml-auto border-accent/30 bg-accent/10 text-text"
                : "border-border bg-panel text-text"
            }`}
          >
            {m.content || (m.streaming ? "…" : "")}
          </div>
        ))}
        {streaming && !messages.some((m) => m.streaming) && (
          <div className="flex max-w-[90%] items-center gap-1 border border-border bg-panel p-2.5">
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted [animation-delay:-0.3s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted [animation-delay:-0.15s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted" />
          </div>
        )}
        {pendingInterrupt && <ApprovalCard interrupt={pendingInterrupt} onResolve={resolve} />}
        {error && <p className="border border-status-rejected/30 bg-status-rejected/10 p-2 text-xs text-status-rejected">{error}</p>}
      </div>

      <div className="flex gap-2 border-t border-border p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder={pendingInterrupt ? "Resolve the pending approval above…" : "Message the assistant…"}
          disabled={streaming || !!pendingInterrupt}
          className="flex-1 border border-border bg-panel px-2 py-2 text-sm text-text placeholder:text-faint focus:border-accent disabled:opacity-50"
        />
        <button
          onClick={submit}
          disabled={streaming || !!pendingInterrupt || !input.trim()}
          className="label border border-accent/50 bg-accent/10 px-3 text-accent transition-all duration-150 active:scale-95 disabled:opacity-40 disabled:active:scale-100"
        >
          Send
        </button>
      </div>
    </aside>
  )
}
