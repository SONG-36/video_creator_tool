import { apiConfig } from '../api/client'
import { AppShell } from '../components/AppShell'
import { StatCard } from '../components/StatCard'
import { useDashboardMetrics } from '../hooks/useDashboardMetrics'
import { Link } from 'react-router-dom'

export function Dashboard() {
  const { metrics, recentProjects } = useDashboardMetrics()

  return (
    <AppShell
      title="生产工作台 Dashboard"
      subtitle="用于承接项目总览与流程入口。当前阶段仅提供可启动的前端骨架、静态数据展示和 API 基础配置，不连接后端业务接口。"
    >
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <StatCard
            key={metric.label}
            label={metric.label}
            value={metric.value}
            accent={metric.accent}
          />
        ))}
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-[1.35fr_0.9fr]">
        <article className="rounded-[1.8rem] border border-white/70 bg-white/78 p-6 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.7)] backdrop-blur">
          <div className="flex items-end justify-between gap-4 border-b border-slate-200/80 pb-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                最近项目
              </p>
              <h2 className="mt-2 text-2xl font-bold tracking-[-0.04em] text-slate-950">
                当前生产进度
              </h2>
            </div>
            <button
              type="button"
              className="rounded-full border border-slate-300 bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700"
            >
              创建项目
            </button>
          </div>

          <div className="mt-4 overflow-hidden rounded-[1.4rem] border border-slate-200/80">
            <div className="grid grid-cols-[1.6fr_1.1fr_1fr_1fr] bg-slate-100/90 px-4 py-3 text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
              <span>项目名称</span>
              <span>产品</span>
              <span>当前阶段</span>
              <span>状态</span>
            </div>
            <div className="divide-y divide-slate-200/80 bg-white/85">
              {recentProjects.map((project) => (
                <div
                  key={project.id}
                  className="grid grid-cols-1 gap-2 px-4 py-4 text-sm text-slate-700 md:grid-cols-[1.6fr_1.1fr_1fr_1fr]"
                >
                  <div>
                    <p className="font-semibold text-slate-950">{project.name}</p>
                    <p className="mt-1 text-xs uppercase tracking-[0.18em] text-slate-400">
                      {project.id} · {project.updatedAt}
                    </p>
                  </div>
                  <span>{project.product}</span>
                  <span>{project.stage}</span>
                  <span className="font-semibold text-emerald-800">
                    {project.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </article>

        <aside className="rounded-[1.8rem] border border-white/70 bg-[linear-gradient(180deg,rgba(20,45,38,0.96),rgba(33,65,54,0.92))] p-6 text-emerald-50 shadow-[0_28px_80px_-50px_rgba(20,45,38,0.82)]">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-100/70">
            Frontend Bootstrap
          </p>
          <h2 className="mt-3 text-2xl font-bold tracking-[-0.04em]">
            基础配置已就绪
          </h2>
          <div className="mt-6 space-y-4 text-sm leading-7 text-emerald-50/85">
            <p>React、TypeScript、Tailwind CSS 已初始化。</p>
            <p>页面入口当前固定为 Dashboard，后续 Task 再逐步接入业务流程页面。</p>
            <p className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3 font-medium">
              API Base URL: {apiConfig.baseUrl}
            </p>
          </div>
          <div className="mt-8 grid gap-3">
            <div className="rounded-2xl bg-white/8 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-emerald-100/70">
                当前限制
              </p>
              <p className="mt-2 text-sm text-emerald-50/88">
                当前前端只接入 Storyboard 审核页与 AI 生产页，不包含 Generation 页面，也不触发真实视频生成。
              </p>
            </div>
            <div className="rounded-2xl bg-white/8 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-emerald-100/70">
                下一阶段
              </p>
              <p className="mt-2 text-sm text-emerald-50/88">
                在后续 Task 中继续接入视频生成任务与更完整的生产状态追踪。
              </p>
            </div>
            <Link
              to="/storyboards/storyboard_demo/review"
              className="inline-flex rounded-2xl bg-amber-300 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-amber-200"
            >
              打开 Storyboard 审核页
            </Link>
            <Link
              to="/shots/shot_demo/production"
              className="inline-flex rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-50"
            >
              打开 AI 生产页
            </Link>
          </div>
        </aside>
      </section>
    </AppShell>
  )
}
