export function StatTile({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="border border-border bg-panel p-4">
      <p className="label">{label}</p>
      <p className={`mono mt-2 text-2xl font-semibold ${accent ? "text-accent" : "text-text"}`}>{value}</p>
    </div>
  )
}
