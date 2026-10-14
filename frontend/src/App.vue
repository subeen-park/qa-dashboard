<template>
  <div class="app" :class="{scrolled: scrollY > 40}">
    <!-- 서버 연결 중 -->
    <div v-if="serverWaking" class="waking-overlay">
      <div class="waking-box">
        <div class="waking-spinner"></div>
        <div class="waking-title">서버에 연결 중...</div>
        <div class="waking-sub">최초 접속 시 잠시 걸릴 수 있어요 (약 30초)</div>
      </div>
    </div>

    <!-- 상단 네비 -->
    <header class="gnb" :class="{solid: scrollY > 40 || view !== 'home'}">
      <div class="gnb-inner">
        <div class="logo" @click="goHome">
          <div class="logo-mark">QA</div>
          <span class="logo-name">Hub</span>
        </div>
        <nav class="gnb-nav">
          <div class="gnb-item" :class="{active: view==='home'}" @click="goHome">홈</div>
          <div class="gnb-item" :class="{active: view==='list' || view==='detail'}" @click="goList">테스트 플랜</div>
          <div class="gnb-item" :class="{active: view==='automation'}" @click="goPage('automation')">자동화 테스트</div>
          <div class="gnb-item" :class="{active: view==='defect'}" @click="goPage('defect')">결함 트래커</div>
          <div class="gnb-item" :class="{active: view==='quality'}" @click="goPage('quality')">품질 대시보드</div>
        </nav>
        <div class="gnb-right">
          <a href="https://github.com/subeen-park/qa-dashboard" target="_blank" class="icon-btn" title="GitHub">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
            </svg>
          </a>
          <button v-if="view==='list'||view==='detail'" class="btn btn-primary btn-sm" @click="showProjectForm=true">+ 새 플랜</button>
        </div>
      </div>
    </header>

    <!-- 홈 -->
    <div v-if="view==='home'" class="home-page">

      <!-- Section 1: Hero -->
      <section class="hero">
        <div class="hero-bg">
          <div class="hero-blob blob1"></div>
          <div class="hero-blob blob2"></div>
          <div class="hero-blob blob3"></div>
        </div>
        <div class="hero-inner">
          <div class="hero-left">
            <div class="hero-badge">
              <span class="badge-dot"></span>
              QA Engineering Platform
            </div>
            <h1 class="hero-title">
              <span class="line">서비스 품질을</span>
              <span class="line">
                <span class="grad">하나의 흐름</span>으로.
              </span>
            </h1>
            <p class="hero-desc">
              테스트 플랜 수립부터 자동화 실행, 결함 트래킹,<br>
              품질 지표 분석까지 — QA 엔지니어링의 모든 과정을<br>
              한 곳에서 관리하세요.
            </p>
            <div class="hero-cta">
              <button class="btn btn-primary btn-lg" @click="goPage('automation')">
                자동화 테스트 실행
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5 3l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
              <button class="btn btn-ghost-lg" @click="goList">테스트 플랜 보기</button>
            </div>
            <div class="hero-trusted">
              <div class="trusted-label">Powered by</div>
              <div class="trusted-logos">
                <span>Selenium</span>
                <span class="sep">·</span>
                <span>Appium</span>
                <span class="sep">·</span>
                <span>Postman</span>
                <span class="sep">·</span>
                <span>Jira</span>
                <span class="sep">·</span>
                <span>GitLab</span>
              </div>
            </div>
          </div>

          <!-- 라이브 미니 대시보드 -->
          <div class="hero-right">
            <div class="live-card">
              <div class="live-head">
                <div class="live-title">
                  <span class="live-dot"></span>
                  Live Metrics
                </div>
                <div class="live-time mono">{{ liveTime }}</div>
              </div>
              <div class="live-metric-row">
                <div class="live-metric">
                  <div class="lm-label">통과율</div>
                  <div class="lm-val" style="color:var(--green)">{{ liveMetrics.passRate }}<span class="lm-u">%</span></div>
                  <div class="lm-bar"><div class="lm-fill" :style="{width: liveMetrics.passRate + '%', background: 'var(--green)'}"></div></div>
                </div>
                <div class="live-metric">
                  <div class="lm-label">자동화율</div>
                  <div class="lm-val" style="color:var(--primary)">{{ liveMetrics.autoRate }}<span class="lm-u">%</span></div>
                  <div class="lm-bar"><div class="lm-fill" :style="{width: liveMetrics.autoRate + '%', background: 'var(--primary)'}"></div></div>
                </div>
              </div>
              <div class="live-chart">
                <div class="lc-label">최근 10회 실행</div>
                <svg viewBox="0 0 300 60" class="spark">
                  <polyline :points="sparkPoints" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <polyline :points="sparkArea" :fill="'url(#spark-grad)'" stroke="none"/>
                  <defs>
                    <linearGradient id="spark-grad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="var(--primary)" stop-opacity="0.3"/>
                      <stop offset="100%" stop-color="var(--primary)" stop-opacity="0"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <div class="live-foot">
                <div class="lf-item">
                  <div class="lf-dot" style="background:var(--green)"></div>
                  <span>Pass {{ liveMetrics.pass }}</span>
                </div>
                <div class="lf-item">
                  <div class="lf-dot" style="background:var(--red)"></div>
                  <span>Fail {{ liveMetrics.fail }}</span>
                </div>
                <div class="lf-item">
                  <div class="lf-dot" style="background:var(--muted)"></div>
                  <span>Skip {{ liveMetrics.skip }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="scroll-hint">
          <span>스크롤해서 더보기</span>
          <div class="scroll-arrow">↓</div>
        </div>
      </section>

      <!-- Section 2: Big Numbers -->
      <section class="section-numbers">
        <div class="section-inner">
          <div class="section-eyebrow">현황</div>
          <h2 class="section-title">숫자로 보는 QA Hub</h2>
          <div class="numbers-grid">
            <div class="num-card">
              <div class="num-val">{{ projects.length }}<span class="num-u">건</span></div>
              <div class="num-label">진행 중 테스트 플랜</div>
              <div class="num-trend">
                <span class="trend-up">▲ 최근 1주 +{{ Math.max(1, Math.floor(projects.length * 0.1)) }}</span>
              </div>
            </div>
            <div class="num-card">
              <div class="num-val">{{ totalTasks }}<span class="num-u">개</span></div>
              <div class="num-label">전체 테스트 케이스</div>
              <div class="num-trend">
                <span class="trend-neutral">관리 중</span>
              </div>
            </div>
            <div class="num-card featured">
              <div class="num-val">68<span class="num-u">%</span></div>
              <div class="num-label">자동화율</div>
              <div class="num-trend">
                <span class="trend-up">▲ 지난달 대비 +5%</span>
              </div>
            </div>
            <div class="num-card">
              <div class="num-val" :style="{color: overdueCount > 0 ? 'var(--red)' : 'var(--green)'}">{{ overdueCount }}<span class="num-u">건</span></div>
              <div class="num-label">지연 검증</div>
              <div class="num-trend">
                <span v-if="overdueCount === 0" class="trend-up">정상</span>
                <span v-else class="trend-down">즉시 확인 필요</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 3: QA Workflow -->
      <section class="section-flow">
        <div class="section-inner">
          <div class="section-eyebrow">업무 흐름</div>
          <h2 class="section-title">
            설계부터 지표까지,<br>
            <span class="grad">끊김 없는 QA 사이클</span>
          </h2>
          <p class="section-sub">QA 엔지니어의 실제 업무 흐름을 그대로 녹여낸 4단계 구조</p>

          <div class="flow-grid">
            <div class="flow-card flow-01" @click="goList">
              <div class="fc-top">
                <div class="fc-num">01</div>
                <div class="fc-tag tag-plan">PLAN</div>
              </div>
              <h3 class="fc-title">테스트 플랜</h3>
              <p class="fc-desc">리스크 기반 TC 설계, Smoke/Regression/Integration 카테고리 관리, 담당자 배정과 진행률 추적까지.</p>
              <div class="fc-foot">
                <span class="fc-link">바로 가기 →</span>
              </div>
            </div>
            <div class="flow-card flow-02" @click="goPage('automation')">
              <div class="fc-top">
                <div class="fc-num">02</div>
                <div class="fc-tag tag-auto">AUTO</div>
              </div>
              <h3 class="fc-title">자동화 테스트</h3>
              <p class="fc-desc">PC·모바일·API·부하 테스트 통합 실행. Selenium/Appium/Postman/JMeter 스크립트를 한 곳에서.</p>
              <div class="fc-foot">
                <span class="fc-link">바로 가기 →</span>
              </div>
            </div>
            <div class="flow-card flow-03" @click="goPage('defect')">
              <div class="fc-top">
                <div class="fc-num">03</div>
                <div class="fc-tag tag-bug">BUG</div>
              </div>
              <h3 class="fc-title">결함 트래커</h3>
              <p class="fc-desc">Jira × GitLab 교차 검증으로 릴리즈 범위 자동 매칭. 탈출/재발 결함 플래그로 품질 리스크 선제 탐지.</p>
              <div class="fc-foot">
                <span class="fc-link">바로 가기 →</span>
              </div>
            </div>
            <div class="flow-card flow-04" @click="goPage('quality')">
              <div class="fc-top">
                <div class="fc-num">04</div>
                <div class="fc-tag tag-dash">DASH</div>
              </div>
              <h3 class="fc-title">품질 대시보드</h3>
              <p class="fc-desc">릴리즈별 통과율·결함 밀도·자동화율 추이를 SVG 차트로 시각화. 품질 기준의 정량 관리.</p>
              <div class="fc-foot">
                <span class="fc-link">바로 가기 →</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 4: Tool Integration -->
      <section class="section-tools">
        <div class="section-inner">
          <div class="section-eyebrow">도구 연동</div>
          <h2 class="section-title">
            실무에서 쓰는 모든 도구를<br>
            <span class="grad">하나의 콘솔</span>로.
          </h2>
          <div class="tools-grid">
            <div class="tool-badge">
              <div class="tb-cat">자동화</div>
              <div class="tb-name">Selenium</div>
            </div>
            <div class="tool-badge">
              <div class="tb-cat">모바일</div>
              <div class="tb-name">Appium</div>
            </div>
            <div class="tool-badge">
              <div class="tb-cat">API</div>
              <div class="tb-name">Postman</div>
            </div>
            <div class="tool-badge">
              <div class="tb-cat">부하</div>
              <div class="tb-name">JMeter · k6</div>
            </div>
            <div class="tool-badge">
              <div class="tb-cat">이슈</div>
              <div class="tb-name">Jira</div>
            </div>
            <div class="tool-badge">
              <div class="tb-cat">코드</div>
              <div class="tb-name">GitLab · GitHub</div>
            </div>
            <div class="tool-badge">
              <div class="tb-cat">언어</div>
              <div class="tb-name">Python · Java · JS · TS</div>
            </div>
            <div class="tool-badge">
              <div class="tb-cat">모니터링</div>
              <div class="tb-name">Firebase Crashlytics</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 5: CTA -->
      <section class="section-cta">
        <div class="section-inner cta-inner">
          <div class="cta-left">
            <div class="cta-eyebrow">Get started</div>
            <h2 class="cta-title">
              지금 바로 시작하세요.
            </h2>
            <p class="cta-sub">
              테스트 플랜부터 자동화 실행까지,<br>
              QA 업무의 전 과정을 한 곳에서 관리합니다.
            </p>
            <div class="cta-actions">
              <button class="btn btn-white btn-lg" @click="goList">
                테스트 플랜 시작하기
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5 3l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
              <button class="btn btn-outline-white btn-lg" @click="goPage('automation')">
                자동화 실행
              </button>
            </div>
          </div>
          <div class="cta-right">
            <div class="cta-stats-grid">
              <div class="cta-stat">
                <div class="cs-num">4</div>
                <div class="cs-label">통합 자동화 도구</div>
                <div class="cs-sub">Selenium · Appium · Postman · JMeter</div>
              </div>
              <div class="cta-stat">
                <div class="cs-num">5</div>
                <div class="cs-label">QA 업무 영역</div>
                <div class="cs-sub">플랜 · 실행 · 결함 · 지표 · 분석</div>
              </div>
              <div class="cta-stat">
                <div class="cs-num">1</div>
                <div class="cs-label">통합 콘솔</div>
                <div class="cs-sub">모든 과정을 한 화면에서</div>
              </div>
              <div class="cta-stat">
                <div class="cs-num">∞</div>
                <div class="cs-label">확장 가능성</div>
                <div class="cs-sub">Jira · GitLab · GitHub 연동</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer class="footer">
        <div class="footer-inner">
          <div class="footer-logo">
            <div class="logo-mark">QA</div>
            <span>Hub</span>
          </div>
          <div class="footer-txt">© 2026 QA Hub · Built by <a href="https://github.com/subeen-park" target="_blank">@subeen-park</a></div>
        </div>
      </footer>
    </div>

    <!-- 다른 페이지 -->
    <w-b-s-list v-if="view==='list'" :projects="projects" :loading="projectsLoading"
      @select="selectProject" @new="showProjectForm=true" @edit="editProj" @delete="deleteProject" />
    <w-b-s-detail v-if="view==='detail' && selectedProject" :project="selectedProject" :logs="logs"
      @back="goList" @edit-project="editProj" @toast="showToast" @reload-logs="loadLogs" @refresh-projects="loadProjects" />
    <automation-test v-if="view==='automation'" />

    <div v-if="view==='defect'" class="placeholder-page">
      <div class="ph-inner">
        <div class="ph-badge">COMING SOON</div>
        <h2 class="ph-title">결함 트래커</h2>
        <p class="ph-desc">Jira 티켓과 GitLab MR을 교차 검증해 릴리즈 범위를 자동 매칭하는 페이지가 들어갑니다.</p>
      </div>
    </div>
    <div v-if="view==='quality'" class="placeholder-page">
      <div class="ph-inner">
        <div class="ph-badge">COMING SOON</div>
        <h2 class="ph-title">품질 대시보드</h2>
        <p class="ph-desc">릴리즈별 TC 통과율, 결함 밀도, 자동화율 추이를 시각화합니다.</p>
      </div>
    </div>

    <project-form v-model="showProjectForm" :edit-project="editingProject" @save="saveProject" @delete="deleteProject" />

    <div class="toast-wrap">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="'toast-'+t.type">{{ t.msg }}</div>
    </div>
  </div>
</template>

<script>
import { api } from './api/index.js'
import WBSList         from './components/WBSList.vue'
import WBSDetail       from './components/WBSDetail.vue'
import ProjectForm     from './components/ProjectForm.vue'
import AutomationTest  from './components/AutomationTest.vue'

export default {
  name: 'App',
  components: { WBSList, WBSDetail, ProjectForm, AutomationTest },
  data() {
    return {
      view: 'home',
      projects: [], selectedProject: null, logs: [],
      showProjectForm: false, editingProject: null,
      toasts: [],
      projectsLoading: true,
      serverWaking: false,
      scrollY: 0,
      liveTime: '',
      liveMetrics: { passRate: 73, autoRate: 68, pass: 8, fail: 2, skip: 1 },
      sparkData: [65, 70, 68, 72, 71, 75, 73, 78, 76, 73],
      liveTimer: null,
    }
  },
  computed: {
    totalTasks()   { return this.projects.reduce((s, p) => s + (p.total || 0), 0) },
    overdueCount() { return this.projects.reduce((s, p) => s + (p.overdue || 0), 0) },
    sparkPoints() {
      const max = Math.max(...this.sparkData), min = Math.min(...this.sparkData)
      const range = max - min || 1
      return this.sparkData.map((v, i) => {
        const x = (i / (this.sparkData.length - 1)) * 290 + 5
        const y = 55 - ((v - min) / range) * 45
        return `${x},${y}`
      }).join(' ')
    },
    sparkArea() {
      return this.sparkPoints + ' 295,55 5,55'
    },
  },
  async mounted() {
    await this.loadWithWakeup()
    await this.loadLogs()
    window.addEventListener('hashchange', this.onHashChange)
    window.addEventListener('scroll', this.onScroll)
    if (!location.hash || location.hash === '#') location.hash = 'home'
    this.applyHash()
    this.updateLiveTime()
    this.liveTimer = setInterval(() => {
      this.updateLiveTime()
      this.jitterMetrics()
    }, 3000)
  },
  beforeUnmount() {
    window.removeEventListener('hashchange', this.onHashChange)
    window.removeEventListener('scroll', this.onScroll)
    if (this.liveTimer) clearInterval(this.liveTimer)
  },
  methods: {
    onScroll() { this.scrollY = window.scrollY },
    updateLiveTime() {
      const d = new Date()
      this.liveTime = d.toLocaleTimeString('ko', {hour: '2-digit', minute: '2-digit', second: '2-digit'})
    },
    jitterMetrics() {
      const delta = () => Math.floor(Math.random() * 3) - 1
      this.liveMetrics.passRate = Math.max(60, Math.min(95, this.liveMetrics.passRate + delta()))
      this.sparkData.shift()
      this.sparkData.push(this.liveMetrics.passRate)
    },
    async loadWithWakeup() {
      const wakeTimer = setTimeout(() => { this.serverWaking = true }, 3000)
      try { await this.loadProjects() }
      finally { clearTimeout(wakeTimer); this.serverWaking = false }
    },
    async loadProjects() {
      this.projectsLoading = true
      try {
        this.projects = await api.getProjects()
        if (this.selectedProject) {
          const updated = this.projects.find(p => p.id === this.selectedProject.id)
          if (updated) this.selectedProject = updated
        }
      } catch(e) { console.error(e) }
      finally { this.projectsLoading = false }
    },
    async loadLogs() { try { this.logs = await api.getLogs() } catch(e) {} },
    selectProject(proj) { this.selectedProject = proj; this.view = 'detail'; location.hash = 'detail'; window.scrollTo(0, 0) },
    goHome()     { this.view = 'home'; this.selectedProject = null; location.hash = 'home'; window.scrollTo(0, 0) },
    goList()     { this.view = 'list'; this.selectedProject = null; location.hash = 'list'; window.scrollTo(0, 0) },
    goPage(p)    { this.view = p; this.selectedProject = null; location.hash = p; window.scrollTo(0, 0) },
    onHashChange() {
      const hash = location.hash.replace('#', '') || 'home'
      const valid = ['home','list','detail','automation','defect','quality']
      if (valid.includes(hash)) {
        if (hash === 'detail' && !this.selectedProject) { this.view = 'list'; location.hash = 'list' }
        else { this.view = hash; if (hash !== 'detail') this.selectedProject = null }
      } else { this.view = 'home'; location.hash = 'home' }
    },
    applyHash() {
      const hash = location.hash.replace('#', '') || 'home'
      const valid = ['home','list','detail','automation','defect','quality']
      if (valid.includes(hash) && hash !== 'detail') this.view = hash
      else { this.view = 'home'; location.hash = 'home' }
    },
    editProj(proj) { this.editingProject = {...proj}; this.showProjectForm = true },
    async saveProject(form) {
      if (form.id) {
        await api.updateProject(form.id, form)
        this.showToast({msg: '테스트 플랜이 수정되었습니다', type: 'ok'})
        if (this.selectedProject?.id === form.id) this.selectedProject = {...this.selectedProject, ...form}
      } else {
        await api.createProject(form)
        this.showToast({msg: '테스트 플랜이 등록되었습니다', type: 'ok'})
      }
      this.showProjectForm = false; this.editingProject = null
      await this.loadProjects()
    },
    async deleteProject(id) {
      try {
        await api.deleteProject(id)
        this.showProjectForm = false; this.editingProject = null
        this.showToast({msg: '삭제되었습니다', type: 'info'})
        if (this.selectedProject?.id === id) this.goList()
        await this.loadProjects()
      } catch(e) { this.showToast({msg: '삭제 실패', type: 'err'}) }
    },
    showToast({msg, type='info'}) {
      const id = Date.now()
      this.toasts.push({id, msg, type})
      setTimeout(() => { this.toasts = this.toasts.filter(t => t.id !== id) }, 4000)
    },
  }
}
</script>

<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

:root{
  --bg:#ffffff;
  --bg2:#ffffff;
  --bg3:#f6f7f9;
  --bg4:#eef0f3;
  --surface-soft:#f9fafc;
  --primary:#0064FF;
  --primary-dim:#e5f0ff;
  --primary-hover:#0051d3;
  --primary-grad:linear-gradient(135deg,#0064FF 0%,#06B6D4 100%);
  --accent:#06C755;
  --coral:#FF5F57;
  --green:#06C755;
  --green-dim:#e3f8ec;
  --red:#F04452;
  --red-dim:#feecee;
  --yellow:#FFB800;
  --yellow-dim:#fff5db;
  --purple:#8B5CF6;
  --purple-dim:#f0ebfd;
  --text:#0F172A;
  --text-sub:#334155;
  --muted:#64748B;
  --faint:#CBD5E1;
  --border:#E5E8EB;
  --border2:#D1D6DB;
  --radius:12px;
  --shadow-sm:0 1px 2px rgba(15,23,42,.04);
  --shadow-md:0 4px 16px rgba(15,23,42,.06);
  --shadow-lg:0 12px 40px rgba(15,23,42,.08);
  --shadow-cta:0 10px 30px rgba(0,100,255,.25);
}

html{scroll-behavior:smooth}
body{
  background:var(--bg);
  color:var(--text);
  font-family:'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  font-size:16px;
  min-height:100vh;
  -webkit-font-smoothing:antialiased;
  letter-spacing:-0.01em;
}
.app{min-height:100vh}

/* ── GNB ── */
.gnb{
  position:fixed;top:0;left:0;right:0;
  z-index:100;
  height:68px;
  background:transparent;
  transition:background .25s, border-color .25s, box-shadow .25s;
  border-bottom:1px solid transparent;
}
.gnb.solid{
  background:rgba(255,255,255,.9);
  backdrop-filter:blur(16px);
  border-bottom-color:var(--border);
}
.gnb-inner{
  max-width:1240px;margin:0 auto;
  height:100%;padding:0 32px;
  display:flex;align-items:center;gap:40px;
}
.logo{display:flex;align-items:center;gap:8px;cursor:pointer}
.logo-mark{
  background:var(--primary-grad);
  color:#fff;font-size:12px;font-weight:800;
  width:30px;height:30px;
  display:flex;align-items:center;justify-content:center;
  border-radius:8px;font-family:'Inter',sans-serif;letter-spacing:.02em;
}
.logo-name{font-size:17px;font-weight:800;color:var(--text);letter-spacing:-.03em}

.gnb-nav{display:flex;align-items:center;gap:4px;flex:1}
.gnb-item{
  padding:8px 14px;font-size:14px;font-weight:500;color:var(--text-sub);
  cursor:pointer;border-radius:8px;transition:all .15s;
  white-space:nowrap;
}
.gnb-item:hover{background:var(--bg3);color:var(--text)}
.gnb-item.active{color:var(--primary);background:var(--primary-dim);font-weight:600}

.gnb-right{display:flex;align-items:center;gap:10px}
.icon-btn{
  background:transparent;border:none;color:var(--muted);
  width:36px;height:36px;border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;transition:all .15s;text-decoration:none;
}
.icon-btn:hover{background:var(--bg3);color:var(--text)}

/* ── 공통 버튼 ── */
.btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:10px 20px;border-radius:10px;
  font-size:14px;font-family:inherit;cursor:pointer;border:none;
  font-weight:600;transition:all .15s;letter-spacing:-.01em;
}
.btn-primary{background:var(--primary);color:#fff;box-shadow:var(--shadow-cta)}
.btn-primary:hover{background:var(--primary-hover);transform:translateY(-1px);box-shadow:0 14px 36px rgba(0,100,255,.3)}
.btn-ghost-lg{
  background:transparent;color:var(--text);
  padding:14px 26px;border-radius:12px;font-size:15px;font-weight:600;
  border:1.5px solid var(--border2);cursor:pointer;transition:all .15s;
}
.btn-ghost-lg:hover{background:var(--bg3);border-color:var(--text)}
.btn-sm{padding:7px 14px;font-size:13px}
.btn-lg{padding:14px 26px;font-size:15px;border-radius:12px}

/* ── HOME HERO ── */
.home-page{padding-top:0}

.hero{
  position:relative;
  min-height:100vh;
  padding:120px 32px 60px;
  display:flex;align-items:center;
  overflow:hidden;
  background:linear-gradient(180deg, #fafbfc 0%, #ffffff 100%);
}
.hero-bg{position:absolute;inset:0;overflow:hidden;z-index:0;pointer-events:none}
.hero-blob{
  position:absolute;border-radius:50%;filter:blur(100px);opacity:.5;
}
.hero-blob.blob1{
  width:500px;height:500px;background:#0064FF;opacity:.08;
  top:-150px;right:-100px;animation:float 20s ease-in-out infinite;
}
.hero-blob.blob2{
  width:400px;height:400px;background:#06C755;opacity:.08;
  bottom:-100px;left:-100px;animation:float 18s ease-in-out infinite reverse;
}
.hero-blob.blob3{
  width:300px;height:300px;background:#8B5CF6;opacity:.06;
  top:40%;left:50%;animation:float 22s ease-in-out infinite;
}
@keyframes float{
  0%,100%{transform:translate(0,0) scale(1)}
  50%{transform:translate(30px,-20px) scale(1.1)}
}

.hero-inner{
  position:relative;z-index:1;
  max-width:1240px;margin:0 auto;width:100%;
  display:grid;grid-template-columns:1.1fr 1fr;gap:60px;align-items:center;
}

.hero-left{animation:fadeInUp .8s ease}
@keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}

.hero-badge{
  display:inline-flex;align-items:center;gap:8px;
  background:var(--bg2);border:1px solid var(--border);
  padding:8px 14px;border-radius:100px;
  font-size:13px;font-weight:600;color:var(--text-sub);
  margin-bottom:28px;box-shadow:var(--shadow-sm);
}
.badge-dot{
  width:8px;height:8px;border-radius:50%;background:var(--green);
  box-shadow:0 0 8px var(--green);animation:pulse 2s infinite;
}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}

.hero-title{
  font-size:68px;font-weight:900;line-height:1.08;
  letter-spacing:-.045em;color:var(--text);
  margin-bottom:28px;word-break:keep-all;
}
.hero-title .line{display:block}
.grad{
  background:linear-gradient(135deg,#0064FF 0%,#06B6D4 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
}

.hero-desc{
  font-size:17px;line-height:1.7;color:var(--text-sub);
  margin-bottom:40px;font-weight:400;
}

.hero-cta{display:flex;align-items:center;gap:12px;margin-bottom:48px;flex-wrap:wrap}

.hero-trusted{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.trusted-label{font-size:12px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.08em}
.trusted-logos{display:flex;align-items:center;gap:10px;color:var(--text-sub);font-size:14px;font-weight:600}
.trusted-logos .sep{color:var(--faint)}

/* 라이브 미니 대시보드 */
.hero-right{animation:fadeInUp .8s ease .2s both}
.live-card{
  background:var(--bg2);border:1px solid var(--border);border-radius:20px;
  padding:28px;box-shadow:var(--shadow-lg);
  position:relative;overflow:hidden;
}
.live-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--primary-grad);
}
.live-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}
.live-title{display:flex;align-items:center;gap:8px;font-size:14px;font-weight:700}
.live-dot{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green);animation:pulse 1.5s infinite}
.live-time{font-size:12px;color:var(--muted);font-family:'JetBrains Mono',monospace}

