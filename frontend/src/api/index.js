const BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

// 앱 시작 시 Render 서버 워밍업
fetch(BASE.replace('/api', '/api/health')).catch(() => {})

async function http(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch(BASE + path, opts)
  if (!res.ok) throw new Error(`${method} ${path} → ${res.status}`)
  return res.json()
}

export const api = {
  getProjects:    ()            => http('GET',    '/projects'),
  createProject:  (body)        => http('POST',   '/projects', body),
  updateProject:  (id, body)    => http('PUT',    `/projects/${id}`, body),
  deleteProject:  (id)          => http('DELETE', `/projects/${id}`),
  
  getTasks:       (pid)         => http('GET',    `/projects/${pid}/tasks`),
  createTask:     (pid, body)   => http('POST',   `/projects/${pid}/tasks`, body),
  updateTask:     (pid, tid, b) => http('PUT',    `/projects/${pid}/tasks/${tid}`, b),
  deleteTask:     (pid, tid)    => http('DELETE', `/projects/${pid}/tasks/${tid}`),
  
  // 엑셀 에러 핸들링 고도화
  uploadExcel:    async (pid, file) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${BASE}/projects/${pid}/tasks/upload`, {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || '알 수 없는 서버 에러 발생')
    return data
  },
  
  uploadSheetsUrl: (pid, csvUrl) => http('POST', `/projects/${pid}/tasks/upload-sheets`, { csv_url: csvUrl }),

  getWebhook:     ()            => http('GET',    '/webhook'),
  saveWebhook:    (body)        => http('POST',   '/webhook', body),
  testWebhook:    ()            => http('POST',   '/webhook/test'),
  getLogs:        ()            => http('GET',    '/logs'),
  notifyNow:      ()            => http('POST',   '/notify/now'),
}