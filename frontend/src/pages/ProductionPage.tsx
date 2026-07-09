import { Link, useParams } from 'react-router-dom'
import { AppShell } from '../components/AppShell'
import { AssetRequirementCard } from '../components/AssetRequirementCard'
import { ProductionPlanPanel } from '../components/ProductionPlanPanel'
import { useProductionPage } from '../hooks/useProductionPage'

export function ProductionPage() {
  const params = useParams()
  const shotId = params.shotId ?? ''
  const { plan, isLoading, isUploadingAssetKey, error, reload, uploadAsset } =
    useProductionPage(shotId)

  return (
    <AppShell
      title="AI 生产页面"
      subtitle="展示 AI Production Plan 和素材需求，并支持通过 Asset 管理接口上传参考素材。"
    >
      <section className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <article className="rounded-[1.8rem] border border-white/70 bg-white/80 p-6 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.75)]">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
            页面信息
          </p>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl bg-slate-100/80 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                Shot ID
              </p>
              <p className="mt-3 break-all text-sm font-semibold text-slate-950">
                {shotId}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-100/80 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                Production Task
              </p>
              <p className="mt-3 break-all text-sm font-semibold text-slate-950">
                {plan?.task_id ?? '加载中'}
              </p>
            </div>
            <div className="rounded-2xl bg-slate-100/80 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                Asset Requirement
              </p>
              <p className="mt-3 text-3xl font-bold tracking-[-0.04em] text-slate-950">
                {plan?.asset_requirement.length ?? 0}
              </p>
            </div>
          </div>
        </article>

        <aside className="rounded-[1.8rem] border border-white/70 bg-[linear-gradient(180deg,rgba(20,45,38,0.96),rgba(33,65,54,0.92))] p-6 text-emerald-50 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.82)]">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-100/70">
            资产准备
          </p>
          <p className="mt-3 text-sm leading-7 text-emerald-50/88">
            本页只负责展示 Production Plan 与上传素材，不创建视频生成按钮，也不进入真实视频 API 调用。
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => void reload()}
              className="rounded-full bg-amber-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-amber-200"
            >
              刷新 Production Plan
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
            正在加载 AI Production Plan...
          </div>
        ) : null}

        {!isLoading && plan ? <ProductionPlanPanel plan={plan} /> : null}

        {!isLoading && plan
          ? plan.asset_requirement.map((asset) => (
              <AssetRequirementCard
                key={asset.asset_id}
                asset={asset}
                isUploading={
                  isUploadingAssetKey === `${asset.role}:${asset.reference_tag}`
                }
                onUpload={(role, referenceTag, requirementNote, file) => {
                  void uploadAsset(role, referenceTag, requirementNote, file)
                }}
              />
            ))
          : null}
      </section>
    </AppShell>
  )
}
