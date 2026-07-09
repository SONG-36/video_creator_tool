import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { StoryboardReviewPage } from './StoryboardReviewPage'
import { renderWithRouter } from '../test/test-utils'

const shotsPayload = {
  data: {
    shots: [
      {
        shot_id: 'shot-1',
        storyboard_id: 'storyboard-1',
        shot_number: 1,
        time_start: 0,
        time_end: 3,
        scene: '厨房污渍特写',
        purpose: '展示问题',
        action: '镜头推进到污渍位置',
        camera: 'Close-up push-in',
        production_type: 'pending',
        review_status: 'waiting_review',
      },
      {
        shot_id: 'shot-2',
        storyboard_id: 'storyboard-1',
        shot_number: 2,
        time_start: 3,
        time_end: 6,
        scene: '产品喷洒清洁剂',
        purpose: '展示解决方案',
        action: '泡沫覆盖表面',
        camera: 'Medium side shot',
        production_type: 'ai_generate',
        review_status: 'approved',
      },
    ],
  },
}

describe('StoryboardReviewPage', () => {
  beforeEach(() => {
    let reviewCalled = false

    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)

      if (url.endsWith('/storyboards/storyboard-1/shots')) {
        return new Response(JSON.stringify(shotsPayload), { status: 200 })
      }

      if (url.endsWith('/shots/shot-1/review') && init?.method === 'POST') {
        reviewCalled = true
        return new Response(
          JSON.stringify({
            data: { review: { shot_id: 'shot-1', result: 'approved' } },
          }),
          { status: 200 },
        )
      }

      if (url.endsWith('/shots/shot-1') && reviewCalled) {
        return new Response(
          JSON.stringify({
            data: {
              shot: {
                ...shotsPayload.data.shots[0],
                review_status: 'approved',
              },
            },
          }),
          { status: 200 },
        )
      }

      return new Response(JSON.stringify({ detail: 'not found' }), { status: 404 })
    }) as typeof fetch
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders storyboard and shot details from api', async () => {
    renderWithRouter(
      <Routes>
        <Route
          path="/storyboards/:storyboardId/review"
          element={<StoryboardReviewPage />}
        />
      </Routes>,
      { route: '/storyboards/storyboard-1/review' },
    )

    expect(await screen.findByText('Storyboard 审核')).toBeInTheDocument()
    expect((await screen.findAllByText('厨房污渍特写')).length).toBeGreaterThan(0)
    expect(screen.getAllByText('产品喷洒清洁剂').length).toBeGreaterThan(0)
    expect(screen.getByText('Close-up push-in')).toBeInTheDocument()
  })

  it('calls review api and refreshes shot status', async () => {
    const user = userEvent.setup()

    renderWithRouter(
      <Routes>
        <Route
          path="/storyboards/:storyboardId/review"
          element={<StoryboardReviewPage />}
        />
      </Routes>,
      { route: '/storyboards/storyboard-1/review' },
    )

    await screen.findAllByText('厨房污渍特写')
    await user.click(screen.getAllByRole('button', { name: 'approved' })[0])

    await waitFor(() => {
      expect(screen.getAllByText('approved').length).toBeGreaterThan(1)
    })

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/shots/shot-1/review'),
      expect.objectContaining({ method: 'POST' }),
    )
  })
})
