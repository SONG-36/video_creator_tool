import { useCallback, useEffect, useState } from 'react'
import {
  getGenerationResult,
  reviewGenerationResult,
} from '../api/generation'
import type {
  GenerationResult,
  GenerationReviewAction,
  GenerationTaskSummary,
} from '../types/generation'

type UseGenerationResultReviewState = {
  result: GenerationResult | null
  promptDraft: string
  isLoading: boolean
  isSubmitting: boolean
  error: string | null
  lastCreatedTask: GenerationTaskSummary | null
  setPromptDraft: (value: string) => void
  approveResult: () => Promise<void>
  regenerateResult: () => Promise<void>
  revisePrompt: () => Promise<void>
  reload: () => Promise<void>
}

export function useGenerationResultReview(
  resultId: string,
): UseGenerationResultReviewState {
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [promptDraft, setPromptDraft] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastCreatedTask, setLastCreatedTask] =
    useState<GenerationTaskSummary | null>(null)

  const loadResult = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const nextResult = await getGenerationResult(resultId)
      setResult(nextResult)
      setPromptDraft(nextResult.prompt)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : '加载失败')
    } finally {
      setIsLoading(false)
    }
  }, [resultId])

  useEffect(() => {
    void loadResult()
  }, [loadResult])

  async function submitReview(
    reviewStatus: GenerationReviewAction,
    options: {
      regenerate?: boolean
      promptOverride?: string
    } = {},
  ) {
    setIsSubmitting(true)
    setError(null)

    try {
      const outcome = await reviewGenerationResult({
        resultId,
        reviewStatus,
        regenerate: options.regenerate,
        promptOverride: options.promptOverride,
      })
      setLastCreatedTask(outcome.next_generation_task)
      const refreshedResult = await getGenerationResult(resultId)
      setResult(refreshedResult)
    } catch (reviewError) {
      setError(reviewError instanceof Error ? reviewError.message : '审核失败')
    } finally {
      setIsSubmitting(false)
    }
  }

  return {
    result,
    promptDraft,
    isLoading,
    isSubmitting,
    error,
    lastCreatedTask,
    setPromptDraft,
    approveResult: () => submitReview('approved'),
    regenerateResult: () => submitReview('rejected', { regenerate: true }),
    revisePrompt: () =>
      submitReview('revision_required', {
        regenerate: true,
        promptOverride: promptDraft,
      }),
    reload: loadResult,
  }
}