.live-metric-row{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px}
.live-metric{display:flex;flex-direction:column;gap:6px}
.lm-label{font-size:12px;color:var(--muted);font-weight:600}
.lm-val{font-size:36px;font-weight:800;font-family:'Inter',sans-serif;line-height:1;letter-spacing:-.03em}
.lm-u{font-size:18px;color:var(--muted);font-weight:600;margin-left:2px}
.lm-bar{height:4px;background:var(--bg4);border-radius:2px;overflow:hidden;margin-top:4px}
.lm-fill{height:100%;transition:width .5s;border-radius:2px}

.live-chart{margin-bottom:20px}
.lc-label{font-size:11px;color:var(--muted);font-weight:600;margin-bottom:8px}
.spark{width:100%;height:60px}

.live-foot{display:flex;gap:16px;padding-top:16px;border-top:1px solid var(--border)}
.lf-item{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-sub);font-weight:500}
.lf-dot{width:8px;height:8px;border-radius:50%}

.scroll-hint{
  position:absolute;bottom:30px;left:50%;transform:translateX(-50%);
  display:flex;flex-direction:column;align-items:center;gap:6px;
  font-size:12px;color:var(--muted);font-weight:500;
  animation:bounce 2s infinite;z-index:1;
}
.scroll-arrow{font-size:16px}
@keyframes bounce{0%,100%{transform:translateX(-50%) translateY(0)}50%{transform:translateX(-50%) translateY(6px)}}

