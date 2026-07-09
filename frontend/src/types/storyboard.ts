export type ReviewStatus =
  | 'waiting_review'
  | 'approved'
  | 'revision_required'
  | 'rejected'

export type ReviewResult = 'approved' | 'revision_required' | 'rejected'

export type Shot = {
  shot_id: string
  storyboard_id: string
  shot_number: number
  time_start: number
  time_end: number
  scene: string
  purpose: string
  action: string
  camera: string
  production_type: string
  review_status: ReviewStatus
}

export type StoryboardReviewSummary = {
  storyboardId: string
  shotCount: number
  waitingCount: number
}
