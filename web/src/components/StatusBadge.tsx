import type { Status } from "../types"
import { STATUS_LABELS } from "../types"

const DOT_COLOR: Record<Status, string> = {
  applied: "bg-status-applied",
  screening: "bg-status-screening",
  interview: "bg-status-interview",
  offer: "bg-status-offer",
  rejected: "bg-status-rejected",
}

export function StatusBadge({ status }: { status: Status }) {
  return (
    <span className="label inline-flex items-center gap-1.5 text-muted">
      <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT_COLOR[status]}`} aria-hidden />
      {STATUS_LABELS[status]}
    </span>
  )
}
