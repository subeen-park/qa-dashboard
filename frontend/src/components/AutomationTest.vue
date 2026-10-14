<template>
  <div class="auto-page">
    <div class="auto-header">
      <div>
        <div class="page-title">자동화 테스트</div>
        <div class="page-sub">PC · 모바일 · API · 부하 테스트 자동화 통합 관리</div>
      </div>
      <button class="btn btn-ghost" @click="openForm()">+ 스크립트 등록</button>
    </div>

    <!-- 서브탭 -->
    <div class="subtabs">
      <div v-for="t in TABS" :key="t.key"
        class="subtab" :class="{on: subTab===t.key}"
        @click="subTab=t.key">
        <span class="st-icon" v-html="t.icon"></span>
        {{ t.label }}
        <span class="st-count">{{ countBy(t.key) }}</span>
      </div>
    </div>

    <!-- 1. 컨트롤 패널 -->
    <div v-if="subTab!=='dashboard'" class="ctrl-panel">
      <div class="ctrl-head">
        <span class="ctrl-icon" v-html="currentTabIcon"></span>
        <span class="ctrl-title">{{ currentTabLabel }} 실행</span>
        <span class="ctrl-sub">{{ currentTabDesc }}</span>
      </div>
      <div class="ctrl-grid">
        <div class="ctrl-field">
          <label>Targets (시나리오)</label>
          <div class="multi-pick" @click="showPicker=!showPicker">
            <span v-if="!selectedScripts.length" class="picker-empty">시나리오를 선택하세요</span>
            <span v-else class="picker-count">🎯 {{ selectedScripts.length }}개 선택됨</span>
            <span class="picker-caret">▾</span>
          </div>
          <div v-if="showPicker" class="picker-pop" @click.stop>
            <div v-for="s in filtered" :key="s.id" class="picker-item" @click="toggleScript(s.id)">
              <input type="checkbox" :checked="selectedScripts.includes(s.id)" @click.stop />
              <span class="picker-name">{{ s.name }}</span>
              <span class="picker-tag">{{ s.target }}</span>
            </div>
            <div v-if="!filtered.length" class="picker-empty-list">등록된 스크립트가 없어요</div>
          </div>
        </div>
        <div class="ctrl-field">
          <label>Environment</label>
          <select v-model="ctrlEnv">
            <option>local</option><option>dev</option><option>stage</option><option>prod</option>
          </select>
        </div>
        <div class="ctrl-field">
          <label>{{ targetCtrlLabel }}</label>
          <select v-model="ctrlBrowser">
            <option v-for="opt in targetOptions" :key="opt">{{ opt }}</option>
          </select>
        </div>
        <div class="ctrl-field">
          <label>사용자명</label>
          <input v-model="ctrlUser" placeholder="예: 박수빈" />
        </div>
        <div class="ctrl-field">
          <label>Gemini API Key</label>
          <input v-model="ctrlApiKey" type="password" placeholder="AI 분석용 (선택)" />
        </div>
        <div class="ctrl-field">
          <label>Parallel Workers</label>
          <input v-model.number="ctrlWorkers" type="number" min="1" max="16" />
        </div>
      </div>
      <button class="btn-run" :disabled="!selectedScripts.length || isRunning" @click="runAutomation">
        <span v-if="!isRunning">▶ Start Automation</span>
        <span v-else>● 실행 중... {{ runProgress }}%</span>
      </button>
    </div>

    <!-- 2. 대시보드 (전 탭 공통 요약) -->
    <div v-if="subTab==='dashboard'">
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-label">Total Projects</div>
          <div class="metric-val" style="color:var(--primary)">{{ runs.length }}</div>
          <div class="metric-sub">누적 실행 횟수</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Avg Success Rate</div>
          <div class="metric-val" style="color:var(--green)">{{ avgSuccess }}%</div>
          <div class="metric-sub">{{ totalPassed }} / {{ totalScenarios }} 통과</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Avg Failure Rate</div>
          <div class="metric-val" style="color:var(--red)">{{ avgFailure }}%</div>
          <div class="metric-sub">{{ totalFailed }}건 실패</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">자동화율</div>
          <div class="metric-val" style="color:var(--yellow)">68%</div>
          <div class="metric-sub">수동 → 자동 전환</div>
        </div>
      </div>

      <div class="chart-row">
        <!-- 도넛 차트 -->
        <div class="dash-card">
          <div class="dash-title">Test Execution Status (Pass/Fail Rate)</div>
          <div class="donut-wrap">
            <svg viewBox="0 0 200 200" class="donut">
              <circle cx="100" cy="100" r="70" fill="none" stroke="var(--bg4)" stroke-width="28"/>
              <circle cx="100" cy="100" r="70" fill="none" stroke="var(--green)" stroke-width="28"
                :stroke-dasharray="donutDash" stroke-dashoffset="0" transform="rotate(-90 100 100)"/>
              <text x="100" y="92" class="donut-text-top" text-anchor="middle">{{ avgSuccess }}%</text>
              <text x="100" y="112" class="donut-text-sub" text-anchor="middle">Pass</text>
            </svg>
            <div class="donut-legend">
              <div class="leg-row"><span class="leg-dot" style="background:var(--green)"></span>scenario passed<span class="leg-val mono">{{ totalPassed }}</span></div>
              <div class="leg-row"><span class="leg-dot" style="background:var(--red)"></span>scenario failed<span class="leg-val mono">{{ totalFailed }}</span></div>
            </div>
          </div>
        </div>

        <!-- 실행 추세 -->
        <div class="dash-card">
          <div class="dash-title">Execution Trends</div>
          <svg viewBox="0 0 500 200" class="bar-chart">
            <line v-for="y in [0,1,2,3,4]" :key="'g'+y" :x1="30" :y1="20+y*35" :x2="490" :y2="20+y*35" class="grid"/>
            <text v-for="y in [0,2,4]" :key="'t'+y" :x="24" :y="25+y*35" text-anchor="end" class="axis-text">{{ 4-y }}</text>
            <g v-for="(r,i) in runs.slice(0,8).reverse()" :key="'b'+i">
              <rect :x="40+i*55" :y="160-r.passed*30" :width="22" :height="r.passed*30" fill="var(--green)"/>
              <rect :x="40+i*55" :y="160-(r.passed+r.failed)*30" :width="22" :height="r.failed*30" fill="var(--red)"/>
              <text :x="51+i*55" :y="178" text-anchor="middle" class="axis-text">{{ r.date.slice(5) }}</text>
            </g>
            <g class="legend-g">
              <rect x="380" y="6" width="10" height="10" fill="var(--red)"/>
              <text x="395" y="15" class="axis-text">Failed</text>
              <rect x="430" y="6" width="10" height="10" fill="var(--green)"/>
              <text x="445" y="15" class="axis-text">Passed</text>
            </g>
          </svg>
        </div>
      </div>

      <!-- Recent Projects Overview -->
      <div class="dash-card">
        <div class="dash-title">Recent Projects Overview</div>
        <div class="proj-table">
          <div class="proj-head">
            <div>date</div><div>project</div><div>env</div><div>passed</div><div>failed</div><div>total</div><div>time(s)</div>
          </div>
          <div v-for="r in runs.slice(0,8)" :key="r.id" class="proj-row" @click="expandRun(r)">
            <div class="mono small">{{ r.timestamp }}</div>
            <div class="proj-name mono">{{ r.name }}</div>
            <div><span class="env-chip">{{ r.env }}</span></div>
            <div class="mono" style="color:var(--green)">{{ r.passed }}</div>
            <div class="mono" style="color:var(--red)">{{ r.failed }}</div>
            <div class="mono">{{ r.passed + r.failed }}</div>
            <div class="mono small">{{ r.duration }}</div>
          </div>
          <div v-if="!runs.length" class="empty">아직 실행 내역이 없어요. 다른 탭에서 자동화를 시작하세요.</div>
        </div>
      </div>
    </div>

    <!-- 3. 카테고리별 실행 결과 -->
    <div v-else>
      <!-- 스크립트 등록 테이블 -->
      <div class="dash-card">
        <div class="dash-title-row">
          <div class="dash-title">등록된 시나리오</div>
          <div class="cs-stats">
            <div class="cs-stat"><span class="cs-l">전체</span><span class="cs-v mono">{{ filtered.length }}</span></div>
            <div class="cs-stat"><span class="cs-l">통과율</span><span class="cs-v mono" :style="{color:passRateBy(subTab)>=90?'var(--green)':passRateBy(subTab)>=70?'var(--yellow)':'var(--red)'}">{{ passRateBy(subTab) }}%</span></div>
          </div>
        </div>
        <div class="table-wrap" style="border:none;border-radius:0">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width:30%">시나리오</th>
                <th>{{ targetColLabel }}</th>
                <th style="width:90px">언어</th>
                <th style="width:80px">상태</th>
                <th style="width:100px">통과율</th>
                <th style="width:60px">실행</th>
                <th style="width:40px"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filtered.length===0">
                <td colspan="7" class="empty">등록된 자동화 스크립트가 없어요</td>
              </tr>
              <tr v-for="s in filtered" :key="s.id">
                <td>
                  <div class="script-name">{{ s.name }}</div>
                  <div class="script-desc">{{ s.description }}</div>
                </td>
                <td class="mono target-cell">{{ s.target }}</td>
                <td><span class="lang-chip">{{ s.language }}</span></td>
                <td><span class="chip" :class="'chip-'+s.last_status">{{ statusLabel(s.last_status) }}</span></td>
                <td>
                  <div class="rate-cell">
                    <div class="rate-bar"><div class="rate-fill" :class="s.pass_rate>=90?'rf-good':s.pass_rate>=70?'rf-mid':'rf-bad'" :style="{width:s.pass_rate+'%'}"></div></div>
                    <span class="rate-num mono">{{ s.pass_rate }}%</span>
                  </div>
                </td>
                <td><button class="run-btn" @click="runSingle(s)">▶ Run</button></td>
                <td><button class="icon-btn-sm" @click="openForm(s)">⋯</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 실행 히스토리 (펼침 카드) -->
      <div v-if="categoryRuns.length" class="history-section">
        <div class="dash-title" style="margin-bottom:12px">실행 히스토리</div>
        <div v-for="r in categoryRuns" :key="r.id" class="run-card" :class="{open: openRunId===r.id}">
          <div class="run-card-head" @click="toggleRun(r.id)">
            <span class="run-toggle">{{ openRunId===r.id ? '▾' : '▸' }}</span>
            <span class="run-status-dot" :class="r.failed > 0 ? 'rsd-fail' : 'rsd-pass'"></span>
            <span class="run-card-title mono">[{{ r.timestamp }}]</span>
            <span class="run-card-name">{{ r.name }}</span>
            <span class="run-card-result">
              <span style="color:var(--green)">Passed: {{ r.passed }}</span> /
              <span style="color:var(--red)">Failed: {{ r.failed }}</span>
            </span>
          </div>
          <div v-if="openRunId===r.id" class="run-card-body">
            <div class="run-meta">
              <span class="rm-item"><b>FILES:</b> {{ r.files }}</span>
              <span class="rm-item"><b>ENV:</b> {{ r.env }}</span>
              <span class="rm-item"><b>{{ targetCtrlLabel.toUpperCase() }}:</b> {{ r.browser }}</span>
              <span class="rm-item"><b>TOTAL TIME:</b> {{ r.duration }}s</span>
            </div>

            <div class="run-grid">
              <div>
                <div class="rg-title">✓ Scenarios Execution</div>
                <table class="data-table compact">
                  <thead>
                    <tr><th>Scenario</th><th>Status</th><th>Duration</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="sc in r.scenarios" :key="sc.name+sc.idx">
                      <td>{{ sc.name }}</td>
                      <td><span :class="'sc-'+sc.status" style="font-weight:600">{{ sc.status }}</span></td>
                      <td class="mono">{{ sc.duration }}s</td>
                    </tr>
                  </tbody>
                </table>

                <div class="step-logs">
                  <div class="rg-title" style="margin-top:18px">Step Logs:</div>
                  <div v-for="(log,i) in r.logs" :key="i" class="step-log" :class="log.type">
                    <span class="step-icon">{{ log.type==='pass'?'✓':'✕' }}</span>
                    <span class="step-time mono">[{{ log.time }}]</span>
                    <span class="step-msg">{{ log.msg }}</span>
                  </div>
                </div>
              </div>

              <div>
                <div class="rg-title rg-fail">✕ Failed Details</div>
                <div v-for="(f,i) in r.failedDetails" :key="i" class="fail-block">
                  <div class="fail-name">▸ {{ f.scenario }}</div>
                  <button class="ai-btn">🤖 에러 원인 AI 분석하기</button>
                  <details class="trace">
                    <summary>🔍 상세 에러 로그 (Traceback) 보기</summary>
                    <pre>{{ f.traceback }}</pre>
                  </details>
                </div>
                <div v-if="!r.failedDetails.length" class="all-pass">✓ 모든 시나리오 통과</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 등록/수정 모달 -->
    <div v-if="showForm" class="overlay" @click.self="showForm=false">
      <div class="modal">
        <div class="modal-title">{{ editing ? '스크립트 수정' : '자동화 스크립트 등록' }}</div>
        <div class="field"><label>시나리오명 *</label><input v-model="form.name" placeholder="예: 로그인 회귀 테스트" /></div>
        <div class="field-row">
          <div class="field"><label>카테고리</label>
            <select v-model="form.category">
              <option value="pc">PC 자동화 (Selenium)</option>
              <option value="mobile">모바일 자동화 (Appium)</option>
              <option value="api">API 자동화 (REST/GraphQL)</option>
              <option value="load">부하/성능 (JMeter/k6)</option>
            </select>
          </div>
          <div class="field"><label>언어</label>
            <select v-model="form.language">
              <option>Python</option><option>JavaScript</option><option>Java</option><option>TypeScript</option>
            </select>
          </div>
        </div>
        <div class="field"><label>{{ targetLabelFor(form.category) }}</label><input v-model="form.target" :placeholder="targetPlaceholder(form.category)" /></div>
        <div class="field"><label>설명</label><textarea v-model="form.description" placeholder="검증 시나리오" rows="2"></textarea></div>
        <div class="modal-actions">
          <button v-if="editing" class="btn btn-danger" @click="del">삭제</button>
          <div style="flex:1"></div>
          <button class="btn btn-ghost" @click="showForm=false">취소</button>
          <button class="btn btn-primary" @click="save">저장</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const MOCK_SCRIPTS = [
  { id:'a1', category:'pc', name:'로그인 회귀 테스트', description:'이메일/소셜 5종', target:'Chrome 120', language:'Python', last_status:'pass', pass_rate:96 },
  { id:'a2', category:'pc', name:'결제 플로우 E2E',   description:'장바구니→결제→완료', target:'Chrome 120', language:'JavaScript', last_status:'pass', pass_rate:88 },
  { id:'a3', category:'pc', name:'회원가입 폼 검증', description:'입력 유효성 25케이스', target:'Chrome · Safari', language:'Python', last_status:'fail', pass_rate:72 },
  { id:'a4', category:'mobile', name:'카카오톡 로그인',description:'안드로이드 자동 로그인', target:'Pixel 7 · Android 14', language:'Java', last_status:'pass', pass_rate:94 },
  { id:'a5', category:'mobile', name:'푸시 알림 수신', description:'백그라운드 푸시', target:'iPhone 14 · iOS 17', language:'JavaScript', last_status:'pass', pass_rate:91 },
  { id:'a6', category:'api', name:'GET /users 검증', description:'유저 목록 응답 스키마', target:'GET /api/v1/users', language:'JavaScript', last_status:'pass', pass_rate:100 },
  { id:'a7', category:'api', name:'POST /orders 검증', description:'주문 생성 응답', target:'POST /api/v1/orders', language:'Python', last_status:'pass', pass_rate:98 },
  { id:'a8', category:'load', name:'로그인 1000 동접', description:'1분간 1000 동시 요청', target:'POST /api/v1/login', language:'JavaScript', last_status:'pass', pass_rate:92 },
]

