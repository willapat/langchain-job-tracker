import { useState } from "react"
import { api } from "../../api/client"
import type { Application, Status } from "../../types"
import { STATUSES, STATUS_LABELS } from "../../types"

function isLikelyUrl(value: string): boolean {
  return /^https?:\/\/\S+$/i.test(value.trim())
}

function ManualForm({ onClose, onCreated }: { onClose: () => void; onCreated: (application: Application) => void }) {
  const [company, setCompany] = useState("")
  const [role, setRole] = useState("")
  const [salary, setSalary] = useState("")
  const [location, setLocation] = useState("")
  const [status, setStatus] = useState<Status>("applied")
  const [busy, setBusy] = useState(false)

  async function submit() {
    if (!company.trim() || !role.trim()) return
    setBusy(true)
    try {
      const application = await api.createApplication({
        company: company.trim(),
        role: role.trim(),
        salary: salary.trim() || null,
        location: location.trim() || null,
        status,
      })
      onCreated(application)
      onClose()
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label mb-1 block">Company *</label>
          <input
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            className="w-full border border-border bg-panel px-2 py-1.5 text-sm text-text placeholder:text-faint focus:border-accent"
          />
        </div>
        <div>
          <label className="label mb-1 block">Role *</label>
          <input
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full border border-border bg-panel px-2 py-1.5 text-sm text-text placeholder:text-faint focus:border-accent"
          />
        </div>
        <div>
          <label className="label mb-1 block">Salary</label>
          <input
            value={salary}
            onChange={(e) => setSalary(e.target.value)}
            className="w-full border border-border bg-panel px-2 py-1.5 text-sm text-text placeholder:text-faint focus:border-accent"
          />
        </div>
        <div>
          <label className="label mb-1 block">Location</label>
          <input
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full border border-border bg-panel px-2 py-1.5 text-sm text-text placeholder:text-faint focus:border-accent"
          />
        </div>
        <div>
          <label className="label mb-1 block">Status</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as Status)}
            className="w-full border border-border bg-panel px-2 py-1.5 text-sm text-text focus:border-accent"
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABELS[s]}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <button onClick={onClose} className="label border border-border-strong px-3 py-2 text-muted">
          Cancel
        </button>
        <button
          onClick={submit}
          disabled={busy || !company.trim() || !role.trim()}
          className="label border border-accent/50 bg-accent/10 px-3 py-2 text-accent transition-all duration-150 active:scale-95 disabled:opacity-40 disabled:active:scale-100"
        >
          {busy ? "Saving…" : "Save"}
        </button>
      </div>
    </div>
  )
}

export function AddApplicationModal({
  onClose,
  onCreated,
  onSendToAssistant,
}: {
  onClose: () => void
  onCreated: (application: Application) => void
  onSendToAssistant: (message: string) => void
}) {
  const [mode, setMode] = useState<"agent" | "manual">("agent")
  const [text, setText] = useState("")

  function submitToAssistant() {
    const trimmed = text.trim()
    if (!trimmed) return
    const message = isLikelyUrl(trimmed)
      ? `Add this job application from the posting at ${trimmed}. Fetch it, extract the details, ask me if anything important is missing, then save it.`
      : `Add this job application from the description below. Extract the details, ask me if anything important is missing, then save it.\n\n${trimmed}`
    onSendToAssistant(message)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center p-4">
      <button aria-label="Close" className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="relative w-full max-w-lg animate-riseIn border border-border bg-canvas">
        <div className="flex items-center justify-between border-b border-border p-4">
          <h2 className="text-sm font-semibold text-text">Add application</h2>
          <button onClick={onClose} className="label text-muted hover:text-text">
            Close
          </button>
        </div>

        {mode === "agent" ? (
          <>
            <div className="p-4">
              <label className="label mb-2 block">Paste a job posting link or description</label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="https://job-boards.greenhouse.io/company/jobs/123  — or paste the full description"
                rows={7}
                autoFocus
                className="w-full resize-none border border-border bg-panel px-3 py-2 text-sm text-text placeholder:text-faint focus:border-accent"
              />
              <p className="label mt-2 text-faint">
                The assistant will fetch/extract the details itself and ask you here if anything important
                (like salary or location) is missing before saving. Some sites (LinkedIn, Indeed) block automated
                reads — paste the description instead if a link doesn't work.
              </p>
            </div>
            <div className="flex items-center justify-between border-t border-border p-4">
              <button onClick={() => setMode("manual")} className="label text-muted hover:text-text">
                Enter manually instead
              </button>
              <div className="flex gap-2">
                <button onClick={onClose} className="label border border-border-strong px-3 py-2 text-muted">
                  Cancel
                </button>
                <button
                  onClick={submitToAssistant}
                  disabled={!text.trim()}
                  className="label border border-accent/50 bg-accent/10 px-3 py-2 text-accent transition-all duration-150 active:scale-95 disabled:opacity-40 disabled:active:scale-100"
                >
                  Send to assistant
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="p-4">
            <ManualForm onClose={onClose} onCreated={onCreated} />
            <button onClick={() => setMode("agent")} className="label mt-3 text-muted hover:text-text">
              ← Paste a link or description instead
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
