export type AssetRequirement = {
  asset_id: string
  asset_type: string
  role: string
  reference_tag: string
  requirement_note: string
  status: string
}

export type ProductionPlan = {
  task_id: string
  shot_id: string
  model: string
  generation_mode: string
  prompt: string
  negative_prompt: string
  camera: string
  motion: string
  lighting: string
  status: string
  asset_requirement: AssetRequirement[]
}

export type UploadedAsset = {
  asset_id: string
  production_task_id: string | null
  role: string
  reference_tag: string
  requirement_note: string
  status: string
  file_name: string | null
}