const MOCK_RUNS = [
  {
    id:'r1', category:'pc', timestamp:'2026-06-12 17:50', name:'RUN_20260612_175027',
    env:'local', browser:'Chrome 120', duration:13.4, passed:2, failed:2,
    files:'test_login.py, test_sample.py', date:'06-12',
    scenarios:[
      { idx:0, name:'google_main', status:'failed', duration:2.7 },
      { idx:1, name:'daum_main', status:'failed', duration:4.26 },
      { idx:2, name:'soop_login_and_save_session', status:'passed', duration:4.17 },
      { idx:3, name:'naver_main', status:'passed', duration:2.31 },
    ],
    logs:[
      { type:'pass', time:'17:50:18', msg:'google.com 접속 시도' },
      { type:'pass', time:'17:50:21', msg:'페이지 로딩 완료' },
      { type:'fail', time:'17:50:22', msg:'타이틀 검증 실패 (현재: Google)' },
    ],
    failedDetails:[
      { scenario:'google_main', traceback:'AssertionError: Expected title "Google KR" but got "Google"\n  at test_google.py:14\n  at line 14: assert driver.title == "Google KR"' },
      { scenario:'daum_main', traceback:'TimeoutException: Element not found: #search-input\n  at test_daum.py:22' },
    ],
  },
  {
    id:'r2', category:'pc', timestamp:'2026-06-12 06:37', name:'RUN_20260612_063731',
    env:'local', browser:'Chrome 120', duration:10.4, passed:1, failed:2,
    files:'test_sample.py', date:'06-12',
    scenarios:[
      { idx:0, name:'sample', status:'failed', duration:2.93 },
      { idx:1, name:'sample', status:'failed', duration:2.72 },
      { idx:2, name:'sample', status:'passed', duration:3.38 },
    ],
    logs:[
      { type:'pass', time:'06:35:18', msg:'다음 메인페이지 접속 시도' },
      { type:'pass', time:'06:35:21', msg:'다음 메인페이지 타이틀 검증 시도' },
      { type:'fail', time:'06:35:21', msg:'타이틀 검증 실패 (현재 타이틀: Daum)' },
    ],
    failedDetails:[
      { scenario:'sample', traceback:'AssertionError: Title mismatch\n  at line 18' },
      { scenario:'sample', traceback:'AssertionError: Element not visible\n  at line 25' },
    ],
  },
  {
    id:'r3', category:'pc', timestamp:'2026-06-11 11:32', name:'RUN_20260611_113235',
    env:'local', browser:'Chrome 120', duration:13.1, passed:2, failed:2,
    files:'test_login.py', date:'06-11',
    scenarios:[
      { idx:0, name:'login_success', status:'passed', duration:3.1 },
      { idx:1, name:'login_fail', status:'passed', duration:2.8 },
      { idx:2, name:'social_kakao', status:'failed', duration:4.2 },
      { idx:3, name:'social_naver', status:'failed', duration:3.0 },
    ],
    logs:[
      { type:'pass', time:'11:32:01', msg:'로그인 페이지 진입' },
      { type:'fail', time:'11:32:08', msg:'카카오 OAuth 콜백 응답 없음' },
    ],
    failedDetails:[
      { scenario:'social_kakao', traceback:'NetworkError: OAuth callback timeout' },
      { scenario:'social_naver', traceback:'ElementNotFound: #naver-login-btn' },
    ],
  },
]

