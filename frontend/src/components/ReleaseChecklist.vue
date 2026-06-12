<template>
  <div class="cl-page">
    <div class="cl-topbar">
      <div>
        <h2 class="cl-title">릴리즈 체크리스트</h2>
        <p class="cl-desc">릴리즈 전 필수 확인 항목을 팀별로 체크하세요</p>
      </div>
      <button class="btn btn-primary" @click="showNewBoard = true">+ 새 체크리스트</button>
    </div>

    <!-- 버전 탭 네비 -->
    <div v-if="boards.length > 0" class="version-nav">
      <div v-for="board in boards" :key="'nav-'+board.id"
        class="version-tab"
        :class="{ 'tab-done': boardProgress(board) === 100, 'tab-active': activeBoard === board.id }"
        @click="scrollToBoard(board.id)">
        <span class="vtab-version">{{ board.version }}</span>
        <span class="vtab-pct">{{ boardProgress(board) }}%</span>
      </div>
    </div>

    <div v-if="boards.length === 0" class="empty-hero">
      <div class="empty-title">체크리스트가 없습니다</div>
      <div class="empty-desc">릴리즈 버전별 체크리스트를 만들어 팀과 함께 진행 상황을 공유하세요.</div>
      <button class="btn btn-primary" @click="showNewBoard = true">+ 체크리스트 만들기</button>
    </div>

    <div v-else class="boards-grid">
      <div v-for="board in boards" :key="board.id" class="board-card"
        :ref="'board-' + board.id"
        :class="{ 'board-done': boardProgress(board) === 100, 'board-focused': activeBoard === board.id }">

        <div class="board-card-header">
          <div class="board-header-info">
            <div class="board-top-row">
              <span class="board-version">{{ board.version }}</span>
              <span class="board-done-badge" v-if="boardProgress(board) === 100">완료</span>
            </div>
            <div class="board-name">{{ board.name }}</div>
            <div class="board-date" v-if="board.date">{{ board.date }}</div>
          </div>
          <div class="board-prog-wrap">
            <svg class="progress-ring" width="52" height="52" viewBox="0 0 52 52">
              <circle class="ring-bg" cx="26" cy="26" r="22" />
              <circle class="ring-fill" cx="26" cy="26" r="22"
                :stroke-dasharray="CIRC + ' ' + CIRC"
                :stroke-dashoffset="ringOffset(board)"
                :stroke="boardProgress(board) === 100 ? 'var(--green)' : 'var(--amber)'" />
            </svg>
            <span class="ring-pct">{{ boardProgress(board) }}%</span>
          </div>
        </div>

        <!-- 진행률 바 -->
        <div class="board-prog-bar-wrap">
          <div class="board-prog-bar" :style="{ width: boardProgress(board) + '%', background: boardProgress(board) === 100 ? 'var(--green)' : 'var(--amber)' }"></div>
        </div>

        <div class="board-categories">
          <div v-for="cat in board.categories" :key="cat.name" class="cat-section">
            <div class="cat-header">
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-progress">{{ cat.items.filter(function(i){ return i.checked }).length }}/{{ cat.items.length }}</span>
            </div>
            <div class="cat-items">
              <div v-for="item in cat.items" :key="item.id"
                class="check-item" :class="{ checked: item.checked }"
                @click="toggleItem(board, cat, item)">
                <div class="check-box">
                  <svg v-if="item.checked" viewBox="0 0 16 16" width="10" height="10" fill="currentColor">
                    <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
                  </svg>
                </div>
                <span class="check-label">{{ item.label }}</span>
                <span class="check-assignee" v-if="item.assignee">{{ item.assignee }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="board-footer">
          <button class="footer-btn" @click="duplicateBoard(board)">복제</button>
          <button class="footer-btn danger" @click="deleteBoard(board.id)">삭제</button>
        </div>
      </div>
    </div>

    <div v-if="showNewBoard" class="overlay" @click.self="showNewBoard = false">
      <div class="modal">
        <div class="modal-title">새 릴리즈 체크리스트</div>
        <p class="modal-desc">버전과 이름을 입력하면 기본 템플릿이 생성됩니다.</p>
        <div class="field">
          <label>버전</label>
          <input v-model="newVersion" placeholder="예: v2.1.0" />
        </div>
        <div class="field">
          <label>릴리즈명</label>
          <input v-model="newName" placeholder="예: 2024년 4월 정기 릴리즈" />
        </div>
        <div class="field">
          <label>릴리즈 예정일</label>
          <input type="date" v-model="newDate" />
        </div>
        <div class="field">
          <label>템플릿</label>
          <div class="template-options">
            <div v-for="tmpl in TEMPLATES" :key="tmpl.key"
              class="tmpl-option" :class="{ selected: selectedTemplate === tmpl.key }"
              @click="selectedTemplate = tmpl.key">
              <div class="tmpl-name">{{ tmpl.name }}</div>
              <div class="tmpl-desc">{{ tmpl.desc }}</div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-ghost" @click="showNewBoard = false">취소</button>
          <button class="btn btn-primary" @click="createBoard" :disabled="!newVersion.trim()">만들기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
var CIRC = 2 * Math.PI * 22

var TEMPLATE_DATA = {
  standard: [
    { name: 'QA / 테스트', items: [
      { label: '기능 테스트 완료', assignee: 'QA' },
      { label: '회귀 테스트 완료', assignee: 'QA' },
      { label: '크로스 브라우저 테스트', assignee: 'QA' },
      { label: '모바일 환경 테스트', assignee: 'QA' },
      { label: '성능/부하 테스트', assignee: 'QA' },
    ]},
    { name: '개발 완료', items: [
      { label: '코드 리뷰 완료', assignee: '개발' },
      { label: 'PR 머지 완료', assignee: '개발' },
      { label: '빌드 성공 확인', assignee: '개발' },
      { label: 'API 문서 업데이트', assignee: '개발' },
    ]},
    { name: '배포 준비', items: [
      { label: '스테이징 배포 확인', assignee: 'DevOps' },
      { label: '환경 변수 확인', assignee: 'DevOps' },
      { label: 'DB 마이그레이션 검토', assignee: 'DevOps' },
      { label: '롤백 플랜 수립', assignee: 'DevOps' },
      { label: '배포 알림 전송', assignee: 'PM' },
    ]},
    { name: '최종 승인', items: [
      { label: 'PM 최종 승인', assignee: 'PM' },
      { label: '디자인 QA 완료', assignee: '디자인' },
      { label: '비즈니스 요구사항 충족 확인', assignee: 'PM' },
    ]},
  ],
  hotfix: [
    { name: '원인 분석', items: [
      { label: '이슈 재현 및 원인 분석', assignee: '개발' },
      { label: '영향 범위 분석', assignee: '개발' },
      { label: '핫픽스 코드 리뷰', assignee: '개발' },
      { label: '빌드 성공 확인', assignee: '개발' },
    ]},
    { name: '빠른 QA', items: [
      { label: '핵심 기능 스모크 테스트', assignee: 'QA' },
      { label: '수정 사항 검증', assignee: 'QA' },
    ]},
    { name: '긴급 배포', items: [
      { label: 'PM / CTO 승인', assignee: 'PM' },
      { label: '스테이징 확인', assignee: 'DevOps' },
      { label: '프로덕션 배포', assignee: 'DevOps' },
      { label: '배포 후 모니터링 (30분)', assignee: 'DevOps' },
    ]},
  ],
  app: [
    { name: 'iOS', items: [
      { label: 'iOS 빌드 (Release)', assignee: 'iOS' },
      { label: 'TestFlight 배포 완료', assignee: 'iOS' },
      { label: 'App Store 심사 제출', assignee: 'iOS' },
      { label: '심사 통과 확인', assignee: 'iOS' },
    ]},
    { name: 'Android', items: [
      { label: 'Android 빌드 (Release)', assignee: 'AOS' },
      { label: '내부 테스트 배포', assignee: 'AOS' },
      { label: 'Play Store 심사 제출', assignee: 'AOS' },
      { label: '심사 통과 확인', assignee: 'AOS' },
    ]},
    { name: '공통 QA', items: [
      { label: '기능 테스트 완료', assignee: 'QA' },
      { label: '디바이스 크로스 테스트', assignee: 'QA' },
      { label: 'PM 최종 승인', assignee: 'PM' },
    ]},
  ]
}

var TEMPLATES = [
  { key: 'standard', name: '웹 릴리즈', desc: '웹 서비스 정기 릴리즈용' },
  { key: 'app',      name: '앱 릴리즈', desc: 'iOS / Android 스토어 배포용' },
  { key: 'hotfix',   name: '핫픽스',   desc: '긴급 수정 배포용' },
]

var _nextId = Date.now()
function makeId() { return ++_nextId }

function makeBoard(version, name, date, templateKey) {
  return {
    id: makeId(), version: version, name: name, date: date,
    categories: TEMPLATE_DATA[templateKey].map(function(cat) {
      return {
        name: cat.name,
        items: cat.items.map(function(item) {
          return { id: makeId(), label: item.label, assignee: item.assignee || '', checked: false }
        })
      }
    })
  }
}

function makeDummyBoards() {
  var boards = []

  // v2.4.0 — 완료된 보드
  var b1 = makeBoard('v2.4.0', '4월 1차 정기 릴리즈', '2026-04-10', 'standard')
  b1.categories.forEach(function(cat) { cat.items.forEach(function(item) { item.checked = true }) })
  boards.push(b1)

  // v2.5.0 — 진행중 보드
  var b2 = makeBoard('v2.5.0', '4월 2차 정기 릴리즈', '2026-04-25', 'standard')
  b2.categories[0].items.forEach(function(item) { item.checked = true }) // QA 완료
  b2.categories[1].items[0].checked = true // 코드리뷰 완료
  b2.categories[1].items[1].checked = true // PR 머지 완료
  boards.push(b2)

  // v1.2.3 — 핫픽스 보드
  var b3 = makeBoard('v1.2.3', '결제 오류 긴급 핫픽스', '2026-04-16', 'hotfix')
  b3.categories[0].items.forEach(function(item) { item.checked = true })
  b3.categories[1].items.forEach(function(item) { item.checked = true })
  boards.push(b3)

  return boards
}

export default {
  name: 'ReleaseChecklist',
  data() {
    return {
      boards: [],
      showNewBoard: false,
      newVersion: '',
      newName: '',
      newDate: '',
      selectedTemplate: 'standard',
      TEMPLATES: TEMPLATES,
      CIRC: CIRC,
      activeBoard: null,
    }
  },
  mounted() {
    var saved = localStorage.getItem('release-checklists')
    if (saved) {
      try { this.boards = JSON.parse(saved) } catch(e) { this.boards = makeDummyBoards() }
    } else {
      this.boards = makeDummyBoards()
      this.save()
    }
  },
  methods: {
    save() { localStorage.setItem('release-checklists', JSON.stringify(this.boards)) },
    scrollToBoard(id) {
      this.activeBoard = id
      var self = this
      this.$nextTick(function() {
        var el = self.$refs['board-' + id]
        if (el) {
          var target = Array.isArray(el) ? el[0] : el
          target.scrollIntoView({ behavior: 'smooth', block: 'start' })
          // 2초 후 포커스 하이라이트 해제
          setTimeout(function() { self.activeBoard = null }, 2000)
        }
      })
    },
    boardProgress(board) {
      var total = 0, done = 0
      board.categories.forEach(function(cat) {
        total += cat.items.length
        done += cat.items.filter(function(i) { return i.checked }).length
      })
      return total === 0 ? 0 : Math.round(done / total * 100)
    },
    ringOffset(board) { return CIRC * (1 - this.boardProgress(board) / 100) },
    toggleItem(board, cat, item) { item.checked = !item.checked; this.save() },
    createBoard() {
      if (!this.newVersion.trim()) return
      var board = makeBoard(
        this.newVersion.trim(),
        this.newName.trim() || this.newVersion.trim() + ' 릴리즈',
        this.newDate, this.selectedTemplate
      )
      this.boards.unshift(board)
      this.save()
      this.showNewBoard = false
      this.newVersion = ''; this.newName = ''; this.newDate = ''
      this.selectedTemplate = 'standard'
    },
    duplicateBoard(board) {
      var copy = JSON.parse(JSON.stringify(board))
      copy.id = makeId()
      copy.version = copy.version + ' (복사)'
      copy.categories.forEach(function(cat) { cat.items.forEach(function(item) { item.id = makeId(); item.checked = false }) })
      this.boards.unshift(copy)
      this.save()
    },
    deleteBoard(id) {
      if (!confirm('이 체크리스트를 삭제하시겠습니까?')) return
      this.boards = this.boards.filter(function(b) { return b.id !== id })
      this.save()
    },
  }
}
</script>

<style scoped>
.cl-page { padding: 20px 24px; min-height: calc(100vh - 60px); box-sizing: border-box }
.cl-topbar { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 24px }
.cl-title  { font-size: 18px; font-weight: 700; color: var(--text); margin-bottom: 2px }
.cl-desc   { font-size: 13px; color: var(--muted) }

/* 버전 탭 네비 */
.version-nav { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border) }
.version-tab { display: flex; align-items: center; gap: 7px; padding: 6px 14px; border-radius: 6px; border: 1px solid var(--border2); background: var(--bg2); cursor: pointer; transition: all .15s }
.version-tab:hover { border-color: var(--amber); background: var(--bg3) }
.version-tab.tab-active { border-color: var(--amber); background: var(--amber-dim) }
.version-tab.tab-done .vtab-pct { color: var(--green) }
.vtab-version { font-size: 12px; font-family: 'DM Mono', monospace; font-weight: 700; color: var(--text) }
.vtab-pct { font-size: 11px; font-family: 'DM Mono', monospace; color: var(--muted) }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 8px; font-size: 13px; font-family: inherit; cursor: pointer; border: none; font-weight: 500; transition: all .15s }
.btn-primary { background: var(--amber); color: #0a0800 }.btn-primary:hover { background: #f0b85a }
.btn-ghost   { background: transparent; color: var(--muted); border: 1px solid var(--border2) }.btn-ghost:hover { background: var(--bg3) }
.btn:disabled { opacity: .5; cursor: not-allowed }

.empty-hero  { text-align: center; padding: 80px 20px; display: flex; flex-direction: column; align-items: center; gap: 12px }
.empty-title { font-size: 16px; font-weight: 700; color: var(--text) }
.empty-desc  { font-size: 13px; color: var(--muted); line-height: 1.7; max-width: 340px }

.boards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 16px }

