import { StatusBadge } from './StatusBadge'
import type { ProductionPlan } from '../types/production'

type ProductionPlanPanelProps = {
  plan: ProductionPlan
}

export function ProductionPlanPanel({ plan }: ProductionPlanPanelProps) {
  return (
    <article className="rounded-[1.8rem] border border-white/70 bg-white/82 p-6 shadow-[0_24px_72px_-52px_rgba(20,45,38,0.8)] backdrop-blur">
      <div className="flex flex-col gap-4 border-b border-slate-200/80 pb-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
            AI Production Plan
          </p>
          <h2 className="mt-2 text-3xl font-bold tracking-[-0.04em] text-slate-950">
            Shot {plan.shot_id}
          </h2>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusBadge status={plan.generation_mode} />
          <StatusBadge status={plan.status} />
        </div>
      </div>

      <dl className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            generation_mode
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">
            {plan.generation_mode}
          </dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            negative_prompt
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">
            {plan.negative_prompt || '无'}
          </dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4 md:col-span-2">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            prompt
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">{plan.prompt}</dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            camera
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">{plan.camera}</dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            motion
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">{plan.motion}</dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4 md:col-span-2">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            lighting
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">{plan.lighting}</dd>
        </div>
      </dl>
    </article>
  )
}
