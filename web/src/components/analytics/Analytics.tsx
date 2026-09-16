import { useEffect, useState } from "react"
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { api } from "../../api/client"
import type { Stats, Status } from "../../types"
import { STATUSES, STATUS_LABELS } from "../../types"
import { StatTile } from "./StatTile"

const STATUS_HEX: Record<Status, string> = {
  applied: "#7c8798",
  screening: "#22d3ee",
  interview: "#f5a524",
  offer: "#34d399",
  rejected: "#f87171",
}

function StatusBreakdown({ stats }: { stats: Stats }) {
  const total = stats.total || 1
  return (
    <div className="border border-border bg-panel p-4">
      <p className="label mb-4">Pipeline breakdown</p>
      <div className="mb-3 flex h-3 w-full overflow-hidden border border-border">
        {STATUSES.map((status) => {
          const count = stats.status_counts[status] ?? 0
          if (count === 0) return null
          return (
            <div
              key={status}
              style={{ width: `${(count / total) * 100}%`, backgroundColor: STATUS_HEX[status] }}
              title={`${STATUS_LABELS[status]}: ${count}`}
            />
          )
        })}
      </div>
      <ul className="grid grid-cols-2 gap-2 sm:grid-cols-5">
        {STATUSES.map((status) => (
          <li key={status} className="flex items-center gap-2">
            <span
              className="h-2 w-2 shrink-0 rounded-full"
              style={{ backgroundColor: STATUS_HEX[status] }}
              aria-hidden
            />
            <span className="text-xs text-muted">{STATUS_LABELS[status]}</span>
            <span className="mono ml-auto text-xs text-text">{stats.status_counts[status] ?? 0}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function OverTimeChart({ stats }: { stats: Stats }) {
  if (stats.applied_over_time.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center border border-dashed border-border">
        <span className="label text-faint">No applications in this window yet</span>
      </div>
    )
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={stats.applied_over_time} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="accentFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#1f262f" vertical={false} />
        <XAxis dataKey="date" tick={{ fill: "#7c8798", fontSize: 11 }} axisLine={{ stroke: "#1f262f" }} tickLine={false} />
        <YAxis allowDecimals={false} tick={{ fill: "#7c8798", fontSize: 11 }} axisLine={false} tickLine={false} width={28} />
        <Tooltip
          contentStyle={{ background: "#171c23", border: "1px solid #2a323d", borderRadius: 0, fontSize: 12 }}
          labelStyle={{ color: "#7c8798" }}
        />
        <Area
          type="monotone"
          dataKey="count"
          stroke="#22d3ee"
          strokeWidth={2}
          fill="url(#accentFill)"
          isAnimationActive={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export function Analytics() {
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    api.getStats().then(setStats)
  }, [])

  if (!stats) return <p className="label">Loading analytics…</p>

  const active = (stats.status_counts.applied ?? 0) + (stats.status_counts.screening ?? 0) + (stats.status_counts.interview ?? 0)

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatTile label="Total applications" value={String(stats.total)} />
        <StatTile label="Active" value={String(active)} accent />
        <StatTile label="Response rate" value={`${Math.round(stats.response_rate * 100)}%`} />
        <StatTile label="Interview rate" value={`${Math.round(stats.interview_rate * 100)}%`} />
      </div>
      <StatusBreakdown stats={stats} />
      <div className="border border-border bg-panel p-4">
        <p className="label mb-2">Applications over time</p>
        <OverTimeChart stats={stats} />
      </div>
    </div>
  )
}