.board-card { background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: box-shadow .2s, border-color .2s }
.board-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.1) }
.board-done { border-color: var(--green) }
.board-focused { border-color: var(--amber) !important; box-shadow: 0 0 0 3px var(--amber-dim) !important }

.board-card-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 16px 18px 12px }
.board-header-info { flex: 1; min-width: 0 }
.board-top-row { display: flex; align-items: center; gap: 8px; margin-bottom: 3px }
.board-version { font-size: 11px; font-family: 'DM Mono', monospace; font-weight: 700; color: var(--amber) }
.board-done-badge { font-size: 10px; font-weight: 700; color: var(--green); background: var(--green-dim); padding: 1px 6px; border-radius: 4px }
.board-name { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 2px }
.board-date { font-size: 11px; color: var(--muted); font-family: 'DM Mono', monospace }

.board-prog-wrap { position: relative; display: flex; align-items: center; justify-content: center; flex-shrink: 0 }
.progress-ring { transform: rotate(-90deg) }
.ring-bg   { fill: none; stroke: var(--bg4); stroke-width: 3.5 }
.ring-fill { fill: none; stroke-width: 3.5; stroke-linecap: round; transition: stroke-dashoffset .4s ease }
.ring-pct  { position: absolute; font-size: 10px; font-weight: 700; font-family: 'DM Mono', monospace; color: var(--text) }

