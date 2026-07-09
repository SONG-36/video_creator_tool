import { useCallback, useEffect, useState } from 'react'
import { getShot, getStoryboardShots, reviewShot } from '../api/storyboard'
import type {
  ReviewResult,
  Shot,
  StoryboardReviewSummary,
} from '../types/storyboard'

type StoryboardReviewState = {
  shots: Shot[]
  summary: StoryboardReviewSummary
  isLoading: boolean
  isSubmittingShotId: string | null
  error: string | null
  reviewShotById: (shotId: string, result: ReviewResult) => Promise<void>
  reload: () => Promise<void>
}

export function useStoryboardReview(
  storyboardId: string,
): StoryboardReviewState {
  const [shots, setShots] = useState<Shot[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmittingShotId, setIsSubmittingShotId] = useState<string | null>(
    null,
  )
  const [error, setError] = useState<string | null>(null)

  const loadShots = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const nextShots = await getStoryboardShots(storyboardId)
      setShots(nextShots)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : '加载失败')
    } finally {
      setIsLoading(false)
    }
  }, [storyboardId])

  useEffect(() => {
    void loadShots()
  }, [loadShots])

  async function reviewShotById(shotId: string, result: ReviewResult) {
    setIsSubmittingShotId(shotId)
    setError(null)

    try {
      await reviewShot(shotId, result)
      const refreshedShot = await getShot(shotId)
      setShots((currentShots) =>
        currentShots.map((shot) => (shot.shot_id === shotId ? refreshedShot : shot)),
      )
    } catch (reviewError) {
      setError(reviewError instanceof Error ? reviewError.message : '审核失败')
    } finally {
      setIsSubmittingShotId(null)
    }
  }

  const summary: StoryboardReviewSummary = {
    storyboardId,
    shotCount: shots.length,
    waitingCount: shots.filter((shot) => shot.review_status === 'waiting_review')
      .length,
  }

  return {
    shots,
    summary,
    isLoading,
    isSubmittingShotId,
    error,
    reviewShotById,
    reload: loadShots,
  }
}
