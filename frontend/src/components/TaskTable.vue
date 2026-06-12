<template>
  <div>
    <!-- 정렬 필터 -->
    <div class="sort-bar">
      <span class="sort-label">정렬</span>
      <div class="sort-btns">
        <button v-for="s in SORT_OPTIONS" :key="s.key"
          class="sort-btn" :class="{on: sortKey===s.key}" @click="sortKey=s.key">
          {{ s.label }}
        </button>
      </div>
    </div>

    <div class="wbs-wrap">
      <div style="overflow-x:auto">
      <table class="wbs-table">
        <colgroup>
          <col style="width:36px">
          <col style="width:200px">
          <col style="width:88px">
          <col style="width:96px">
          <col style="width:96px">
          <col style="width:80px">
          <col style="width:112px">
          <col style="width:64px">
          <col style="width:200px">
          <col style="width:36px">
        </colgroup>
        <thead>
          <tr>
            <th>그룹</th>
            <th>태스크</th>
            <th>담당자</th>
            <th>시작일</th>
            <th>마감일</th>
            <th>Jira</th>
            <th>진행률</th>
            <th>상태</th>
            <th>메모</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <!-- 로딩 스켈레톤 -->
          <template v-if="loading">
            <tr v-for="i in 5" :key="'sk'+i" class="sk-row">
              <td><div class="sk sk-xs"></div></td>
              <td><div class="sk sk-name"></div></td>
              <td><div class="sk sk-sm"></div></td>
              <td><div class="sk sk-sm"></div></td>
              <td><div class="sk sk-sm"></div></td>
              <td><div class="sk sk-sm"></div></td>
              <td><div class="sk sk-md"></div></td>
              <td><div class="sk sk-xs"></div></td>
              <td><div class="sk sk-lg"></div></td>
              <td></td>
            </tr>
          </template>
          <template v-else-if="!Object.keys(grouped).length">
            <tr><td colspan="10" class="empty-state">{{ search ? '검색 결과 없음' : '태스크가 없습니다' }}</td></tr>
          </template>
          <template v-for="(list, group) in grouped" :key="group">
            <tr class="group-row"
              @dragover.prevent="onDragOver(group)"
              @drop.prevent="onDrop(group)"
              :class="{ 'drop-target': dragOverGroup===group && draggingGroup!==group }">
              <td colspan="10">
                <span class="group-badge" :class="GROUP_COLORS[group]||'gb-plan'">{{ group }}</span>
                <span v-if="dragOverGroup===group && draggingGroup!==group" class="drop-hint">여기에 놓기</span>
              </td>
            </tr>
            <tr v-for="t in list" :key="t.id"
              class="task-row"
              :class="{ 'row-focused': focusedId===t.id, 'dragging': draggingId===t.id }"
              :data-task-id="t.id"
              draggable="true"
              @dragstart="onDragStart(t, group)"
              @dragend="onDragEnd">
              <td class="muted center drag-handle" title="드래그로 그룹 이동">⠿</td>
              <td class="ellipsis task-name-cell" @click="showDetail(t)" style="cursor:pointer">
                <span class="task-name" :title="t.task">{{ t.task }}</span>
                <span v-if="t.endDate && isOverdue(t)" class="overdue-chip">
                  {{ Math.abs(diffDays(t.endDate)) }}일 지연
                </span>
                <span v-else-if="t.endDate && getStatus(t)==='risk'" class="risk-chip">
                  D-{{ diffDays(t.endDate) }}
                </span>
              </td>
              <td class="cell-text muted nowrap">{{ t.assignee || '-' }}</td>
              <td class="cell-date muted nowrap">{{ t.startDate || '-' }}</td>

              <!-- 마감일: 날짜만 표시 -->
              <td v-if="!t.endDate" class="cell-text muted nowrap">-</td>
              <td v-else class="cell-date nowrap" :class="dateClass(t)">{{ t.endDate }}</td>

              <td>
                <template v-if="t.jira">
                  <a v-if="isLink(t.jira)" :href="t.jira" target="_blank" class="jira-link">
                    {{ jiraLabel(t.jira) }} ↗
                  </a>
                  <span v-else class="cell-text muted">{{ t.jira }}</span>
                </template>
                <span v-else class="cell-text muted">-</span>
              </td>

              <td>
                <div class="prog-row">
                  <div class="prog-wrap">
                    <div class="prog-fill" :class="pbClass(t)" :style="{width:(t.progress||0)+'%'}"></div>
                  </div>
                  <span class="cell-text">{{ t.progress || 0 }}%</span>
                </div>
              </td>

              <td>
                <span class="status-badge" :class="STATUS_CLASS[getStatus(t)]">
                  {{ STATUS_LABEL[getStatus(t)] }}
                </span>
              </td>

              <td class="ellipsis note cell-text muted" :title="t.note" @click="t.note && showDetail(t)">{{ t.note }}</td>

              <td class="action-cell">
                <div class="menu-wrapper" @click.stop>
                  <button class="dot-btn" @click="toggleMenu(t.id, $event)">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                      <circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/>
                    </svg>
                  </button>
                  <div v-if="activeMenuId===t.id" class="dropdown-menu">
                    <button class="dropdown-item" @click="handleEdit(t)">수정</button>
                    <button class="dropdown-item danger" @click="handleDelete(t)">삭제</button>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      </div>
    </div>

    <!-- 태스크 상세 팝업 -->
    <div v-if="detailTask" class="detail-overlay" @click.self="detailTask=null">
      <div class="detail-popup">
        <div class="detail-popup-header">
          <span class="detail-popup-title">{{ detailTask.task }}</span>
          <button class="detail-close" @click="detailTask=null">✕</button>
        </div>
        <div class="detail-popup-body">
          <div class="detail-row"><span class="detail-key">그룹</span><span>{{ detailTask.group }}</span></div>
          <div class="detail-row"><span class="detail-key">담당자</span><span>{{ detailTask.assignee || '-' }}</span></div>
          <div class="detail-row"><span class="detail-key">시작일</span><span>{{ detailTask.startDate || '-' }}</span></div>
          <div class="detail-row"><span class="detail-key">마감일</span><span>{{ detailTask.endDate || '-' }}</span></div>
          <div class="detail-row"><span class="detail-key">진행률</span><span>{{ detailTask.progress || 0 }}%</span></div>
          <div class="detail-row"><span class="detail-key">Jira</span><span>{{ detailTask.jira || '-' }}</span></div>
          <div v-if="detailTask.note" class="detail-row detail-note"><span class="detail-key">메모</span><span>{{ detailTask.note }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getStatus, diffDays, GROUP_COLORS, STATUS_LABEL, STATUS_CLASS } from '../utils.js'

