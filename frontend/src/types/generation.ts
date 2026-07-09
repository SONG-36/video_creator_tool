export type GenerationReviewStatus =
  | 'reviewing'
  | 'approved'
  | 'revision_required'
  | 'rejected'

export type GenerationReviewAction =
  | 'approved'
  | 'revision_required'
  | 'rejected'

export type GenerationTaskSummary = {
  task_id: string
  production_task_id: string
  provider: string
  status: string
  request_payload: Record<string, unknown>
  result_payload: Record<string, unknown> | null
  error_message: string
  created_at: string
  updated_at: string
}

export type GenerationResult = {
  result_id: string
  generation_task_id: string
  production_task_id: string
  shot_id: string
  provider: string
  prompt: string
  negative_prompt: string
  camera: string
  motion: string
  lighting: string
  video_url: string
  video_path: string
  thumbnail_url: string
  version: number
  generation_cost: number
  status: string
  review_status: GenerationReviewStatus
  created_at: string
  updated_at: string
}

export type GenerationReview = {
  id: string
  generation_result_id: string
  review_status: GenerationReviewAction
  comment: string
  reviewer: string
  created_at: string
}

export type GenerationReviewOutcome = {
  review: GenerationReview
  next_generation_task: GenerationTaskSummary | null
}
