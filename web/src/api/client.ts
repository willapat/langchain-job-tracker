import type { Application, Note, Stats } from "../types"

class ApiError extends Error {
  status: number
  detail: unknown
  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : JSON.stringify(detail))
    this.status = status
    this.detail = detail
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  })
  if (!res.ok) {
    let detail: unknown
    try {
      detail = (await res.json()).detail
    } catch {
      detail = res.statusText
    }
    throw new ApiError(res.status, detail)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export { ApiError }

export const api = {
  listApplications: (status?: string) =>
    request<Application[]>(`/api/applications${status ? `?status=${status}` : ""}`),
  createApplication: (payload: Partial<Application>) =>
    request<Application>("/api/applications", { method: "POST", body: JSON.stringify(payload) }),
  updateApplication: (id: number, payload: Partial<Application>) =>
    request<Application>(`/api/applications/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteApplication: (id: number) => request<void>(`/api/applications/${id}`, { method: "DELETE" }),

  addNote: (applicationId: number, content: string, kind: "note" | "interview" = "note") =>
    request<Note>(`/api/applications/${applicationId}/notes`, {
      method: "POST",
      body: JSON.stringify({ content, kind }),
    }),
  updateNote: (noteId: number, content: string) =>
    request<Note>(`/api/notes/${noteId}`, { method: "PATCH", body: JSON.stringify({ content }) }),
  deleteNote: (noteId: number) => request<void>(`/api/notes/${noteId}`, { method: "DELETE" }),

  getStats: () => request<Stats>("/api/stats"),
}