const SORT_OPTIONS = [
  { key: 'default',   label: '등록순' },
  { key: 'startDate', label: '시작일 빠른순' },
  { key: 'endDate',   label: '마감일 빠른순' },
]

export default {
  name: 'TaskTable',
  props: {
    tasks:          { type: Array, default: () => [] },
    search:         { type: String, default: '' },
    focusOverdueAt: { type: Number, default: 0 },
    focusStatusAt:  { type: Object, default: () => ({ status: '', ts: 0 }) },
    loading:        { type: Boolean, default: false },
  },
  emits: ['edit', 'delete', 'move-group'],
  data() {
    return {
      GROUP_COLORS, STATUS_LABEL, STATUS_CLASS, SORT_OPTIONS,
      sortKey: 'startDate',
      activeMenuId: null,
      focusedId: null,
      overdueRefs: {},
      overdueIndex: 0,
      detailTask: null,
      statusIdx: {},
      draggingId: null,
      draggingGroup: null,
      dragOverGroup: null,
    }
  },
  computed: {
    filtered() {
      const q = (this.search || '').toLowerCase()
      if (!q) return this.tasks
      return this.tasks.filter(t =>
        t.task.toLowerCase().includes(q) ||
        (t.assignee || '').toLowerCase().includes(q)
      )
    },
    sorted() {
      const list = [...this.filtered]
      if (this.sortKey === 'startDate') {
        list.sort((a, b) => (a.startDate || '9999') < (b.startDate || '9999') ? -1 : 1)
      } else if (this.sortKey === 'endDate') {
        list.sort((a, b) => (a.endDate || '9999') < (b.endDate || '9999') ? -1 : 1)
      }
      return list
    },
    grouped() {
      const g = {}
      this.sorted.forEach(t => {
        if (!g[t.group]) g[t.group] = []
        g[t.group].push(t)
      })
      return g
    },
  },
  watch: {
    focusStatusAt(val)  { if (val && val.ts > 0) this.focusNextByStatus(val.status) },
    tasks()             { this.overdueRefs = {}; this.overdueIndex = 0 },
  },
  mounted()      { document.addEventListener('click', this.closeMenu) },
  beforeUnmount(){ document.removeEventListener('click', this.closeMenu) },
  methods: {
    getStatus,
    diffDays,
    showDetail(t) { this.detailTask = t },
    onDragStart(t, group) {
      this.draggingId = t.id
      this.draggingGroup = group
      this._draggingTask = t
    },
    onDragEnd() {
      this.draggingId = null
      this.draggingGroup = null
      this.dragOverGroup = null
    },
    onDragOver(group) { this.dragOverGroup = group },
    onDrop(targetGroup) {
      if (!this._draggingTask || targetGroup === this.draggingGroup) {
        this.dragOverGroup = null; return
      }
      const updated = { ...this._draggingTask, group: targetGroup }
      this.$emit('edit', updated)
      // 즉시 저장
      this.$emit('move-group', { task: this._draggingTask, newGroup: targetGroup })
      this.dragOverGroup = null
    },
    isOverdue(t) {
      const d = diffDays(t.endDate)
      return d !== null && d < 0 && parseInt(t.progress || 0) < 100
    },
    dateClass(t) {
      const d = diffDays(t.endDate)
      if (d === null) return 'muted'
      if (d < 0)  return 'date-over'
      if (d === 0) return 'date-today'
      if (d <= 7)  return 'date-soon'
      return 'muted'
    },
    pbClass(t) {
      const p = parseInt(t.progress || 0)
      return p >= 100 ? 'pf-green' : p >= 50 ? 'pf-yellow' : 'pf-red'
    },
    isLink(str)  { return str && (str.startsWith('http') || str.startsWith('www')) },
    jiraLabel(url) {
      try {
        const match = url.match(/([A-Z]+-\d+)/)
        if (match) return match[1]
        return 'Link'
      } catch { return 'Link' }
    },
    toggleMenu(id, event) {
      if (this.activeMenuId === id) { this.activeMenuId = null; return }
      this.activeMenuId = id
      this.$nextTick(() => {
        const btn = event.currentTarget
        const rect = btn.getBoundingClientRect()
        const menu = this.$el.querySelector('.dropdown-menu')
        if (menu) {
          menu.style.top  = (rect.bottom + 4) + 'px'
          menu.style.left = (rect.right - 88) + 'px'
        }
      })
    },
    closeMenu()    { this.activeMenuId = null },
    handleEdit(t)  { this.$emit('edit', t); this.closeMenu() },
    handleDelete(t){
      if (confirm(`[${t.task}] 태스크를 삭제하시겠습니까?`)) this.$emit('delete', t.id)
      this.closeMenu()
    },
    focusNextOverdue() { this.focusNextByStatus('overdue') },
    focusNextByStatus(status) {
      if (!this.statusIdx[status]) this.statusIdx[status] = 0
      const ids = []
      Object.values(this.grouped).forEach(list => {
        list.filter(t => {
          const s = getStatus(t)
          if (status === 'overdue')  return s === 'overdue'
          if (status === 'risk')     return s === 'risk'
          if (status === 'progress') return s === 'progress' || s === 'done'
          return false
        }).forEach(t => ids.push(t.id))
      })
      if (!ids.length) return
      const id = ids[this.statusIdx[status] % ids.length]
      this.statusIdx[status]++
      this.focusedId = id
      this.$nextTick(() => {
        const el = this.$el.querySelector(`[data-task-id="${id}"]`)
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        setTimeout(() => { this.focusedId = null }, 1800)
      })
    },
  }
}
</script>

