import { requestJson } from './http'
import type { ReviewResult, Shot } from '../types/storyboard'

type ShotListResponse =
  | {
      data?: {
        shots?: Shot[]
      }
    }
  | Shot[]

type ShotResponse =
  | {
      data?: {
        shot?: Shot
      }
    }
  | Shot

type ReviewResponse = {
  data?: {
    review?: {
      shot_id: string
      result: ReviewResult
    }
  }
}

export async function getStoryboardShots(storyboardId: string): Promise<Shot[]> {
  const response = await requestJson<ShotListResponse>(
    `/storyboards/${storyboardId}/shots`,
  )

  if (Array.isArray(response)) {
    return response
  }

  return response.data?.shots ?? []
}

export async function getShot(shotId: string): Promise<Shot> {
  const response = await requestJson<ShotResponse>(`/shots/${shotId}`)

  if ('shot_id' in response) {
    return response
  }

  const shot = response.data?.shot
  if (!shot) {
    throw new Error('Shot payload is missing.')
  }

  return shot
}

export async function reviewShot(
  shotId: string,
  result: ReviewResult,
): Promise<ReviewResponse> {
  return requestJson<ReviewResponse>(`/shots/${shotId}/review`, {
    method: 'POST',
    body: JSON.stringify({
      result,
      comment: '',
      reviewer: 'frontend_reviewer',
    }),
  })
}
