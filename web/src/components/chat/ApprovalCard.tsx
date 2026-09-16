import { useState } from "react"
import type { PendingInterrupt } from "../../types"

export function ApprovalCard({
  interrupt,
  onResolve,
}: {
  interrupt: PendingInterrupt
  onResolve: (approve: boolean, reason?: string) => void
}) {
  const [reason, setReason] = useState("")
  const [rejecting, setRejecting] = useState(false)

  return (
    <div className="border border-status-interview/40 bg-status-interview/10 p-3">
      <p className="label mb-2 text-status-interview">Approval needed</p>
      {interrupt.action_requests.map((action, i) => (
        <p key={i} className="mb-2 whitespace-pre-wrap text-sm text-text">
          {action.description}
        </p>
      ))}

      {!rejecting ? (
        <div className="flex gap-2">
          <button
            onClick={() => onResolve(true)}
            className="label flex-1 border border-status-offer/50 bg-status-offer/10 py-1.5 text-status-offer"
          >
            Approve
          </button>
          <button
            onClick={() => setRejecting(true)}
            className="label flex-1 border border-status-rejected/50 bg-status-rejected/10 py-1.5 text-status-rejected"
          >
            Reject
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <input
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Reason (optional)"
            className="border border-border bg-panel px-2 py-1 text-xs text-text placeholder:text-faint"
            autoFocus
          />
          <div className="flex gap-2">
            <button
              onClick={() => onResolve(false, reason)}
              className="label flex-1 border border-status-rejected/50 bg-status-rejected/10 py-1.5 text-status-rejected"
            >
              Confirm reject
            </button>
            <button onClick={() => setRejecting(false)} className="label flex-1 border border-border-strong py-1.5 text-muted">
              Back
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
