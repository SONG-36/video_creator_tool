import { requestJson } from './http'
import type {
  GenerationResult,
  GenerationReviewAction,
  GenerationReviewOutcome,
} from '../types/generation'

type GenerationResultResponse = {
  data?: {
    result?: GenerationResult
  }
}

type GenerationReviewResponse = {
  data?: {
    review?: GenerationReviewOutcome
  }
}

export async function getGenerationResult(
  resultId: string,
): Promise<GenerationResult> {
  const response = await requestJson<GenerationResultResponse>(
    `/generation-results/${resultId}`,
  )

  const result = response.data?.result
  if (!result) {
    throw new Error('Generation result payload is missing.')
  }

  return result
}

export async function reviewGenerationResult(input: {
  resultId: string
  reviewStatus: GenerationReviewAction
  comment?: string
  regenerate?: boolean
  promptOverride?: string
}): Promise<GenerationReviewOutcome> {
  const response = await requestJson<GenerationReviewResponse>(
    `/generation-results/${input.resultId}/review`,
    {
      method: 'POST',
      body: JSON.stringify({
        review_status: input.reviewStatus,
        comment: input.comment ?? '',
        reviewer: 'frontend_video_reviewer',
        regenerate: input.regenerate ?? false,
        prompt_override: input.promptOverride ?? null,
      }),
    },
  )

  const review = response.data?.review
  if (!review) {
    throw new Error('Generation review payload is missing.')
  }

  return review
}
