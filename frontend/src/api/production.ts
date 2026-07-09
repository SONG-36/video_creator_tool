import type { ProductionPlan, UploadedAsset } from '../types/production'
import { API_BASE_URL } from './client'
import { ApiError, requestJson } from './http'

type ProductionPlanResponse = {
  data?: {
    production_task?: ProductionPlan
  }
}

type AssetUploadResponse = {
  data?: {
    asset?: UploadedAsset
  }
}

export async function getProductionPlan(shotId: string): Promise<ProductionPlan> {
  const response = await requestJson<ProductionPlanResponse>(
    `/shots/${shotId}/production-plan`,
  )

  const plan = response.data?.production_task
  if (!plan) {
    throw new Error('Production plan payload is missing.')
  }

  return plan
}

export async function uploadProductionAsset(input: {
  productionTaskId: string
  role: string
  referenceTag: string
  requirementNote: string
  file: File
}): Promise<UploadedAsset> {
  const formData = new FormData()
  formData.append('production_task_id', input.productionTaskId)
  formData.append('role', input.role)
  formData.append('reference_tag', input.referenceTag)
  formData.append('requirement_note', input.requirementNote)
  formData.append('file', input.file)

  const response = await fetch(`${API_BASE_URL}/assets/upload`, {
    method: 'POST',
    body: formData,
  })

  const body = await response.json().catch(() => null)
  if (!response.ok) {
    const message =
      (body && typeof body.detail === 'string' && body.detail) ||
      `Request failed with status ${response.status}`
    throw new ApiError(message, response.status)
  }

  const asset = (body as AssetUploadResponse).data?.asset
  if (!asset) {
    throw new Error('Uploaded asset payload is missing.')
  }

  return asset
}
