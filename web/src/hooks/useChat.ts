import { useCallback, useEffect, useRef, useState } from "react"
import { postSSE } from "../api/sse"
import type { ChatMessage, PendingInterrupt } from "../types"

const THREAD_ID_KEY = "waypoint.chat.thread_id"

function getThreadId(): string {
  let id = localStorage.getItem(THREAD_ID_KEY)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(THREAD_ID_KEY, id)
  }
  return id
}

export function useChat() {
  const threadId = useRef(getThreadId())
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [pendingInterrupt, setPendingInterrupt] = useState<PendingInterrupt | null>(null)
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`/api/chat/${threadId.current}/state`)
      .then((r) => (r.ok ? r.json() : null))
      .then((state) => {
        if (!state) return
        setMessages(state.messages ?? [])
        setPendingInterrupt(state.pending_interrupt ?? null)
      })
      .catch(() => {
        /* fresh thread, nothing to rehydrate */
      })
  }, [])

  const consume = useCallback(async (path: string, body: unknown) => {
    setStreaming(true)
    setError(null)
    let assistantText = ""
    try {
      for await (const evt of postSSE(path, body)) {
        if (evt.event === "token") {
          const { text } = JSON.parse(evt.data) as { text: string }
          assistantText += text
          setMessages((prev) => {
            const next = [...prev]
            const last = next[next.length - 1]
            if (last && last.role === "ai" && last.streaming) {
              next[next.length - 1] = { ...last, content: assistantText }
            } else {
              next.push({ role: "ai", content: assistantText, streaming: true })
            }
            return next
          })
        } else if (evt.event === "interrupt") {
          setPendingInterrupt(JSON.parse(evt.data) as PendingInterrupt)
          break // the turn is logically over; don't wait on the stream's own close
        } else if (evt.event === "error") {
          const { message } = JSON.parse(evt.data) as { message: string }
          setError(message)
          break
        } else if (evt.event === "done") {
          break
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat request failed.")
    } finally {
      setStreaming(false)
      setMessages((prev) => prev.map((m) => ({ ...m, streaming: false })))
    }
  }, [])

  const sendMessage = useCallback(
    async (message: string) => {
      setMessages((prev) => [...prev, { role: "human", content: message }])
      await consume("/api/chat", { message, thread_id: threadId.current })
    },
    [consume],
  )

  const resolveInterrupt = useCallback(
    async (approve: boolean, reason?: string) => {
      const decision = approve
        ? { type: "approve" as const }
        : {
            type: "reject" as const,
            // The middleware uses `message` verbatim as the tool's result if
            // provided, so a bare custom reason would silently replace (not
            // append to) its "tool was not executed" context, leaving the
            // model unaware the action didn't happen. State that explicitly.
            message: `The user rejected this action; the tool was NOT executed.${reason ? ` Reason given: ${reason}` : ""}`,
          }
      setPendingInterrupt(null)
      await consume("/api/chat/resume", { thread_id: threadId.current, decisions: [decision] })
    },
    [consume],
  )

  return { messages, pendingInterrupt, streaming, error, sendMessage, resolveInterrupt }
}
