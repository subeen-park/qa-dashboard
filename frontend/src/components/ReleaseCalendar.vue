<template>
  <div class="cal-page">
    <div class="cal-topbar">
      <div class="cal-title-area">
        <h2 class="cal-title">릴리즈 캘린더</h2>
        <p class="cal-desc">전체 프로젝트 마감일과 태스크 일정을 월별로 확인하세요</p>
      </div>
      <div class="cal-controls">
        <div class="legend-row">
          <span class="legend-dot ld-done"></span><span class="legend-lbl">완료</span>
          <span class="legend-dot ld-progress"></span><span class="legend-lbl">진행중</span>
          <span class="legend-dot ld-risk"></span><span class="legend-lbl">리스크</span>
          <span class="legend-dot ld-overdue"></span><span class="legend-lbl">지연</span>
          <span class="legend-dot ld-pending"></span><span class="legend-lbl">대기</span>
        </div>
        <div class="nav-row">
          <button class="nav-btn" @click="prevMonth">&#8249;</button>
          <span class="month-label">{{ year }}년 {{ month + 1 }}월</span>
          <button class="nav-btn" @click="nextMonth">&#8250;</button>
          <button class="today-btn" @click="goToday">오늘</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-wrap">
      <div class="loading-spinner"></div>
      <span class="loading-text">불러오는 중...</span>
    </div>

    <div v-else class="cal-body">
      <!-- 캘린더 그리드 -->
      <div class="cal-main">
        <div class="weekday-row">
          <div v-for="d in WEEKDAYS" :key="d" class="weekday-cell"
            :class="d === '일' ? 'sunday' : d === '토' ? 'saturday' : ''">{{ d }}</div>
        </div>
        <div class="cal-grid">
          <div v-for="(cell, idx) in cells" :key="idx"
            class="cal-cell"
            :class="{
              'other-month': !cell.thisMonth,
              'today-cell': cell.isToday,
              'sunday-cell': cell.weekday === 0,
              'saturday-cell': cell.weekday === 6
            }">
            <div class="cell-num" :class="cell.isToday ? 'today-num' : ''">{{ cell.day }}</div>
            <div class="cell-events">
              <div v-for="ev in cell.events.slice(0, 4)" :key="ev.key"
                class="cell-ev" :class="'cev-' + ev.status"
                :title="ev.label + ' — ' + ev.project"
                @click="selectedEvent = ev">
                <span class="cev-bar"></span>
                <span class="cev-text">{{ ev.label }}</span>
              </div>
              <div v-if="cell.events.length > 4" class="cell-more">+{{ cell.events.length - 4 }}개</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 사이드 패널 -->
      <div class="side-panel">
        <!-- 집계 카드 -->
        <div class="summary-row">
          <div class="sum-card">
            <div class="sum-num">{{ allProjects.length }}</div>
            <div class="sum-label">전체</div>
          </div>
          <div class="sum-card">
            <div class="sum-num red">{{ overdueProjects }}</div>
            <div class="sum-label">지연</div>
          </div>
          <div class="sum-card">
            <div class="sum-num yellow">{{ riskProjects }}</div>
            <div class="sum-label">리스크</div>
          </div>
          <div class="sum-card">
            <div class="sum-num green">{{ doneProjects }}</div>
            <div class="sum-label">완료</div>
          </div>
        </div>

        <!-- 다가오는 마감 -->
        <div class="side-section">
          <div class="side-sec-title">다가오는 마감 <span class="side-sec-sub">30일 이내</span></div>
          <div v-if="upcoming.length === 0" class="side-empty">30일 이내 마감 없음</div>
          <div v-for="p in upcoming" :key="'up-'+p.id" class="upcoming-row" :class="'urow-'+p.status">
            <div class="upcoming-left">
              <div class="upcoming-name">{{ p.name }}</div>
              <div class="upcoming-pm" v-if="p.pm">{{ p.pm }}</div>
            </div>
            <div class="upcoming-right">
              <span class="upcoming-dday"
                :class="p.daysLeft < 0 ? 'red' : p.daysLeft <= 7 ? 'yellow' : 'muted'">
                {{ p.daysLeft < 0 ? 'D+' + Math.abs(p.daysLeft) : p.daysLeft === 0 ? 'D-day' : 'D-' + p.daysLeft }}
              </span>
            </div>
          </div>
        </div>

        <!-- 이번달 일정 -->
        <div class="side-section">
          <div class="side-sec-title">이번 달 일정 <span class="side-sec-sub">{{ monthEventsSorted.length }}건</span></div>
          <div v-if="monthEventsSorted.length === 0" class="side-empty">이번 달 일정이 없습니다</div>
          <div v-for="ev in monthEventsSorted.slice(0, 12)" :key="ev.key"
            class="side-event" :class="'sev-'+ev.status"
            @click="selectedEvent = ev">
            <div class="sev-indicator" :class="'ind-'+ev.status"></div>
            <div class="sev-info">
              <div class="sev-name">{{ ev.label }}</div>
              <div class="sev-meta">{{ fmtDay(ev.date) }} · {{ ev.project }}</div>
            </div>
            <span class="sev-badge" :class="'badge-'+ev.status">{{ STATUS_LABEL[ev.status] }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 이벤트 상세 팝업 -->
    <div v-if="selectedEvent" class="ev-overlay" @click.self="selectedEvent = null">
      <div class="ev-popup">
        <div class="ev-popup-header">
          <div class="ev-type-tag" :class="'tag-'+selectedEvent.status">{{ STATUS_LABEL[selectedEvent.status] }}</div>
          <div class="ev-popup-name">{{ selectedEvent.label }}</div>
          <button class="ev-close" @click="selectedEvent = null">&#x2715;</button>
        </div>
        <div class="ev-popup-body">
          <div class="ev-row"><span class="ev-key">프로젝트</span><span>{{ selectedEvent.project }}</span></div>
          <div class="ev-row" v-if="selectedEvent.pm"><span class="ev-key">담당 PM</span><span>{{ selectedEvent.pm }}</span></div>
          <div class="ev-row" v-if="selectedEvent.assignee"><span class="ev-key">담당자</span><span>{{ selectedEvent.assignee }}</span></div>
          <div class="ev-row"><span class="ev-key">마감일</span><span class="mono">{{ selectedEvent.date }}</span></div>
          <div class="ev-row" v-if="selectedEvent.progress !== undefined">
            <span class="ev-key">진행률</span><span class="mono">{{ selectedEvent.progress }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../api/index.js'
import { getStatus } from '../utils.js'

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']
const STATUS_LABEL = { done: '완료', progress: '진행중', risk: '리스크', overdue: '지연', pending: '대기' }

function diffDaysFromToday(dateStr) {
  if (!dateStr) return null
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const d = new Date(dateStr); d.setHours(0, 0, 0, 0)
  return Math.round((d - today) / 86400000)
}

function projectStatus(proj) {
  if ((proj.progress || 0) >= 100) return 'done'
  if (!proj.endDate) return proj.status || 'pending'
  const diff = diffDaysFromToday(proj.endDate)
  if (diff < 0) return 'overdue'
  if (diff <= 14) return 'risk'
  if ((proj.progress || 0) > 0) return 'progress'
  return proj.status || 'pending'
}

export default {
  name: 'ReleaseCalendar',
  data() {
    const now = new Date()
    return {
      year: now.getFullYear(),
      month: now.getMonth(),
      today: new Date(),
      WEEKDAYS, STATUS_LABEL,
      loading: true,
      allProjects: [],
      allTasks: [],
      selectedEvent: null,
    }
  },
  async mounted() { await this.loadData() },
  computed: {
    cells() {
      const y = this.year, m = this.month
      const firstDay = new Date(y, m, 1).getDay()
      const lastDate = new Date(y, m + 1, 0).getDate()
      const prevLastDate = new Date(y, m, 0).getDate()
      const todayStr = this.toDateStr(this.today)
      const cells = []
      for (let i = firstDay - 1; i >= 0; i--) {
        const d = prevLastDate - i
        const date = new Date(y, m - 1, d)
        cells.push({ day: d, thisMonth: false, isToday: false, weekday: date.getDay(), events: [] })
      }
      for (let d = 1; d <= lastDate; d++) {
        const date = new Date(y, m, d)
        const dateStr = this.toDateStr(date)
        cells.push({ day: d, thisMonth: true, isToday: dateStr === todayStr, weekday: date.getDay(), dateStr, events: this.eventsOnDate(dateStr) })
      }
      const remaining = 42 - cells.length
      for (let d = 1; d <= remaining; d++) {
        const date = new Date(y, m + 1, d)
        cells.push({ day: d, thisMonth: false, isToday: false, weekday: date.getDay(), events: [] })
      }
      return cells
    },
    events() {
      const evs = []
      this.allProjects.forEach(p => {
        if (p.endDate) evs.push({ key: 'proj-' + p.id, type: 'project', date: p.endDate, label: p.name, project: p.name, pm: p.pm, assignee: null, status: projectStatus(p), progress: p.progress })
      })
      this.allTasks.forEach(t => {
        if (t.endDate) evs.push({ key: 'task-' + t.id + '-' + t.projectId, type: 'task', date: t.endDate, label: t.task, project: t.projectName, pm: t.pm, assignee: t.assignee, status: getStatus(t), progress: t.progress })
      })
      return evs
    },
    monthEventsSorted() {
      return this.events.filter(ev => {
        if (!ev.date) return false
        const [y, m] = ev.date.split('-').map(Number)
        return y === this.year && m - 1 === this.month
      }).sort((a, b) => a.date < b.date ? -1 : 1)
    },
    overdueProjects() { return this.allProjects.filter(p => projectStatus(p) === 'overdue').length },
    riskProjects()    { return this.allProjects.filter(p => projectStatus(p) === 'risk').length },
    doneProjects()    { return this.allProjects.filter(p => projectStatus(p) === 'done').length },
    upcoming() {
      return this.allProjects.filter(p => p.endDate)
        .map(p => ({ ...p, status: projectStatus(p), daysLeft: diffDaysFromToday(p.endDate) }))
        .filter(p => p.daysLeft !== null && p.daysLeft <= 30)
        .sort((a, b) => a.daysLeft - b.daysLeft)
    },
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        this.allProjects = await api.getProjects()
        const arrays = await Promise.all(this.allProjects.map(p =>
          api.getTasks(p.id).then(tasks => tasks.map(t => ({ ...t, projectId: p.id, projectName: p.name, pm: p.pm }))).catch(() => [])
        ))
        this.allTasks = arrays.flat()
      } catch(e) { console.error(e) }
      this.loading = false
    },
    eventsOnDate(dateStr) { return this.events.filter(ev => ev.date === dateStr) },
    toDateStr(d) {
      return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    },
    fmtDay(dateStr) {
      if (!dateStr) return ''
      const [, m, d] = dateStr.split('-')
      return `${parseInt(m)}/${parseInt(d)}`
    },
    prevMonth() { if (this.month === 0) { this.year--; this.month = 11 } else this.month-- },
    nextMonth() { if (this.month === 11) { this.year++; this.month = 0 } else this.month++ },
    goToday()   { const n = new Date(); this.year = n.getFullYear(); this.month = n.getMonth() },
  }
}
</script>

