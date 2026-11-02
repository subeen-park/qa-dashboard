<template>
  <div class="auto-page">
    <!-- Header -->
    <section class="auto-header">
      <div class="ah-inner">
        <div class="ah-left">
          <div class="ah-eyebrow">Automation Test</div>
          <h1 class="ah-title">실제 돌아가는 자동화 테스트 콘솔</h1>
          <p class="ah-sub">
            Playwright 기반 웹 자동화 러너. TC를 선택해 Run을 누르면 서버에서 Chromium을
            띄워 실제 사이트를 조종하고, 각 스텝의 스크린샷이 500ms마다 라이브로 전송됩니다.
          </p>
        </div>
        <div class="ah-stats">
          <div class="stat-tile">
            <div class="st-ic" style="background:#DBEAFE;color:#1E40AF">TC</div>
            <div><div class="st-v mono">{{ testcases.length }}</div><div class="st-l">TC 등록</div></div>
          </div>
          <div class="stat-tile">
            <div class="st-ic" style="background:#D1FAE5;color:#065F46">P</div>
            <div><div class="st-v mono">{{ passCount }}</div><div class="st-l">최근 Pass</div></div>
          </div>
          <div class="stat-tile">
            <div class="st-ic" style="background:#FEE2E2;color:#991B1B">F</div>
            <div><div class="st-v mono">{{ failCount }}</div><div class="st-l">최근 Fail</div></div>
          </div>
          <div class="stat-tile">
            <div class="st-ic" style="background:#FEF3C7;color:#92400E">%</div>
            <div><div class="st-v mono">{{ passRate }}%</div><div class="st-l">성공률</div></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Testcase List -->
    <section class="section-wrap">
      <div class="sec-inner">
        <div class="sec-head">
          <div>
            <h2 class="sec-title">테스트 케이스</h2>
            <p class="sec-sub">DB에서 로드. Run 버튼으로 Playwright 러너 즉시 실행.</p>
          </div>
          <button class="btn-refresh" @click="loadAll" :disabled="loading">
            <span :class="{spinning: loading}">↻</span>
            {{ loading ? '로딩 중...' : '새로고침' }}
          </button>
        </div>

        <div class="tc-table" v-if="testcases.length">
          <div class="tc-head">
            <div>ID</div>
            <div>제목</div>
            <div>카테고리</div>
            <div>Priority</div>
            <div>예상 결과</div>
            <div class="tc-actions-head">실행</div>
          </div>
          <div class="tc-row" v-for="tc in testcases" :key="tc.id">
            <div class="tc-id mono">{{ tc.id }}</div>
            <div class="tc-title-cell">
              <div class="tc-title">{{ tc.title }}</div>
              <div class="tc-desc">{{ tc.description }}</div>
            </div>
            <div><span class="chip" :class="'chip-cat-'+tc.category">{{ tc.category }}</span></div>
            <div><span class="chip-prio" :class="'prio-'+(tc.priority||'').toLowerCase()">{{ tc.priority }}</span></div>
            <div>
              <span class="chip-expected" :class="'exp-'+tc.expected_result">
                {{ tc.expected_result === 'pass' ? 'PASS' : 'FAIL' }}
              </span>
            </div>
            <div class="tc-actions">
              <button class="btn-run" @click="runTc(tc)" :disabled="activeRun != null">
                ▶ Run
              </button>
            </div>
          </div>
        </div>
        <div v-else-if="loading" class="empty-state">로딩 중...</div>
        <div v-else class="empty-state">
          TC가 없거나 API를 불러올 수 없어요.
          <div class="es-sub">백엔드 서버가 켜져 있는지 확인하세요 ({{ API_BASE }})</div>
        </div>
      </div>
    </section>

    <!-- Run History -->
    <section class="section-wrap">
      <div class="sec-inner">
        <div class="sec-head">
          <h2 class="sec-title">최근 실행 이력</h2>
        </div>
        <div class="hist-table" v-if="runs.length">
          <div class="hist-head">
            <div>Run #</div>
            <div>TC</div>
            <div>상태</div>
            <div>소요</div>
            <div>시작 시각</div>
            <div>-</div>
          </div>
          <div class="hist-row" v-for="run in runs" :key="run.id">
            <div class="mono"># {{ run.id }}</div>
            <div>
              <div class="hist-tc-id mono">{{ run.tc_id }}</div>
              <div class="hist-tc-title">{{ run.tc_title }}</div>
            </div>
            <div><span class="status-chip" :class="'st-'+run.status">{{ statusLabel(run.status) }}</span></div>
            <div class="mono">{{ run.duration_ms ? (run.duration_ms/1000).toFixed(2) + 's' : '-' }}</div>
            <div class="mono hist-time">{{ fmtTime(run.started_at) }}</div>
            <div>
              <button class="btn-detail" @click="viewRun(run.id)">상세</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          실행 이력이 없어요. 위에서 TC Run 눌러보세요.
        </div>
      </div>
    </section>

    <!-- Runner Modal (라이브 뷰) -->
    <div v-if="activeRun || runnerModal" class="modal-overlay" @click.self="closeRunnerModal">
      <div class="runner-modal">
        <div class="rm-head">
          <div class="rm-title">
            <span class="rm-dot" :class="'dot-'+(runnerModal && runnerModal.status || 'running')"></span>
            <span class="rm-run-id mono">Run #{{ runnerModal && runnerModal.id || '-' }}</span>
            <span>·</span>
            <span>{{ runnerModal && runnerModal.tc_title || activeTc && activeTc.title }}</span>
          </div>
          <button class="rm-close" @click="closeRunnerModal" :disabled="activeRun && !isDone">
            {{ activeRun && !isDone ? '실행 중...' : '×' }}
          </button>
        </div>

        <div class="rm-body">
          <!-- 좌측: 라이브 스크린샷 -->
          <div class="rm-screenshot">
            <div class="ss-head">
              <div class="ss-label">
                <span class="ss-live-dot" v-if="activeRun && !isDone"></span>
                {{ activeRun && !isDone ? 'LIVE' : '완료' }}
              </div>
              <div class="ss-ts mono">{{ screenshotTs }}</div>
            </div>
            <div class="ss-frame">
              <img v-if="screenshotUrl" :src="screenshotUrl" class="ss-img" @error="onImgError" />
              <div v-else class="ss-placeholder">
                <div class="ss-ph-icon">📸</div>
                <div>스크린샷 대기 중...</div>
              </div>
            </div>
            <div class="ss-meta mono" v-if="runnerModal">
              <div><span class="ss-k">상태:</span> {{ runnerModal.status }}</div>
              <div v-if="runnerModal.duration_ms"><span class="ss-k">소요:</span> {{ (runnerModal.duration_ms/1000).toFixed(2) }}s</div>
            </div>
          </div>

          <!-- 우측: 스텝 리스트 -->
          <div class="rm-steps">
            <div class="rm-steps-head">
              스텝 진행 상황
              <span class="step-counter mono">
                {{ completedSteps }} / {{ totalSteps }}
              </span>
            </div>
            <div class="step-list">
              <div
                v-for="(step, i) in displaySteps" :key="i"
                class="step-item"
                :class="'step-'+step.status"
              >
                <div class="step-ic">
                  <span v-if="step.status === 'pass'">✓</span>
                  <span v-else-if="step.status === 'fail'">✗</span>
                  <span v-else-if="step.status === 'running'" class="step-spin"></span>
                  <span v-else>○</span>
                </div>
                <div class="step-body">
                  <div class="step-top">
                    <span class="step-action mono">[{{ step.action }}]</span>
                    <span class="step-dur mono" v-if="step.duration_ms">{{ step.duration_ms }}ms</span>
                  </div>
                  <div class="step-desc">{{ step.description || '(no description)' }}</div>
                  <div v-if="step.error" class="step-error mono">
                    Error: {{ step.error }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 완료 요약 -->
            <div v-if="isDone && runnerModal" class="rm-summary" :class="'summary-'+runnerModal.status">
              <div class="sum-head">
                <span v-if="runnerModal.status === 'pass'">✅ 테스트 통과</span>
                <span v-else-if="runnerModal.status === 'fail'">❌ 테스트 실패</span>
                <span v-else>⚠ 오류 발생</span>
              </div>
              <div v-if="runnerModal.status === 'fail' && runnerModal.tc_expected === 'fail'" class="sum-note">
                ✨ 의도된 실패 — 자동화가 실제 이슈를 정확히 검출했습니다
              </div>
              <div v-if="runnerModal.error_message" class="sum-err mono">
                {{ runnerModal.error_message }}
              </div>
              <div class="sum-actions" v-if="runnerModal.video_path">
                <a :href="videoUrl" target="_blank" class="btn-video">🎬 녹화 영상 보기</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default {
  name: 'AutomationTest',
  data() {
    return {
      API_BASE,
      testcases: [],
      runs: [],
      loading: false,
      activeRun: null,
      activeTc: null,
      runnerModal: null,
      runPollTimer: null,
      ssPollTimer: null,
      screenshotUrl: '',
      screenshotTs: '',
    }
  },
  computed: {
    passCount() { return this.runs.filter(r => r.status === 'pass').length },
    failCount() { return this.runs.filter(r => r.status === 'fail').length },
    passRate() {
      const total = this.passCount + this.failCount
      if (total === 0) return 0
      return Math.round((this.passCount / total) * 100)
    },
    isDone() {
      return this.runnerModal && ['pass', 'fail', 'error'].includes(this.runnerModal.status)
    },
    displaySteps() {
      const tcSteps = (this.activeTc && this.activeTc.steps) || (this.runnerModal && this.runnerModal.steps) || []
      const results = (this.runnerModal && this.runnerModal.step_results) || []
      return tcSteps.map((s, i) => {
        const r = results[i]
        if (r) return { ...s, ...r, status: r.status, duration_ms: r.duration_ms }
        const isCurrent = this.activeRun && results.length === i
        return { ...s, status: isCurrent ? 'running' : 'pending' }
      })
    },
    totalSteps() { return this.displaySteps.length },
    completedSteps() { return this.displaySteps.filter(s => ['pass', 'fail'].includes(s.status)).length },
    videoUrl() {
      if (!this.runnerModal || !this.runnerModal.video_path) return null
      const filename = this.runnerModal.video_path.split('/').pop()
      return `${API_BASE}/api/output/videos/${filename}`
    },
  },
  async mounted() {
    await this.loadAll()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        await Promise.all([this.loadTestcases(), this.loadRuns()])
      } finally {
        this.loading = false
      }
    },
    async loadTestcases() {
      try {
        const res = await fetch(`${API_BASE}/api/testcases`)
        this.testcases = await res.json()
      } catch (e) {
        console.error('loadTestcases failed:', e)
        this.testcases = []
      }
    },
    async loadRuns() {
      try {
        const res = await fetch(`${API_BASE}/api/test-runs?limit=30`)
        this.runs = await res.json()
      } catch (e) {
        console.error('loadRuns failed:', e)
        this.runs = []
      }
    },
    async runTc(tc) {
      this.activeTc = tc
      this.runnerModal = {
        id: '-',
        status: 'queued',
        tc_title: tc.title,
        step_results: [],
        steps: tc.steps,
      }
      try {
        const res = await fetch(`${API_BASE}/api/testcases/${tc.id}/run`, { method: 'POST' })
        const data = await res.json()
        this.activeRun = data.run_id
        this.runnerModal.id = data.run_id
        this.runnerModal.status = 'running'
        this.startPolling()
      } catch (e) {
        console.error('runTc failed:', e)
        this.runnerModal.status = 'error'
        this.runnerModal.error_message = e.message
      }
    },
    startPolling() {
      this.runPollTimer = setInterval(this.pollRun, 1000)
      this.ssPollTimer = setInterval(this.pollScreenshot, 500)
    },
    stopPolling() {
      if (this.runPollTimer) clearInterval(this.runPollTimer)
      if (this.ssPollTimer) clearInterval(this.ssPollTimer)
      this.runPollTimer = null
      this.ssPollTimer = null
    },
    async pollRun() {
      if (!this.activeRun) return
      try {
        const res = await fetch(`${API_BASE}/api/test-runs/${this.activeRun}`)
        const run = await res.json()
        this.runnerModal = { ...this.runnerModal, ...run }
        if (['pass', 'fail', 'error'].includes(run.status)) {
          this.stopPolling()
          this.activeRun = null
          await this.loadRuns()
        }
      } catch (e) {
        console.error('pollRun failed:', e)
      }
    },
    pollScreenshot() {
      if (!this.activeRun) return
      this.screenshotUrl = `${API_BASE}/api/test-runs/${this.activeRun}/latest-screenshot?t=${Date.now()}`
      const d = new Date()
      const pad = n => n.toString().padStart(2,'0')
      this.screenshotTs = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
    },
    onImgError() { /* 스크린샷 아직 없음 - 무시 */ },
    async viewRun(runId) {
      try {
        const res = await fetch(`${API_BASE}/api/test-runs/${runId}`)
        const run = await res.json()
        const tc = this.testcases.find(t => t.id === run.tc_id)
        this.activeTc = tc || null
        this.runnerModal = { ...run, steps: (tc && tc.steps) || [] }
        this.screenshotUrl = ''
        if (run.step_results && run.step_results.length) {
          const lastIdx = run.step_results.length
          const padded = String(lastIdx).padStart(2, '0')
          this.screenshotUrl = `${API_BASE}/api/output/screenshots/${runId}/step_${padded}.png`
        }
      } catch (e) {
        console.error('viewRun failed:', e)
      }
    },
    closeRunnerModal() {
      if (this.activeRun && !this.isDone) return
      this.runnerModal = null
      this.activeTc = null
      this.screenshotUrl = ''
    },
    statusLabel(s) {
      const map = { queued: '대기', running: '실행 중', pass: '통과', fail: '실패', error: '오류' }
      return map[s] || s
    },
    fmtTime(iso) {
      if (!iso) return '-'
      const d = new Date(iso)
      const pad = n => n.toString().padStart(2, '0')
      return `${pad(d.getMonth()+1)}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
    },
  },
}
</script>

<style scoped>
.auto-page { padding-top: 68px; min-height: 100vh; background: #fafbfc; }
.mono { font-family: 'JetBrains Mono', monospace; }

.auto-header { padding: 48px 32px 32px; background: linear-gradient(180deg, #fff 0%, #fafbfc 100%); border-bottom: 1px solid #E5E8EB; }
.ah-inner { max-width: 1240px; margin: 0 auto; display: grid; grid-template-columns: 1.3fr 1fr; gap: 48px; align-items: center; }
.ah-eyebrow { font-size: 12px; font-weight: 700; color: #0064FF; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 12px; }
.ah-title { font-size: 32px; font-weight: 900; letter-spacing: -.03em; color: #0F172A; margin-bottom: 14px; word-break: keep-all; }
.ah-sub { font-size: 14px; line-height: 1.75; color: #334155; word-break: keep-all; }
.ah-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.stat-tile { background: #fff; border: 1px solid #E5E8EB; border-radius: 10px; padding: 14px; display: flex; align-items: center; gap: 10px; }
.st-ic { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; }
.st-v { font-size: 20px; font-weight: 800; color: #0F172A; letter-spacing: -.02em; }
.st-l { font-size: 11px; color: #64748B; font-weight: 500; margin-top: 2px; }

.section-wrap { padding: 32px; }
.sec-inner { max-width: 1240px; margin: 0 auto; }
.sec-head { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px; }
.sec-title { font-size: 20px; font-weight: 800; color: #0F172A; letter-spacing: -.02em; }
.sec-sub { font-size: 13px; color: #64748B; margin-top: 4px; }
.btn-refresh { background: #fff; border: 1px solid #E5E8EB; padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; color: #334155; font-family: inherit; display: flex; align-items: center; gap: 6px; }
.btn-refresh:hover { background: #f6f7f9; }
.spinning { display: inline-block; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.tc-table { background: #fff; border: 1px solid #E5E8EB; border-radius: 12px; overflow: hidden; }
.tc-head, .tc-row { display: grid; grid-template-columns: 100px 2fr 100px 80px 100px 120px; gap: 16px; padding: 14px 20px; align-items: center; }
.tc-head { background: #f9fafc; border-bottom: 1px solid #E5E8EB; font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.tc-actions-head { text-align: center; }
.tc-row { border-bottom: 1px solid #f1f3f5; transition: background .15s; }
.tc-row:last-child { border-bottom: none; }
.tc-row:hover { background: #fafbfc; }
.tc-id { font-size: 13px; font-weight: 700; color: #0F172A; }
.tc-title-cell { min-width: 0; }
.tc-title { font-size: 14px; font-weight: 700; color: #0F172A; margin-bottom: 2px; }
.tc-desc { font-size: 12px; color: #64748B; line-height: 1.5; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.tc-actions { display: flex; justify-content: center; }
.btn-run { background: #0064FF; color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit; }
.btn-run:hover:not(:disabled) { background: #0051d3; }
.btn-run:disabled { background: #CBD5E1; cursor: not-allowed; }

.chip { display: inline-block; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 700; letter-spacing: -.01em; }
.chip-cat-smoke { background: #DBEAFE; color: #1E40AF; }
.chip-cat-regression { background: #FEF3C7; color: #92400E; }
.chip-cat-e2e { background: #E0E7FF; color: #4338CA; }
.chip-prio { display: inline-block; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
.prio-p1 { background: #FEE2E2; color: #991B1B; }
.prio-p2 { background: #FEF3C7; color: #92400E; }
.prio-p3 { background: #E5E7EB; color: #374151; }
.chip-expected { display: inline-block; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: 700; }
.exp-pass { background: #D1FAE5; color: #065F46; }
.exp-fail { background: #FEE2E2; color: #991B1B; }

.hist-table { background: #fff; border: 1px solid #E5E8EB; border-radius: 12px; overflow: hidden; }
.hist-head, .hist-row { display: grid; grid-template-columns: 80px 2fr 110px 80px 160px 80px; gap: 16px; padding: 12px 20px; align-items: center; }
.hist-head { background: #f9fafc; border-bottom: 1px solid #E5E8EB; font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.hist-row { border-bottom: 1px solid #f1f3f5; font-size: 13px; }
.hist-row:last-child { border-bottom: none; }
.hist-tc-id { font-size: 11px; color: #64748B; }
.hist-tc-title { font-size: 13px; color: #0F172A; font-weight: 600; }
.hist-time { font-size: 11px; color: #64748B; }
.status-chip { display: inline-block; padding: 3px 10px; border-radius: 5px; font-size: 11px; font-weight: 700; }
.st-pass { background: #D1FAE5; color: #065F46; }
.st-fail { background: #FEE2E2; color: #991B1B; }
.st-error { background: #FEF3C7; color: #92400E; }
.st-running { background: #DBEAFE; color: #1E40AF; }
.st-queued { background: #F1F5F9; color: #475569; }
.btn-detail { background: #f6f7f9; border: 1px solid #E5E8EB; padding: 5px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; font-family: inherit; color: #334155; }
.btn-detail:hover { background: #eef0f3; }

.empty-state { padding: 60px 20px; text-align: center; background: #fff; border: 1px dashed #E5E8EB; border-radius: 12px; color: #64748B; font-size: 14px; }
.es-sub { font-size: 12px; margin-top: 8px; color: #94A3B8; }

.modal-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(15,23,42,.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; padding: 20px; animation: fadeIn .2s; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.runner-modal { background: #fff; border-radius: 16px; max-width: 1100px; width: 100%; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; animation: slideUp .25s; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.rm-head { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #E5E8EB; }
.rm-title { display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 700; color: #0F172A; }
.rm-dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-running { background: #0064FF; box-shadow: 0 0 8px #0064FF; animation: pulse 1.5s infinite; }
.dot-pass { background: #06C755; }
.dot-fail { background: #F04452; }
.dot-error { background: #F59E0B; }
.dot-queued { background: #94A3B8; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .4; } }
.rm-run-id { font-size: 13px; color: #64748B; }
.rm-close { background: #f6f7f9; border: none; padding: 6px 12px; min-width: 40px; height: 32px; border-radius: 8px; font-size: 16px; cursor: pointer; color: #64748B; font-family: inherit; }
.rm-close:hover:not(:disabled) { background: #eef0f3; color: #0F172A; }
.rm-close:disabled { opacity: .5; cursor: not-allowed; font-size: 11px; }

.rm-body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 20px; padding: 20px 24px; overflow-y: auto; }

.rm-screenshot { display: flex; flex-direction: column; gap: 10px; }
.ss-head { display: flex; justify-content: space-between; align-items: center; }
.ss-label { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 800; color: #0F172A; letter-spacing: .05em; }
.ss-live-dot { width: 7px; height: 7px; background: #F04452; border-radius: 50%; animation: pulse 1s infinite; }
.ss-ts { font-size: 11px; color: #64748B; }
.ss-frame { background: #0F172A; border-radius: 10px; aspect-ratio: 16 / 9; overflow: hidden; display: flex; align-items: center; justify-content: center; }
.ss-img { width: 100%; height: 100%; object-fit: contain; }
.ss-placeholder { color: #64748B; text-align: center; font-size: 13px; }
.ss-ph-icon { font-size: 36px; margin-bottom: 8px; opacity: .5; }
.ss-meta { display: flex; gap: 16px; font-size: 11px; color: #334155; padding: 10px 14px; background: #f9fafc; border-radius: 8px; }
.ss-k { color: #64748B; }

.rm-steps { display: flex; flex-direction: column; }
.rm-steps-head { font-size: 13px; font-weight: 700; color: #0F172A; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
.step-counter { font-size: 11px; color: #64748B; background: #f1f3f5; padding: 2px 8px; border-radius: 10px; }
.step-list { display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto; padding-right: 4px; }
.step-item { display: flex; gap: 10px; padding: 10px 12px; border-radius: 8px; background: #f9fafc; border: 1px solid transparent; }
.step-pass { background: #F0FDF4; border-color: #BBF7D0; }
.step-fail { background: #FEF2F2; border-color: #FECACA; }
.step-running { background: #EFF6FF; border-color: #BFDBFE; }
.step-pending { opacity: .5; }
.step-ic { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; flex-shrink: 0; margin-top: 1px; }
.step-pass .step-ic { background: #06C755; color: #fff; }
.step-fail .step-ic { background: #F04452; color: #fff; }
.step-running .step-ic { background: #0064FF; color: #fff; }
.step-pending .step-ic { background: #CBD5E1; color: #fff; }
.step-spin { display: inline-block; width: 10px; height: 10px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin .7s linear infinite; }
.step-body { flex: 1; min-width: 0; }
.step-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
.step-action { font-size: 10px; color: #64748B; font-weight: 700; }
.step-dur { font-size: 10px; color: #64748B; }
.step-desc { font-size: 12px; color: #0F172A; font-weight: 500; word-break: break-all; }
.step-error { font-size: 10px; color: #991B1B; margin-top: 4px; background: rgba(240,68,82,.08); padding: 4px 6px; border-radius: 4px; word-break: break-all; }

.rm-summary { margin-top: 16px; padding: 16px; border-radius: 10px; border: 1px solid; }
.summary-pass { background: #F0FDF4; border-color: #BBF7D0; }
.summary-fail { background: #FEF2F2; border-color: #FECACA; }
.summary-error { background: #FEF3C7; border-color: #FDE68A; }
.sum-head { font-size: 14px; font-weight: 800; color: #0F172A; margin-bottom: 6px; }
.sum-note { font-size: 12px; color: #065F46; background: #D1FAE5; padding: 8px 10px; border-radius: 6px; margin-top: 6px; font-weight: 600; }
.sum-err { font-size: 11px; color: #991B1B; margin-top: 6px; background: rgba(240,68,82,.08); padding: 6px 8px; border-radius: 4px; word-break: break-all; }
.sum-actions { margin-top: 10px; }
.btn-video { display: inline-flex; align-items: center; gap: 6px; background: #0F172A; color: #fff; text-decoration: none; padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 700; }
.btn-video:hover { background: #1e293b; }

@media (max-width: 1024px) {
  .ah-inner { grid-template-columns: 1fr; }
  .rm-body { grid-template-columns: 1fr; }
  .tc-head, .tc-row { grid-template-columns: 80px 2fr 90px 70px 90px 100px; font-size: 12px; }
  .hist-head, .hist-row { grid-template-columns: 60px 1.5fr 90px 70px 130px 70px; }
}
</style>