.board-prog-bar-wrap { height: 2px; background: var(--bg4); margin: 0 18px 14px; border-radius: 2px; overflow: hidden }
.board-prog-bar { height: 100%; transition: width .4s ease; border-radius: 2px }

.board-categories { padding: 0 18px 14px; display: flex; flex-direction: column; gap: 12px; flex: 1 }
.cat-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px }
.cat-name   { font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em }
.cat-progress { font-size: 10px; color: var(--muted); font-family: 'DM Mono', monospace }
.cat-items  { display: flex; flex-direction: column; gap: 2px }

.check-item { display: flex; align-items: center; gap: 8px; padding: 5px 8px; border-radius: 6px; cursor: pointer; transition: background .1s }
.check-item:hover { background: var(--bg3) }
.check-item.checked .check-label { text-decoration: line-through; color: var(--muted) }

.check-box { width: 16px; height: 16px; border: 1.5px solid var(--border2); border-radius: 4px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all .15s }
.check-item.checked .check-box { background: var(--green); border-color: var(--green); color: #fff }
.check-label    { font-size: 12px; color: var(--text); flex: 1 }
.check-assignee { font-size: 10px; color: var(--muted); flex-shrink: 0; white-space: nowrap }

.board-footer { display: flex; align-items: center; gap: 6px; padding: 10px 18px; border-top: 1px solid var(--border); background: var(--bg3) }
.footer-btn   { background: none; border: 1px solid var(--border2); color: var(--muted); font-size: 11px; padding: 4px 10px; border-radius: 5px; cursor: pointer; font-family: inherit; transition: all .15s }
.footer-btn:hover { background: var(--bg4); color: var(--text) }
.footer-btn.danger { color: var(--red); border-color: var(--red-dim) }
.footer-btn.danger:hover { background: var(--red-dim) }

.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.45); z-index: 300; display: flex; align-items: center; justify-content: center }
.modal   { background: var(--bg2); border: 1px solid var(--border2); border-radius: 12px; padding: 24px; width: 460px; max-width: 90vw }
.modal-title { font-size: 15px; font-weight: 700; margin-bottom: 5px; color: var(--text) }
.modal-desc  { font-size: 12px; color: var(--muted); margin-bottom: 16px; line-height: 1.6 }
.field       { margin-bottom: 12px }
.field label { display: block; font-size: 10px; color: var(--muted); margin-bottom: 4px; font-weight: 700; text-transform: uppercase; letter-spacing: .04em }
.field input  { width: 100%; background: var(--bg3); border: 1px solid var(--border2); border-radius: 7px; padding: 8px 11px; color: var(--text); font-size: 13px; font-family: inherit; outline: none; box-sizing: border-box }
.field input:focus { border-color: var(--amber) }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 18px }

.template-options { display: flex; gap: 8px }
.tmpl-option { flex: 1; background: var(--bg3); border: 1.5px solid var(--border2); border-radius: 8px; padding: 10px 12px; cursor: pointer; transition: all .15s }
.tmpl-option:hover { border-color: var(--amber) }
.tmpl-option.selected { border-color: var(--amber); background: var(--amber-dim) }
.tmpl-name { font-size: 12px; font-weight: 700; color: var(--text); margin-bottom: 2px }
.tmpl-desc { font-size: 10px; color: var(--muted); line-height: 1.4 }
</style>
