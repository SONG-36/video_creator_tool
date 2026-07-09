import { StatusBadge } from './StatusBadge'
import type { ReviewResult, Shot } from '../types/storyboard'

type ShotReviewCardProps = {
  shot: Shot
  isSubmitting: boolean
  onReview: (shotId: string, result: ReviewResult) => void
}

const REVIEW_ACTIONS: Array<{
  label: string
  value: ReviewResult
  style: string
}> = [
  {
    label: 'approved',
    value: 'approved',
    style: 'bg-emerald-900 text-white hover:bg-emerald-800',
  },
  {
    label: 'revision_required',
    value: 'revision_required',
    style: 'bg-amber-300 text-slate-950 hover:bg-amber-200',
  },
  {
    label: 'rejected',
    value: 'rejected',
    style: 'bg-rose-600 text-white hover:bg-rose-500',
  },
]

export function ShotReviewCard({
  shot,
  isSubmitting,
  onReview,
}: ShotReviewCardProps) {
  return (
    <article className="rounded-[1.8rem] border border-white/70 bg-white/82 p-6 shadow-[0_24px_72px_-52px_rgba(20,45,38,0.8)] backdrop-blur">
      <div className="flex flex-col gap-4 border-b border-slate-200/80 pb-4 md:flex-row md:items-start md:justify-between">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
            Shot {String(shot.shot_number).padStart(3, '0')}
          </p>
          <h3 className="text-2xl font-bold tracking-[-0.04em] text-slate-950">
            {shot.scene}
          </h3>
          <p className="text-sm leading-7 text-slate-600">{shot.purpose}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusBadge status={shot.review_status} />
          <StatusBadge status={shot.production_type} />
        </div>
      </div>

      <dl className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            shot描述
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">{shot.scene}</dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            action
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">{shot.action}</dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            camera
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">{shot.camera}</dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            时间
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">
            {shot.time_start}s - {shot.time_end}s
          </dd>
        </div>
      </dl>

      <div className="mt-5 flex flex-wrap gap-3">
        {REVIEW_ACTIONS.map((action) => (
          <button
            key={action.value}
            type="button"
            className={`rounded-full px-4 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${action.style}`}
            disabled={isSubmitting}
            onClick={() => onReview(shot.shot_id, action.value)}
          >
            {action.label}
          </button>
        ))}
      </div>
    </article>
  )
}
