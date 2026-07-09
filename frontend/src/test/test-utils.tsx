import type { PropsWithChildren, ReactElement } from 'react'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

type RouterRenderOptions = {
  route?: string
}

export function renderWithRouter(
  ui: ReactElement,
  options: RouterRenderOptions = {},
) {
  const route = options.route ?? '/'

  function Wrapper({ children }: PropsWithChildren) {
    return <MemoryRouter initialEntries={[route]}>{children}</MemoryRouter>
  }

  return render(ui, { wrapper: Wrapper })
}
