export type ApiErrorBody = { error: { code: string; message: string; retryable: boolean; scope: string } }

export class ApiClientError extends Error {
  code: string
  retryable: boolean
  scope: string

  constructor(body: ApiErrorBody['error']) {
    super(body.message)
    this.code = body.code
    this.retryable = body.retryable
    this.scope = body.scope
  }
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal, headers: { Accept: 'application/json' } })
  const body = await response.json()
  if (!response.ok) throw new ApiClientError(body.error)
  return body as T
}
