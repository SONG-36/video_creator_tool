import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { ProductionPage } from './ProductionPage'
import { renderWithRouter } from '../test/test-utils'

const initialPlan = {
  data: {
    production_task: {
      task_id: 'task-1',
      shot_id: 'shot-1',
      model: 'seedance',
      generation_mode: 'r2v',
      prompt:
        'Preserve @Image1 identity and use @Video1 for motion pacing.',
      negative_prompt: 'blur, distortion',
      camera: 'Controlled lateral move ending on label.',
      motion: 'Foam crosses frame and wipes stain clean.',
      lighting: 'Soft daylight with reflective highlights.',
      status: 'waiting_asset',
      asset_requirement: [
        {
          asset_id: 'asset-1',
          asset_type: 'product_image',
          role: 'identity_reference',
          reference_tag: '@Image1',
          requirement_note: 'Provide hero product packshot.',
          status: 'pending',
        },
        {
          asset_id: 'asset-2',
          asset_type: 'reference_video',
          role: 'motion_reference',
          reference_tag: '@Video1',
          requirement_note: 'Provide wipe-action timing reference.',
          status: 'pending',
        },
      ],
    },
  },
}

const refreshedPlan = {
  data: {
    production_task: {
      ...initialPlan.data.production_task,
      asset_requirement: [
        {
          ...initialPlan.data.production_task.asset_requirement[0],
          status: 'uploaded',
        },
        initialPlan.data.production_task.asset_requirement[1],
      ],
    },
  },
}

describe('ProductionPage', () => {
  beforeEach(() => {
    let refreshed = false

    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)

      if (url.endsWith('/shots/shot-1/production-plan')) {
        return new Response(
          JSON.stringify(refreshed ? refreshedPlan : initialPlan),
          { status: 200 },
        )
      }

      if (url.endsWith('/assets/upload') && init?.method === 'POST') {
        refreshed = true
        return new Response(
          JSON.stringify({
            data: {
              asset: {
                asset_id: 'asset-1',
                production_task_id: 'task-1',
                role: 'identity_reference',
                reference_tag: '@Image1',
                requirement_note: 'Provide hero product packshot.',
                status: 'uploaded',
                file_name: 'product.png',
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

  it('renders production plan and asset requirements', async () => {
    renderWithRouter(
      <Routes>
        <Route path="/shots/:shotId/production" element={<ProductionPage />} />
      </Routes>,
      { route: '/shots/shot-1/production' },
    )

    expect(await screen.findByText('AI 生产页面')).toBeInTheDocument()
    expect(screen.getByText('Preserve @Image1 identity and use @Video1 for motion pacing.')).toBeInTheDocument()
    expect(screen.getByText('Controlled lateral move ending on label.')).toBeInTheDocument()
    expect(screen.getAllByText('identity_reference').length).toBeGreaterThan(0)
    expect(screen.getAllByText('@Video1').length).toBeGreaterThan(0)
  })

  it('uploads asset and refreshes requirement status', async () => {
    const user = userEvent.setup()

    renderWithRouter(
      <Routes>
        <Route path="/shots/:shotId/production" element={<ProductionPage />} />
      </Routes>,
      { route: '/shots/shot-1/production' },
    )

    await screen.findByText('AI 生产页面')
    const fileInput = screen.getAllByLabelText('上传素材')[0]
    const file = new File(['image-bytes'], 'product.png', { type: 'image/png' })

    await user.upload(fileInput, file)

    await waitFor(() => {
      expect(screen.getAllByText('uploaded').length).toBeGreaterThan(0)
    })

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/assets/upload'),
      expect.objectContaining({ method: 'POST' }),
    )
  })
})
