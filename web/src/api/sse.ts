// The backend streams chat responses as Server-Sent Events over a POST body
// (POST /api/chat, POST /api/chat/resume). The native EventSource API only
// supports GET, so this parses the "event: ...\ndata: ...\n\n" wire format by
// hand from a fetch() ReadableStream.

export interface SseEvent {
  event: string
  data: string
}

export async function* postSSE(path: string, body: unknown, signal?: AbortSignal): AsyncGenerator<SseEvent> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  })
  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed: HTTP ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      // Normalize CRLF to LF: the dev proxy (and some intermediaries) rewrite the
      // backend's "\n\n" frame separators to "\r\n\r\n", which silently never
      // matched a bare "\n\n" search below — every event was dropped with no error.
      buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n")

      let boundary = buffer.indexOf("\n\n")
      while (boundary !== -1) {
        const rawEvent = buffer.slice(0, boundary)
        buffer = buffer.slice(boundary + 2)

        let event = "message"
        const dataLines: string[] = []
        for (const line of rawEvent.split("\n")) {
          if (line.startsWith("event:")) event = line.slice(6).trim()
          else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim())
          // ":"-prefixed lines are SSE keep-alive comments (e.g. "ping") — ignore them.
        }
        if (dataLines.length > 0) {
          yield { event, data: dataLines.join("\n") }
        }
        boundary = buffer.indexOf("\n\n")
      }
    }
  } finally {
    // If the consumer stops iterating early (e.g. on a "done"/"interrupt" event,
    // without waiting for the underlying connection to close — proxies can lag
    // that close well after the logical turn has ended), release the reader
    // instead of leaving a dangling read.
    reader.cancel().catch(() => {})
  }
}
