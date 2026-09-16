import { useState } from "react"
import { Route, Routes } from "react-router-dom"
import { Analytics } from "./components/analytics/Analytics"
import { Board } from "./components/board/Board"
import { ChatPanel } from "./components/chat/ChatPanel"
import { ApplicationDrawer } from "./components/detail/ApplicationDrawer"
import { AddApplicationModal } from "./components/ingest/AddApplicationModal"
import { Layout } from "./components/Layout"
import { useApplications } from "./hooks/useApplications"
import { useChat } from "./hooks/useChat"
import type { Application } from "./types"

function BoardPage({
  applications,
  loading,
  error,
  setStatus,
  onOpen,
}: {
  applications: Application[]
  loading: boolean
  error: string | null
  setStatus: (id: number, status: Application["status"]) => void
  onOpen: (application: Application) => void
}) {
  if (loading) return <p className="label">Loading applications…</p>
  return (
    <>
      {error && <p className="mb-3 border border-status-rejected/30 bg-status-rejected/10 p-2 text-sm text-status-rejected">{error}</p>}
      <Board applications={applications} onOpen={onOpen} onStatusChange={setStatus} />
    </>
  )
}

export default function App() {
  const { applications, loading, error, refresh, setStatus } = useApplications()
  const chat = useChat()
  const [selected, setSelected] = useState<Application | null>(null)
  const [addOpen, setAddOpen] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)

  function sendToAssistant(message: string) {
    setChatOpen(true)
    chat.sendMessage(message).then(refresh)
  }

  return (
    <Layout
      onAddApplication={() => setAddOpen(true)}
      onToggleChat={() => setChatOpen((v) => !v)}
      chatOpen={chatOpen}
      assistantNeedsAttention={!!chat.pendingInterrupt && !chatOpen}
    >
      <Routes>
        <Route
          path="/"
          element={
            <BoardPage
              applications={applications}
              loading={loading}
              error={error}
              setStatus={setStatus}
              onOpen={setSelected}
            />
          }
        />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>

      {selected && (
        <ApplicationDrawer
          application={applications.find((a) => a.id === selected.id) ?? selected}
          onClose={() => setSelected(null)}
          onDeleted={() => {
            setSelected(null)
            refresh()
          }}
          onRefresh={(updated) => {
            setSelected(updated)
            refresh()
          }}
        />
      )}

      {addOpen && (
        <AddApplicationModal
          onClose={() => setAddOpen(false)}
          onCreated={() => refresh()}
          onSendToAssistant={sendToAssistant}
        />
      )}

      {chatOpen && <ChatPanel chat={chat} onClose={() => setChatOpen(false)} onMutated={refresh} />}
    </Layout>
  )
}