<style scoped>
.sort-bar   { display:flex; align-items:center; gap:10px; margin-bottom:10px }
.sort-label { font-size:12px; color:var(--muted) }
.sort-btns  { display:flex; gap:4px }
.sort-btn   { padding:4px 10px; border-radius:6px; border:1px solid var(--border2); background:transparent; color:var(--muted); font-size:12px; cursor:pointer; font-family:inherit; transition:all .15s }
.sort-btn.on{ background:var(--bg4); color:var(--text); border-color:var(--border) }

.wbs-wrap  { background:var(--bg2); border:1px solid var(--border); border-radius:12px; overflow:hidden }
.wbs-table { width:100%; border-collapse:collapse; table-layout:fixed; min-width:978px }
.wbs-table th { background:var(--bg3); padding:9px 10px; text-align:left; font-size:12px; font-weight:600; color:var(--muted); border-bottom:1px solid var(--border); white-space:nowrap }
.wbs-table td { padding:9px 10px; border-bottom:1px solid var(--border); vertical-align:middle; height:44px }
.wbs-table td.ellipsis { overflow:hidden; white-space:nowrap; text-overflow:ellipsis }
.wbs-table tr:last-child td { border-bottom:none }

/* 공통 셀 폰트 — 담당자 기준으로 통일 */
.cell-text { font-size:13px; font-weight:400; font-family:'Noto Sans KR',sans-serif }
.cell-date { font-size:13px; font-weight:400; font-family:'DM Mono',monospace; white-space:nowrap }

