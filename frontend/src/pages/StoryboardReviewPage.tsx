import { Link, useParams } from 'react-router-dom'
import { AppShell } from '../components/AppShell'
import { ShotReviewCard } from '../components/ShotReviewCard'
import { useStoryboardReview } from '../hooks/useStoryboardReview'

export function StoryboardReviewPage() {
  const params = useParams()
  const storyboardId = params.storyboardId ?? ''
  const {
    shots,
    summary,
    isLoading,
    isSubmittingShotId,
    error,
    reviewShotById,
    reload,
  } = useStoryboardReview(storyboardId)

  return (
    <AppShell
      title="Storyboard 审核"
      subtitle="查看 Storyboard 信息、逐镜头审核 shot 描述、action、camera 与状态，并在审核成功后刷新对应 Shot 状态。"
    >
      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-[1.8rem] border border-white/70 bg-white/80 p-6 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.75)]">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
            Storyboard 信息
          </p>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl bg-slate-100/80 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                Storyboard ID
              </p>
              <p className="mt-3 break-all text-sm font-semibold text-slate-950">
                {summary.storyboardId}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-100/80 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                Shot 数量
              </p>
              <p className="mt-3 text-3xl font-bold tracking-[-0.04em] text-slate-950">
                {summary.shotCount}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-100/80 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                待审核
              </p>
              <p className="mt-3 text-3xl font-bold tracking-[-0.04em] text-amber-700">
                {summary.waitingCount}
              </p>
            </div>
          </div>
        </article>

        <aside className="rounded-[1.8rem] border border-white/70 bg-[linear-gradient(180deg,rgba(20,45,38,0.96),rgba(33,65,54,0.92))] p-6 text-emerald-50 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.82)]">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-100/70">
            审核工作流
          </p>
          <p className="mt-3 text-sm leading-7 text-emerald-50/88">
            点击审核按钮后将调用后端 `/shots/{'{shot_id}'}/review`，成功后刷新对应 Shot 的最新状态。
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => void reload()}
              className="rounded-full bg-amber-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-amber-200"
            >
              刷新 Shot 列表
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

      <section className="mt-6 space-y-4">
        {isLoading ? (
          <div className="rounded-[1.8rem] border border-white/70 bg-white/80 px-6 py-10 text-sm text-slate-600 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.75)]">
            正在加载 Shot 列表...
          </div>
        ) : null}

        {!isLoading && shots.length === 0 ? (
          <div className="rounded-[1.8rem] border border-white/70 bg-white/80 px-6 py-10 text-sm text-slate-600 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.75)]">
            当前 Storyboard 暂无 Shot 数据。
          </div>
        ) : null}

        {!isLoading
          ? shots.map((shot) => (
              <ShotReviewCard
                key={shot.shot_id}
                shot={shot}
                isSubmitting={isSubmittingShotId === shot.shot_id}
                onReview={(shotId, result) => {
                  void reviewShotById(shotId, result)
                }}
              />
            ))
          : null}
      </section>
    </AppShell>
  )
}
