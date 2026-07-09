import { formatMetricValue } from '../utils/format'

type StatCardProps = {
  label: string
  value: number
  accent: string
}

export function StatCard({ label, value, accent }: StatCardProps) {
  return (
    <article className="rounded-[1.6rem] border border-white/70 bg-white/78 p-5 shadow-[0_22px_60px_-44px_rgba(20,45,38,0.7)] backdrop-blur">
      <div
        className="mb-6 h-2.5 w-16 rounded-full"
        style={{ background: accent }}
      />
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
        {label}
      </p>
      <p className="mt-3 text-4xl font-bold tracking-[-0.05em] text-slate-950">
        {formatMetricValue(value)}
      </p>
    </article>
  )
}
