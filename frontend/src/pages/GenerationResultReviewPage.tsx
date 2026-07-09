import { Link, useParams } from 'react-router-dom'
import { AppShell } from '../components/AppShell'
import { GenerationResultReviewPanel } from '../components/GenerationResultReviewPanel'
import { useGenerationResultReview } from '../hooks/useGenerationResultReview'

export function GenerationResultReviewPage() {
  const params = useParams()
  const resultId = params.resultId ?? ''
  const {
    result,
    promptDraft,
    isLoading,
    isSubmitting,
    error,
    lastCreatedTask,
    setPromptDraft,
    approveResult,
    regenerateResult,
    revisePrompt,
    reload,
  } = useGenerationResultReview(resultId)

  return (
    <AppShell
      title="视频结果审核"
      subtitle="查看生成视频、核对 Prompt 与镜头参数，并通过、重生成或修改 Prompt 触发新的 GenerationTask。"
    >
      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-[1.8rem] border border-white/70 bg-white/80 p-6 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.75)]">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
            Result 信息
          </p>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl bg-slate-100/80 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                Result ID
              </p>
              <p className="mt-3 break-all text-sm font-semibold text-slate-950">
                {resultId}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-100/80 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                当前版本
              </p>
              <p className="mt-3 text-3xl font-bold tracking-[-0.04em] text-slate-950">
                {result ? `v${result.version}` : '-'}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-100/80 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                新任务
              </p>
              <p className="mt-3 break-all text-sm font-semibold text-slate-950">
                {lastCreatedTask?.task_id ?? '未创建'}
              </p>
            </div>
          </div>
        </article>

        <aside className="rounded-[1.8rem] border border-white/70 bg-[linear-gradient(180deg,rgba(20,45,38,0.96),rgba(33,65,54,0.92))] p-6 text-emerald-50 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.82)]">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-100/70">
            审核闭环
          </p>
          <p className="mt-3 text-sm leading-7 text-emerald-50/88">
            审核接口会保存 GenerationReview。重生成和修改 Prompt 都会保留当前结果，并创建新的 GenerationTask。
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => void reload()}
              className="rounded-full bg-amber-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-amber-200"
            >
              刷新结果
            </button>
            <Link
              to="/"
              className="rounded-full border border-white/20 px-4 py-2 text-sm font-semibold text-white/92 transition hover:bg-white/8"
            >
              返回 Dashboard
            </Link>
          </div>
        </aside>
      </section>

      {error ? (
        <div className="mt-6 rounded-[1.5rem] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <section className="mt-6">
        {isLoading ? (
          <div className="rounded-[1.8rem] border border-white/70 bg-white/80 px-6 py-10 text-sm text-slate-600 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.75)]">
            正在加载视频结果...
          </div>
        ) : null}

        {!isLoading && result ? (
          <GenerationResultReviewPanel
            result={result}
            promptDraft={promptDraft}
            isSubmitting={isSubmitting}
            lastCreatedTask={lastCreatedTask}
            onPromptDraftChange={setPromptDraft}
            onApprove={() => {
              void approveResult()
            }}
            onRegenerate={() => {
              void regenerateResult()
            }}
            onRevisePrompt={() => {
              void revisePrompt()
            }}
          />
        ) : null}
      </section>
    </AppShell>
  )
}