.task-name-cell { display:flex; align-items:center; gap:6px; overflow:hidden }
.task-name  { font-size:13px; font-weight:600; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; flex:1; min-width:0 }
.overdue-chip {
  flex-shrink:0;
  display:inline-flex; align-items:center;
  padding:1px 6px; border-radius:4px;
  font-size:11px; font-weight:600;
  background:var(--red-dim); color:var(--red);
  white-space:nowrap;
}
.center    { text-align:center }
.muted     { color:var(--muted) }

/* 마감일 색상 */
.date-over  { color:var(--red) !important; font-family:'DM Mono',monospace; font-size:13px }
.date-today { color:var(--yellow) !important; font-family:'DM Mono',monospace; font-size:13px }
.date-soon  { color:var(--blue) !important; font-family:'DM Mono',monospace; font-size:13px }

.jira-link { color:var(--blue); text-decoration:none; font-size:13px; font-weight:500 }
.jira-link:hover { text-decoration:underline }

.prog-row  { display:flex; align-items:center; gap:8px }
.prog-wrap { flex:0 0 70px; height:5px; background:var(--bg4); border-radius:3px; overflow:hidden }
.prog-fill { height:100%; transition:width .3s }
.pf-green  { background:var(--green) }
.pf-yellow { background:var(--yellow) }
.pf-red    { background:var(--red) }

/* 상태 — 왼쪽 정렬 (td 기본이 left) */
.status-badge { padding:3px 10px; border-radius:6px; font-size:12px; font-weight:600; display:inline-block; white-space:nowrap }
.sb-done    { background:var(--green-dim); color:var(--green) }
.sb-progress{ background:var(--blue-dim);  color:var(--blue) }
.sb-risk    { background:var(--yellow-dim);color:var(--yellow) }
.sb-overdue { background:var(--red-dim);   color:var(--red) }
.sb-pending { background:var(--bg4);       color:var(--muted) }

.note { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; cursor:pointer; max-width:0; width:100% }
.note:hover { color:var(--text) }
.nowrap { white-space:nowrap }

