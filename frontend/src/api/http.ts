import { API_BASE_URL } from './client'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

export async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  const body = await response.json().catch(() => null)
  if (!response.ok) {
    const message =
      (body && typeof body.detail === 'string' && body.detail) ||
      `Request failed with status ${response.status}`
    throw new ApiError(message, response.status)
  }

  return body as T
}
