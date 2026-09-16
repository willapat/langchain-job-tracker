import { useDraggable } from "@dnd-kit/core"
import type { Application, Status } from "../../types"
import { STATUSES, STATUS_LABELS } from "../../types"

export function Card({
  application,
  onOpen,
  onStatusChange,
}: {
  application: Application
  onOpen: () => void
  onStatusChange: (status: Status) => void
}) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: application.id,
  })

  const style = transform
    ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)` }
    : undefined

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`group border border-border bg-panel p-3 transition-all duration-150 ease-out ${
        isDragging
          ? "z-10 scale-[1.02] border-accent/50 opacity-70 shadow-[0_8px_24px_rgba(0,0,0,0.4)]"
          : "hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-[0_4px_16px_rgba(0,0,0,0.35)]"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <button
          {...listeners}
          {...attributes}
          onClick={onOpen}
          className="cursor-grab text-left text-sm font-semibold leading-tight text-text transition-colors hover:text-accent active:cursor-grabbing"
        >
          {application.company}
        </button>
        <div className="flex shrink-0 items-center gap-1">
          {application.source_url && (
            <a
              href={application.source_url}
              target="_blank"
              rel="noreferrer"
              onClick={(e) => e.stopPropagation()}
              title="Open original posting"
              aria-label={`Open original posting for ${application.company}`}
              className="text-faint opacity-0 transition-opacity hover:text-accent group-hover:opacity-100"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <path d="M15 3h6v6" />
                <path d="M10 14 21 3" />
              </svg>
            </a>
          )}
          <label className="sr-only" htmlFor={`status-${application.id}`}>
            Change status for {application.company}
          </label>
          <select
            id={`status-${application.id}`}
            value={application.status}
            onChange={(e) => onStatusChange(e.target.value as Status)}
            className="mono border border-border bg-panel-raised px-1 py-0.5 text-[10px] text-muted opacity-0 transition-opacity focus:opacity-100 group-hover:opacity-100"
            aria-label={`Change status for ${application.company}`}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABELS[s]}
              </option>
            ))}
          </select>
        </div>
      </div>
      <p className="mt-1 truncate text-xs text-muted">{application.role}</p>
      {application.salary && <p className="mono mt-2 text-[11px] text-faint">{application.salary}</p>}
      {application.notes.length > 0 && (
        <p className="label mt-2 text-accent/70">{application.notes.length} note{application.notes.length > 1 ? "s" : ""}</p>
      )}
    </div>
  )
}
