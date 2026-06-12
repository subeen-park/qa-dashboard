<template>
  <div class="app">
    <!-- 서버 연결 중 오버레이 -->
    <div v-if="serverWaking" class="waking-overlay">
      <div class="waking-box">
        <div class="waking-spinner"></div>
        <div class="waking-title">서버에 연결 중...</div>
        <div class="waking-sub">최초 접속 시 잠시 걸릴 수 있어요 (약 30초)</div>
        <div class="waking-dots"><span></span><span></span><span></span></div>
      </div>
    </div>

    <header class="gnb">
      <div class="logo" @click="goHome" style="cursor:pointer">
        <span class="logo-dot">●</span> PM Suite
      </div>
      <nav class="gnb-nav">
        <div class="gnb-item" :class="{active: view==='home'}" @click="goHome">홈</div>
        <div class="gnb-item" :class="{active: view==='list' || view==='detail'}" @click="goList">릴리즈 보드</div>
        <div class="gnb-item gnb-sub" v-if="view==='detail' && selectedProject">› {{ selectedProject.name }}</div>
        <div class="gnb-item" :class="{active: view==='calendar'}" @click="goPage('calendar')">릴리즈 캘린더</div>
        <div class="gnb-item" :class="{active: view==='checklist'}" @click="goPage('checklist')">체크리스트</div>
        <div class="gnb-item" :class="{active: view==='merge'}" @click="goPage('merge')">머지 트래커</div>
        <div class="gnb-item" :class="{active: view==='jira'}" @click="goPage('jira')">Jira 레이더</div>
      </nav>
      <div class="gnb-right">
        <span class="last-saved">{{ lastSaved }}</span>
        <a href="https://github.com/subeen-park" target="_blank" class="icon-btn" title="GitHub">
          <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor">
            <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
          </svg>
        </a>
        <button class="icon-btn theme-btn" @click="toggleTheme" :title="theme==='dark'?'라이트 모드':'다크 모드'">
          {{ theme==='dark' ? '☀️' : '🌙' }}
        </button>
        <button v-if="view==='list'||view==='detail'" class="btn btn-primary btn-sm" @click="showProjectForm=true">+ 새 WBS</button>
      </div>
    </header>

    <!-- 홈 랜딩 -->
    <div v-if="view==='home'" class="home-page">
      <div class="home-inner">

        <!-- 히어로 -->
        <div class="home-hero">
          <div class="home-badge">PM Suite — 릴리즈 관리 도구</div>
          <h1 class="home-title">PM 업무,<br>한 곳에서 끝내기.</h1>
          <p class="home-desc">WBS 관리부터 릴리즈 캘린더, 머지 추적, Jira 정체 분석까지<br>팀의 모든 일정을 하나의 대시보드에서 관리하세요.</p>
          <div class="home-actions">
            <button class="btn btn-cta" @click="goList">WBS 보드 시작하기 →</button>
            <button class="btn btn-outline" @click="goPage('merge')">머지 트래커 보기</button>
          </div>
          <!-- 통계 칩 -->
          <div class="home-stats">
            <div class="stat-chip">
              <span class="stat-num">{{ projects.length }}</span>
              <span class="stat-label">진행 중인 WBS</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-chip">
              <span class="stat-num">{{ totalTasks }}</span>
              <span class="stat-label">전체 태스크</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-chip">
              <span class="stat-num" :style="{color: overdueCount > 0 ? 'var(--red)' : 'var(--green)'}">{{ overdueCount }}</span>
              <span class="stat-label">지연 태스크</span>
            </div>
          </div>
        </div>

        <!-- 기능 카드 그리드 -->
        <div class="home-cards">
          <div class="home-card card-wbs" @click="goList">
            <div class="card-icon ci-wbs">WBS</div>
            <div class="card-content">
              <div class="card-num">01</div>
              <div class="card-title">WBS 보드</div>
              <div class="card-desc">프로젝트별 태스크를 그룹으로 관리하고 간트 차트로 일정을 시각화해요.</div>
            </div>
            <div class="card-arrow">→</div>
          </div>
          <div class="home-card card-cal" @click="goPage('calendar')">
            <div class="card-icon ci-cal">CAL</div>
            <div class="card-content">
              <div class="card-num">02</div>
              <div class="card-title">릴리즈 캘린더</div>
              <div class="card-desc">전체 프로젝트 마감일과 마일스톤을 월별 캘린더로 한눈에 확인해요.</div>
            </div>
            <div class="card-arrow">→</div>
          </div>
          <div class="home-card card-check" @click="goPage('checklist')">
            <div class="card-icon ci-chk">CHK</div>
            <div class="card-content">
              <div class="card-num">03</div>
              <div class="card-title">릴리즈 체크리스트</div>
              <div class="card-desc">릴리즈 전 QA, 배포, 롤백 플랜 등 팀 협업 체크리스트를 관리해요.</div>
            </div>
            <div class="card-arrow">→</div>
          </div>
          <div class="home-card card-merge" @click="goPage('merge')">
            <div class="card-icon ci-mrg">MRG</div>
            <div class="card-content">
              <div class="card-num">04</div>
              <div class="card-title">머지 트래커</div>
              <div class="card-desc">버전별 머지/빌드 현황을 플랫폼별로 실시간 추적하고 배포를 준비해요.</div>
            </div>
            <div class="card-arrow">→</div>
          </div>
          <div class="home-card card-jira" @click="goPage('jira')">
            <div class="card-icon ci-jra">JIRA</div>
            <div class="card-content">
              <div class="card-num">05</div>
              <div class="card-title">Jira 레이더</div>
              <div class="card-desc">Jira 티켓의 정체 구간을 분석하고 병목 담당자 Top 10을 추적해요.</div>
            </div>
            <div class="card-arrow">→</div>
          </div>
        </div>

      </div>
    </div>

    <w-b-s-list v-if="view==='list'" :projects="projects" :loading="projectsLoading"
      @select="selectProject" @new="showProjectForm=true" @edit="editProj" @delete="deleteProject" />
    <w-b-s-detail v-if="view==='detail' && selectedProject" :project="selectedProject" :logs="logs"
      @back="goList" @edit-project="editProj" @toast="showToast" @reload-logs="loadLogs" @refresh-projects="loadProjects" />
    <merge-tracker    v-if="view==='merge'" />
    <jira-radar       v-if="view==='jira'" />
    <release-calendar  v-if="view==='calendar'" />
    <release-checklist v-if="view==='checklist'" />

    <project-form v-model="showProjectForm" :edit-project="editingProject" @save="saveProject" @delete="deleteProject" />

    <div class="toast-wrap">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="'toast-'+t.type">{{ t.msg }}</div>
    </div>
  </div>
