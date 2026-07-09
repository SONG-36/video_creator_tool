import type { PropsWithChildren } from 'react'

type AppShellProps = PropsWithChildren<{
  title: string
  subtitle: string
}>

export function AppShell({ title, subtitle, children }: AppShellProps) {
  return (
    <div className="min-h-screen px-4 py-6 text-slate-900 sm:px-6 lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="overflow-hidden rounded-[2rem] border border-white/60 bg-white/75 shadow-[0_30px_120px_-48px_rgba(16,35,29,0.65)] backdrop-blur">
          <div className="grid gap-5 px-6 py-8 sm:px-8 lg:grid-cols-[1.4fr_0.9fr] lg:px-10 lg:py-10">
            <div className="space-y-4">
              <p className="inline-flex rounded-full bg-emerald-900 px-3 py-1 text-xs font-semibold uppercase tracking-[0.28em] text-emerald-50">
                Video Creator Tool
              </p>
              <div className="space-y-3">
                <h1 className="max-w-3xl text-4xl leading-none font-bold tracking-[-0.05em] text-slate-950 sm:text-5xl">
                  {title}
                </h1>
                <p className="max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">
                  {subtitle}
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 rounded-[1.75rem] bg-[linear-gradient(160deg,#18392f_0%,#264e41_48%,#315f4d_100%)] p-4 text-emerald-50">
              <div className="rounded-2xl bg-white/8 p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-emerald-100/70">
                  Phase
                </p>
                <p className="mt-3 text-2xl font-semibold">Frontend</p>
              </div>
              <div className="rounded-2xl bg-white/8 p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-emerald-100/70">
                  Task
                </p>
                <p className="mt-3 text-2xl font-semibold">012</p>
              </div>
              <div className="col-span-2 rounded-2xl border border-white/10 bg-white/6 p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-emerald-100/70">
                  Workspace State
                </p>
                <p className="mt-2 text-sm leading-6 text-emerald-50/88">
                  React + TypeScript + Tailwind is initialized. Dashboard is the
                  only active page in this phase.
                </p>
              </div>
            </div>
          </div>
        </header>

        <main>{children}</main>
      </div>
    </div>
  )
}
