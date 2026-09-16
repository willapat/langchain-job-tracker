import { useState } from "react"
import { api } from "../../api/client"
import type { Application, Note } from "../../types"
import { StatusBadge } from "../StatusBadge"

function NoteRow({ note, onDelete }: { note: Note; onDelete: () => void }) {
  return (
    <li className="group border-l-2 border-border py-2 pl-3">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm text-text">{note.content}</p>
        <button
          onClick={onDelete}
          className="label shrink-0 text-faint opacity-0 hover:text-status-rejected group-hover:opacity-100"
          aria-label="Delete note"
        >
          Delete
        </button>
      </div>
      <p className="label mt-1 text-faint">
        {note.kind === "interview" ? "Interview" : "Note"} · {new Date(note.created_at).toLocaleString()}
      </p>
    </li>
  )
}

export function ApplicationDrawer({
  application,
  onClose,
  onDeleted,
  onRefresh,
}: {
  application: Application
  onClose: () => void
  onDeleted: (id: number) => void
  onRefresh: (application: Application) => void
}) {
  const [noteText, setNoteText] = useState("")
  const [noteKind, setNoteKind] = useState<"note" | "interview">("note")
  const [busy, setBusy] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)

  async function addNote() {
    if (!noteText.trim()) return
    setBusy(true)
    try {
      const note = await api.addNote(application.id, noteText.trim(), noteKind)
      onRefresh({ ...application, notes: [note, ...application.notes] })
      setNoteText("")
    } finally {
      setBusy(false)
    }
  }

  async function deleteNote(noteId: number) {
    await api.deleteNote(noteId)
    onRefresh({ ...application, notes: application.notes.filter((n) => n.id !== noteId) })
  }

  async function handleDelete() {
    setBusy(true)
    try {
      await api.deleteApplication(application.id)
      onDeleted(application.id)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <button aria-label="Close" className="absolute inset-0 bg-black/60" onClick={onClose} />
      <aside className="relative flex h-full w-full max-w-md flex-col border-l border-border bg-canvas">
        <div className="flex items-start justify-between border-b border-border p-4">
          <div>
            <h2 className="text-lg font-semibold text-text">{application.company}</h2>
            <p className="text-sm text-muted">{application.role}</p>
            <div className="mt-2">
              <StatusBadge status={application.status} />
            </div>
          </div>
          <button onClick={onClose} className="label text-muted hover:text-text" aria-label="Close drawer">
            Close
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <dl className="grid grid-cols-2 gap-3 text-sm">
            {application.salary && (
              <div>
                <dt className="label">Salary</dt>
                <dd className="mono mt-1 text-text">{application.salary}</dd>
              </div>
            )}
            {application.location && (
              <div>
                <dt className="label">Location</dt>
                <dd className="mt-1 text-text">{application.location}</dd>
              </div>
            )}
            <div>
              <dt className="label">Applied</dt>
              <dd className="mono mt-1 text-text">{application.applied_date}</dd>
            </div>
            {application.source_url && (
              <div>
                <dt className="label">Source</dt>
                <dd className="mt-1 truncate">
                  <a href={application.source_url} target="_blank" rel="noreferrer" className="text-accent hover:underline">
                    Original posting ↗
                  </a>
                </dd>
              </div>
            )}
          </dl>

          {application.requirements.length > 0 && (
            <div className="mt-4">
              <p className="label mb-2">Requirements</p>
              <ul className="list-inside list-disc space-y-1 text-sm text-muted">
                {application.requirements.map((req, i) => (
                  <li key={i}>{req}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-6 border-t border-border pt-4">
            <p className="label mb-3">Notes &amp; interview prep</p>
            <div className="mb-3 flex gap-2">
              <select
                value={noteKind}
                onChange={(e) => setNoteKind(e.target.value as "note" | "interview")}
                className="mono border border-border bg-panel px-2 py-1.5 text-xs text-text"
              >
                <option value="note">Note</option>
                <option value="interview">Interview</option>
              </select>
              <input
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addNote()}
                placeholder="Add a note…"
                className="flex-1 border border-border bg-panel px-2 py-1.5 text-sm text-text placeholder:text-faint focus:border-accent"
              />
              <button
                onClick={addNote}
                disabled={busy || !noteText.trim()}
                className="label border border-border-strong px-3 text-text hover:border-accent hover:text-accent disabled:opacity-40"
              >
                Add
              </button>
            </div>
            <ul className="divide-y divide-border">
              {application.notes.map((note) => (
                <NoteRow key={note.id} note={note} onDelete={() => deleteNote(note.id)} />
              ))}
              {application.notes.length === 0 && <p className="text-sm text-faint">No notes yet.</p>}
            </ul>
          </div>
        </div>

        <div className="border-t border-border p-4">
          {!confirmingDelete ? (
            <button
              onClick={() => setConfirmingDelete(true)}
              className="label w-full border border-border-strong py-2 text-status-rejected hover:border-status-rejected"
            >
              Delete application
            </button>
          ) : (
            <div className="flex gap-2">
              <button
                onClick={handleDelete}
                disabled={busy}
                className="label flex-1 border border-status-rejected bg-status-rejected/10 py-2 text-status-rejected"
              >
                Confirm delete
              </button>
              <button
                onClick={() => setConfirmingDelete(false)}
                className="label flex-1 border border-border-strong py-2 text-muted"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </aside>
    </div>
  )
}
