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

    <!-- 2-column grid -->
    <section class="section-wrap">
      <div class="auto-grid">

        <!-- 좌측 -->
        <div class="auto-left">
          <!-- TC 목록 -->
          <div class="panel">
            <div class="sec-head">
              <div>
                <h2 class="sec-title">테스트 케이스</h2>
                <p class="sec-sub">DB에서 로드. Run 버튼으로 Playwright 러너 즉시 실행.</p>
              </div>
              <div class="sec-actions">
                <button class="btn-ai" @click="showAiModal = true">
                  <span class="sparkle">✦</span>
                  AI로 TC 생성
                </button>
                <button class="btn-refresh" @click="loadAll" :disabled="loading">
                  <span :class="{spinning: loading}">↻</span>
                  {{ loading ? '로딩' : '새로고침' }}
                </button>
              </div>
            </div>
            <!-- Level 필터 탭 -->
            <div class="level-tabs">
              <button
                v-for="t in LEVEL_TABS" :key="t.k"
                class="lv-tab" :class="{active: levelFilter === t.k, ['lv-' + t.k.toLowerCase()]: true}"
                @click="levelFilter = t.k"
              >
                {{ t.label }}
                <span class="lv-count">{{ levelCounts[t.k] || 0 }}</span>
              </button>
            </div>

            <div class="tc-table" v-if="filteredTestcases.length">
              <div class="tc-head">
                <div>ID</div>
                <div>제목</div>
                <div>Level</div>
                <div>카테고리</div>
                <div>예상</div>
                <div class="tc-actions-head">액션</div>
              </div>
              <div class="tc-row" v-for="tc in filteredTestcases" :key="tc.id">
                <div class="tc-id mono">
                  <span v-if="tc.id.startsWith('TC-AI-')" class="tc-ai-tag">✦ AI</span>
                  {{ tc.id }}
                </div>
                <div class="tc-title-cell">
                  <div class="tc-title">{{ tc.title }}</div>
                  <div class="tc-desc">{{ tc.description }}</div>
                </div>
                <div><span class="chip-level" :class="'lvchip-'+(tc.level||'Smoke').toLowerCase()">{{ tc.level || 'Smoke' }}</span></div>
                <div><span class="chip-domain">{{ tc.category || '-' }}</span></div>
                <div>
                  <span class="chip-expected" :class="'exp-'+tc.expected_result">
                    {{ tc.expected_result === 'pass' ? 'PASS' : 'FAIL' }}
                  </span>
                </div>
                <div class="tc-actions">
                  <button class="btn-run" @click="runTc(tc)" :disabled="activeRun != null" title="실행">▶</button>
                  <button class="btn-edit" @click="openEditModal(tc)" title="수정">✎</button>
                  <button class="btn-delete" @click="confirmDelete(tc)" title="삭제">🗑</button>
                </div>
              </div>
            </div>
            <div v-else-if="loading" class="empty-state">로딩 중...</div>
            <div v-else-if="testcases.length === 0" class="empty-state">
              TC가 없거나 API를 불러올 수 없어요.
              <div class="es-sub">백엔드 서버가 켜져 있는지 확인하세요</div>
            </div>
            <div v-else class="empty-state">
              <strong>{{ levelFilter }}</strong> 레벨의 TC가 없어요.
              <div class="es-sub">다른 Level 탭을 선택하거나 ✦ AI로 TC 생성 하세요</div>
            </div>
          </div>

          <!-- 최근 실행 이력 -->
          <div class="panel">
            <div class="sec-head">
              <h2 class="sec-title">최근 실행 이력</h2>
            </div>
            <div class="hist-table" v-if="runs.length">
              <div class="hist-head">
                <div>Run #</div>
                <div>TC</div>
                <div>상태</div>
                <div>소요</div>
                <div>시각</div>
                <div>-</div>
              </div>
              <div class="hist-row" v-for="run in runs" :key="run.id">
                <div class="mono"># {{ run.id }}</div>
                <div>
                  <div class="hist-tc-id mono">{{ run.tc_id }}</div>
                  <div class="hist-tc-title">{{ run.tc_title }}</div>
                </div>
                <div><span class="status-chip" :class="'st-'+run.status">{{ statusLabel(run.status) }}</span></div>
                <div class="mono">{{ run.duration_ms ? (run.duration_ms/1000).toFixed(1) + 's' : '-' }}</div>
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
        </div>

        <!-- 우측 Run 패널 (sticky) -->
        <div class="auto-right">
          <div class="run-panel-wrap">
            <!-- Run 뷰 -->
            <div v-if="runnerModal" class="run-panel">
              <div class="rp-head">
                <div class="rp-title">
                  <span class="rp-dot" :class="'dot-'+(runnerModal.status || 'running')"></span>
                  <span class="rp-run-id mono">Run #{{ runnerModal.id || '-' }}</span>
                </div>
                <button class="rp-close" @click="handleClose" title="닫기">×</button>
              </div>
              <div class="rp-tc-title">{{ runnerModal.tc_title || (activeTc && activeTc.title) }}</div>

              <!-- 라이브 스크린샷 -->
              <div class="rp-screenshot">
                <div class="ss-head">
                  <div class="ss-label">
                    <span class="ss-live-dot" v-if="activeRun && !isDone"></span>
                    {{ activeRun && !isDone ? 'LIVE' : '완료' }}
                  </div>
                  <div class="ss-ts mono">{{ screenshotTs }}</div>
                </div>
                <div class="ss-frame">
                  <img
                    v-show="screenshotLoaded"
                    :src="screenshotUrl"
                    class="ss-img"
                    @load="onImgLoad"
                    @error="onImgError"
                  />
                  <div v-if="!screenshotLoaded" class="ss-placeholder">
                    <div class="ss-ph-spinner"></div>
                    <div v-if="activeRun && !isDone">테스트 진행 중...</div>
                    <div v-else>스크린샷 대기 중...</div>
                    <div class="ss-ph-sub" v-if="activeRun && !isDone">Chromium 로드 + 스텝 실행 중</div>
                  </div>
                </div>
                <div class="ss-meta mono">
                  <div><span class="ss-k">상태:</span> {{ runnerModal.status }}</div>
                  <div v-if="runnerModal.duration_ms"><span class="ss-k">소요:</span> {{ (runnerModal.duration_ms/1000).toFixed(2) }}s</div>
                </div>
              </div>

              <!-- 스텝 리스트 -->
              <div class="rp-steps">
                <div class="rp-steps-head">
                  스텝 진행 상황
                  <span class="step-counter mono">{{ completedSteps }} / {{ totalSteps }}</span>
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
                      <div class="step-desc">{{ step.description || stepLabel(step) }}</div>
                      <div v-if="step.error" class="step-error mono">
                        Error: {{ step.error }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 실행 중 안내 -->
                <div v-if="activeRun && !isDone" class="rp-bg-note">
                  💡 창을 닫아도 테스트는 백그라운드에서 계속 실행돼요.
                </div>

                <!-- 완료 요약 -->
                <div v-if="isDone && runnerModal" class="rp-summary" :class="'summary-'+runnerModal.status">
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
                </div>
              </div>
            </div>

            <!-- Empty state -->
            <div v-else class="run-empty">
              <div class="re-icon">▶</div>
              <div class="re-title">TC를 선택해 Run을 눌러보세요</div>
              <div class="re-sub">왼쪽 테스트 케이스에서 ▶ Run 버튼을 누르면 여기에<br>라이브 뷰가 뜹니다.</div>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- AI TC 생성 모달 -->
    <div v-if="showAiModal" class="ai-overlay" @click.self="closeAiModal">
      <div class="ai-modal">
        <div class="ai-head">
          <div class="ai-head-left">
            <div class="ai-icon">✦</div>
            <div>
              <div class="ai-title">AI로 TC 생성</div>
              <div class="ai-sub">자연어 요청 → Gemini 2.0 Flash → Playwright TC JSON → 자동 저장</div>
            </div>
          </div>
          <button class="ai-close" @click="closeAiModal">×</button>
        </div>

        <div class="ai-body">
          <div class="ai-field">
            <label>대상 URL</label>
            <input v-model="aiForm.url" placeholder="https://www.saucedemo.com" />
          </div>
          <div class="ai-field">
            <label>테스트하고 싶은 시나리오 (자연어)</label>
            <textarea
              v-model="aiForm.description"
              rows="4"
              placeholder="예: 유효한 standard_user 계정으로 로그인한 뒤 백팩 상품을 장바구니에 담아서 뱃지가 1로 뜨는지 검증"
            ></textarea>
          </div>
          <div class="ai-field">
            <label>Level (테스트 티어)</label>
            <div class="level-radio-group">
              <label v-for="opt in LEVEL_OPTIONS" :key="opt.value" class="level-radio" :class="{active: aiForm.level === opt.value}">
                <input type="radio" v-model="aiForm.level" :value="opt.value" />
                <div class="lr-main">{{ opt.value }}</div>
                <div class="lr-desc">{{ opt.desc }}</div>
              </label>
            </div>
          </div>
          <div class="ai-field ai-field-row">
            <div>
              <label>Category (도메인)</label>
              <select v-model="aiForm.category">
                <option v-for="d in DOMAIN_OPTIONS" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            <div class="ai-mode-pill" :class="'mode-' + aiMode">
              <span class="mode-dot"></span>
              {{ aiMode === 'gemini' ? 'Gemini 2.0 Flash' : 'Demo Mode (키 없음)' }}
            </div>
          </div>

          <div v-if="aiError" class="ai-error">{{ aiError }}</div>

          <div v-if="aiResult" class="ai-result">
            <div class="ai-result-head">
              <span class="ai-result-badge">생성됨</span>
              <span class="ai-result-title">{{ aiResult.title }}</span>
            </div>
            <div class="ai-result-meta mono">
              {{ aiResult.id }} · {{ aiResult.category }} · {{ aiResult.priority }} · {{ aiResult.steps.length }} steps
            </div>
            <div class="ai-result-note">왼쪽 TC 목록에 추가되었어요. Run 눌러서 바로 실행 가능.</div>
          </div>
        </div>

        <div class="ai-foot">
          <button class="ai-btn ai-btn-ghost" @click="closeAiModal">닫기</button>
          <button
            class="ai-btn ai-btn-primary"
            @click="runAiGenerate"
            :disabled="aiGenerating || !aiForm.url || !aiForm.description"
          >
            <span v-if="aiGenerating" class="ai-spinner"></span>
            {{ aiGenerating ? '생성 중...' : '✦ 생성' }}
          </button>
        </div>
      </div>
    </div>

    <!-- TC 수정 모달 -->
    <div v-if="editTc" class="ai-overlay" @click.self="closeEditModal">
      <div class="ai-modal edit-modal">
        <div class="ai-head">
          <div class="ai-head-left">
            <div class="ai-icon edit-icon">✎</div>
            <div>
              <div class="ai-title">TC 수정 — <span class="mono">{{ editTc.id }}</span></div>
              <div class="ai-sub">제목·설명·분류·URL 수정 가능. steps 는 DB에서 직접 수정.</div>
            </div>
          </div>
          <button class="ai-close" @click="closeEditModal">×</button>
        </div>

        <div class="ai-body">
          <div class="ai-field">
            <label>제목</label>
            <input v-model="editForm.title" />
          </div>
          <div class="ai-field">
            <label>설명</label>
            <textarea v-model="editForm.description" rows="2"></textarea>
          </div>
          <div class="ai-field">
            <label>대상 URL</label>
            <input v-model="editForm.target_url" />
          </div>
          <div class="ai-field">
            <label>Level</label>
            <div class="level-radio-group">
              <label v-for="opt in LEVEL_OPTIONS" :key="opt.value" class="level-radio" :class="{active: editForm.level === opt.value}">
                <input type="radio" v-model="editForm.level" :value="opt.value" />
                <div class="lr-main">{{ opt.value }}</div>
                <div class="lr-desc">{{ opt.desc }}</div>
              </label>
            </div>
          </div>
          <div class="ai-field ai-field-row">
            <div>
              <label>Category (도메인)</label>
              <select v-model="editForm.category">
                <option v-for="d in DOMAIN_OPTIONS" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            <div>
              <label>Priority</label>
              <select v-model="editForm.priority">
                <option>P1</option>
                <option>P2</option>
                <option>P3</option>
              </select>
            </div>
            <div>
              <label>예상 결과</label>
              <select v-model="editForm.expected_result">
                <option value="pass">pass</option>
                <option value="fail">fail (의도된)</option>
              </select>
            </div>
          </div>
          <div v-if="editError" class="ai-error">{{ editError }}</div>
        </div>

        <div class="ai-foot">
          <button class="ai-btn ai-btn-ghost" @click="closeEditModal">취소</button>
          <button class="ai-btn ai-btn-primary" @click="saveEdit" :disabled="editSaving">
            <span v-if="editSaving" class="ai-spinner"></span>
            {{ editSaving ? '저장 중...' : '저장' }}
          </button>
        </div>
      </div>
    </div>

    <!-- TC 삭제 확인 모달 -->
    <div v-if="deleteTarget" class="ai-overlay" @click.self="deleteTarget = null">
      <div class="ai-modal delete-modal">
        <div class="ai-head">
          <div class="ai-head-left">
            <div class="ai-icon delete-icon">🗑</div>
            <div>
              <div class="ai-title">TC 삭제 확인</div>
              <div class="ai-sub">실행 이력도 함께 삭제됩니다. 되돌릴 수 없어요.</div>
            </div>
          </div>
        </div>
        <div class="ai-body">
          <div class="del-target">
            <div class="del-id mono">{{ deleteTarget.id }}</div>
            <div class="del-title">{{ deleteTarget.title }}</div>
          </div>
        </div>
        <div class="ai-foot">
          <button class="ai-btn ai-btn-ghost" @click="deleteTarget = null">취소</button>
          <button class="ai-btn ai-btn-danger" @click="performDelete" :disabled="deleteBusy">
            {{ deleteBusy ? '삭제 중...' : '삭제' }}
          </button>
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
      screenshotLoaded: false,
      confirmDialog: null,
      // Level 필터 + 상수
      levelFilter: 'all',
      LEVEL_TABS: [
        { k: 'all',        label: '전체' },
        { k: 'Smoke',      label: 'Smoke' },
        { k: 'Regression', label: 'Regression' },
        { k: 'E2E',        label: 'E2E' },
      ],
      LEVEL_OPTIONS: [
        { value: 'Smoke',      desc: '핵심 플로우 빠른 확인 (릴리즈 전 필수)' },
        { value: 'Regression', desc: '기존 기능 깨짐 없는지 전체 점검' },
        { value: 'E2E',        desc: '사용자 시나리오 끝에서 끝까지 검증' },
      ],
      DOMAIN_OPTIONS: [
        '로그인', '회원가입', '결제', '장바구니', '이미지', '검색',
        '알림', '마이페이지', '상품', '리뷰', '기타',
      ],
      // AI 생성 모달
      showAiModal: false,
      aiMode: 'demo',
      aiGenerating: false,
      aiResult: null,
      aiError: '',
      aiForm: {
        url: 'https://www.saucedemo.com',
        description: '',
        level: 'Smoke',
        category: '로그인',
      },
      // TC 수정 모달
      editTc: null,
      editForm: {
        title: '',
        description: '',
        target_url: '',
        level: 'Smoke',
        category: '기타',
        priority: 'P2',
        expected_result: 'pass',
      },
      editSaving: false,
      editError: '',
      // TC 삭제
      deleteTarget: null,
      deleteBusy: false,
    }
  },
  computed: {
    filteredTestcases() {
      if (this.levelFilter === 'all') return this.testcases
      return this.testcases.filter(tc => (tc.level || 'Smoke') === this.levelFilter)
    },
    levelCounts() {
      const counts = { all: this.testcases.length, Smoke: 0, Regression: 0, E2E: 0 }
      this.testcases.forEach(tc => {
        const lv = tc.level || 'Smoke'
        if (counts[lv] !== undefined) counts[lv]++
      })
      return counts
    },
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
  },
  async mounted() {
    await this.loadAll()
    await this.checkAiMode()
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
        this.testcases = []
      }
    },
    async loadRuns() {
      try {
        const res = await fetch(`${API_BASE}/api/test-runs?limit=30`)
        this.runs = await res.json()
      } catch (e) {
        this.runs = []
      }
    },
    async runTc(tc) {
      this.activeTc = tc
      this.screenshotUrl = ''
      this.screenshotLoaded = false
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
      } catch (e) {}
    },
    pollScreenshot() {
      if (!this.activeRun) return
      this.screenshotUrl = `${API_BASE}/api/test-runs/${this.activeRun}/latest-screenshot?t=${Date.now()}`
      const d = new Date()
      const pad = n => n.toString().padStart(2,'0')
      this.screenshotTs = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
    },
    onImgLoad() { this.screenshotLoaded = true },
    onImgError() { /* 이미 로드된 적 있으면 유지 */ },
    async viewRun(runId) {
      try {
        const res = await fetch(`${API_BASE}/api/test-runs/${runId}`)
        const run = await res.json()
        const tc = this.testcases.find(t => t.id === run.tc_id)
        this.activeTc = tc || null
        this.runnerModal = { ...run, steps: (tc && tc.steps) || [] }
        this.screenshotUrl = ''
        this.screenshotLoaded = false
        if (run.step_results && run.step_results.length) {
          const lastIdx = run.step_results.length
          const padded = String(lastIdx).padStart(2, '0')
          this.screenshotUrl = `${API_BASE}/api/output/screenshots/${runId}/step_${padded}.png`
        }
      } catch (e) {}
    },
    handleClose() {
      // 바로 닫음. 백엔드 러너는 백그라운드로 계속 돌아가서 결과 저장됨.
      this.closeRunnerPanel()
    },

    // ───────── 스텝 자동 설명 ─────────
    stepLabel(step) {
      const s = step || {}
      const sel = s.selector || ''
      switch (s.action) {
        case 'goto':            return `${s.url || ''} 로 이동`
        case 'fill':            return `${sel} 에 "${s.value || ''}" 입력`
        case 'click':           return `${sel} 클릭`
        case 'wait':            return `${s.ms || 0}ms 대기`
        case 'wait_for':        return `${sel} 요소 로드 대기`
        case 'assert_visible':  return `${sel} 노출 확인`
        case 'assert_text':     return `${sel} 에 "${s.expected || ''}" 포함 검증`
        case 'assert_url':      return `URL 에 "${s.expected || ''}" 포함 검증`
        case 'assert_attribute':return `${sel} 의 ${s.attribute || ''} 속성 검증`
        case 'screenshot':      return `스크린샷 저장`
        default:                return '(설명 없음)'
      }
    },

    // ───────── AI TC 생성 ─────────
    async checkAiMode() {
      try {
        const res = await fetch(`${API_BASE}/api/ai/health`)
        if (res.ok) {
          const data = await res.json()
          this.aiMode = data.mode || 'demo'
        }
      } catch (e) {}
    },
    closeAiModal() {
      this.showAiModal = false
      this.aiResult = null
      this.aiError = ''
    },
    async runAiGenerate() {
      this.aiGenerating = true
      this.aiError = ''
      this.aiResult = null
      try {
        const res = await fetch(`${API_BASE}/api/ai/generate-tc`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            url: this.aiForm.url,
            description: this.aiForm.description,
            level: this.aiForm.level,
            category: this.aiForm.category,
          }),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.error || '생성 실패')
        this.aiResult = data.testcase
        await this.loadAll()
      } catch (e) {
        this.aiError = e.message
      } finally {
        this.aiGenerating = false
      }
    },

    // ───────── TC 수정 ─────────
    openEditModal(tc) {
      this.editTc = tc
      this.editForm = {
        title: tc.title || '',
        description: tc.description || '',
        target_url: tc.target_url || '',
        level: tc.level || 'Smoke',
        category: tc.category || '기타',
        priority: tc.priority || 'P2',
        expected_result: tc.expected_result || 'pass',
        steps: tc.steps || [],
        note: tc.note || '',
      }
      this.editError = ''
    },
    closeEditModal() {
      this.editTc = null
      this.editError = ''
    },
    async saveEdit() {
      if (!this.editTc) return
      this.editSaving = true
      this.editError = ''
      try {
        const res = await fetch(`${API_BASE}/api/testcases/${this.editTc.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.editForm),
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.error || '저장 실패')
        await this.loadAll()
        this.closeEditModal()
      } catch (e) {
        this.editError = e.message
      } finally {
        this.editSaving = false
      }
    },

    // ───────── TC 삭제 ─────────
    confirmDelete(tc) {
      this.deleteTarget = tc
    },
    async performDelete() {
      if (!this.deleteTarget) return
      this.deleteBusy = true
      try {
        const res = await fetch(`${API_BASE}/api/testcases/${this.deleteTarget.id}`, {
          method: 'DELETE',
        })
        if (!res.ok) throw new Error('삭제 실패')
        await this.loadAll()
        this.deleteTarget = null
      } catch (e) {
        alert('삭제 실패: ' + e.message)
      } finally {
        this.deleteBusy = false
      }
    },
    closeRunnerPanel() {
      this.stopPolling()
      this.activeRun = null
      this.runnerModal = null
      this.activeTc = null
      this.screenshotUrl = ''
      this.screenshotLoaded = false
      this.screenshotTs = ''
      this.loadRuns()
    },
    statusLabel(s) {
      const map = { queued: '대기', running: '실행 중', pass: '통과', fail: '실패', error: '오류' }
      return map[s] || s
    },
    fmtTime(iso) {
      if (!iso) return '-'
      const d = new Date(iso)
      const pad = n => n.toString().padStart(2, '0')
      return `${pad(d.getMonth()+1)}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
    },
  },
}
</script>