/* ── SECTIONS ── */
.section-inner{max-width:1240px;margin:0 auto;padding:0 32px}
.section-eyebrow{
  display:inline-block;font-size:13px;font-weight:700;color:var(--primary);
  letter-spacing:.1em;text-transform:uppercase;margin-bottom:16px;
}
.section-title{
  font-size:48px;font-weight:900;line-height:1.2;letter-spacing:-.04em;
  color:var(--text);margin-bottom:16px;word-break:keep-all;
}
.section-sub{font-size:16px;color:var(--text-sub);line-height:1.7;margin-bottom:56px}

/* Numbers */
.section-numbers{padding:120px 0;background:var(--surface-soft)}
.numbers-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:56px}
.num-card{
  background:var(--bg2);border:1px solid var(--border);border-radius:16px;
  padding:32px 24px;transition:all .25s;position:relative;overflow:hidden;
}
.num-card:hover{border-color:var(--primary);box-shadow:var(--shadow-md);transform:translateY(-4px)}
.num-card.featured{
  background:var(--primary-grad);color:#fff;border-color:transparent;
}
.num-card.featured .num-label,.num-card.featured .trend-up{color:rgba(255,255,255,.9)}
.num-val{
  font-size:48px;font-weight:900;line-height:1;
  letter-spacing:-.04em;font-family:'Inter',sans-serif;color:var(--primary);
  margin-bottom:12px;
}
.num-card.featured .num-val{color:#fff}
.num-u{font-size:20px;font-weight:700;margin-left:4px;color:var(--muted)}
.num-card.featured .num-u{color:rgba(255,255,255,.8)}
.num-label{font-size:14px;color:var(--text-sub);font-weight:600;margin-bottom:12px}
.num-trend{font-size:12px;font-weight:600}
.trend-up{color:var(--green)}
.trend-down{color:var(--red)}
.trend-neutral{color:var(--muted)}

/* Flow */
.section-flow{padding:120px 0}
.flow-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.flow-card{
  background:var(--bg2);border:1.5px solid var(--border);border-radius:20px;
  padding:32px 28px;cursor:pointer;transition:all .25s;
  display:flex;flex-direction:column;gap:16px;
}
.flow-card:hover{border-color:var(--primary);transform:translateY(-6px);box-shadow:var(--shadow-lg)}
.fc-top{display:flex;justify-content:space-between;align-items:center}
.fc-num{font-size:13px;font-weight:800;color:var(--muted);font-family:'JetBrains Mono',monospace;letter-spacing:.08em}
.fc-tag{font-size:10px;font-weight:800;padding:4px 10px;border-radius:6px;font-family:'JetBrains Mono',monospace;letter-spacing:.08em}
.tag-plan{background:#e5f0ff;color:#0064FF}
.tag-auto{background:#fff5db;color:#c48500}
.tag-bug{background:#f0ebfd;color:#8B5CF6}
.tag-dash{background:#feecee;color:#F04452}
.fc-title{font-size:22px;font-weight:800;letter-spacing:-.03em;color:var(--text);margin-top:8px}
.fc-desc{font-size:14px;color:var(--text-sub);line-height:1.6;flex:1;word-break:keep-all}
.fc-foot{padding-top:12px;border-top:1px solid var(--border)}
.fc-link{font-size:13px;color:var(--primary);font-weight:600;transition:gap .15s}
.flow-card:hover .fc-link{letter-spacing:.02em}

/* Tools */
.section-tools{padding:120px 0;background:var(--surface-soft)}
.tools-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:56px}
.tool-badge{
  background:var(--bg2);border:1px solid var(--border);border-radius:14px;
  padding:24px;display:flex;flex-direction:column;gap:8px;transition:all .2s;
}
.tool-badge:hover{border-color:var(--primary);transform:translateY(-2px);box-shadow:var(--shadow-md)}
.tb-cat{font-size:11px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.tb-name{font-size:17px;font-weight:800;color:var(--text);letter-spacing:-.02em}

/* CTA */
.section-cta{
  padding:120px 0;position:relative;overflow:hidden;
  background:linear-gradient(135deg,#0064FF 0%,#06B6D4 100%);
}
.section-cta::before{
  content:'';position:absolute;inset:0;
  background-image:radial-gradient(circle at 20% 30%,rgba(255,255,255,.15) 0,transparent 50%),
                   radial-gradient(circle at 80% 70%,rgba(255,255,255,.08) 0,transparent 50%);
  pointer-events:none;
}
.section-cta::after{
  content:'';position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(255,255,255,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.04) 1px, transparent 1px);
  background-size:60px 60px;
  pointer-events:none;
}
.cta-inner{position:relative;z-index:1;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}
.cta-left{color:#fff}
.cta-eyebrow{display:inline-block;font-size:12px;font-weight:700;color:rgba(255,255,255,.85);letter-spacing:.12em;text-transform:uppercase;margin-bottom:16px;padding:6px 12px;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.2);border-radius:100px;backdrop-filter:blur(10px)}
.cta-title{font-size:52px;font-weight:900;color:#fff;letter-spacing:-.04em;margin-bottom:20px;line-height:1.1}
.cta-sub{font-size:17px;color:rgba(255,255,255,.9);margin-bottom:36px;font-weight:400;line-height:1.65}
.cta-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.btn-white{background:#fff;color:var(--primary);box-shadow:0 10px 30px rgba(0,0,0,.15);font-weight:700}
.btn-white:hover{background:#f5f5f5;box-shadow:0 14px 40px rgba(0,0,0,.2);transform:translateY(-1px)}
.btn-outline-white{background:transparent;color:#fff;border:1.5px solid rgba(255,255,255,.4);padding:14px 26px;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s;letter-spacing:-.01em}
.btn-outline-white:hover{background:rgba(255,255,255,.1);border-color:#fff}

.cta-right{position:relative}
.cta-stats-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.cta-stat{background:rgba(255,255,255,.1);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.2);border-radius:16px;padding:24px 20px;transition:all .25s}
.cta-stat:hover{background:rgba(255,255,255,.15);transform:translateY(-2px)}
.cs-num{font-size:52px;font-weight:900;color:#fff;line-height:1;letter-spacing:-.04em;font-family:'Inter',sans-serif;margin-bottom:12px}
.cs-label{font-size:14px;color:#fff;font-weight:700;margin-bottom:4px;letter-spacing:-.01em}
.cs-sub{font-size:11px;color:rgba(255,255,255,.7);line-height:1.5;font-weight:500}

/* Footer */
.footer{padding:40px 32px;background:var(--text);color:#fff}
.footer-inner{max-width:1240px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}
.footer-logo{display:flex;align-items:center;gap:8px;font-size:17px;font-weight:800}
.footer-txt{font-size:13px;color:rgba(255,255,255,.6)}
.footer-txt a{color:#fff;text-decoration:none}
.footer-txt a:hover{text-decoration:underline}

/* Placeholder */
.placeholder-page{display:flex;align-items:center;justify-content:center;min-height:100vh;padding:40px;padding-top:120px}
.ph-inner{text-align:center;max-width:520px}
.ph-badge{display:inline-block;background:var(--yellow-dim);color:var(--yellow);font-size:11px;font-weight:800;padding:5px 12px;border-radius:6px;letter-spacing:.1em;margin-bottom:20px;font-family:'JetBrains Mono',monospace}
.ph-title{font-size:36px;font-weight:900;letter-spacing:-.03em;margin-bottom:14px}
.ph-desc{font-size:15px;color:var(--text-sub);line-height:1.75;word-break:keep-all}

/* 공통 (내부 페이지용) */
.page-title{font-size:17px;font-weight:800;letter-spacing:-.02em}
.page-sub{font-size:13px;color:var(--muted);margin-top:4px}
.metrics-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:14px;margin-bottom:24px}
.metric-card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px}
.metric-label{font-size:11px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px}
.metric-val{font-size:28px;font-weight:800;font-family:'Inter',sans-serif;letter-spacing:-.03em}
.metric-sub{font-size:11px;color:var(--muted);margin-top:4px}
.table-wrap{background:var(--bg2);border:1px solid var(--border);border-radius:12px;overflow:hidden}
.data-table{width:100%;border-collapse:collapse}
.data-table th{background:var(--bg3);padding:12px 16px;text-align:left;font-size:11px;font-weight:700;color:var(--muted);border-bottom:1px solid var(--border);text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
.data-table td{padding:13px 16px;border-bottom:1px solid var(--border);font-size:14px;vertical-align:middle}
.data-table tr:last-child td{border-bottom:none}
.data-table tr:hover td{background:var(--bg3)}
.chip{display:inline-flex;align-items:center;padding:3px 9px;border-radius:6px;font-size:11px;font-weight:700}
.chip-pass{background:var(--green-dim);color:var(--green)}
.chip-fail{background:var(--red-dim);color:var(--red)}
.chip-running{background:var(--yellow-dim);color:var(--yellow)}
.chip-skipped{background:var(--bg4);color:var(--muted)}
.btn-ghost{background:var(--bg3);color:var(--text-sub);border:1px solid var(--border2);padding:8px 14px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:500}
.btn-ghost:hover{background:var(--bg4);color:var(--text)}
.btn-danger{background:var(--red-dim);color:var(--red);border:1px solid rgba(240,68,82,.25);padding:8px 14px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:500}
.btn-danger:hover{background:rgba(240,68,82,.15)}
.mono{font-family:'JetBrains Mono',monospace}
.empty{text-align:center;padding:48px;color:var(--muted);font-size:14px}
.overlay{position:fixed;inset:0;background:rgba(15,23,42,.5);z-index:300;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.modal{background:var(--bg2);border-radius:16px;padding:28px;width:540px;max-width:90vw;max-height:85vh;overflow-y:auto;box-shadow:var(--shadow-lg)}
.modal-title{font-size:18px;font-weight:800;letter-spacing:-.02em;margin-bottom:20px}
.field{margin-bottom:14px}
.field label{display:block;font-size:12px;color:var(--text-sub);font-weight:700;margin-bottom:6px}
.field input,.field select,.field textarea{width:100%;background:var(--bg3);border:1px solid var(--border2);border-radius:10px;padding:10px 14px;color:var(--text);font-size:14px;font-family:inherit;outline:none;transition:border-color .15s}
.field input:focus,.field select:focus,.field textarea:focus{border-color:var(--primary);background:#fff}
.field textarea{resize:vertical;min-height:80px}
.field-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:24px;padding-top:20px;border-top:1px solid var(--border)}

/* 서버 깨우기 */
.waking-overlay{position:fixed;inset:0;background:rgba(15,23,42,.7);backdrop-filter:blur(8px);z-index:500;display:flex;align-items:center;justify-content:center}
.waking-box{background:#fff;border-radius:20px;padding:48px 60px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:16px;box-shadow:var(--shadow-lg)}
.waking-spinner{width:40px;height:40px;border:3px solid var(--bg4);border-top-color:var(--primary);border-radius:50%;animation:spin 1s linear infinite}
.waking-title{font-size:16px;font-weight:700}
.waking-sub{font-size:13px;color:var(--muted)}
@keyframes spin{to{transform:rotate(360deg)}}

/* 토스트 */
.toast-wrap{position:fixed;bottom:28px;right:28px;z-index:400;display:flex;flex-direction:column;gap:10px}
.toast{background:#fff;border-radius:12px;padding:14px 20px;font-size:14px;animation:slideIn .25s ease;min-width:260px;color:var(--text);box-shadow:var(--shadow-lg);font-weight:500}
.toast-ok{border-left:3px solid var(--green)}
.toast-err{border-left:3px solid var(--red)}
.toast-info{border-left:3px solid var(--primary)}
@keyframes slideIn{from{transform:translateX(120%);opacity:0}to{transform:translateX(0);opacity:1}}

/* 반응형 */
@media(max-width:1024px){
  .hero-inner{grid-template-columns:1fr;gap:40px}
  .hero-title{font-size:48px}
  .section-title{font-size:36px}
  .numbers-grid{grid-template-columns:repeat(2,1fr)}
  .cta-inner{grid-template-columns:1fr;gap:40px}
  .flow-grid{grid-template-columns:repeat(2,1fr)}
  .tools-grid{grid-template-columns:repeat(2,1fr)}
  .gnb-nav{display:none}
}
@media(max-width:640px){
  .hero{padding:100px 20px 40px}
  .hero-title{font-size:36px}
  .section-inner{padding:0 20px}
  .section-title{font-size:28px}
  .cta-title{font-size:32px}
  .section-numbers,.section-flow,.section-tools,.section-cta{padding:72px 0}
  .numbers-grid,.flow-grid,.tools-grid{grid-template-columns:1fr}
  .num-val,.lm-val{font-size:36px}
  .gnb-inner{padding:0 20px}
}
</style>