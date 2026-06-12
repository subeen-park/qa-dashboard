<template>
  <div>
    <div class="detail-bar">
      <div class="breadcrumb">
        <span class="bc-link" @click="$emit('back')">WBS 목록</span>
        <span class="bc-sep">›</span>
        <span class="bc-cur">{{ project.name }}</span>
      </div>
      <div class="bar-right">
        <div class="inner-search">
          <span style="color:var(--muted);font-size:13px">⌕</span>
          <input v-model="taskSearch" placeholder="태스크, 담당자 검색..." />
        </div>

        <div class="upload-wrap" ref="uploadWrap">
          <button class="btn btn-ghost btn-sm" @click="showUploadMenu=!showUploadMenu" :disabled="isUploading">
            {{ isUploading ? '⏳ 업로드 중...' : '업로드 ▾' }}
          </button>
          <div v-if="showUploadMenu" class="upload-menu">
            <input type="file" ref="excelInput" style="display:none" accept=".xlsx,.xls,.csv" @change="onFileSelected" />
            <button class="upload-item" @click="$refs.excelInput.click(); showUploadMenu=false">
              📄 엑셀 파일 업로드
            </button>
            <button class="upload-item" @click="showSheetsModal=true; showUploadMenu=false">
              🔗 Google Sheets 링크
            </button>
            <div class="upload-divider"></div>
            <button class="upload-item" @click="downloadTemplate(); showUploadMenu=false">
              ⬇️ 업로드 양식 다운받기
            </button>
            <div class="upload-divider"></div>
            <button class="upload-item" @click="showHistory=true; loadSnapshots(); showUploadMenu=false">
              🕐 업로드 기록 / 원복
            </button>
          </div>
        </div>

        <button class="btn btn-ghost btn-sm" @click="$emit('edit-project', project)">프로젝트 수정</button>
        <button class="btn btn-ghost btn-sm" @click="showBulkModal=true" v-if="tasks.length">📊 진행률 일괄 수정</button>
        <button class="btn btn-danger-ghost btn-sm" @click="confirmDeleteAll" v-if="tasks.length">🗑 전체 삭제</button>
        <button class="btn btn-primary btn-sm" @click="openAdd">+ 태스크 추가</button>
      </div>
    </div>

    <div class="detail-body">
      <div class="metrics">
        <div class="mc"><div class="mc-label">전체</div><div class="mc-val" style="color:var(--blue)">{{ tasks.length }}</div></div>
        <div class="mc mc-clickable" @click="focusStatus('progress')" title="진행중 태스크로 이동">
          <div class="mc-label">진행중 <span class="mc-arrow">↓</span></div>
          <div class="mc-val" style="color:var(--green)">{{ cnt('progress') + cnt('done') }}</div>
          <div v-if="cnt('progress')+cnt('done')" class="mc-sub">클릭해서 확인</div>
        </div>
        <div class="mc mc-clickable" @click="focusStatus('risk')" title="리스크 태스크로 이동">
          <div class="mc-label">리스크 <span class="mc-hint">D-7 이내</span> <span class="mc-arrow">↓</span></div>
          <div class="mc-val" style="color:var(--yellow)">{{ cnt('risk') }}</div>
          <div v-if="cnt('risk')" class="mc-sub">클릭해서 확인</div>
        </div>
        <div class="mc mc-clickable" @click="focusStatus('overdue')" title="지연 태스크로 이동">
          <div class="mc-label">지연 <span class="mc-arrow">↓</span></div>
          <div class="mc-val" style="color:var(--red)">{{ cnt('overdue') }}</div>
          <div v-if="cnt('overdue')" class="mc-sub">클릭해서 확인</div>
        </div>
      </div>

      <div class="tabs">
        <div v-for="t in TABS" :key="t.key" class="tab" :class="{on: activeTab===t.key}" @click="activeTab=t.key">
          {{ t.label }}
        </div>
      </div>

      <task-table v-if="activeTab==='tasks'" :tasks="tasks" :search="taskSearch"
        :focus-overdue-at="focusOverdueAt" :focus-status-at="focusStatusAt"
        :loading="tasksLoading"
        @edit="openEdit" @delete="deleteTask" @move-group="moveTaskGroup" />

      <!-- 스티키 네비게이터 (진행중/리스크/지연) -->
      <div v-if="activeTab==='tasks' && navStatus && !navClosed"
        class="status-nav" :class="'nav-'+navStatus">
        <div class="status-nav-inner">
          <span class="status-nav-icon">{{ navIcon }}</span>
          <span class="status-nav-text">
            {{ navLabel }} <b>{{ navCount }}건</b> — 클릭해서 순서대로 확인
          </span>
          <button class="status-nav-btn" @click="focusStatus(navStatus)">
            다음 ↓
          </button>
          <button class="status-nav-close" @click="navClosed=true">✕</button>
        </div>
      </div>
      <gantt-chart v-if="activeTab==='gantt'" :tasks="tasks" />
      <notif-panel v-if="activeTab==='notif'" :tasks="tasks" :logs="logs"
        @toast="$emit('toast',$event)" @reload-logs="$emit('reload-logs')" />
    </div>

    <task-form v-model="showForm" :edit-task="editingTask" :project-id="project.id"
      @save="saveTask" @delete="deleteTask" />

    <!-- 진행률 일괄 수정 모달 -->
    <div v-if="showBulkModal" class="overlay" @click.self="showBulkModal=false">
      <div class="modal modal-wide">
        <div class="modal-title">📊 진행률 일괄 수정</div>
        <p class="modal-desc">태스크별 진행률을 한번에 수정할 수 있어요.</p>
        <div class="bulk-list">
          <div v-for="t in bulkTasks" :key="t.id" class="bulk-row">
            <div class="bulk-info">
              <span class="bulk-group" :style="groupBadgeStyle(t.group)">{{ t.group }}</span>
              <span class="bulk-name">{{ t.task }}</span>
            </div>
            <div class="bulk-control">
              <input type="range" min="0" max="100" step="5" v-model.number="t.progress" class="bulk-slider" />
              <span class="bulk-val">{{ t.progress }}%</span>
              <select v-model.number="t.progress" class="bulk-select">
                <option v-for="p in [0,10,20,30,40,50,60,70,80,90,100]" :key="p" :value="p">{{ p }}%</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-ghost" @click="showBulkModal=false">취소</button>
          <button class="btn btn-primary" @click="saveBulkProgress" :disabled="isSavingBulk">
            {{ isSavingBulk ? '저장 중...' : '저장하기' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 업로드 확인 모달 -->
    <div v-if="showUploadConfirm" class="overlay">
      <div class="modal">
        <div class="modal-icon">⚠️</div>
        <div class="modal-title">기존 태스크를 삭제하고 업로드할까요?</div>
        <p class="modal-desc">
          현재 <b>{{ tasks.length }}개</b>의 태스크가 등록되어 있습니다.<br>
          업로드 시 기존 데이터는 <b>자동 백업</b>되고, 새 데이터로 교체됩니다.<br>
          업로드 기록에서 언제든 원복할 수 있어요.
        </p>
        <div class="modal-actions">
          <button class="btn btn-ghost" @click="cancelUpload">취소</button>
          <button class="btn btn-danger" @click="confirmUpload">교체하기</button>
        </div>
      </div>
    </div>

    <!-- Google Sheets 모달 -->
    <div v-if="showSheetsModal" class="overlay" @click.self="showSheetsModal=false">
      <div class="modal">
        <div class="modal-title">Google Sheets 링크로 업로드</div>
        <p class="modal-desc">Google Sheets를 <b>링크가 있는 모든 사용자 — 뷰어</b> 공유 설정 후 URL을 붙여넣으세요.</p>
        <div class="field">
          <label>Google Sheets URL</label>
          <input v-model="sheetsUrl" placeholder="https://docs.google.com/spreadsheets/d/..." />
        </div>
        <div class="modal-actions">
          <button class="btn btn-ghost" @click="showSheetsModal=false">취소</button>
          <button class="btn btn-primary" @click="onSheetsConfirmRequest" :disabled="isUploading">확인</button>
        </div>
      </div>
    </div>

    <!-- 히스토리 / 원복 모달 -->
    <div v-if="showHistory" class="overlay" @click.self="showHistory=false">
      <div class="modal modal-wide">
        <div class="modal-title">🕐 업로드 기록 / 원복</div>
        <p class="modal-desc">업로드 전 자동 저장된 백업 목록이에요. 원하는 시점으로 원복할 수 있어요.</p>
        <div v-if="snapshots.length === 0" class="empty-state">저장된 백업이 없습니다</div>
        <div v-else class="snapshot-list">
          <div v-for="s in snapshots" :key="s.id" class="snapshot-row">
            <div class="snapshot-info">
              <div class="snapshot-label">{{ s.label }}</div>
              <div class="snapshot-time">{{ s.created_at }}</div>
            </div>
            <button class="btn btn-ghost btn-sm" @click="restoreSnapshot(s)" :disabled="isRestoring">
              {{ isRestoring && restoringId===s.id ? '복원 중...' : '이 시점으로 원복' }}
            </button>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-ghost" @click="showHistory=false">닫기</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { api } from '../api/index.js'
import { getStatus } from '../utils.js'
import TaskTable  from './TaskTable.vue'
import GanttChart from './GanttChart.vue'
import NotifPanel from './NotifPanel.vue'
import TaskForm   from './TaskForm.vue'

const TABS = [
  { key:'tasks', label:'태스크 목록' },
  { key:'gantt', label:'간트 차트' },
  { key:'notif', label:'알림 설정' },
]

export default {
  name: 'WBSDetail',
  components: { TaskTable, GanttChart, NotifPanel, TaskForm },
  props: { project: Object, logs: Array },
  emits: ['back', 'edit-project', 'toast', 'reload-logs', 'refresh-projects'],
  data() {
    return {
      tasks: [], activeTab: 'tasks', showForm: false,
      editingTask: null, taskSearch: '', TABS,
      isUploading: false, showUploadMenu: false,
      showSheetsModal: false, sheetsUrl: '',
      focusOverdueAt: 0, tasksLoading: true,
      navStatus: '', navClosed: true,
      focusStatusAt: { status: '', ts: 0 },
      showBulkModal: false, bulkTasks: [], isSavingBulk: false,
      showUploadConfirm: false,
      pendingFile: null, pendingSheetsUrl: null,
      showHistory: false, snapshots: [],
      isRestoring: false, restoringId: null,
    }
  },
  async mounted() {
    await this.loadTasks()
    document.addEventListener('click', this.closeUploadMenu)
  },
  beforeUnmount() { document.removeEventListener('click', this.closeUploadMenu) },
  watch: {
    project() { this.loadTasks() },
    showBulkModal(v) {
      if (v) this.bulkTasks = this.tasks.map(t => ({ ...t }))
    },
  },
  computed: {
    navIcon()  { return { progress:'🟢', risk:'⚠️', overdue:'🚨' }[this.navStatus] || '' },
    navLabel() { return { progress:'진행중', risk:'리스크', overdue:'지연' }[this.navStatus] || '' },
    navCount() {
      if (this.navStatus === 'overdue')  return this.cnt('overdue')
      if (this.navStatus === 'risk')     return this.cnt('risk')
      if (this.navStatus === 'progress') return this.cnt('progress') + this.cnt('done')
      return 0
    },
  },
  methods: {
    async loadTasks() {
      this.tasksLoading = true
      this.tasks = await api.getTasks(this.project.id)
      this.tasksLoading = false
    },
    cnt(s) { return this.tasks.filter(t => getStatus(t) === s).length },
    openAdd()      { this.editingTask = null; this.showForm = true },
    openEdit(task) { this.editingTask = {...task}; this.showForm = true },

    focusStatus(status) {
      const hasItems = status === 'overdue' ? this.cnt('overdue') :
                       status === 'risk'    ? this.cnt('risk') :
                       this.cnt('progress') + this.cnt('done')
      if (!hasItems) return
      if (this.activeTab !== 'tasks') this.activeTab = 'tasks'
      this.navStatus = status
      this.navClosed = false
      this.$nextTick(() => { this.focusStatusAt = { status, ts: Date.now() } })
    },
    focusOverdue() { this.focusStatus('overdue') },

    closeUploadMenu(e) {
      if (this.$refs.uploadWrap && !this.$refs.uploadWrap.contains(e.target)) {
        this.showUploadMenu = false
      }
    },

    onFileSelected(event) {
      var file = event.target.files[0]
      if (!file) return
      if (this.tasks.length > 0) {
        this.pendingFile = file
        this.showUploadConfirm = true
      } else {
        this.doFileUpload(file)
      }
      event.target.value = ''
    },

    onSheetsConfirmRequest() {
      if (!this.sheetsUrl.trim()) { this.$emit('toast', {msg:'URL을 입력하세요', type:'err'}); return }
      if (this.tasks.length > 0) {
        this.pendingSheetsUrl = this.sheetsUrl
        this.showSheetsModal = false
        this.showUploadConfirm = true
      } else {
        this.showSheetsModal = false
        this.doSheetsUpload(this.sheetsUrl)
      }
    },

    confirmUpload() {
      this.showUploadConfirm = false
      if (this.pendingFile) {
        this.doFileUpload(this.pendingFile)
        this.pendingFile = null
      } else if (this.pendingSheetsUrl) {
        this.doSheetsUpload(this.pendingSheetsUrl)
        this.pendingSheetsUrl = null
      }
    },
    cancelUpload() {
      this.showUploadConfirm = false
      this.pendingFile = null
      this.pendingSheetsUrl = null
    },

    async doFileUpload(file) {
      this.isUploading = true
      try {
        var res = await api.uploadExcel(this.project.id, file)
        this.$emit('toast', {msg: res.count + '개 태스크 등록 완료', type:'ok'})
        await this.loadTasks(); this.$emit('refresh-projects')
      } catch(e) {
        this.$emit('toast', {msg: '업로드 실패: ' + e.message, type:'err'})
      } finally { this.isUploading = false }
    },

    async doSheetsUpload(url) {
      var csvUrl = this.sheetsToCsvUrl(url)
      if (!csvUrl) { this.$emit('toast', {msg:'올바른 Google Sheets URL이 아닙니다', type:'err'}); return }
      this.isUploading = true
      try {
        var res = await api.uploadSheetsUrl(this.project.id, csvUrl)
        this.$emit('toast', {msg: res.count + '개 태스크 등록 완료', type:'ok'})
        this.sheetsUrl = ''
        await this.loadTasks(); this.$emit('refresh-projects')
      } catch(e) {
        this.$emit('toast', {msg: '가져오기 실패: ' + e.message, type:'err'})
      } finally { this.isUploading = false }
    },

    sheetsToCsvUrl(url) {
      var match = url.match(/spreadsheets\/d\/([a-zA-Z0-9-_]+)/)
      if (!match) return null
      var id = match[1]
      var gidMatch = url.match(/gid=(\d+)/)
      var gid = gidMatch ? gidMatch[1] : '0'
      return 'https://docs.google.com/spreadsheets/d/' + id + '/export?format=csv&gid=' + gid
    },

    downloadTemplate() {
      var headers = ['Group', 'Task', 'Subtask', 'Note', 'JIRA', 'Team', 'Assignee', 'Start Date', 'End Date', 'Progress']
      var sample = [
        ['기획', '', '신규 기능 기획서 작성', '요구사항 정의 포함', 'PROJ-001', '기획팀', '기획자1', '2025-10-17', '2025-10-27', '100'],
        ['디자인', '', 'UI 화면 설계', '와이어프레임 포함', '', '디자인팀', '디자인1', '2025-10-20', '2025-11-05', '80'],
        ['개발(BE)', '', 'API 개발', '', 'PROJ-002', '개발(BE)팀', '백엔드1', '2025-11-01', '2025-11-20', '60'],
        ['개발(FE)', '', 'UI 구현', '', '', '개발(FE)팀', '프론트1', '2025-11-10', '2025-11-30', '0'],
        ['QA', '', '기능 테스트', '', '', 'QA팀', 'QA1', '2025-12-01', '2025-12-10', '0'],
      ]
      var rows = [headers].concat(sample).map(function(row) {
        return row.map(function(v) { return '"' + String(v).replace(/"/g, '""') + '"' }).join(',')
      })
      var csv = '\uFEFF' + rows.join('\r\n')
      var blob = new Blob([csv], {type:'text/csv;charset=utf-8;'})
      var url = URL.createObjectURL(blob)
      var a = document.createElement('a')
      a.href = url; a.download = 'wbs_upload_template.csv'
      document.body.appendChild(a); a.click()
      document.body.removeChild(a); URL.revokeObjectURL(url)
    },

    async saveBulkProgress() {
      this.isSavingBulk = true
      try {
        for (var i = 0; i < this.bulkTasks.length; i++) {
          var t = this.bulkTasks[i]
          var orig = this.tasks.find(function(o) { return o.id === t.id })
          if (orig && orig.progress !== t.progress) {
            await api.updateTask(this.project.id, t.id, Object.assign({}, orig, { progress: t.progress }))
          }
        }
        this.$emit('toast', { msg: '진행률이 저장되었습니다', type: 'ok' })
        this.showBulkModal = false
        await this.loadTasks(); this.$emit('refresh-projects')
      } catch(e) {
        this.$emit('toast', { msg: '저장 실패: ' + e.message, type: 'err' })
      } finally { this.isSavingBulk = false }
    },

    groupBadgeStyle(group) {
      var palettes = {
        '기획': { bg:'#dbeafe', color:'#1e40af' }, '기획팀': { bg:'#dbeafe', color:'#1e40af' },
        '디자인': { bg:'#ede9fe', color:'#5b21b6' }, '디자인팀': { bg:'#ede9fe', color:'#5b21b6' },
        '개발(BE)': { bg:'#dcfce7', color:'#166534' }, '개발(FE)': { bg:'#fef9c3', color:'#854d0e' },
        'QA': { bg:'#fce7f3', color:'#9d174d' }, 'QA팀': { bg:'#fce7f3', color:'#9d174d' },
      }
      var p = palettes[group] || { bg:'#f1f5f9', color:'#475569' }
      return { background: p.bg, color: p.color }
    },

    async moveTaskGroup(payload) {
      var task = payload.task, newGroup = payload.newGroup
      try {
        await api.updateTask(this.project.id, task.id, Object.assign({}, task, { group: newGroup }))
        await this.loadTasks()
        this.$emit('toast', { msg: task.task + ' → ' + newGroup + ' 이동 완료', type: 'ok' })
      } catch(e) {
        this.$emit('toast', { msg: '이동 실패: ' + e.message, type: 'err' })
      }
    },

    async confirmDeleteAll() {
      if (!confirm('태스크 ' + this.tasks.length + '개를 전체 삭제하시겠습니까?')) return
      try {
        await api.saveSnapshotBeforeDelete(this.project.id)
        for (var i = 0; i < this.tasks.length; i++) {
          await api.deleteTask(this.project.id, this.tasks[i].id)
        }
        this.$emit('toast', { msg: '전체 태스크가 삭제되었습니다', type: 'info' })
        await this.loadTasks(); this.$emit('refresh-projects')
      } catch(e) {
        this.$emit('toast', { msg: '삭제 실패: ' + e.message, type: 'err' })
      }
    },

    async loadSnapshots() {
      try { this.snapshots = await api.getSnapshots(this.project.id) }
      catch(e) { this.snapshots = [] }
    },

    async restoreSnapshot(s) {
      if (!confirm(s.label + '\n\n이 시점으로 원복하시겠습니까? 현재 데이터는 백업됩니다.')) return
      this.isRestoring = true; this.restoringId = s.id
      try {
        var res = await api.restoreSnapshot(this.project.id, s.id)
        this.$emit('toast', {msg: res.count + '개 태스크로 원복 완료', type:'ok'})
        await this.loadTasks(); this.$emit('refresh-projects')
        await this.loadSnapshots()
      } catch(e) {
        this.$emit('toast', {msg: '원복 실패: ' + e.message, type:'err'})
      } finally { this.isRestoring = false; this.restoringId = null }
    },

    async saveTask(form) {
      if (form.id) await api.updateTask(this.project.id, form.id, form)
      else         await api.createTask(this.project.id, form)
      this.showForm = false
      await this.loadTasks(); this.$emit('refresh-projects')
      this.$emit('toast', {msg: form.id ? '태스크가 수정되었습니다' : '태스크가 추가되었습니다', type:'ok'})
    },
    async deleteTask(tid) {
      await api.deleteTask(this.project.id, tid)
      this.showForm = false
      await this.loadTasks(); this.$emit('refresh-projects')
      this.$emit('toast', {msg:'삭제되었습니다', type:'info'})
    },
  }
}
</script>

<style scoped>
.detail-bar { background:var(--bg2); border-bottom:1px solid var(--border); padding:14px 24px; display:flex; align-items:center; justify-content:space-between; gap:12px }
.breadcrumb { display:flex; align-items:center; gap:10px; font-size:14px }
.bc-link    { color:var(--amber); cursor:pointer }.bc-link:hover{ text-decoration:underline }
.bc-sep     { color:var(--faint) }
.bc-cur     { color:var(--text); font-weight:600 }
.bar-right  { display:flex; align-items:center; gap:10px }
.inner-search{ display:flex; align-items:center; gap:8px; background:var(--bg3); border:1px solid var(--border2); border-radius:8px; padding:7px 12px }
.inner-search input{ background:transparent; border:none; outline:none; color:var(--text); font-size:13px; width:180px; font-family:inherit }
.inner-search input::placeholder{ color:var(--muted) }
.detail-body{ padding:20px 24px }

.metrics  { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:20px }
.mc       { background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:16px 20px }
.mc-label { font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:6px; display:flex; align-items:center; gap:6px }
.mc-hint  { font-size:10px; color:var(--muted); font-weight:400; text-transform:none; letter-spacing:0 }
.mc-val   { font-size:26px; font-family:'DM Mono',monospace; font-weight:600 }
.mc-sub   { font-size:11px; color:var(--muted); margin-top:4px }
.mc-arrow { font-size:11px }
.mc-clickable { cursor:pointer; transition:all .15s; user-select:none }
.mc-clickable:hover { filter:brightness(.95) }
.mc-clickable:active { transform:scale(.98) }

.tabs { display:flex; gap:4px; background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:5px; width:fit-content; margin-bottom:16px }
.tab  { padding:8px 20px; border-radius:8px; cursor:pointer; font-size:14px; color:var(--muted); transition:all .15s; font-weight:500 }
.tab.on { background:var(--bg4); color:var(--text) }

.btn        { display:inline-flex; align-items:center; gap:6px; padding:7px 14px; border-radius:7px; font-size:13px; font-family:inherit; cursor:pointer; border:none; font-weight:500; transition:all .15s }
.btn-primary{ background:var(--amber); color:#0a0800 }.btn-primary:hover{ background:#f0b85a }
.btn-ghost  { background:transparent; color:var(--muted); border:1px solid var(--border2) }.btn-ghost:hover{ background:var(--bg3); color:var(--text) }
.btn-danger { background:var(--red); color:#fff }.btn-danger:hover{ opacity:.85 }
.btn-danger-ghost { background:transparent; color:var(--red); border:1px solid var(--red) }.btn-danger-ghost:hover{ background:var(--red-dim) }
.btn-sm     { padding:6px 12px; font-size:12px }
.btn:disabled{ opacity:.5; cursor:not-allowed }

.upload-wrap { position:relative }
.upload-menu { position:absolute; right:0; top:36px; background:var(--bg2); border:1px solid var(--border2); border-radius:8px; padding:4px; z-index:200; min-width:180px; box-shadow:0 2px 8px rgba(0,0,0,.12); display:flex; flex-direction:column; gap:2px }
.upload-item { width:100%; background:none; border:none; padding:9px 12px; text-align:left; color:var(--text); font-size:13px; cursor:pointer; border-radius:6px; font-family:inherit; font-weight:500 }
.upload-item:hover { background:var(--bg3) }
.upload-divider { height:1px; background:var(--border); margin:3px 0 }

.overlay { position:fixed; inset:0; background:rgba(0,0,0,.5); z-index:300; display:flex; align-items:center; justify-content:center }
.modal   { background:var(--bg2); border:1px solid var(--border2); border-radius:12px; padding:28px; width:440px; max-width:90vw }
.modal-wide { width:560px }
.modal-icon  { font-size:32px; margin-bottom:12px }
.modal-title { font-size:15px; font-weight:600; margin-bottom:8px }
.modal-desc  { font-size:13px; color:var(--muted); margin-bottom:16px; line-height:1.7 }
.field       { margin-bottom:12px }
.field label { display:block; font-size:11px; color:var(--muted); margin-bottom:4px }
.field input { width:100%; background:var(--bg3); border:1px solid var(--border2); border-radius:6px; padding:8px 10px; color:var(--text); font-size:13px; font-family:inherit; outline:none }
.field input:focus { border-color:var(--amber) }
.modal-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:20px }

.snapshot-list { display:flex; flex-direction:column; gap:6px; max-height:300px; overflow-y:auto; margin-bottom:8px }
.snapshot-row  { display:flex; align-items:center; justify-content:space-between; background:var(--bg3); border:1px solid var(--border); border-radius:8px; padding:10px 14px; gap:12px }
.snapshot-info { flex:1 }
.snapshot-label{ font-size:13px; font-weight:500; color:var(--text) }
.snapshot-time { font-size:11px; color:var(--muted); margin-top:2px }
.empty-state { text-align:center; padding:24px; color:var(--muted); font-size:13px }

/* 일괄 수정 */
.bulk-list  { display:flex; flex-direction:column; gap:6px; max-height:400px; overflow-y:auto; margin-bottom:12px }
.bulk-row   { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:8px 10px; background:var(--bg3); border-radius:8px }
.bulk-info  { display:flex; align-items:center; gap:8px; flex:1; min-width:0 }
.bulk-group { padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600; white-space:nowrap; flex-shrink:0 }
.bulk-name  { font-size:13px; color:var(--text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap }
.bulk-control { display:flex; align-items:center; gap:8px; flex-shrink:0 }
.bulk-slider{ width:100px; accent-color:var(--amber) }
.bulk-val   { font-size:12px; font-family:'DM Mono',monospace; color:var(--text); width:36px; text-align:right }
.bulk-select{ background:var(--bg2); border:1px solid var(--border2); border-radius:5px; padding:3px 6px; color:var(--text); font-size:12px; outline:none }

/* 스티키 상태 네비게이터 */
.status-nav { position:sticky; bottom:16px; z-index:100; display:flex; justify-content:center; margin-top:12px; pointer-events:none }
.status-nav-inner { display:flex; align-items:center; gap:10px; padding:10px 16px; border-radius:28px; font-size:13px; font-weight:500; box-shadow:0 4px 16px rgba(0,0,0,.2); pointer-events:all; transition:all .2s }
.nav-progress .status-nav-inner { background:var(--green); color:#fff }
.nav-risk     .status-nav-inner { background:var(--yellow); color:#0a0800 }
.nav-overdue  .status-nav-inner { background:var(--red); color:#fff }
.status-nav-icon  { font-size:15px }
.status-nav-text  { white-space:nowrap }
.status-nav-text b{ font-weight:700 }
.status-nav-btn   { background:rgba(255,255,255,.2); border:1px solid rgba(255,255,255,.4); color:inherit; padding:5px 12px; border-radius:16px; cursor:pointer; font-size:12px; font-weight:600; font-family:inherit; white-space:nowrap; transition:background .15s }
.status-nav-btn:hover { background:rgba(255,255,255,.35) }
.status-nav-close { background:none; border:none; color:inherit; opacity:.8; cursor:pointer; font-size:14px; padding:2px 4px; line-height:1 }
.status-nav-close:hover { opacity:1 }
</style>