<style scoped>
.auto-page { padding-top: 68px; min-height: 100vh; background: #fafbfc; }
.mono { font-family: 'JetBrains Mono', monospace; }

/* Header */
.auto-header { padding: 48px 32px 32px; background: linear-gradient(180deg, #fff 0%, #fafbfc 100%); border-bottom: 1px solid #E5E8EB; }
.ah-inner { max-width: 1440px; margin: 0 auto; display: grid; grid-template-columns: 1.3fr 1fr; gap: 48px; align-items: center; }
.ah-eyebrow { font-size: 12px; font-weight: 700; color: #0064FF; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 12px; }
.ah-title { font-size: 32px; font-weight: 900; letter-spacing: -.03em; color: #0F172A; margin-bottom: 14px; word-break: keep-all; }
.ah-sub { font-size: 14px; line-height: 1.75; color: #334155; word-break: keep-all; }
.ah-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.stat-tile { background: #fff; border: 1px solid #E5E8EB; border-radius: 10px; padding: 14px; display: flex; align-items: center; gap: 10px; }
.st-ic { width: 32px; height: 32px; border-radius: 8px; background: #F1F5F9 !important; color: #64748B !important; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; }
.st-v { font-size: 20px; font-weight: 800; color: #0F172A; letter-spacing: -.02em; }
.st-l { font-size: 11px; color: #64748B; font-weight: 500; margin-top: 2px; }

/* 2-column grid */
.section-wrap { padding: 32px; }
.auto-grid { max-width: 1440px; margin: 0 auto; display: grid; grid-template-columns: 1fr 440px; gap: 20px; align-items: start; }
.auto-left { display: flex; flex-direction: column; gap: 20px; min-width: 0; }
.auto-right { position: sticky; top: 88px; }

.panel { background: #fff; border: 1px solid #E5E8EB; border-radius: 12px; overflow: hidden; }
.sec-head { display: flex; justify-content: space-between; align-items: flex-end; padding: 20px 24px 12px; gap: 16px; }
.sec-title { font-size: 17px; font-weight: 800; color: #0F172A; letter-spacing: -.02em; }
.sec-sub { font-size: 12px; color: #64748B; margin-top: 2px; }
.btn-refresh { background: #fff; border: 1px solid #E5E8EB; padding: 7px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; color: #334155; font-family: inherit; display: flex; align-items: center; gap: 6px; }
.btn-refresh:hover { background: #f6f7f9; }

/* AI 버튼 & 영역 */
.sec-actions { display: flex; gap: 8px; align-items: center; }
.btn-ai {
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  color: #fff; border: none;
  padding: 7px 14px; border-radius: 8px;
  font-size: 12px; font-weight: 700;
  cursor: pointer; font-family: inherit;
  display: flex; align-items: center; gap: 6px;
  letter-spacing: -0.01em;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  transition: all .15s;
}
.btn-ai:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35); }
.btn-ai .sparkle { font-size: 13px; animation: sparkle 2s infinite; }
@keyframes sparkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.15); }
}

/* AI 모달 */
.ai-overlay {
  position: fixed; inset: 0; z-index: 2000;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
  padding: 20px; animation: aiFadeIn .2s;
}
@keyframes aiFadeIn { from { opacity: 0 } to { opacity: 1 } }
.ai-modal {
  background: #fff; border-radius: 16px;
  width: 100%; max-width: 560px; max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 60px rgba(0,0,0,.25);
  animation: aiSlide .25s;
}
@keyframes aiSlide { from { opacity: 0; transform: translateY(16px) } to { opacity: 1; transform: translateY(0) } }

.ai-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 22px 24px 18px;
  border-bottom: 1px solid #F1F5F9;
}
.ai-head-left { display: flex; gap: 14px; align-items: flex-start; }
.ai-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 800; flex-shrink: 0;
  box-shadow: 0 6px 18px rgba(99, 102, 241, 0.3);
}
.ai-title { font-size: 17px; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; margin-bottom: 4px; }
.ai-sub { font-size: 12px; color: #64748B; line-height: 1.5; }
.ai-close {
  background: #F1F5F9; border: none; width: 32px; height: 32px;
  border-radius: 8px; font-size: 20px; cursor: pointer; color: #64748B;
  display: flex; align-items: center; justify-content: center;
}
.ai-close:hover { background: #E2E8F0; }

.ai-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.ai-field { display: flex; flex-direction: column; gap: 6px; }
.ai-field label { font-size: 12px; font-weight: 700; color: #334155; letter-spacing: -0.01em; }
.ai-field input, .ai-field textarea, .ai-field select {
  background: #F8FAFC; border: 1px solid #E2E8F0;
  padding: 10px 12px; border-radius: 8px;
  font-size: 13px; font-family: inherit; color: #0F172A;
  outline: none; transition: border-color .15s;
}
.ai-field input:focus, .ai-field textarea:focus, .ai-field select:focus { border-color: #6366F1; background: #fff; }
.ai-field textarea { resize: vertical; min-height: 80px; line-height: 1.5; }
.ai-field-row { flex-direction: row; justify-content: space-between; align-items: flex-end; gap: 14px; }
.ai-field-row > div:first-child { flex: 1; display: flex; flex-direction: column; gap: 6px; }

.ai-mode-pill {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 8px 12px; border-radius: 100px;
  font-size: 11px; font-weight: 700;
  flex-shrink: 0;
}
.mode-gemini { background: #DBEAFE; color: #1E40AF; }
.mode-demo { background: #FEF3C7; color: #92400E; }
.mode-dot { width: 6px; height: 6px; border-radius: 50%; }
.mode-gemini .mode-dot { background: #3B82F6; animation: pulse 2s infinite; }
.mode-demo .mode-dot { background: #F59E0B; }

.ai-error {
  background: #FEE2E2; color: #991B1B;
  padding: 10px 14px; border-radius: 8px;
  font-size: 12px; border: 1px solid #FCA5A5;
}
.ai-result {
  background: #ECFDF5; border: 1px solid #86EFAC;
  padding: 14px 16px; border-radius: 10px;
}
.ai-result-head { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.ai-result-badge {
  background: #10B981; color: #fff;
  font-size: 10px; font-weight: 800; letter-spacing: 0.06em;
  padding: 3px 8px; border-radius: 4px;
}
.ai-result-title { font-size: 14px; font-weight: 700; color: #065F46; }
.ai-result-meta { font-size: 11px; color: #047857; margin-bottom: 8px; }
.ai-result-note { font-size: 12px; color: #065F46; }

.ai-foot {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 24px 20px;
  border-top: 1px solid #F1F5F9;
}
.ai-btn {
  padding: 10px 18px; border-radius: 9px;
  font-size: 13px; font-weight: 700;
  border: none; cursor: pointer; font-family: inherit;
  display: inline-flex; align-items: center; gap: 7px;
  transition: all .15s;
}
.ai-btn-ghost { background: #F1F5F9; color: #334155; }
.ai-btn-ghost:hover { background: #E2E8F0; }
.ai-btn-primary {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: #fff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
.ai-btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4); }
.ai-btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.ai-spinner {
  width: 12px; height: 12px;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { display: inline-block; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* TC Table */
.tc-table { border-top: 1px solid #f1f3f5; }
.tc-head, .tc-row { display: grid; grid-template-columns: 70px 2fr 85px 55px 70px 90px; gap: 12px; padding: 11px 20px; align-items: center; }
.tc-head { background: #f9fafc; border-bottom: 1px solid #E5E8EB; font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.tc-actions-head { text-align: center; }
.tc-row { border-bottom: 1px solid #f1f3f5; transition: background .15s; }
.tc-row:last-child { border-bottom: none; }
.tc-row:hover { background: #fafbfc; }
/* Level 필터 탭 */
.level-tabs {
  display: flex; gap: 4px;
  padding: 10px 14px 0;
  border-bottom: 1px solid #F1F5F9;
  background: #fff;
  flex-wrap: wrap;
}
.lv-tab {
  background: transparent; border: none;
  padding: 8px 14px; border-radius: 8px 8px 0 0;
  font-size: 12.5px; font-weight: 600;
  color: #64748B; cursor: pointer; font-family: inherit;
  display: inline-flex; align-items: center; gap: 7px;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.lv-tab:hover { background: #F8FAFC; color: #0F172A; }
.lv-tab.active { color: #0F172A; border-bottom-color: #0F172A; }
.lv-tab.active.lv-smoke { border-bottom-color: #3B82F6; color: #1E40AF; }
.lv-tab.active.lv-regression { border-bottom-color: #F59E0B; color: #92400E; }
.lv-tab.active.lv-e2e { border-bottom-color: #8B5CF6; color: #6D28D9; }
.lv-count {
  background: #F1F5F9; color: #64748B;
  font-size: 10px; font-weight: 800;
  padding: 2px 7px; border-radius: 100px;
  font-family: 'JetBrains Mono', monospace;
}
.lv-tab.active .lv-count { background: #0F172A; color: #fff; }
.lv-tab.active.lv-smoke .lv-count { background: #3B82F6; color: #fff; }
.lv-tab.active.lv-regression .lv-count { background: #F59E0B; color: #fff; }
.lv-tab.active.lv-e2e .lv-count { background: #8B5CF6; color: #fff; }

/* Level/Domain 뱃지 */
.chip-level {
  display: inline-block;
  font-size: 10px; font-weight: 800;
  padding: 3px 8px; border-radius: 4px;
  letter-spacing: 0.05em;
}
.lvchip-smoke      { background: #DBEAFE; color: #1E40AF; }
.lvchip-regression { background: #FEF3C7; color: #92400E; }
.lvchip-e2e        { background: #EDE9FE; color: #6D28D9; }
.chip-domain {
  display: inline-block;
  font-size: 11px; font-weight: 600;
  padding: 3px 8px; border-radius: 4px;
  background: #F1F5F9; color: #475569;
}

/* 수정/삭제 버튼 */
.btn-edit, .btn-delete {
  background: #fff; border: 1px solid #E5E8EB;
  width: 28px; height: 28px; border-radius: 6px;
  font-size: 13px; cursor: pointer; font-family: inherit;
  color: #64748B; display: inline-flex; align-items: center; justify-content: center;
  margin-left: 4px;
}
.btn-edit:hover { background: #EFF6FF; border-color: #93C5FD; color: #2563EB; }
.btn-delete:hover { background: #FEE2E2; border-color: #FCA5A5; color: #DC2626; }

/* Level radio group (AI/수정 모달) */
.level-radio-group {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
}
.level-radio {
  background: #F8FAFC; border: 2px solid #E2E8F0;
  padding: 10px 12px; border-radius: 10px;
  cursor: pointer; transition: all .15s;
  display: flex; flex-direction: column; gap: 4px;
}
.level-radio input { display: none; }
.level-radio.active {
  background: #EFF6FF; border-color: #3B82F6;
}
.level-radio:hover { background: #F1F5F9; }
.level-radio.active:hover { background: #DBEAFE; }
.lr-main {
  font-size: 13px; font-weight: 800; color: #0F172A;
  letter-spacing: -0.01em;
}
.lr-desc {
  font-size: 10.5px; color: #64748B; line-height: 1.4;
}

/* 수정 모달 */
.edit-modal { max-width: 620px; }
.edit-icon {
  background: linear-gradient(135deg, #3B82F6, #06B6D4) !important;
}
.ai-field-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; align-items: flex-end; }

/* 삭제 모달 */
.delete-modal { max-width: 440px; }
.delete-icon {
  background: linear-gradient(135deg, #EF4444, #DC2626) !important;
}
.del-target {
  background: #FEF2F2; border: 1px solid #FECACA;
  padding: 14px 16px; border-radius: 10px;
}
.del-id { font-size: 12px; font-weight: 700; color: #991B1B; margin-bottom: 4px; }
.del-title { font-size: 14px; font-weight: 600; color: #0F172A; }
.ai-btn-danger {
  background: #EF4444; color: #fff;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}
.ai-btn-danger:hover { background: #DC2626; }

.tc-id { font-size: 12px; font-weight: 700; color: #0F172A; display: inline-flex; align-items: center; gap: 5px; flex-wrap: wrap; }
.tc-ai-tag {
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  color: #fff;
  font-size: 9px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 3px;
  letter-spacing: 0.06em;
  box-shadow: 0 1px 4px rgba(99, 102, 241, 0.3);
}
.tc-title-cell { min-width: 0; }
.tc-title { font-size: 13px; font-weight: 700; color: #0F172A; margin-bottom: 2px; }
.tc-desc { font-size: 11px; color: #64748B; line-height: 1.4; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.tc-actions { display: flex; justify-content: center; }
.btn-run { background: #0064FF; color: #fff; border: none; padding: 7px 14px; border-radius: 7px; font-size: 12px; font-weight: 700; cursor: pointer; font-family: inherit; }
.btn-run:hover:not(:disabled) { background: #0051d3; }
.btn-run:disabled { background: #CBD5E1; cursor: not-allowed; }

/* 통일된 chip — 거의 다 회색 톤, Pass/Fail 결과만 강조 */
.chip { display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; letter-spacing: -.01em; background: #F1F5F9; color: #475569; }
.chip-cat-smoke, .chip-cat-regression, .chip-cat-e2e { background: #F1F5F9; color: #475569; }
.chip-prio { display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 800; font-family: 'JetBrains Mono', monospace; background: #F1F5F9; }
.prio-p1 { color: #0F172A; }
.prio-p2 { color: #64748B; }
.prio-p3 { color: #94A3B8; }
.chip-expected { display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.exp-pass { background: #DCFCE7; color: #166534; }
.exp-fail { background: #FEE2E2; color: #991B1B; }

/* History */
.hist-table { border-top: 1px solid #f1f3f5; }
.hist-head, .hist-row { display: grid; grid-template-columns: 70px 2fr 85px 60px 100px 55px; gap: 12px; padding: 10px 20px; align-items: center; }
.hist-head { background: #f9fafc; border-bottom: 1px solid #E5E8EB; font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.hist-row { border-bottom: 1px solid #f1f3f5; font-size: 12px; }
.hist-row:last-child { border-bottom: none; }
.hist-tc-id { font-size: 10px; color: #64748B; }
.hist-tc-title { font-size: 12px; color: #0F172A; font-weight: 600; }
.hist-time { font-size: 10px; color: #64748B; }
.status-chip { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.st-pass { background: #DCFCE7; color: #166534; }
.st-fail { background: #FEE2E2; color: #991B1B; }
.st-error { background: #F1F5F9; color: #475569; }
.st-running { background: #e5f0ff; color: #0064FF; }
.st-queued { background: #F1F5F9; color: #94A3B8; }
.btn-detail { background: #f6f7f9; border: 1px solid #E5E8EB; padding: 4px 9px; border-radius: 5px; font-size: 11px; cursor: pointer; font-family: inherit; color: #334155; }
.btn-detail:hover { background: #eef0f3; }

.empty-state { padding: 48px 20px; text-align: center; color: #64748B; font-size: 13px; border-top: 1px solid #f1f3f5; }
.es-sub { font-size: 11px; margin-top: 6px; color: #94A3B8; }

/* Right panel */
.run-panel-wrap { background: #fff; border: 1px solid #E5E8EB; border-radius: 12px; max-height: calc(100vh - 108px); overflow: hidden; display: flex; flex-direction: column; }
.run-panel { display: flex; flex-direction: column; min-height: 0; }

.rp-head { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid #E5E8EB; flex-shrink: 0; }
.rp-title { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: #0F172A; }
.rp-dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-running { background: #0064FF; box-shadow: 0 0 8px #0064FF; animation: pulse 1.5s infinite; }
.dot-pass { background: #06C755; }
.dot-fail { background: #F04452; }
.dot-error { background: #F59E0B; }
.dot-queued { background: #94A3B8; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .4; } }
.rp-run-id { font-size: 12px; color: #64748B; }
.rp-close { background: #f6f7f9; border: none; width: 28px; height: 28px; border-radius: 7px; font-size: 15px; cursor: pointer; color: #64748B; font-family: inherit; }
.rp-close:hover { background: #eef0f3; color: #0F172A; }
.rp-tc-title { padding: 10px 18px 14px; font-size: 14px; font-weight: 600; color: #334155; border-bottom: 1px solid #f1f3f5; }

/* Screenshot */
.rp-screenshot { padding: 14px 18px; border-bottom: 1px solid #f1f3f5; }
.ss-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.ss-label { display: flex; align-items: center; gap: 6px; font-size: 10px; font-weight: 800; color: #0F172A; letter-spacing: .05em; }
.ss-live-dot { width: 7px; height: 7px; background: #F04452; border-radius: 50%; animation: pulse 1s infinite; }
.ss-ts { font-size: 10px; color: #64748B; }
.ss-frame { background: #0F172A; border-radius: 8px; aspect-ratio: 16 / 9; overflow: hidden; display: flex; align-items: center; justify-content: center; }
.ss-img { width: 100%; height: 100%; object-fit: contain; }
.ss-placeholder { color: #94A3B8; text-align: center; font-size: 12px; font-weight: 600; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 20px; }
.ss-ph-spinner { width: 28px; height: 28px; border: 3px solid rgba(148,163,184,.2); border-top-color: #0064FF; border-radius: 50%; animation: spin 0.9s linear infinite; margin-bottom: 4px; }
.ss-ph-sub { font-size: 10px; color: #64748B; font-weight: 400; }
.ss-meta { display: flex; gap: 14px; font-size: 10px; color: #334155; padding: 8px 10px; background: #f9fafc; border-radius: 6px; margin-top: 8px; }
.ss-k { color: #64748B; }

/* Steps */
.rp-steps { padding: 14px 18px 18px; overflow-y: auto; flex: 1; }
.rp-steps-head { font-size: 12px; font-weight: 700; color: #0F172A; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
.step-counter { font-size: 10px; color: #64748B; background: #f1f3f5; padding: 2px 7px; border-radius: 10px; }
.step-list { display: flex; flex-direction: column; gap: 6px; }
.step-item { display: flex; gap: 8px; padding: 8px 10px; border-radius: 7px; background: #f9fafc; border: 1px solid transparent; }
.step-pass { background: #F0FDF4; border-color: #BBF7D0; }
.step-fail { background: #FEF2F2; border-color: #FECACA; }
.step-running { background: #EFF6FF; border-color: #BFDBFE; }
.step-pending { opacity: .5; }
.step-ic { width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 800; flex-shrink: 0; margin-top: 1px; }
.step-pass .step-ic { background: #06C755; color: #fff; }
.step-fail .step-ic { background: #F04452; color: #fff; }
.step-running .step-ic { background: #0064FF; color: #fff; }
.step-pending .step-ic { background: #CBD5E1; color: #fff; }
.step-spin { display: inline-block; width: 9px; height: 9px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin .7s linear infinite; }
.step-body { flex: 1; min-width: 0; }
.step-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
.step-action { font-size: 9px; color: #64748B; font-weight: 700; }
.step-dur { font-size: 9px; color: #64748B; }
.step-desc { font-size: 11px; color: #0F172A; font-weight: 500; word-break: break-all; line-height: 1.4; }
.step-error { font-size: 9px; color: #991B1B; margin-top: 3px; background: rgba(240,68,82,.08); padding: 3px 5px; border-radius: 3px; word-break: break-all; }

.rp-bg-note { margin-top: 12px; padding: 9px 11px; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 7px; font-size: 11px; color: #1E40AF; line-height: 1.5; }

.rp-summary { margin-top: 14px; padding: 12px; border-radius: 8px; border: 1px solid; }
.summary-pass { background: #F0FDF4; border-color: #BBF7D0; }
.summary-fail { background: #FEF2F2; border-color: #FECACA; }
.summary-error { background: #FEF3C7; border-color: #FDE68A; }
.sum-head { font-size: 13px; font-weight: 800; color: #0F172A; margin-bottom: 4px; }
.sum-note { font-size: 11px; color: #065F46; background: #D1FAE5; padding: 7px 9px; border-radius: 5px; margin-top: 5px; font-weight: 600; }
.sum-err { font-size: 10px; color: #991B1B; margin-top: 5px; background: rgba(240,68,82,.08); padding: 5px 7px; border-radius: 4px; word-break: break-all; }

/* Empty state (Run 안 돌릴 때) */
.run-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 32px; text-align: center; }
.re-icon { width: 56px; height: 56px; border-radius: 50%; background: #e5f0ff; color: #0064FF; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px; }
.re-title { font-size: 15px; font-weight: 700; color: #0F172A; margin-bottom: 8px; }
.re-sub { font-size: 12px; color: #64748B; line-height: 1.6; }

/* Confirm Modal */
.confirm-overlay { position: fixed; inset: 0; z-index: 1100; background: rgba(15,23,42,.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; animation: fadeIn .18s; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.confirm-modal { background: #fff; border-radius: 16px; max-width: 420px; width: 100%; padding: 28px 24px 20px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,.25); animation: slideUp .22s; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.confirm-icon { width: 48px; height: 48px; border-radius: 50%; background: #FEF3C7; color: #B45309; font-size: 24px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.confirm-title { font-size: 17px; font-weight: 800; color: #0F172A; letter-spacing: -.02em; margin-bottom: 10px; }
.confirm-message { font-size: 13px; line-height: 1.65; color: #475569; margin-bottom: 24px; word-break: keep-all; }
.confirm-actions { display: flex; gap: 10px; }
.confirm-btn-cancel, .confirm-btn-ok { flex: 1; padding: 12px 16px; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; border: none; font-family: inherit; transition: all .15s; }
.confirm-btn-cancel { background: #f1f3f5; color: #475569; }
.confirm-btn-cancel:hover { background: #e2e8f0; }
.confirm-btn-ok { background: #0064FF; color: #fff; }
.confirm-btn-ok:hover { background: #0051d3; }

@media (max-width: 1200px) {
  .auto-grid { grid-template-columns: 1fr; }
  .auto-right { position: static; }
  .run-panel-wrap { max-height: none; }
  .ah-inner { grid-template-columns: 1fr; }
}
</style>