export default {
  name: 'AutomationTest',
  data() {
    return {
      subTab: 'dashboard',
      all: [...MOCK_SCRIPTS],
      runs: [...MOCK_RUNS],
      openRunId: 'r1',
      showForm: false, editing: null,
      form: { name:'', category:'pc', language:'Python', target:'', description:'' },
      // 컨트롤
      selectedScripts: [],
      showPicker: false,
      ctrlEnv: 'local',
      ctrlBrowser: 'Chrome 120',
      ctrlUser: '',
      ctrlApiKey: '',
      ctrlWorkers: 4,
      isRunning: false,
      runProgress: 0,
      TABS: [
        { key:'dashboard', label:'대시보드',  icon:'<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 14V2M2 14h12"/><path d="m5 11 3-4 2 2 4-5"/></svg>' },
        { key:'pc',        label:'PC 자동화', icon:'<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2" y="3" width="12" height="8" rx="1"/><path d="M6 14h4M8 11v3"/></svg>' },
        { key:'mobile',    label:'모바일 자동화', icon:'<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="2" width="8" height="12" rx="1"/><path d="M7 12h2"/></svg>' },
        { key:'api',       label:'API 자동화', icon:'<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 8h4M9 8h4M5 5l-2 3 2 3M11 5l2 3-2 3"/></svg>' },
        { key:'load',      label:'부하/성능', icon:'<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8 2v6l4 2"/><circle cx="8" cy="8" r="6"/></svg>' },
      ]
    }
  },
  computed: {
    filtered() {
      if (this.subTab === 'dashboard') return this.all
      return this.all.filter(s => s.category === this.subTab)
    },
    categoryRuns() {
      return this.runs.filter(r => r.category === this.subTab)
    },
    currentTab() { return this.TABS.find(t => t.key === this.subTab) || this.TABS[0] },
    currentTabLabel() { return this.currentTab.label },
    currentTabIcon() { return this.currentTab.icon },
    currentTabDesc() {
      const m = {
        pc: 'Selenium 기반 웹 브라우저 자동화 실행',
        mobile: 'Appium 기반 Android/iOS 디바이스 자동화 실행',
        api: 'REST/GraphQL API 응답 검증 자동화',
        load: 'JMeter/k6 기반 부하 테스트 실행',
      }
      return m[this.subTab] || ''
    },
    targetColLabel() {
      const m = { pc:'대상 브라우저', mobile:'대상 디바이스', api:'엔드포인트', load:'대상 URL' }
      return m[this.subTab] || '대상'
    },
    targetCtrlLabel() {
      const m = { pc:'Browser', mobile:'Device', api:'Endpoint Base URL', load:'Target URL' }
      return m[this.subTab] || 'Target'
    },
    targetOptions() {
      const m = {
        pc: ['Chrome 120', 'Chrome 119', 'Edge 120', 'Firefox 121', 'Safari 17'],
        mobile: ['Pixel 7 · Android 14', 'Galaxy S23 · Android 14', 'iPhone 14 · iOS 17', 'iPhone 15 · iOS 17'],
        api: ['https://api.dev.example.com', 'https://api.stage.example.com', 'https://api.example.com'],
        load: ['https://example.com', 'https://api.example.com'],
      }
      return m[this.subTab] || []
    },
    totalScenarios() { return this.runs.reduce((s, r) => s + r.passed + r.failed, 0) },
    totalPassed() { return this.runs.reduce((s, r) => s + r.passed, 0) },
    totalFailed() { return this.runs.reduce((s, r) => s + r.failed, 0) },
    avgSuccess() {
      if (!this.totalScenarios) return 0
      return Math.round(this.totalPassed / this.totalScenarios * 1000) / 10
    },
    avgFailure() {
      if (!this.totalScenarios) return 0
      return Math.round(this.totalFailed / this.totalScenarios * 1000) / 10
    },
    donutDash() {
      const circ = 2 * Math.PI * 70
      const passLen = circ * (this.avgSuccess / 100)
      return `${passLen} ${circ}`
    },
  },
  methods: {
    countBy(cat) {
      if (cat === 'dashboard') return this.all.length
      return this.all.filter(s => s.category === cat).length
    },
    passRateBy(cat) {
      const list = this.all.filter(s => s.category === cat)
      if (!list.length) return 0
      const passed = list.filter(s => s.last_status === 'pass').length
      return Math.round(passed / list.length * 100)
    },
    statusLabel(st) { return ({pass:'✓ Pass', fail:'✕ Fail', running:'● Running', skipped:'– Skip'})[st] || st },
    targetLabelFor(cat) { return ({pc:'대상 브라우저', mobile:'대상 디바이스', api:'엔드포인트', load:'대상 URL'})[cat] || '대상' },
    targetPlaceholder(cat) { return ({pc:'Chrome 120 · Safari', mobile:'Pixel 7 · Android 14', api:'GET /api/v1/users', load:'POST /api/v1/login'})[cat] || '' },
    toggleScript(id) {
      const i = this.selectedScripts.indexOf(id)
      if (i >= 0) this.selectedScripts.splice(i, 1)
      else this.selectedScripts.push(id)
    },
    toggleRun(id) { this.openRunId = this.openRunId === id ? null : id },
    expandRun(r) { this.subTab = r.category; this.openRunId = r.id },
    openForm(s) {
      this.editing = s || null
      this.form = s ? Object.assign({}, s) : { name:'', category: this.subTab !== 'dashboard' ? this.subTab : 'pc', language:'Python', target:'', description:'' }
      this.showForm = true
    },
    save() {
      if (!this.form.name.trim()) return
      if (this.editing) {
        const idx = this.all.findIndex(s => s.id === this.editing.id)
        if (idx >= 0) this.all.splice(idx, 1, Object.assign({}, this.editing, this.form))
      } else {
        this.all.push(Object.assign({ id:'n'+Date.now(), last_status:'skipped', pass_rate:0 }, this.form))
      }
      this.showForm = false
    },
    del() {
      if (!confirm('삭제?')) return
      this.all = this.all.filter(s => s.id !== this.editing.id)
      this.showForm = false
    },
    runSingle(s) {
      this.selectedScripts = [s.id]
      this.runAutomation()
    },
    runAutomation() {
      if (!this.selectedScripts.length) return
      this.isRunning = true
      this.runProgress = 0
      const scripts = this.all.filter(s => this.selectedScripts.includes(s.id))
      const totalSteps = 100
      const interval = setInterval(() => {
        this.runProgress += 5
        if (this.runProgress >= totalSteps) {
          clearInterval(interval)
          this.finishRun(scripts)
        }
      }, 80)
    },
    finishRun(scripts) {
      const scenarios = scripts.map((s, i) => {
        const isPass = Math.random() > 0.3
        return { idx:i, name:s.name, status: isPass ? 'passed' : 'failed', duration: +(Math.random() * 5 + 1).toFixed(2) }
      })
      const passed = scenarios.filter(s => s.status === 'passed').length
      const failed = scenarios.length - passed
      const totalDur = scenarios.reduce((s, x) => s + x.duration, 0).toFixed(1)
      const now = new Date()
      const ts = now.toLocaleString('ko', { year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' }).replace(/\. /g, '-').replace(/\./g, '')
      const newRun = {
        id: 'r' + Date.now(),
        category: this.subTab,
        timestamp: ts,
        name: 'RUN_' + now.toISOString().slice(0,10).replace(/-/g,'') + '_' + now.toTimeString().slice(0,8).replace(/:/g,''),
        env: this.ctrlEnv,
        browser: this.ctrlBrowser,
        duration: totalDur,
        passed, failed,
        files: scripts.map(s => s.name + '.py').join(', '),
        date: now.toISOString().slice(5,10),
        scenarios,
        logs: [
          { type:'pass', time: now.toTimeString().slice(0,8), msg:'테스트 시작' },
          { type: failed > 0 ? 'fail' : 'pass', time: now.toTimeString().slice(0,8), msg: failed > 0 ? '일부 시나리오 실패' : '모든 시나리오 통과' },
        ],
        failedDetails: scenarios.filter(s => s.status === 'failed').map(s => ({
          scenario: s.name,
          traceback: `AssertionError: ${s.name} 검증 실패\n  at line ${Math.floor(Math.random()*100)+1}`,
        })),
      }
      this.runs.unshift(newRun)
      // 스크립트 상태 업데이트
      scripts.forEach(s => {
        const idx = this.all.findIndex(x => x.id === s.id)
        if (idx < 0) return
        const isPass = scenarios.find(sc => sc.name === s.name)?.status === 'passed'
        this.all.splice(idx, 1, Object.assign({}, this.all[idx], {
          last_status: isPass ? 'pass' : 'fail',
          pass_rate: Math.max(0, Math.min(100, this.all[idx].pass_rate + (isPass ? 1 : -3))),
        }))
      })
      this.isRunning = false
      this.runProgress = 0
      this.openRunId = newRun.id
      this.selectedScripts = []
    },
  },
  mounted() {
    document.addEventListener('click', () => { this.showPicker = false })
  }
}
</script>

<style scoped>
.auto-page { display: flex; flex-direction: column; gap: 18px; padding: 24px 32px; max-width: 1400px; margin: 0 auto; }
.auto-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }

/* 서브탭 */
.subtabs { display: flex; gap: 2px; background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 4px; width: fit-content; max-width: 100%; overflow-x: auto; }
.subtab { display: flex; align-items: center; gap: 7px; padding: 8px 14px; border-radius: 7px; font-size: 13px; color: var(--muted); cursor: pointer; white-space: nowrap; transition: all .15s; }
.subtab:hover { color: var(--text); }
.subtab.on { background: var(--bg4); color: var(--text); font-weight: 600; }
.st-icon { width: 14px; height: 14px; display: flex; }
.st-icon svg { width: 14px; height: 14px; }
.st-count { background: var(--bg3); color: var(--muted); font-size: 11px; padding: 1px 6px; border-radius: 9px; font-family: 'JetBrains Mono', monospace; }
.subtab.on .st-count { background: var(--primary); color: #fff; }

/* 컨트롤 패널 */
.ctrl-panel { background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; padding: 22px 24px; }
.ctrl-head { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
.ctrl-icon { width: 18px; height: 18px; color: var(--primary); }
.ctrl-icon svg { width: 18px; height: 18px; }
.ctrl-title { font-size: 15px; font-weight: 700; }
.ctrl-sub { font-size: 12px; color: var(--muted); margin-left: auto; }
.ctrl-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 18px; }
.ctrl-field label { display: block; font-size: 11px; color: var(--muted); font-weight: 600; margin-bottom: 5px; }
.ctrl-field input, .ctrl-field select { width: 100%; background: var(--bg3); border: 1px solid var(--border2); border-radius: 7px; padding: 9px 11px; color: var(--text); font-size: 13px; font-family: inherit; outline: none; }
.ctrl-field input:focus, .ctrl-field select:focus { border-color: var(--primary); }
.multi-pick { position: relative; background: var(--bg3); border: 1px solid var(--border2); border-radius: 7px; padding: 9px 11px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; font-size: 13px; }
.multi-pick:hover { border-color: var(--primary); }
.picker-empty { color: var(--muted); }
.picker-count { color: var(--primary); font-weight: 600; }
.picker-pop { position: absolute; top: 100%; left: 0; right: 0; margin-top: 4px; background: var(--bg2); border: 1px solid var(--border2); border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,.1); max-height: 240px; overflow-y: auto; z-index: 50; }
.picker-item { display: flex; align-items: center; gap: 9px; padding: 9px 12px; cursor: pointer; font-size: 13px; }
.picker-item:hover { background: var(--bg3); }
.picker-name { flex: 1; }
.picker-tag { font-size: 11px; color: var(--muted); font-family: 'JetBrains Mono', monospace; }
.picker-empty-list { padding: 16px; text-align: center; color: var(--muted); font-size: 12px; }
.btn-run { width: 100%; background: var(--primary); color: #fff; border: none; padding: 13px; border-radius: 9px; font-size: 14px; font-weight: 700; cursor: pointer; font-family: inherit; transition: background .15s; }
.btn-run:hover:not(:disabled) { background: var(--primary-hover); }
.btn-run:disabled { background: var(--bg4); color: var(--muted); cursor: not-allowed; }

/* 대시보드 */
.chart-row { display: grid; grid-template-columns: 1fr 1.4fr; gap: 14px; margin-bottom: 14px; }
.dash-card { background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
.dash-title { font-size: 13px; font-weight: 700; margin-bottom: 14px; }
.dash-title-row { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid var(--border); }
.dash-title-row .dash-title { margin-bottom: 0; }
.cs-stats { display: flex; gap: 18px; }
.cs-stat { display: flex; align-items: baseline; gap: 6px; }
.cs-l { font-size: 11px; color: var(--muted); }
.cs-v { font-size: 14px; font-weight: 700; }

/* 도넛 */
.donut-wrap { display: flex; align-items: center; gap: 18px; }
.donut { width: 180px; height: 180px; }
.donut-text-top { font-size: 24px; font-weight: 700; fill: var(--text); font-family: 'JetBrains Mono', monospace; }
.donut-text-sub { font-size: 11px; fill: var(--muted); }
.donut-legend { flex: 1; display: flex; flex-direction: column; gap: 10px; }
.leg-row { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.leg-dot { width: 10px; height: 10px; border-radius: 50%; }
.leg-val { margin-left: auto; font-weight: 600; }

/* 막대 */
.bar-chart { width: 100%; height: 220px; }
.grid { stroke: var(--border); stroke-width: 1; }
.axis-text { fill: var(--muted); font-size: 9px; font-family: 'JetBrains Mono', monospace; }

/* Recent Projects */
.proj-table { font-size: 12px; }
.proj-head, .proj-row { display: grid; grid-template-columns: 130px 1.4fr 80px 70px 70px 70px 80px; gap: 8px; padding: 9px 4px; }
.proj-head { font-size: 11px; color: var(--muted); border-bottom: 1px solid var(--border); font-weight: 600; }
.proj-row { border-bottom: 1px solid var(--border); cursor: pointer; }
.proj-row:hover { background: var(--bg3); }
.proj-row:last-child { border-bottom: none; }
.proj-name { color: var(--primary); }
.env-chip { background: var(--bg4); color: var(--muted); padding: 2px 6px; border-radius: 4px; font-size: 11px; font-family: 'JetBrains Mono', monospace; }
.small { font-size: 11px; }

/* 스크립트 테이블 */
.script-name { font-size: 13px; font-weight: 600; }
.script-desc { font-size: 11px; color: var(--muted); margin-top: 2px; }
.target-cell { font-size: 11px; color: var(--muted); }
.lang-chip { display: inline-block; padding: 2px 7px; border-radius: 4px; background: var(--bg4); color: var(--text); font-size: 11px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.rate-cell { display: flex; align-items: center; gap: 7px; }
.rate-bar { width: 50px; height: 5px; background: var(--bg4); border-radius: 3px; overflow: hidden; }
.rate-fill { height: 100%; }
.rf-good { background: #10B981; }
.rf-bad { background: #EF4444; opacity: 0.85; }
.rf-mid { background: #F59E0B; }
.rate-num { font-size: 11px; min-width: 32px; }
.run-btn { background: var(--primary-dim); color: var(--primary); border: none; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; font-family: inherit; }
.run-btn:hover { background: var(--primary); color: #fff; }
.icon-btn-sm { background: transparent; border: none; color: var(--muted); cursor: pointer; padding: 4px; }

/* 실행 히스토리 */
.history-section { margin-top: 18px; }
.run-card { background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; margin-bottom: 10px; overflow: hidden; }
.run-card.open { border-color: var(--border2); }
.run-card-head { display: flex; align-items: center; gap: 10px; padding: 14px 18px; cursor: pointer; font-size: 13px; }
.run-card-head:hover { background: var(--bg3); }
.run-toggle { color: var(--muted); font-size: 10px; width: 10px; }
.run-status-dot { width: 9px; height: 9px; border-radius: 50%; }
.rsd-pass { background: var(--green); }
.rsd-fail { background: var(--red); }
.run-card-title { color: var(--muted); font-size: 12px; }
.run-card-name { font-weight: 600; flex: 1; }
.run-card-result { font-size: 12px; font-weight: 600; }
.run-card-body { padding: 0 18px 20px; border-top: 1px solid var(--border); }
.run-meta { background: var(--bg3); border-left: 3px solid var(--primary); padding: 10px 14px; margin: 14px 0 18px; font-size: 11px; display: flex; flex-wrap: wrap; gap: 14px; font-family: 'JetBrains Mono', monospace; }
.rm-item b { color: var(--text); font-weight: 700; }

.run-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
.rg-title { font-size: 13px; font-weight: 700; color: var(--primary); margin-bottom: 10px; }
.rg-fail { color: var(--red); }
.data-table.compact th, .data-table.compact td { padding: 7px 10px; font-size: 12px; }
.sc-passed { color: var(--green); }
.sc-failed { color: var(--red); }

.step-logs { margin-top: 16px; padding: 12px 14px; background: var(--bg3); border-radius: 8px; }
.step-log { display: flex; align-items: center; gap: 8px; font-size: 12px; padding: 4px 0; }
.step-log.pass { color: var(--green); }
.step-log.fail { color: var(--red); }
.step-icon { font-weight: 700; }
.step-time { color: var(--muted); font-size: 11px; }
.step-msg { color: var(--text); }

.fail-block { margin-bottom: 16px; }
.fail-name { font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.ai-btn { background: var(--bg3); color: var(--text); border: 1px solid var(--border2); padding: 6px 12px; border-radius: 7px; font-size: 12px; cursor: pointer; font-family: inherit; margin-bottom: 8px; }
.ai-btn:hover { background: var(--bg4); }
.trace { background: var(--bg3); border-radius: 7px; padding: 8px 12px; font-size: 12px; }
.trace summary { cursor: pointer; color: var(--muted); }
.trace pre { margin-top: 8px; font-family: 'JetBrains Mono', monospace; font-size: 11px; white-space: pre-wrap; color: var(--text); padding: 8px; background: var(--bg2); border-radius: 5px; }
.all-pass { padding: 20px; text-align: center; color: var(--green); font-weight: 600; font-size: 13px; }

@media (max-width: 900px) {
  .ctrl-grid { grid-template-columns: 1fr 1fr; }
  .chart-row { grid-template-columns: 1fr; }
  .run-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .auto-page { padding: 16px 14px; }
  .ctrl-grid { grid-template-columns: 1fr; }
  .proj-head, .proj-row { grid-template-columns: 100px 1fr 60px 50px 50px; }
  .proj-head > div:nth-child(6), .proj-row > div:nth-child(6),
  .proj-head > div:nth-child(7), .proj-row > div:nth-child(7) { display: none; }
}
</style>