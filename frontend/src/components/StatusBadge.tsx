type StatusBadgeProps = {
  status: string
}

const STATUS_STYLES: Record<string, string> = {
  waiting_review: 'bg-amber-100 text-amber-900',
  reviewing: 'bg-amber-100 text-amber-900',
  approved: 'bg-emerald-100 text-emerald-900',
  revision_required: 'bg-orange-100 text-orange-900',
  rejected: 'bg-rose-100 text-rose-900',
  pending: 'bg-slate-100 text-slate-700',
  queued: 'bg-sky-100 text-sky-900',
  running: 'bg-cyan-100 text-cyan-900',
  generating: 'bg-cyan-100 text-cyan-900',
  completed: 'bg-emerald-100 text-emerald-900',
  failed: 'bg-rose-100 text-rose-900',
  uploaded: 'bg-sky-100 text-sky-900',
  ai_generate: 'bg-cyan-100 text-cyan-900',
  real_shoot: 'bg-violet-100 text-violet-900',
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${
        STATUS_STYLES[status] ?? 'bg-slate-100 text-slate-700'
      }`}
    >
      {status}
    </span>
  )
}
