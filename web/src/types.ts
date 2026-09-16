export type Status = "applied" | "screening" | "interview" | "offer" | "rejected"

export const STATUSES: Status[] = ["applied", "screening", "interview", "offer", "rejected"]

export const STATUS_LABELS: Record<Status, string> = {
  applied: "Applied",
  screening: "Screening",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
}

export interface Note {
  id: number
  application_id: number
  content: string
  kind: "note" | "interview"
  created_at: string
}

export interface Application {
  id: number
  company: string
  role: string
  salary: string | null
  location: string | null
  requirements: string[]
  status: Status
  source_url: string | null
  applied_date: string
  created_at: string
  updated_at: string
  notes: Note[]
}

export interface Stats {
  total: number
  status_counts: Partial<Record<Status, number>>
  applied_over_time: { date: string; count: number }[]
  response_rate: number
  interview_rate: number
}

export interface ActionRequest {
  name: string
  args: Record<string, unknown>
  description: string
}

export interface ReviewConfig {
  action_name: string
  allowed_decisions: string[]
}

export interface PendingInterrupt {
  interrupt_id: string
  thread_id: string
  action_requests: ActionRequest[]
  review_configs: ReviewConfig[]
}

export interface ChatMessage {
  role: "human" | "ai" | "assistant" | "system" | "unknown"
  content: string
  streaming?: boolean
}
