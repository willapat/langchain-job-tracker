import { useDroppable } from "@dnd-kit/core"
import type { CSSProperties } from "react"
import type { Application, Status } from "../../types"
import { STATUS_LABELS } from "../../types"
import { Card } from "./Card"

const ACCENT: Record<Status, string> = {
  applied: "border-t-status-applied",
  screening: "border-t-status-screening",
  interview: "border-t-status-interview",
  offer: "border-t-status-offer",
  rejected: "border-t-status-rejected",
}

export function Column({
  status,
  applications,
  onOpen,
  onStatusChange,
  style,
}: {
  status: Status
  applications: Application[]
  onOpen: (application: Application) => void
  onStatusChange: (id: number, status: Status) => void
  style?: CSSProperties
}) {
  const { setNodeRef, isOver } = useDroppable({ id: status })

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex h-full min-w-[260px] flex-1 flex-col animate-fadeInUp border border-border border-t-2 bg-panel/40 transition-colors duration-150 ${ACCENT[status]} ${
        isOver ? "bg-panel" : ""
      }`}
    >
      <div className="flex shrink-0 items-center justify-between border-b border-border px-3 py-2">
        <span className="label text-text">{STATUS_LABELS[status]}</span>
        <span className="mono text-xs text-faint">{applications.length}</span>
      </div>
      <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto p-2">
        {applications.map((app) => (
          <Card
            key={app.id}
            application={app}
            onOpen={() => onOpen(app)}
            onStatusChange={(s) => onStatusChange(app.id, s)}
          />
        ))}
        {applications.length === 0 && (
          <div className="flex flex-1 items-center justify-center border border-dashed border-border p-4">
            <span className="label text-faint">Empty</span>
          </div>
        )}
      </div>
    </div>
  )
}
