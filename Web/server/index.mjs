import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import express from 'express'

import { createApp } from './app.mjs'

const port = Number(process.env.PORT || 5174)
const app = createApp()
const webRoot = dirname(dirname(fileURLToPath(import.meta.url)))
const distPath = join(webRoot, 'dist')

if (existsSync(distPath)) {
  app.use(express.static(distPath))
  app.get('/{*splat}', (_request, response) => response.sendFile(join(distPath, 'index.html')))
}

app.listen(port, '127.0.0.1', () => {
  console.log(`企业财务深度分析服务已启动：http://127.0.0.1:${port}`)
})
