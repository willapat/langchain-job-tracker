import ReactMarkdown from "react-markdown"
import type { Components } from "react-markdown"

const components: Components = {
  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold text-text">{children}</strong>,
  h1: ({ children }) => <p className="label mb-1.5 mt-3 text-accent first:mt-0">{children}</p>,
  h2: ({ children }) => <p className="label mb-1.5 mt-3 text-accent first:mt-0">{children}</p>,
  h3: ({ children }) => <p className="label mb-1.5 mt-3 text-accent first:mt-0">{children}</p>,
  ul: ({ children }) => <ul className="mb-2 list-inside list-disc space-y-1 last:mb-0">{children}</ul>,
  ol: ({ children }) => <ol className="mb-2 list-inside list-decimal space-y-1 last:mb-0">{children}</ol>,
  li: ({ children }) => <li className="text-sm">{children}</li>,
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noreferrer" className="text-accent hover:underline">
      {children}
    </a>
  ),
  code: ({ children }) => <code className="mono border border-border bg-panel-raised px-1 py-0.5 text-xs">{children}</code>,
}

export function MarkdownMessage({ content }: { content: string }) {
  return (
    <div className="text-sm leading-relaxed text-text [&>*:last-child]:mb-0">
      <ReactMarkdown components={components}>{content}</ReactMarkdown>
    </div>
  )
}
