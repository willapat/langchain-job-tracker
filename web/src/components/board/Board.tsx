import { DndContext, KeyboardSensor, PointerSensor, useSensor, useSensors, type DragEndEvent } from "@dnd-kit/core"
import type { Application, Status } from "../../types"
import { STATUSES } from "../../types"
import { Column } from "./Column"

export function Board({
  applications,
  onOpen,
  onStatusChange,
}: {
  applications: Application[]
  onOpen: (application: Application) => void
  onStatusChange: (id: number, status: Status) => void
}) {
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor),
  )

  const byStatus = (status: Status) => applications.filter((a) => a.status === status)

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (!over) return
    const newStatus = over.id as Status
    const app = applications.find((a) => a.id === active.id)
    if (app && app.status !== newStatus) {
      onStatusChange(app.id, newStatus)
    }
  }

  return (
    <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
      <div className="flex h-[calc(100vh-9.5rem)] min-h-[420px] gap-3 overflow-x-auto pb-2">
        {STATUSES.map((status, i) => (
          <Column
            key={status}
            status={status}
            applications={byStatus(status)}
            onOpen={onOpen}
            onStatusChange={onStatusChange}
            style={{ animationDelay: `${i * 40}ms` }}
          />
        ))}
      </div>
    </DndContext>
  )
}
