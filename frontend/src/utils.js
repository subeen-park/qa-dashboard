export const GROUPS = ['기획','디자인','개발(BE)','개발(FE)','Android','iOS','QA']

export const GROUP_COLORS = {
  '기획':    'gb-plan',   '디자인':  'gb-design',
  '개발(BE)':'gb-be',     '개발(FE)':'gb-fe',
  'Android': 'gb-android','iOS':     'gb-ios',
  'QA':      'gb-qa',
}

export function today() {
  return new Date().toISOString().slice(0, 10)
}
export function addDays(d, n) {
  const dt = new Date(d); dt.setDate(dt.getDate() + n)
  return dt.toISOString().slice(0, 10)
}
export function diffDays(endStr) {
  if (!endStr) return null
  return Math.round((new Date(endStr) - new Date(today())) / 86400000)
}
export function getStatus(task) {
  const p = parseInt(task.progress || 0)
  const d = diffDays(task.endDate)
  if (p >= 100)   return 'done'
  if (d === null) return 'pending'
  if (d < 0)      return 'overdue'
  if (d <= 7)     return 'risk'
  if (p > 0)      return 'progress'
  return 'pending'
}
export const STATUS_LABEL = { done:'완료', progress:'진행중', risk:'리스크', overdue:'지연', pending:'대기' }
export const STATUS_CLASS = { done:'sb-done', progress:'sb-progress', risk:'sb-risk', overdue:'sb-overdue', pending:'sb-pending' }