</template>

<script>
import { api } from './api/index.js'
import WBSList           from './components/WBSList.vue'
import WBSDetail         from './components/WBSDetail.vue'
import ProjectForm       from './components/ProjectForm.vue'
import MergeTracker      from './components/MergeTracker.vue'
import JiraRadar         from './components/JiraRadar.vue'
import ReleaseCalendar   from './components/ReleaseCalendar.vue'
import ReleaseChecklist  from './components/ReleaseChecklist.vue'

export default {
  name: 'App',
  components: { WBSList, WBSDetail, ProjectForm, MergeTracker, JiraRadar, ReleaseCalendar, ReleaseChecklist },
  data() {
    return {
      view: 'home',
      projects: [], selectedProject: null, logs: [],
      showProjectForm: false, editingProject: null,
      lastSaved: '', toasts: [],
      theme: 'light',
      projectsLoading: true,
      serverWaking: false,
    }
  },
  computed: {
    totalTasks()   { return this.projects.reduce((s, p) => s + (p.total || 0), 0) },
    overdueCount() { return this.projects.reduce((s, p) => s + (p.overdue || 0), 0) },
  },
  async mounted() {
    const savedTheme = localStorage.getItem('wbs-theme') || 'light'
    this.setTheme(savedTheme)
    await this.loadWithWakeup()
    await this.loadLogs()
    window.addEventListener('hashchange', this.onHashChange)
    if (!location.hash || location.hash === '#') location.hash = 'home'
    this.applyHash()
  },
  beforeUnmount() { window.removeEventListener('hashchange', this.onHashChange) },
  methods: {
    async loadWithWakeup() {
      const wakeTimer = setTimeout(() => { this.serverWaking = true }, 3000)
      try { await this.loadProjects() }
      finally { clearTimeout(wakeTimer); this.serverWaking = false }
    },
    async loadProjects() {
      this.projectsLoading = true
      try {
        this.projects = await api.getProjects()
        this.lastSaved = new Date().toLocaleTimeString('ko', { hour:'2-digit', minute:'2-digit' }) + ' 업데이트'
        if (this.selectedProject) {
          const updated = this.projects.find(p => p.id === this.selectedProject.id)
          if (updated) this.selectedProject = updated
        }
      } catch(e) { console.error(e) }
      finally { this.projectsLoading = false }
    },
    async loadLogs() { try { this.logs = await api.getLogs() } catch(e) {} },
    selectProject(proj) { this.selectedProject = proj; this.view = 'detail'; location.hash = 'detail' },
    goHome()      { this.view = 'home'; this.selectedProject = null; location.hash = 'home' },
    goList()      { this.view = 'list'; this.selectedProject = null; location.hash = 'list' },
    goPage(page)  { this.view = page;  this.selectedProject = null; location.hash = page  },
    onHashChange() {
      const hash = location.hash.replace('#', '') || 'home'
      const valid = ['home','list','detail','merge','jira','calendar','checklist']
      if (valid.includes(hash)) {
        if (hash === 'detail' && !this.selectedProject) { this.view = 'list'; location.hash = 'list' }
        else { this.view = hash; if (hash !== 'detail') this.selectedProject = null }
      } else { this.view = 'home'; location.hash = 'home' }
    },
    applyHash() {
      const hash = location.hash.replace('#', '') || 'home'
      const valid = ['home','list','detail','merge','jira','calendar','checklist']
      if (valid.includes(hash) && hash !== 'detail') this.view = hash
      else { this.view = 'home'; location.hash = 'home' }
    },
    editProj(proj) { this.editingProject = {...proj}; this.showProjectForm = true },
    async saveProject(form) {
      if (form.id) {
        await api.updateProject(form.id, form)
        this.showToast({ msg: 'WBS가 수정되었습니다', type: 'ok' })
        if (this.selectedProject?.id === form.id) this.selectedProject = { ...this.selectedProject, ...form }
      } else {
        await api.createProject(form)
        this.showToast({ msg: 'WBS가 등록되었습니다', type: 'ok' })
      }
      this.showProjectForm = false; this.editingProject = null
      await this.loadProjects()
    },
    async deleteProject(id) {
      try {
        await api.deleteProject(id)
        this.showProjectForm = false; this.editingProject = null
        this.showToast({ msg: 'WBS가 삭제되었습니다', type: 'info' })
        if (this.selectedProject?.id === id) this.goList()
        await this.loadProjects()
      } catch(e) { this.showToast({ msg: '삭제 실패: ' + e.message, type: 'err' }) }
    },
    showToast({ msg, type='info' }) {
      const id = Date.now()
      this.toasts.push({ id, msg, type })
      setTimeout(() => { this.toasts = this.toasts.filter(t => t.id !== id) }, 5000)
    },
    toggleTheme() { this.setTheme(this.theme==='dark' ? 'light' : 'dark') },
    setTheme(t) {
      this.theme = t
      document.documentElement.setAttribute('data-theme', t)
      localStorage.setItem('wbs-theme', t)
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=DM+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

/* ── 라이트 모드 기본 (배민/토스 느낌 — 블루 계열 포인트) ── */
:root{
  --bg:#f7f8fa;
  --bg2:#ffffff;
  --bg3:#f0f2f5;
  --bg4:#e8eaed;
  --primary:#3563E9;       /* 포인트 — 진한 인디고 블루 */
  --primary-dim:#e8edf8;
  --primary-hover:#2450d0;
  --amber:#3563E9;         /* 하위 호환 */
  --amber-dim:#e8edf8;
  --blue:#3563E9;
  --blue-dim:#e8edf8;
  --green:#18a058;
  --green-dim:#e6f4ee;
  --red:#e53e3e;
  --red-dim:#fde8e8;
  --yellow:#d48806;
  --yellow-dim:#fef3cd;
  --text:#111827;
  --muted:#6b7280;
  --faint:#d1d5db;
  --border:rgba(0,0,0,.08);
  --border2:rgba(0,0,0,.14);
}

/* ── 다크 모드 ── */
:root[data-theme="dark"]{
  --bg:#0f1117;
  --bg2:#1a1d27;
  --bg3:#22263a;
  --bg4:#2a2f45;
  --primary:#5b8af5;
  --primary-dim:rgba(91,138,245,.12);
  --primary-hover:#7aa3f7;
  --amber:#5b8af5;
  --amber-dim:rgba(91,138,245,.12);
  --blue:#5b8af5;
  --blue-dim:rgba(91,138,245,.12);
  --green:#3db87a;
  --green-dim:rgba(61,184,122,.1);
  --red:#e05555;
  --red-dim:rgba(224,85,85,.1);
  --yellow:#d4a843;
  --yellow-dim:rgba(212,168,67,.1);
  --text:#e8eaf0;
  --muted:#8b93a8;
  --faint:#2a2f45;
  --border:rgba(255,255,255,.07);
  --border2:rgba(255,255,255,.14);
}

html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-size:16px;min-height:100vh;transition:background .25s,color .25s;-webkit-font-smoothing:antialiased}
.app{display:grid;grid-template-rows:auto 1fr;min-height:100vh}

/* ── GNB ── */
.gnb{background:var(--bg2);border-bottom:1px solid var(--border);padding:0 28px;height:54px;display:flex;align-items:center;gap:0;position:sticky;top:0;z-index:100;transition:background .25s}
.logo{display:flex;align-items:center;gap:6px;font-size:13px;font-weight:700;color:var(--text);letter-spacing:.02em;margin-right:36px;white-space:nowrap}
.logo-dot{color:var(--primary);font-size:10px}
.gnb-nav{display:flex;align-items:stretch;gap:0;flex:1;height:100%}
.gnb-item{padding:0 14px;font-size:13px;color:var(--muted);cursor:pointer;transition:color .15s;white-space:nowrap;display:flex;align-items:center;border-bottom:2px solid transparent}
.gnb-item:hover{color:var(--text)}
.gnb-item.active{color:var(--primary);border-bottom-color:var(--primary);font-weight:500}
.gnb-sub{color:var(--primary)!important;border-bottom:none!important;font-size:12px;cursor:default;opacity:.8}
.gnb-right{display:flex;align-items:center;gap:8px;margin-left:auto}
.last-saved{font-size:11px;color:var(--muted);white-space:nowrap}
.icon-btn{background:transparent;border:1px solid var(--border2);color:var(--muted);border-radius:7px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:15px;transition:all .15s;text-decoration:none}
.icon-btn:hover{background:var(--bg3);color:var(--text)}
.theme-btn{font-size:14px}

/* ── 공통 버튼 ── */
.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 18px;border-radius:8px;font-size:13px;font-family:'Noto Sans KR',sans-serif;cursor:pointer;border:none;transition:all .15s;font-weight:500}
.btn-primary{background:var(--primary);color:#fff}.btn-primary:hover{background:var(--primary-hover)}
.btn-sm{padding:6px 14px;font-size:12px}

/* ── 홈 ── */
.home-page{overflow-y:auto;min-height:calc(100vh - 54px)}
.home-inner{max-width:1280px;margin:0 auto;padding:72px 32px 72px}

.home-hero{margin-bottom:64px}
.home-badge{display:inline-block;background:var(--primary-dim);color:var(--primary);font-size:12px;font-weight:600;padding:5px 12px;border-radius:20px;letter-spacing:.04em;margin-bottom:24px}
.home-title{font-size:52px;font-weight:900;line-height:1.15;margin-bottom:18px;color:var(--text);letter-spacing:-.03em;word-break:keep-all}
.home-desc{font-size:15px;color:var(--muted);line-height:1.8;margin-bottom:32px;font-weight:400;word-break:keep-all}
.home-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:40px}
.btn-cta{background:var(--primary);color:#fff;padding:12px 24px;font-size:14px;font-weight:600;border-radius:10px;border:none;cursor:pointer;font-family:inherit;transition:all .15s;box-shadow:0 4px 14px rgba(53,99,233,.3)}
.btn-cta:hover{background:var(--primary-hover);transform:translateY(-1px);box-shadow:0 6px 20px rgba(53,99,233,.4)}
.btn-outline{background:transparent;color:var(--text);padding:12px 24px;font-size:14px;font-weight:500;border-radius:10px;border:1.5px solid var(--border2);cursor:pointer;font-family:inherit;transition:all .15s}
.btn-outline:hover{border-color:var(--primary);color:var(--primary);background:var(--primary-dim)}

/* 통계 칩 */
.home-stats{display:flex;align-items:center;gap:0}
.stat-chip{display:flex;align-items:baseline;gap:6px;padding:0 20px}
.stat-chip:first-child{padding-left:0}
.stat-num{font-size:24px;font-weight:700;font-family:'DM Mono',monospace;color:var(--primary)}
.stat-label{font-size:12px;color:var(--muted)}
.stat-divider{width:1px;height:28px;background:var(--border2)}

/* 기능 카드 */
.home-cards{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}

.home-card{background:var(--bg2);border:1.5px solid var(--border);border-radius:14px;padding:22px 18px;cursor:pointer;transition:all .2s;display:flex;flex-direction:column;gap:12px;position:relative;overflow:hidden}
.home-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:14px 14px 0 0;opacity:0;transition:opacity .2s}
.home-card:hover{border-color:transparent;transform:translateY(-3px);box-shadow:0 8px 28px rgba(0,0,0,.1)}
.home-card:hover::before{opacity:1}

/* 카드별 포인트 컬러 */
.card-wbs::before{background:linear-gradient(90deg,#3563E9,#5b8af5)}
.card-wbs:hover{box-shadow:0 8px 28px rgba(53,99,233,.15)}
.card-cal::before{background:linear-gradient(90deg,#18a058,#34d399)}
.card-cal:hover{box-shadow:0 8px 28px rgba(24,160,88,.15)}
.card-check::before{background:linear-gradient(90deg,#d48806,#fbbf24)}
.card-check:hover{box-shadow:0 8px 28px rgba(212,136,6,.15)}
.card-merge::before{background:linear-gradient(90deg,#7c3aed,#a78bfa)}
.card-merge:hover{box-shadow:0 8px 28px rgba(124,58,237,.15)}
.card-jira::before{background:linear-gradient(90deg,#e53e3e,#fc8181)}
.card-jira:hover{box-shadow:0 8px 28px rgba(229,62,62,.15)}

.card-icon{font-size:9px;font-weight:800;letter-spacing:.08em;font-family:'DM Mono',monospace;display:inline-flex;align-items:center;justify-content:center;width:36px;height:22px;border-radius:5px;margin-bottom:2px}
.ci-wbs{background:rgba(53,99,233,.12);color:#3563E9}
.ci-cal{background:rgba(24,160,88,.12);color:#18a058}
.ci-chk{background:rgba(212,136,6,.12);color:#d48806}
.ci-mrg{background:rgba(124,58,237,.12);color:#7c3aed}
.ci-jra{background:rgba(229,62,62,.12);color:#e53e3e}
.card-content{flex:1}
.card-num{font-size:10px;font-family:'DM Mono',monospace;color:var(--muted);letter-spacing:.1em;margin-bottom:6px}
.card-title{font-size:14px;font-weight:700;color:var(--text);margin-bottom:6px;line-height:1.3}
.card-desc{font-size:12px;color:var(--muted);line-height:1.65;word-break:keep-all}
.card-arrow{font-size:16px;color:var(--muted);align-self:flex-end;transition:all .2s;opacity:0;transform:translateX(-4px)}
.home-card:hover .card-arrow{opacity:1;transform:translateX(0)}

/* ── 서버 깨우기 오버레이 ── */
.waking-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(6px);z-index:500;display:flex;align-items:center;justify-content:center}
.waking-box{background:var(--bg2);border:1px solid var(--border2);border-radius:16px;padding:44px 56px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:16px}
.waking-spinner{width:36px;height:36px;border:2px solid var(--border2);border-top-color:var(--primary);border-radius:50%;animation:spin 1s linear infinite}
.waking-title{font-size:16px;font-weight:600;color:var(--text)}
.waking-sub{font-size:12px;color:var(--muted)}
.waking-dots{display:flex;gap:5px}
.waking-dots span{width:7px;height:7px;border-radius:50%;background:var(--primary);animation:dot-bounce .8s infinite alternate}
.waking-dots span:nth-child(2){animation-delay:.2s}
.waking-dots span:nth-child(3){animation-delay:.4s}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes dot-bounce{from{opacity:.3;transform:scale(.8)}to{opacity:1;transform:scale(1)}}

/* ── 토스트 ── */
.toast-wrap{position:fixed;bottom:24px;right:24px;z-index:400;display:flex;flex-direction:column;gap:8px}
.toast{background:var(--bg2);border:1px solid var(--border2);border-radius:9px;padding:12px 18px;font-size:13px;animation:slideIn .2s ease;min-width:240px;line-height:1.5;color:var(--text);box-shadow:0 2px 12px rgba(0,0,0,.1)}
.toast-ok{border-left:3px solid var(--green)}
.toast-err{border-left:3px solid var(--red)}
.toast-info{border-left:3px solid var(--blue)}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}

/* 반응형 */
@media(max-width:1024px){
  .home-cards{grid-template-columns:repeat(3,1fr)}
  .home-title{font-size:40px}
}
@media(max-width:640px){
  .home-inner{padding:40px 20px 60px}
  .home-cards{grid-template-columns:1fr 1fr}
  .home-title{font-size:32px}
}
</style>