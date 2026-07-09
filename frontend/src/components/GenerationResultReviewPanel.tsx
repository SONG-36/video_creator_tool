import { StatusBadge } from './StatusBadge'
import type { GenerationResult, GenerationTaskSummary } from '../types/generation'

type GenerationResultReviewPanelProps = {
  result: GenerationResult
  promptDraft: string
  isSubmitting: boolean
  lastCreatedTask: GenerationTaskSummary | null
  onPromptDraftChange: (value: string) => void
  onApprove: () => void
  onRegenerate: () => void
  onRevisePrompt: () => void
}

export function GenerationResultReviewPanel({
  result,
  promptDraft,
  isSubmitting,
  lastCreatedTask,
  onPromptDraftChange,
  onApprove,
  onRegenerate,
  onRevisePrompt,
}: GenerationResultReviewPanelProps) {
  const videoSource = result.video_url || result.video_path
  const isPromptChanged = promptDraft.trim() !== '' && promptDraft !== result.prompt

  return (
    <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <article className="rounded-[1.8rem] border border-white/70 bg-white/82 p-6 shadow-[0_24px_72px_-52px_rgba(20,45,38,0.8)] backdrop-blur">
        <div className="flex flex-col gap-4 border-b border-slate-200/80 pb-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
              视频播放器
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-[-0.04em] text-slate-950">
              Generation v{result.version}
            </h2>
          </div>
          <div className="flex flex-wrap gap-2">
            <StatusBadge status={result.status} />
            <StatusBadge status={result.review_status} />
          </div>
        </div>

        <div className="mt-5 overflow-hidden rounded-[1.6rem] bg-slate-950 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.04)]">
          <video
            aria-label="视频播放器"
            controls
            className="h-full min-h-[280px] w-full bg-slate-950 object-contain"
          >
            {videoSource ? <source src={videoSource} /> : null}
          </video>
        </div>

        <dl className="mt-5 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl bg-slate-100/80 p-4">
            <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Shot
            </dt>
            <dd className="mt-2 text-sm leading-7 text-slate-700">{result.shot_id}</dd>
          </div>
          <div className="rounded-2xl bg-slate-100/80 p-4">
            <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Provider
            </dt>
            <dd className="mt-2 text-sm leading-7 text-slate-700">
              {result.provider}
            </dd>
          </div>
          <div className="rounded-2xl bg-slate-100/80 p-4 md:col-span-2">
            <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Prompt
            </dt>
            <dd className="mt-2 text-sm leading-7 text-slate-700">{result.prompt}</dd>
          </div>
          <div className="rounded-2xl bg-slate-100/80 p-4">
            <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Camera
            </dt>
            <dd className="mt-2 text-sm leading-7 text-slate-700">{result.camera}</dd>
          </div>
          <div className="rounded-2xl bg-slate-100/80 p-4">
            <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Motion
            </dt>
            <dd className="mt-2 text-sm leading-7 text-slate-700">{result.motion}</dd>
          </div>
          <div className="rounded-2xl bg-slate-100/80 p-4 md:col-span-2">
            <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Lighting
            </dt>
            <dd className="mt-2 text-sm leading-7 text-slate-700">{result.lighting}</dd>
          </div>
        </dl>
      </article>

      <aside className="rounded-[1.8rem] border border-white/70 bg-[linear-gradient(180deg,rgba(20,45,38,0.96),rgba(33,65,54,0.92))] p-6 text-emerald-50 shadow-[0_24px_72px_-52px_rgba(20,45,38,0.82)]">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-100/70">
          审核信息
        </p>
        <div className="mt-4 grid gap-4">
          <div className="rounded-2xl bg-white/8 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-emerald-100/70">
              Generation 版本
            </p>
            <p className="mt-3 text-3xl font-bold tracking-[-0.04em]">
              v{result.version}
            </p>
          </div>
          <div className="rounded-2xl bg-white/8 p-4">
            <label
              htmlFor="prompt-editor"
              className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-100/70"
            >
              Prompt 修改
            </label>
            <textarea
              id="prompt-editor"
              value={promptDraft}
              onChange={(event) => onPromptDraftChange(event.target.value)}
              className="mt-3 min-h-[180px] w-full rounded-2xl border border-white/10 bg-slate-950/35 px-4 py-3 text-sm leading-7 text-white outline-none ring-0 transition placeholder:text-emerald-50/35 focus:border-amber-300"
            />
          </div>
          <div className="grid gap-3">
            <button
              type="button"
              disabled={isSubmitting}
              onClick={onApprove}
              className="rounded-full bg-emerald-300 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-60"
            >
              通过
            </button>
            <button
              type="button"
              disabled={isSubmitting}
              onClick={onRegenerate}
              className="rounded-full bg-rose-400 px-4 py-3 text-sm font-semibold text-white transition hover:bg-rose-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              重新生成
            </button>
            <button
              type="button"
              disabled={isSubmitting || !isPromptChanged}
              onClick={onRevisePrompt}
              className="rounded-full bg-amber-300 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-amber-200 disabled:cursor-not-allowed disabled:opacity-60"
            >
              修改Prompt
            </button>
          </div>

          {lastCreatedTask ? (
            <div className="rounded-2xl border border-emerald-200/20 bg-white/8 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-emerald-100/70">
                新任务已创建
              </p>
              <p className="mt-2 break-all text-sm font-semibold text-white">
                {lastCreatedTask.task_id}
              </p>
              <p className="mt-2 text-sm text-emerald-50/80">
                状态：{lastCreatedTask.status}
              </p>
            </div>
          ) : null}
        </div>
      </aside>
    </section>
  )
}
