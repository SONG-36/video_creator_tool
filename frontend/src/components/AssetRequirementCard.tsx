import { useId } from 'react'
import { StatusBadge } from './StatusBadge'
import type { AssetRequirement } from '../types/production'

type AssetRequirementCardProps = {
  asset: AssetRequirement
  isUploading: boolean
  onUpload: (
    role: string,
    referenceTag: string,
    requirementNote: string,
    file: File,
  ) => void
}

export function AssetRequirementCard({
  asset,
  isUploading,
  onUpload,
}: AssetRequirementCardProps) {
  const inputId = useId()

  return (
    <article className="rounded-[1.8rem] border border-white/70 bg-white/82 p-6 shadow-[0_24px_72px_-52px_rgba(20,45,38,0.8)] backdrop-blur">
      <div className="flex flex-col gap-3 border-b border-slate-200/80 pb-4 md:flex-row md:items-start md:justify-between">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
            Asset Requirement
          </p>
          <h3 className="text-2xl font-bold tracking-[-0.04em] text-slate-950">
            {asset.role}
          </h3>
          <p className="text-sm text-slate-500">{asset.reference_tag}</p>
        </div>
        <StatusBadge status={asset.status} />
      </div>

      <dl className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            role
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">{asset.role}</dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            reference_tag
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">
            {asset.reference_tag}
          </dd>
        </div>
        <div className="rounded-2xl bg-slate-100/80 p-4 md:col-span-2">
          <dt className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            requirement_note
          </dt>
          <dd className="mt-2 text-sm leading-7 text-slate-700">
            {asset.requirement_note}
          </dd>
        </div>
      </dl>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <label
          htmlFor={inputId}
          className="inline-flex cursor-pointer rounded-full bg-emerald-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-800"
        >
          {isUploading ? '上传中...' : '上传素材'}
        </label>
        <input
          id={inputId}
          type="file"
          className="sr-only"
          disabled={isUploading}
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (!file) {
              return
            }
            onUpload(
              asset.role,
              asset.reference_tag,
              asset.requirement_note,
              file,
            )
            event.currentTarget.value = ''
          }}
        />
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
          当前状态将于上传成功后自动刷新
        </p>
      </div>
    </article>
  )
}
