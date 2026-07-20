export class ApiError extends Error {
  constructor(code, message, status = 500, retryable = false, scope = 'application') {
    super(message)
    this.code = code
    this.status = status
    this.retryable = retryable
    this.scope = scope
  }
}

export function errorPayload(error) {
  const known = error instanceof ApiError
  return {
    error: {
      code: known ? error.code : 'INTERNAL_ERROR',
      message: known ? error.message : '服务暂时无法处理请求',
      retryable: known ? error.retryable : true,
      scope: known ? error.scope : 'application',
    },
  }
}
