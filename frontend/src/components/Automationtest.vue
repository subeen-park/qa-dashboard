<template>
  <div class="auto-page">
    <div class="auto-header">
      <div>
        <div class="page-title">자동화 테스트</div>
        <div class="page-sub">PC · 모바일 · API · 부하 테스트 자동화 관리</div>
      </div>
      <button class="btn btn-primary" @click="openForm()">+ 자동화 등록</button>
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

    <!-- 대시보드 탭 -->
    <div v-if="subTab==='dashboard'">
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-label">전체 스크립트</div>
          <div class="metric-val">{{ all.length }}</div>
          <div class="metric-sub">PC · 모바일 · API · 부하</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">통과율</div>
          <div class="metric-val" :style="{color:totalPass>=90?'var(--green)':'var(--red)'}">{{ totalPass }}%</div>
          <div class="metric-sub">{{ passCount }} / {{ all.length }} 통과</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">실패 스크립트</div>
          <div class="metric-val" style="color:var(--red)">{{ failCount }}</div>
          <div class="metric-sub">즉시 점검 필요</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">자동화율</div>
          <div class="metric-val" style="color:var(--primary)">68%</div>
          <div class="metric-sub">수동 → 자동 전환</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">평균 실행시간</div>
          <div class="metric-val mono">{{ avgDuration }}s</div>
          <div class="metric-sub">스크립트당</div>
        </div>
      </div>

      <!-- 카테고리별 통과율 -->
      <div class="dash-card">
        <div class="dash-title">카테고리별 통과율</div>
        <div class="cat-bars">
          <div v-for="t in TABS.filter(x=>x.key!=='dashboard')" :key="t.key" class="cat-row">
            <div class="cat-label">{{ t.label }}</div>
            <div class="cat-bar">
              <div class="cat-fill" :class="passRateBy(t.key)>=90?'cf-good':passRateBy(t.key)>=70?'cf-mid':'cf-bad'"
                :style="{width:passRateBy(t.key)+'%'}"></div>
            </div>
            <div class="cat-pct mono">{{ passRateBy(t.key) }}%</div>
            <div class="cat-count">{{ countBy(t.key) }}건</div>
          </div>
        </div>
      </div>

      <!-- 최근 실행 결과 -->
      <div class="dash-card">
        <div class="dash-title">최근 실행 결과</div>
        <div class="run-list">
          <div v-for="s in recent" :key="s.id" class="run-row">
            <span class="run-cat" :class="'rc-'+s.category">{{ catLabel(s.category) }}</span>
            <span class="run-name">{{ s.name }}</span>
            <span class="run-status" :class="'rs-'+s.last_status">{{ statusLabel(s.last_status) }}</span>
            <span class="run-time mono">{{ s.duration }}s</span>
            <span class="run-date mono">{{ s.last_run }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- PC / 모바일 / API / 부하 공통 테이블 -->
    <div v-else>
      <div class="cat-summary">
        <div class="cs-info">
          <div class="cs-title">{{ subTabLabel }}</div>
          <div class="cs-desc">{{ subTabDesc }}</div>
        </div>
        <div class="cs-stats">
          <div class="cs-stat">
            <div class="cs-stat-label">전체</div>
            <div class="cs-stat-val mono">{{ filtered.length }}</div>
          </div>
          <div class="cs-stat">
            <div class="cs-stat-label">통과</div>
            <div class="cs-stat-val mono" style="color:var(--green)">{{ filteredByStatus('pass').length }}</div>
          </div>
          <div class="cs-stat">
            <div class="cs-stat-label">실패</div>
            <div class="cs-stat-val mono" style="color:var(--red)">{{ filteredByStatus('fail').length }}</div>
          </div>
          <div class="cs-stat">
            <div class="cs-stat-label">통과율</div>
            <div class="cs-stat-val mono" :style="{color:passRateBy(subTab)>=90?'var(--green)':'var(--red)'}">{{ passRateBy(subTab) }}%</div>
          </div>
        </div>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width:30%">스크립트명</th>
              <th>{{ targetColLabel }}</th>
              <th style="width:90px">언어</th>
              <th style="width:80px">상태</th>
              <th style="width:80px">통과율</th>
              <th style="width:90px">최근 실행</th>
              <th style="width:60px">실행</th>
              <th style="width:40px"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filtered.length===0">
              <td colspan="8" class="empty">등록된 자동화 스크립트가 없어요</td>
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
                  <div class="rate-bar"><div class="rate-fill" :class="s.pass_rate>=90?'rf-good':'rf-bad'" :style="{width:s.pass_rate+'%'}"></div></div>
                  <span class="rate-num mono">{{ s.pass_rate }}%</span>
                </div>
              </td>
              <td class="mono small-text">{{ s.last_run }}</td>
              <td><button class="run-btn" @click="runScript(s)">▶ Run</button></td>
              <td><button class="icon-btn" @click="openForm(s)">⋯</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 등록/수정 모달 -->
    <div v-if="showForm" class="overlay" @click.self="showForm=false">
      <div class="modal modal-wide">
        <div class="modal-title">{{ editing ? '스크립트 수정' : '자동화 스크립트 등록' }}</div>
        <div class="field"><label>스크립트명 *</label><input v-model="form.name" placeholder="예: 로그인 회귀 테스트" /></div>
        <div class="field-row">
          <div class="field"><label>카테고리</label>
            <select v-model="form.category">
              <option value="pc">PC 자동화 (Selenium)</option>
              <option value="mobile">모바일 자동화 (Appium)</option>
              <option value="api">API 자동화 (REST/GraphQL)</option>
              <option value="load">부하 / 성능 (JMeter/k6)</option>
            </select>
          </div>
          <div class="field"><label>언어</label>
            <select v-model="form.language">
              <option>Python</option>
              <option>JavaScript</option>
              <option>Java</option>
              <option>TypeScript</option>
            </select>
          </div>
        </div>
        <div class="field"><label>{{ targetLabelFor(form.category) }}</label><input v-model="form.target" :placeholder="targetPlaceholder(form.category)" /></div>
        <div class="field"><label>설명</label><textarea v-model="form.description" placeholder="이 스크립트가 검증하는 시나리오" rows="2"></textarea></div>
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
const MOCK = [
  { id:'a1', category:'pc', name:'로그인 회귀 테스트', description:'이메일/소셜 로그인 5종 시나리오', target:'Chrome 120 · Edge 120', language:'Python', last_status:'pass', pass_rate:96, duration:42, last_run:'10/26 14:21' },
  { id:'a2', category:'pc', name:'결제 플로우 E2E',     description:'장바구니 → 결제 → 완료',           target:'Chrome 120',           language:'JavaScript', last_status:'pass', pass_rate:88, duration:78, last_run:'10/26 14:11' },
  { id:'a3', category:'pc', name:'회원가입 폼 검증',     description:'입력 유효성 25개 케이스',           target:'Chrome 120 · Safari',  language:'Python', last_status:'fail', pass_rate:72, duration:35, last_run:'10/26 13:55' },
  { id:'a4', category:'mobile', name:'카카오톡 로그인',  description:'안드로이드 자동 로그인',            target:'Pixel 7 · Android 14', language:'Java', last_status:'pass', pass_rate:94, duration:55, last_run:'10/26 14:30' },
  { id:'a5', category:'mobile', name:'푸시 알림 수신',    description:'백그라운드 푸시 시나리오',          target:'iPhone 14 · iOS 17',   language:'JavaScript', last_status:'pass', pass_rate:91, duration:48, last_run:'10/26 14:05' },
  { id:'a6', category:'mobile', name:'채팅 메시지 전송',  description:'1:1 채팅방 메시지/이미지',          target:'Galaxy S23 · Android 14', language:'Python', last_status:'fail', pass_rate:68, duration:62, last_run:'10/26 12:40' },
  { id:'a7', category:'api', name:'GET /users 검증',     description:'유저 목록 응답 스키마/시간',        target:'GET /api/v1/users',    language:'JavaScript', last_status:'pass', pass_rate:100, duration:1, last_run:'10/26 14:45' },
  { id:'a8', category:'api', name:'POST /orders 검증',   description:'주문 생성 시 응답 코드/필드',       target:'POST /api/v1/orders',  language:'Python', last_status:'pass', pass_rate:98, duration:1, last_run:'10/26 14:40' },
  { id:'a9', category:'api', name:'OAuth 인증 토큰',      description:'액세스 토큰 발급 + 만료 검증',      target:'POST /oauth/token',    language:'TypeScript', last_status:'fail', pass_rate:84, duration:2, last_run:'10/26 14:00' },
  { id:'a10', category:'load', name:'로그인 1000 동접',  description:'1분간 1000 동시 로그인 요청',       target:'POST /api/v1/login',   language:'JavaScript', last_status:'pass', pass_rate:92, duration:62, last_run:'10/26 13:30' },
  { id:'a11', category:'load', name:'메인 페이지 부하',  description:'5분 5000 동접 응답시간 측정',       target:'GET /api/v1/feed',     language:'JavaScript', last_status:'pass', pass_rate:89, duration:305, last_run:'10/26 11:00' },
]

export default {
  name: 'AutomationTest',
  data() {
    return {
      subTab: 'dashboard',
      all: [...MOCK],
      showForm: false, editing: null,
      form: { name:'', category:'pc', language:'Python', target:'', description:'' },
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
    filtered() { return this.all.filter(s => s.category === this.subTab) },
    subTabLabel() {
      const t = this.TABS.find(x => x.key === this.subTab)
      return t ? t.label : ''
    },
    subTabDesc() {
      const m = {
        pc: 'Selenium 기반 웹 브라우저 자동화 — 핵심 사용자 시나리오를 회귀 검증해요',
        mobile: 'Appium 기반 Android/iOS 디바이스 자동화 — 실기기 + 에뮬레이터 검증',
        api: 'REST/GraphQL API 응답 코드/스키마/응답시간 어설션',
        load: 'JMeter/k6 기반 동시접속 부하 테스트 및 응답시간 측정',
      }
      return m[this.subTab] || ''
    },
    targetColLabel() {
      const m = { pc:'대상 브라우저', mobile:'대상 디바이스', api:'엔드포인트', load:'대상 URL' }
      return m[this.subTab] || '대상'
    },
    recent() {
      return [...this.all].sort((a,b) => b.last_run.localeCompare(a.last_run)).slice(0, 8)
    },
    passCount() { return this.all.filter(s => s.last_status === 'pass').length },
    failCount() { return this.all.filter(s => s.last_status === 'fail').length },
    totalPass() { return this.all.length ? Math.round(this.passCount / this.all.length * 100) : 0 },
    avgDuration() {
      if (!this.all.length) return 0
      return Math.round(this.all.reduce((s, x) => s + x.duration, 0) / this.all.length)
    },
  },
  methods: {
    countBy(cat) {
      if (cat === 'dashboard') return this.all.length
      return this.all.filter(s => s.category === cat).length
    },
    filteredByStatus(st) { return this.filtered.filter(s => s.last_status === st) },
    passRateBy(cat) {
      const list = this.all.filter(s => s.category === cat)
      if (!list.length) return 0
      const passed = list.filter(s => s.last_status === 'pass').length
      return Math.round(passed / list.length * 100)
    },
    catLabel(cat) {
      const m = { pc:'PC', mobile:'모바일', api:'API', load:'부하' }
      return m[cat] || cat
    },
    statusLabel(st) {
      const m = { pass:'✓ Pass', fail:'✕ Fail', running:'● Running', skipped:'– Skip' }
      return m[st] || st
    },
    targetLabelFor(cat) {
      const m = { pc:'대상 브라우저', mobile:'대상 디바이스', api:'엔드포인트', load:'대상 URL' }
      return m[cat] || '대상'
    },
    targetPlaceholder(cat) {
      const m = { pc:'Chrome 120 · Safari', mobile:'Pixel 7 · Android 14', api:'GET /api/v1/users', load:'POST /api/v1/login' }
      return m[cat] || ''
    },
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
        this.all.push(Object.assign({ id:'n'+Date.now(), last_status:'skipped', pass_rate:0, duration:0, last_run:'-' }, this.form))
      }
      this.showForm = false
    },
    del() {
      if (!confirm('삭제하시겠습니까?')) return
      this.all = this.all.filter(s => s.id !== this.editing.id)
      this.showForm = false
    },
    runScript(s) {
      const idx = this.all.findIndex(x => x.id === s.id)
      if (idx < 0) return
      this.all.splice(idx, 1, Object.assign({}, s, { last_status:'running' }))
      setTimeout(() => {
        const isPass = Math.random() > 0.2
        const i = this.all.findIndex(x => x.id === s.id)
        if (i < 0) return
        this.all.splice(i, 1, Object.assign({}, this.all[i], {
          last_status: isPass ? 'pass' : 'fail',
          pass_rate: Math.max(0, Math.min(100, this.all[i].pass_rate + (isPass ? 1 : -2))),
          last_run: new Date().toLocaleString('ko', { month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' }).replace(/\. /g, '/').replace(/\./g, ''),
        }))
      }, 1200 + Math.random() * 800)
    },
  }
}
</script>

<style scoped>
.auto-page { display: flex; flex-direction: column; gap: 20px; padding: 24px 32px; max-width: 1400px; margin: 0 auto; }
.auto-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }

.subtabs { display: flex; gap: 2px; background: var(--bg2); border: 1px solid var(--border); border-radius: 10px; padding: 4px; width: fit-content; max-width: 100%; overflow-x: auto; }
.subtab { display: flex; align-items: center; gap: 7px; padding: 8px 14px; border-radius: 7px; font-size: 13px; color: var(--muted); cursor: pointer; white-space: nowrap; transition: all .15s; }
.subtab:hover { color: var(--text); }
.subtab.on { background: var(--bg4); color: var(--text); font-weight: 600; }
.st-icon { width: 14px; height: 14px; display: flex; }
.st-icon svg { width: 14px; height: 14px; }
.st-count { background: var(--bg3); color: var(--muted); font-size: 11px; padding: 1px 6px; border-radius: 9px; font-family: 'JetBrains Mono', monospace; }
.subtab.on .st-count { background: var(--primary); color: #fff; }

/* 카테고리 상단 요약 */
.cat-summary { display: flex; align-items: center; justify-content: space-between; background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 22px; gap: 16px; flex-wrap: wrap; }
.cs-title { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
.cs-desc { font-size: 12px; color: var(--muted); line-height: 1.5; }
.cs-stats { display: flex; gap: 26px; }
.cs-stat-label { font-size: 11px; color: var(--muted); margin-bottom: 4px; }
.cs-stat-val { font-size: 18px; font-weight: 700; }

/* 대시보드 카드 */
.dash-card { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
.dash-title { font-size: 13px; font-weight: 700; margin-bottom: 14px; }
.cat-bars { display: flex; flex-direction: column; gap: 10px; }
.cat-row { display: grid; grid-template-columns: 120px 1fr 60px 60px; align-items: center; gap: 12px; }
.cat-label { font-size: 13px; color: var(--text); }
.cat-bar { height: 8px; background: var(--bg4); border-radius: 4px; overflow: hidden; }
.cat-fill { height: 100%; transition: width .4s; }
.cf-good { background: var(--green); }
.cf-mid { background: var(--yellow); }
.cf-bad { background: var(--red); }
.cat-pct { font-size: 13px; text-align: right; font-weight: 600; }
.cat-count { font-size: 12px; color: var(--muted); text-align: right; }

/* 최근 실행 */
.run-list { display: flex; flex-direction: column; gap: 4px; }
.run-row { display: grid; grid-template-columns: 60px 1fr 90px 60px 100px; align-items: center; gap: 10px; padding: 8px 4px; border-bottom: 1px solid var(--border); font-size: 13px; }
.run-row:last-child { border-bottom: none; }
.run-cat { font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; text-align: center; }
.rc-pc { background: var(--primary-dim); color: var(--primary); }
.rc-mobile { background: var(--purple-dim); color: var(--purple); }
.rc-api { background: var(--yellow-dim); color: var(--yellow); }
.rc-load { background: var(--green-dim); color: var(--green); }
.run-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.run-status { font-size: 12px; font-weight: 600; }
.rs-pass { color: var(--green); }
.rs-fail { color: var(--red); }
.rs-running { color: var(--yellow); }
.rs-skipped { color: var(--muted); }
.run-time, .run-date { font-size: 11px; color: var(--muted); }

/* 스크립트 테이블 */
.script-name { font-size: 13px; font-weight: 600; }
.script-desc { font-size: 11px; color: var(--muted); margin-top: 2px; }
.target-cell { font-size: 11px; color: var(--muted); }
.lang-chip { display: inline-block; padding: 2px 7px; border-radius: 4px; background: var(--bg4); color: var(--text); font-size: 11px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.rate-cell { display: flex; align-items: center; gap: 7px; }
.rate-bar { width: 50px; height: 5px; background: var(--bg4); border-radius: 3px; overflow: hidden; }
.rate-fill { height: 100%; }
.rf-good { background: var(--green); }
.rf-bad { background: var(--red); }
.rate-num { font-size: 11px; min-width: 32px; }
.small-text { font-size: 11px; }
.run-btn { background: var(--primary-dim); color: var(--primary); border: none; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; font-family: inherit; }
.run-btn:hover { background: var(--primary); color: #fff; }
.modal-wide { width: 560px; }

@media (max-width: 720px) {
  .auto-page { padding: 20px 16px; }
  .cat-row { grid-template-columns: 90px 1fr 50px 50px; }
  .run-row { grid-template-columns: 50px 1fr 70px 50px 80px; }
}
</style>