/* 태스크 상세 팝업 */
.detail-overlay { position:fixed; inset:0; background:rgba(0,0,0,.4); z-index:500; display:flex; align-items:center; justify-content:center }
.detail-popup { background:var(--bg2); border:1px solid var(--border2); border-radius:12px; width:420px; max-width:90vw; overflow:hidden }
.detail-popup-header { display:flex; align-items:flex-start; justify-content:space-between; padding:16px 20px; border-bottom:1px solid var(--border); gap:12px }
.detail-popup-title { font-size:14px; font-weight:600; color:var(--text); line-height:1.5 }
.detail-close { background:none; border:none; color:var(--muted); cursor:pointer; font-size:14px; padding:2px; flex-shrink:0 }
.detail-close:hover { color:var(--text) }
.detail-popup-body { padding:16px 20px; display:flex; flex-direction:column; gap:10px }
.detail-row { display:flex; gap:12px; font-size:13px }
.detail-key { color:var(--muted); width:52px; flex-shrink:0; font-size:12px }
.detail-note { align-items:flex-start }
.detail-note span:last-child { line-height:1.6; color:var(--text) }

/* 그룹 행 — 라이트모드 색상 */
.group-row td { background:var(--bg3); padding:8px 12px; border-bottom:1px solid var(--border) }
.group-badge  { padding:3px 8px; border-radius:5px; font-size:11px; font-weight:600; display:inline-block }
.gb-plan    { background:#dbeafe; color:#1d4ed8 }
.gb-design  { background:#ede9fe; color:#6d28d9 }
.gb-be      { background:#dcfce7; color:#15803d }
.gb-fe      { background:#fef9c3; color:#a16207 }
.gb-android { background:#ffedd5; color:#c2410c }
.gb-ios     { background:#cffafe; color:#0e7490 }
.gb-qa      { background:#fce7f3; color:#be185d }

.risk-chip {
  flex-shrink:0; display:inline-flex; align-items:center;
  padding:2px 6px; border-radius:4px;
  font-size:11px; font-weight:600;
  background:var(--yellow-dim); color:var(--yellow);
  white-space:nowrap;
}
/* 드래그앤드롭 */
.drag-handle { cursor:grab; font-size:14px; color:var(--border2); user-select:none }
.drag-handle:hover { color:var(--muted) }
.task-row.dragging { opacity:.4 }
.group-row.drop-target td { background:var(--amber-dim) !important }
.drop-hint { margin-left:8px; font-size:11px; color:var(--amber); font-weight:600 }
.row-focused td { background:rgba(239,68,68,.1) !important; transition:background .3s }
.task-row td { transition:background .3s }

/* 3dot */
.action-cell  { text-align:center; position:relative }
.menu-wrapper { position:static; display:inline-block }
.dot-btn      { background:none; border:none; color:var(--muted); cursor:pointer; padding:5px; border-radius:5px; display:flex; align-items:center }
.dot-btn:hover{ background:var(--bg4); color:var(--text) }
.dropdown-menu{
  position:fixed;
  background:var(--bg2); border:1px solid var(--border2);
  border-radius:8px; padding:4px; z-index:999;
  min-width:88px;
  box-shadow:0 2px 8px rgba(0,0,0,.15);
  display:flex; flex-direction:column; gap:2px
}
.dropdown-item{ width:100%; background:none; border:none; padding:7px 10px; text-align:left; color:var(--text); font-size:13px; cursor:pointer; border-radius:5px; font-weight:500; font-family:inherit }
.dropdown-item:hover { background:var(--bg3) }
.dropdown-item.danger { color:var(--red) }
.empty-state { text-align:center; padding:40px; color:var(--muted); font-size:13px }

/* 스켈레톤 */
.sk-row td { padding:12px }
.sk { background:var(--bg4); border-radius:5px; animation:shimmer 1.4s infinite }
.sk-name { height:12px; width:80% }
.sk-sm   { height:11px; width:60px }
.sk-md   { height:11px; width:90px }
.sk-lg   { height:11px; width:120px }
.sk-xs   { height:11px; width:30px }
@keyframes shimmer { 0%{opacity:.4} 50%{opacity:.9} 100%{opacity:.4} }
</style>