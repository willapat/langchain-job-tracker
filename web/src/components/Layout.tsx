import { NavLink } from "react-router-dom"
import type { ReactNode } from "react"

function NavItem({ to, children }: { to: string; children: ReactNode }) {
  return (
    <NavLink to={to} className="group relative px-3 py-1.5">
      {({ isActive }) => (
        <>
          <span className={`label transition-colors ${isActive ? "text-accent" : "text-muted group-hover:text-text"}`}>
            {children}
          </span>
          <span
            className={`absolute inset-x-3 -bottom-px h-px origin-left bg-accent transition-transform duration-200 ${
              isActive ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"
            }`}
          />
        </>
      )}
    </NavLink>
  )
}

export function Layout({
  children,
  onAddApplication,
  onToggleChat,
  chatOpen,
  assistantNeedsAttention,
}: {
  children: ReactNode
  onAddApplication: () => void
  onToggleChat: () => void
  chatOpen: boolean
  assistantNeedsAttention?: boolean
}) {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-border bg-canvas/90 backdrop-blur">
        <div className="mx-auto flex max-w-[1600px] items-center gap-6 px-6 py-3">
          <div className="flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-accent">
              <path
                d="M12 2 L21 20 L12 16 L3 20 Z"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinejoin="round"
              />
            </svg>
            <span className="text-sm font-bold tracking-wide">WAYPOINT</span>
          </div>
          <nav className="flex items-center gap-1">
            <NavItem to="/">Board</NavItem>
            <NavItem to="/analytics">Analytics</NavItem>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={onAddApplication}
              className="label border border-border-strong px-3 py-1.5 text-text transition-all duration-150 hover:border-accent hover:text-accent active:scale-95"
            >
              + Add application
            </button>
            <button
              onClick={onToggleChat}
              className={`label relative border px-3 py-1.5 transition-all duration-150 active:scale-95 ${
                chatOpen
                  ? "border-accent/40 bg-accent/10 text-accent"
                  : "border-border-strong text-text hover:border-accent hover:text-accent"
              }`}
            >
              Assistant
              {assistantNeedsAttention && (
                <span className="absolute -right-1 -top-1 flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-status-interview opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-status-interview" />
                </span>
              )}
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-[1600px] px-6 py-6">{children}</main>
    </div>
  )
}