<style scoped>
.cal-page { display: flex; flex-direction: column; height: calc(100vh - 60px); padding: 20px 24px; gap: 16px; box-sizing: border-box }

.cal-topbar { display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-shrink: 0 }
.cal-title  { font-size: 18px; font-weight: 700; color: var(--text); margin-bottom: 2px }
.cal-desc   { font-size: 13px; color: var(--muted) }
.cal-controls { display: flex; flex-direction: column; align-items: flex-end; gap: 8px }
.legend-row { display: flex; align-items: center; gap: 8px }
.legend-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0 }
.ld-done    { background: var(--green) }
.ld-progress{ background: #4a90d9 }
.ld-risk    { background: var(--yellow) }
.ld-overdue { background: var(--red) }
.ld-pending { background: var(--muted) }
.legend-lbl { font-size: 11px; color: var(--muted) }
.nav-row { display: flex; align-items: center; gap: 6px }
.nav-btn { background: var(--bg2); border: 1px solid var(--border2); border-radius: 7px; color: var(--text); width: 30px; height: 30px; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center; font-family: inherit; transition: background .15s }
.nav-btn:hover { background: var(--bg3) }
.month-label { font-size: 15px; font-weight: 700; color: var(--text); min-width: 100px; text-align: center }
.today-btn { background: var(--primary); color: #fff; border: none; border-radius: 7px; padding: 5px 12px; font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit }
.today-btn:hover { background: var(--primary-hover) }

.loading-wrap { display: flex; align-items: center; justify-content: center; gap: 10px; flex: 1; color: var(--muted) }
.loading-spinner { width: 20px; height: 20px; border: 2px solid var(--border2); border-top-color: var(--amber); border-radius: 50%; animation: spin 1s linear infinite }
@keyframes spin { to { transform: rotate(360deg) } }

.cal-body { display: grid; grid-template-columns: 1fr 260px; gap: 16px; flex: 1; min-height: 0 }

/* 캘린더 메인 */
.cal-main { background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column }
.weekday-row { display: grid; grid-template-columns: repeat(7, 1fr); border-bottom: 1px solid var(--border); flex-shrink: 0 }
.weekday-cell { text-align: center; padding: 8px 4px; font-size: 11px; font-weight: 700; color: var(--muted); letter-spacing: .06em; text-transform: uppercase }
.weekday-cell.sunday   { color: var(--red) }
.weekday-cell.saturday { color: #4a90d9 }
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); flex: 1; min-height: 0 }
.cal-cell { border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); padding: 6px 5px; transition: background .12s; display: flex; flex-direction: column; overflow: hidden }
.cal-cell:hover { background: var(--bg3) }
.cal-cell:nth-child(7n) { border-right: none }
.other-month   { opacity: .3 }
.today-cell    { background: rgba(53,99,233,.05) }
.sunday-cell   .cell-num { color: var(--red) }
.saturday-cell .cell-num { color: #4a90d9 }
.cell-num  { font-size: 12px; font-weight: 500; color: var(--text); margin-bottom: 3px; flex-shrink: 0 }
.today-num { background: var(--primary); color: #fff; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 11px }
.cell-events { display: flex; flex-direction: column; gap: 2px; overflow: hidden }
.cell-ev   { display: flex; align-items: center; gap: 4px; border-radius: 3px; padding: 1px 4px; cursor: pointer; transition: opacity .12s }
.cell-ev:hover { opacity: .75 }
.cev-bar   { width: 3px; height: 10px; border-radius: 2px; flex-shrink: 0 }
.cev-text  { font-size: 10px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis }
.cell-more { font-size: 10px; color: var(--muted); padding-left: 7px }

.cev-done     .cev-bar { background: var(--green) } .cev-done     .cev-text { color: var(--green) }
.cev-progress .cev-bar { background: #4a90d9 }  .cev-progress .cev-text { color: #2a72c8 }
.cev-risk     .cev-bar { background: var(--yellow) } .cev-risk    .cev-text { color: var(--yellow) }
.cev-overdue  .cev-bar { background: var(--red) }   .cev-overdue  .cev-text { color: var(--red) }
.cev-pending  .cev-bar { background: var(--muted) } .cev-pending  .cev-text { color: var(--muted) }

/* 사이드 패널 */
.side-panel { display: flex; flex-direction: column; gap: 12px; overflow-y: auto; min-height: 0 }
.summary-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; flex-shrink: 0 }
.sum-card  { background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 12px 8px; text-align: center }
.sum-num   { font-size: 20px; font-weight: 700; font-family: 'DM Mono', monospace; color: var(--text) }
.sum-num.red    { color: var(--red) }
.sum-num.yellow { color: var(--yellow) }
.sum-num.green  { color: var(--green) }
.sum-label { font-size: 10px; color: var(--muted); margin-top: 2px }

.side-section { background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; overflow: hidden }
.side-sec-title { font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; padding: 10px 14px 8px; border-bottom: 1px solid var(--border) }
.side-sec-sub   { font-size: 10px; color: var(--faint); font-weight: 400; text-transform: none; letter-spacing: 0; margin-left: 4px }
.side-empty { font-size: 12px; color: var(--muted); padding: 14px; text-align: center }

.upcoming-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 14px; border-bottom: 1px solid var(--border); gap: 8px }
.upcoming-row:last-child { border-bottom: none }
.upcoming-name { font-size: 12px; font-weight: 600; color: var(--text) }
.upcoming-pm   { font-size: 10px; color: var(--muted); margin-top: 1px }
.upcoming-dday { font-size: 11px; font-weight: 700; font-family: 'DM Mono', monospace }
.upcoming-dday.red    { color: var(--red) }
.upcoming-dday.yellow { color: var(--yellow) }
.upcoming-dday.muted  { color: var(--muted) }

.side-event { display: flex; align-items: center; gap: 8px; padding: 8px 14px; cursor: pointer; border-bottom: 1px solid var(--border); transition: background .12s }
.side-event:last-child { border-bottom: none }
.side-event:hover { background: var(--bg3) }
.sev-indicator { width: 3px; height: 30px; border-radius: 2px; flex-shrink: 0 }
.ind-done     { background: var(--green) }
.ind-progress { background: #4a90d9 }
.ind-risk     { background: var(--yellow) }
.ind-overdue  { background: var(--red) }
.ind-pending  { background: var(--muted) }
.sev-info  { flex: 1; min-width: 0 }
.sev-name  { font-size: 12px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis }
.sev-meta  { font-size: 10px; color: var(--muted); margin-top: 2px }
.sev-badge { flex-shrink: 0; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px }
.badge-done     { background: var(--green-dim); color: var(--green) }
.badge-progress { background: rgba(74,144,217,.12);  color: #2a72c8 }
.badge-risk     { background: var(--yellow-dim); color: var(--yellow) }
.badge-overdue  { background: var(--red-dim);   color: var(--red) }
.badge-pending  { background: var(--bg4);       color: var(--muted) }

/* 팝업 */
.ev-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 500; display: flex; align-items: center; justify-content: center }
.ev-popup   { background: var(--bg2); border: 1px solid var(--border2); border-radius: 12px; width: 380px; max-width: 90vw; overflow: hidden }
.ev-popup-header { padding: 18px 20px 14px; border-bottom: 1px solid var(--border); position: relative }
.ev-type-tag { display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px; margin-bottom: 6px }
.tag-done     { background: var(--green-dim); color: var(--green) }
.tag-progress { background: rgba(74,144,217,.12);  color: #2a72c8 }
.tag-risk     { background: var(--yellow-dim); color: var(--yellow) }
.tag-overdue  { background: var(--red-dim);   color: var(--red) }
.tag-pending  { background: var(--bg4);       color: var(--muted) }
.ev-popup-name { font-size: 15px; font-weight: 700; color: var(--text); padding-right: 24px }
.ev-close { position: absolute; top: 16px; right: 16px; background: none; border: none; color: var(--muted); cursor: pointer; font-size: 14px }
.ev-popup-body { padding: 14px 20px 18px; display: flex; flex-direction: column; gap: 9px }
.ev-row  { display: flex; align-items: center; gap: 12px; font-size: 13px }
.ev-key  { color: var(--muted); font-size: 11px; width: 52px; flex-shrink: 0 }
.mono    { font-family: 'DM Mono', monospace }
</style>