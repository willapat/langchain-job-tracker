import { useCallback, useEffect, useState } from "react"
import { api } from "../api/client"
import type { Application, Status } from "../types"

export function useApplications() {
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      setError(null)
      const data = await api.listApplications()
      setApplications(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load applications.")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const setStatus = useCallback(
    async (id: number, status: Status) => {
      const previous = applications
      setApplications((prev) => prev.map((a) => (a.id === id ? { ...a, status } : a)))
      try {
        await api.updateApplication(id, { status })
      } catch (err) {
        setApplications(previous) // rollback optimistic update on failure
        setError(err instanceof Error ? err.message : "Failed to update status.")
      }
    },
    [applications],
  )

  const remove = useCallback(async (id: number) => {
    await api.deleteApplication(id)
    setApplications((prev) => prev.filter((a) => a.id !== id))
  }, [])

  return { applications, loading, error, refresh, setStatus, remove }
}
