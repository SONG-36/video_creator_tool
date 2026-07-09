type StatusBadgeProps = {
  status: string
}

const STATUS_STYLES: Record<string, string> = {
  waiting_review: 'bg-amber-100 text-amber-900',
  approved: 'bg-emerald-100 text-emerald-900',
  revision_required: 'bg-orange-100 text-orange-900',
  rejected: 'bg-rose-100 text-rose-900',
  pending: 'bg-slate-100 text-slate-700',
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
