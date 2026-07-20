import express from 'express'
import { z } from 'zod'

import { DEFAULT_DATABASE_PATH, getCompanies, getCompany, getCompanyAnalysis, getComparison, getDataQuality, getMeta, getPeriods, openDatabase } from './db.mjs'
import { ApiError, errorPayload } from './errors.mjs'

const codeSchema = z.string().regex(/^(SH|SZ)\d{6}$/)

export function createApp({ databasePath = process.env.FINANCIAL_DB_PATH || DEFAULT_DATABASE_PATH } = {}) {
  const app = express()
  app.disable('x-powered-by')

  const route = (handler) => (request, response, next) => {
    let db
    try {
      db = openDatabase(databasePath)
      response.json(handler(db, request))
    } catch (error) {
      next(error)
    } finally {
      if (db?.isOpen) db.close()
    }
  }

  app.get('/api/health', route((db) => ({ status: 'ok', schemaVersion: db.prepare('PRAGMA user_version').get().user_version, databasePath })))
  app.get('/api/meta', route((db) => getMeta(db, databasePath)))
  app.get('/api/periods', route((db) => getPeriods(db)))
  app.get('/api/companies', route((db, request) => getCompanies(db, String(request.query.search ?? '').slice(0, 80))))
  app.get('/api/compare', route((db, request) => {
    const codes = z.array(codeSchema).min(2).max(12).parse(String(request.query.codes ?? '').split(',').filter(Boolean))
    const mode = z.enum(['absolute', 'index', 'percentile']).parse(request.query.mode ?? 'absolute')
    const period = request.query.period ? z.string().regex(/^\d{4}-\d{2}-\d{2}$/).parse(request.query.period) : null
    return getComparison(db, codes, period, mode)
  }))
  app.get('/api/companies/:code', route((db, request) => getCompany(db, codeSchema.parse(request.params.code))))
  app.get('/api/companies/:code/analysis', route((db, request) => getCompanyAnalysis(db, codeSchema.parse(request.params.code))))
  app.get('/api/data-quality', route((db) => getDataQuality(db)))

  app.use((error, _request, response, _next) => {
    if (error instanceof z.ZodError) {
      const apiError = new ApiError('INVALID_PARAMETERS', '请求参数格式不正确', 400, false, 'request')
      response.status(apiError.status).json(errorPayload(apiError))
      return
    }
    const status = error instanceof ApiError ? error.status : 500
    response.status(status).json(errorPayload(error))
  })
  return app
}
