import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { GenerationResultReviewPage } from './GenerationResultReviewPage'
import { renderWithRouter } from '../test/test-utils'

const baseResult = {
  data: {
    result: {
      result_id: 'result-1',
      generation_task_id: 'gen-task-1',
      production_task_id: 'prod-task-1',
      shot_id: 'shot-1',
      provider: 'mock',
      prompt: 'Create a polished hero shot from approved references.',
      negative_prompt: 'distortion, blur',
      camera: 'Controlled side track.',
      motion: 'Bottle enters, wipe clears stain, end on clean frame.',
      lighting: 'Soft daylight with clean rim.',
      video_url: 'https://cdn.example.com/generated/result-1.mp4',
      video_path: 'storage/generated/result-1.mp4',
      thumbnail_url: 'https://cdn.example.com/generated/result-1.jpg',
      version: 1,
      generation_cost: 0.85,
      status: 'completed',
      review_status: 'reviewing',
      created_at: '2026-07-09T01:00:00Z',
      updated_at: '2026-07-09T01:00:00Z',
    },
  },
}

const reviewedResult = {
  data: {
    result: {
      ...baseResult.data.result,
      review_status: 'revision_required',
      updated_at: '2026-07-09T01:05:00Z',
    },
  },
}

describe('GenerationResultReviewPage', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders generation result detail and video player', async () => {
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith('/generation-results/result-1')) {
        return new Response(JSON.stringify(baseResult), { status: 200 })
      }
      return new Response(JSON.stringify({ detail: 'not found' }), { status: 404 })
    }) as typeof fetch

    renderWithRouter(
      <Routes>
        <Route
          path="/generation-results/:resultId/review"
          element={<GenerationResultReviewPage />}
        />
      </Routes>,
      { route: '/generation-results/result-1/review' },
    )

    expect(await screen.findByText('视频结果审核')).toBeInTheDocument()
    expect(
      screen.getByDisplayValue(
        'Create a polished hero shot from approved references.',
      ),
    ).toBeInTheDocument()
    expect(screen.getByText('Controlled side track.')).toBeInTheDocument()
    expect(screen.getByLabelText('视频播放器')).toBeInTheDocument()
    expect(screen.getAllByText('v1').length).toBeGreaterThan(0)
  })

  it('submits prompt revision review and shows the created generation task', async () => {
    const user = userEvent.setup()
    let reviewed = false

    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)

      if (url.endsWith('/generation-results/result-1')) {
        return new Response(JSON.stringify(reviewed ? reviewedResult : baseResult), {
          status: 200,
        })
      }

      if (
        url.endsWith('/generation-results/result-1/review') &&
        init?.method === 'POST'
      ) {
        reviewed = true
        return new Response(
          JSON.stringify({
            data: {
              review: {
                review: {
                  id: 'review-1',
                  generation_result_id: 'result-1',
                  review_status: 'revision_required',
                  comment: '',
                  reviewer: 'frontend_video_reviewer',
                  created_at: '2026-07-09T01:05:00Z',
                },
                next_generation_task: {
                  task_id: 'gen-task-2',
                  production_task_id: 'prod-task-1',
                  provider: 'mock',
                  status: 'queued',
                  request_payload: {
                    prompt: 'Create a tighter hook shot with a faster opening move.',
                  },
                  result_payload: null,
                  error_message: '',
                  created_at: '2026-07-09T01:05:00Z',
                  updated_at: '2026-07-09T01:05:00Z',
                },
              },
            },
          }),
          { status: 200 },
        )
      }

      return new Response(JSON.stringify({ detail: 'not found' }), { status: 404 })
    }) as typeof fetch

    renderWithRouter(
      <Routes>
        <Route
          path="/generation-results/:resultId/review"
          element={<GenerationResultReviewPage />}
        />
      </Routes>,
      { route: '/generation-results/result-1/review' },
    )

    await screen.findByText('视频结果审核')
    const promptEditor = screen.getByLabelText('Prompt 修改')
    await user.clear(promptEditor)
    await user.type(promptEditor, 'Create a tighter hook shot with a faster opening move.')
    await user.click(screen.getByRole('button', { name: '修改Prompt' }))

    await waitFor(() => {
      expect(screen.getAllByText('gen-task-2').length).toBeGreaterThan(0)
    })
    expect(screen.getAllByText('revision_required').length).toBeGreaterThan(0)

    const reviewCall = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls.find(
      ([url, init]) =>
        String(url).endsWith('/generation-results/result-1/review') &&
        init?.method === 'POST',
    )

    expect(reviewCall).toBeTruthy()
    expect(reviewCall?.[1]?.body).toContain('"review_status":"revision_required"')
    expect(reviewCall?.[1]?.body).toContain('"regenerate":true')
    expect(reviewCall?.[1]?.body).toContain(
      '"prompt_override":"Create a tighter hook shot with a faster opening move."',
    )
  })
})
