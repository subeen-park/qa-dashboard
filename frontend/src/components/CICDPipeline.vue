<template>
  <div class="cicd-page">
    <!-- 헤더 -->
    <div class="cicd-header">
      <div>
        <div class="page-title">CI/CD 파이프라인</div>
        <div class="page-sub">GitHub Actions 워크플로우 — 머지 즉시 디바이스팜 전체에서 QA 자동화를 실행합니다</div>
      </div>
      <div class="cicd-header-right">
        <div class="trigger-info">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 2h8v8H2zM2 5h8M5 2v8" stroke="currentColor" stroke-width="1.2"/></svg>
          <span>Trigger: <strong>push to main</strong></span>
        </div>
        <button class="btn-run" :disabled="running" @click="runPipeline">
          <svg v-if="!running" width="12" height="12" viewBox="0 0 12 12" fill="currentColor"><path d="M3 2v8l6-4z"/></svg>
          <span v-else class="spin-icon"></span>
          {{ running ? `실행 중... ${elapsedTime}s` : 'Run Workflow' }}
        </button>
      </div>
    </div>

    <!-- 요약 바 -->
    <div class="summary-bar">
      <div class="sb-item">
        <div class="sb-ic sb-blue">#</div>
        <div class="sb-txt">
          <div class="sb-n">{{ runNumber }}</div>
          <div class="sb-l">현재 실행</div>
        </div>
      </div>
      <div class="sb-item">
        <div class="sb-ic sb-green">✓</div>
        <div class="sb-txt">
          <div class="sb-n">{{ successCount }}/{{ history.length }}</div>
          <div class="sb-l">최근 성공률</div>
        </div>
      </div>
      <div class="sb-item">
        <div class="sb-ic sb-yellow">⏱</div>
        <div class="sb-txt">
          <div class="sb-n">{{ avgDuration }}m</div>
          <div class="sb-l">평균 소요 시간</div>
        </div>
      </div>
      <div class="sb-item">
        <div class="sb-ic sb-purple">📱</div>
        <div class="sb-txt">
          <div class="sb-n">7</div>
          <div class="sb-l">배포 대상 디바이스</div>
        </div>
      </div>
    </div>

    <!-- 메인 — 좌: 파이프라인 | 우: 로그 -->
    <div class="main-grid">
      <!-- 좌: 파이프라인 플로우 -->
      <div class="pipe-section">
        <div class="ps-head">
          <div class="ps-title">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="margin-right:6px"><path d="M3 8h10M8 3v10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            Workflow — <span class="mono">device-qa-pipeline.yml</span>
          </div>
          <div class="ps-meta">
            <span class="ps-branch mono">
              <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor" style="margin-right:4px"><path d="M2 1v8M8 3v3M2 6a2 2 0 004 0 2 2 0 014-0M2 1a1 1 0 100 2 1 1 0 000-2zM2 7a1 1 0 100 2 1 1 0 000-2zM8 1a1 1 0 100 2 1 1 0 000-2zM8 5a1 1 0 100 2 1 1 0 000-2z"/></svg>
              main
            </span>
            <span class="ps-commit mono">{{ currentCommit }}</span>
          </div>
        </div>

        <div class="pipe-flow">
          <div v-for="(stage, i) in stages" :key="stage.id" class="stage-wrap">
            <div class="stage-card" :class="'stage-'+stage.status">
              <div class="stage-head">
                <div class="stage-ic" :class="'si-'+stage.status">
                  <span v-if="stage.status==='done'">✓</span>
                  <span v-else-if="stage.status==='running'" class="spin-icon-sm"></span>
                  <span v-else-if="stage.status==='fail'">✕</span>
                  <span v-else>{{ i + 1 }}</span>
                </div>
                <div class="stage-info">
                  <div class="stage-name">{{ stage.name }}</div>
                  <div class="stage-sub">{{ stage.sub }}</div>
                </div>
                <div class="stage-time mono">
                  <span v-if="stage.status==='done'">{{ stage.duration }}</span>
                  <span v-else-if="stage.status==='running'">진행 중</span>
                  <span v-else-if="stage.status==='fail'">{{ stage.duration }}</span>
                  <span v-else class="stage-wait">대기</span>
                </div>
              </div>
              <!-- 디바이스팜 배포 단계는 디바이스별 상태도 표시 -->
              <div v-if="stage.id === 'deploy' && (stage.status === 'running' || stage.status === 'done')" class="device-grid">
                <div v-for="d in devices" :key="d.name" class="dev-chip" :class="'dc-'+d.deployStatus">
                  <span class="dc-dot"></span>
                  <span class="dc-name">{{ d.name }}</span>
                </div>
              </div>
              <!-- 테스트 실행 단계는 디바이스별 Pass/Fail 표시 -->
              <div v-if="stage.id === 'test' && (stage.status === 'running' || stage.status === 'done' || stage.status === 'fail')" class="device-grid">
                <div v-for="d in devices" :key="d.name" class="dev-result" :class="'dr-'+d.testStatus">
                  <div class="dr-head">
                    <span class="dr-name">{{ d.name }}</span>
                    <span class="dr-mark">
                      <span v-if="d.testStatus==='pass'">✓</span>
                      <span v-else-if="d.testStatus==='fail'">✕</span>
                      <span v-else-if="d.testStatus==='running'" class="spin-icon-xs"></span>
                      <span v-else>·</span>
                    </span>
                  </div>
                  <div class="dr-stats mono" v-if="d.testStatus==='pass' || d.testStatus==='fail'">
                    {{ d.testPassed }}/{{ d.testTotal }}
                  </div>
                </div>
              </div>
            </div>
            <div v-if="i < stages.length - 1" class="stage-arrow">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 2v10M3 8l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
          </div>
        </div>

        <!-- 최종 결과 -->
        <div v-if="finalStatus" class="final-result" :class="'fr-'+finalStatus">
          <div class="fr-ic">
            <span v-if="finalStatus==='pass'">✓</span>
            <span v-else>✕</span>
          </div>
          <div class="fr-body">
            <div class="fr-title">
              {{ finalStatus==='pass' ? '파이프라인 성공' : '파이프라인 실패' }}
            </div>
            <div class="fr-sub">
              {{ finalStatus==='pass'
                ? `전체 ${devices.length}개 디바이스에서 테스트 통과 · ${elapsedTime}s 소요`
                : `일부 디바이스에서 테스트 실패 · Slack 알림 발송됨` }}
            </div>
          </div>
          <div class="fr-actions">
            <button class="btn-ghost">리포트 보기</button>
          </div>
        </div>
      </div>

      <!-- 우: 실시간 로그 -->
      <div class="logs-section">
        <div class="logs-head">
          <div class="logs-title">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style="margin-right:5px"><path d="M2 3h8M2 6h8M2 9h5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            Workflow Logs
          </div>
          <div class="logs-meta mono">{{ elapsedTime }}s</div>
        </div>
        <div class="logs-body" ref="logsBody">
          <div v-for="(log, i) in logs" :key="i" class="log-line" :class="'log-'+log.level">
            <span class="log-time mono">{{ log.time }}</span>
            <span class="log-arrow">
              <span v-if="log.level==='info'">›</span>
              <span v-else-if="log.level==='run'">$</span>
              <span v-else-if="log.level==='success'">✓</span>
              <span v-else-if="log.level==='error'">✕</span>
            </span>
            <span class="log-msg">{{ log.msg }}</span>
          </div>
          <div v-if="logs.length === 0" class="log-empty">
            Run Workflow 버튼을 눌러 파이프라인을 실행하세요
          </div>
        </div>
      </div>
    </div>

    <!-- 하단: 최근 실행 히스토리 -->
    <div class="history-section">
      <div class="hs-head">
        <div class="hs-title">최근 실행 히스토리</div>
        <div class="hs-meta">최근 10회</div>
      </div>
      <div class="hs-list">
        <div v-for="h in history" :key="h.run" class="hs-row" :class="'hs-'+h.status">
          <div class="hs-ic" :class="'hsi-'+h.status">
            <span v-if="h.status==='pass'">✓</span>
            <span v-else>✕</span>
          </div>
          <div class="hs-run mono">#{{ h.run }}</div>
          <div class="hs-branch mono">{{ h.branch }}</div>
          <div class="hs-commit">
            <span class="hs-hash mono">{{ h.commit }}</span>
            <span class="hs-msg">{{ h.message }}</span>
          </div>
          <div class="hs-devices mono">{{ h.devicesPassed }}/{{ h.devicesTotal }} 디바이스</div>
          <div class="hs-time mono">{{ h.duration }}</div>
          <div class="hs-when">{{ h.when }}</div>
        </div>
      </div>
    </div>

    <!-- 어떻게 작동하는지 (워크플로우 YAML 미리보기) -->
    <div class="yaml-section">
      <div class="ys-head">
        <div class="ys-title">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="margin-right:6px"><path d="M3 2h8v10H3zM5 5h4M5 7h4M5 9h3" stroke="currentColor" stroke-width="1.2"/></svg>
          <span class="mono">.github/workflows/device-qa-pipeline.yml</span>
        </div>
        <div class="ys-sub">실제 사용되는 GitHub Actions 워크플로우</div>
      </div>
      <pre class="yaml-code"><code><span class="yml-key">name</span>: Device QA Pipeline

<span class="yml-key">on</span>:
  <span class="yml-key">push</span>:
    <span class="yml-key">branches</span>: [main]

<span class="yml-key">jobs</span>:
  <span class="yml-key">build-and-test</span>:
    <span class="yml-key">runs-on</span>: ubuntu-latest
    <span class="yml-key">steps</span>:
      - <span class="yml-key">uses</span>: actions/checkout@v4

      - <span class="yml-key">name</span>: Build iOS App
        <span class="yml-key">run</span>: xcodebuild -scheme App -configuration Release

      - <span class="yml-key">name</span>: Build Android App
        <span class="yml-key">run</span>: ./gradlew assembleRelease

      - <span class="yml-key">name</span>: Deploy to Device Farm
        <span class="yml-key">run</span>: python scripts/deploy_to_farm.py --devices all

      - <span class="yml-key">name</span>: Run Appium Tests
        <span class="yml-key">run</span>: pytest tests/ --device-matrix all --junit-xml=report.xml

      - <span class="yml-key">name</span>: Send Slack Report
        <span class="yml-key">if</span>: always()
        <span class="yml-key">run</span>: python scripts/notify_slack.py --report report.xml</code></pre>
    </div>
  </div>
</template>

<script>
const INITIAL_STAGES = [
  { id: 'checkout', name: 'Checkout', sub: 'actions/checkout@v4', status: 'wait', duration: '' },
  { id: 'build-ios', name: 'Build iOS App', sub: 'xcodebuild · Release 모드', status: 'wait', duration: '' },
  { id: 'build-android', name: 'Build Android App', sub: 'gradle · assembleRelease', status: 'wait', duration: '' },
  { id: 'deploy', name: 'Deploy to Device Farm', sub: '7개 디바이스에 앱 자동 설치', status: 'wait', duration: '' },
  { id: 'test', name: 'Run Appium Tests', sub: 'pytest + Appium · 디바이스 병렬 실행', status: 'wait', duration: '' },
  { id: 'report', name: 'Send Slack Report', sub: '결과 리포트 + 실패 스크린샷 자동 첨부', status: 'wait', duration: '' },
]

const DEVICES = [
  { name: 'iPhone 14', deployStatus: 'wait', testStatus: 'wait', testPassed: 0, testTotal: 24 },
  { name: 'iPhone 15 Pro', deployStatus: 'wait', testStatus: 'wait', testPassed: 0, testTotal: 24 },
  { name: 'iPad Air', deployStatus: 'wait', testStatus: 'wait', testPassed: 0, testTotal: 24 },
  { name: 'Pixel 7', deployStatus: 'wait', testStatus: 'wait', testPassed: 0, testTotal: 24 },
  { name: 'Pixel 8', deployStatus: 'wait', testStatus: 'wait', testPassed: 0, testTotal: 24 },
  { name: 'Galaxy S23', deployStatus: 'wait', testStatus: 'wait', testPassed: 0, testTotal: 24 },
  { name: 'Galaxy S24', deployStatus: 'wait', testStatus: 'wait', testPassed: 0, testTotal: 24 },
]

const HISTORY = [
  { run: 142, status: 'pass', branch: 'main', commit: 'a3f8b2c', message: 'feat: 소셜 로그인 추가', devicesPassed: 7, devicesTotal: 7, duration: '3m 24s', when: '2분 전' },
  { run: 141, status: 'pass', branch: 'main', commit: '7d41e9a', message: 'fix: 결제 플로우 응답 지연', devicesPassed: 7, devicesTotal: 7, duration: '3m 02s', when: '1시간 전' },
  { run: 140, status: 'fail', branch: 'dev', commit: 'e52c118', message: 'test: 새 TC 추가', devicesPassed: 5, devicesTotal: 7, duration: '1m 48s', when: '2시간 전' },
  { run: 139, status: 'pass', branch: 'main', commit: '9b7a0f3', message: 'chore: 의존성 업데이트', devicesPassed: 7, devicesTotal: 7, duration: '3m 15s', when: '어제' },
  { run: 138, status: 'pass', branch: 'main', commit: '4c82d61', message: 'feat: 푸시 알림 설정 추가', devicesPassed: 7, devicesTotal: 7, duration: '3m 44s', when: '어제' },
  { run: 137, status: 'pass', branch: 'main', commit: '2e917b8', message: 'refactor: API 모듈 분리', devicesPassed: 7, devicesTotal: 7, duration: '3m 08s', when: '2일 전' },
  { run: 136, status: 'fail', branch: 'main', commit: 'f03a4d2', message: 'feat: 다크 모드 지원', devicesPassed: 4, devicesTotal: 7, duration: '2m 22s', when: '2일 전' },
  { run: 135, status: 'pass', branch: 'main', commit: '8a9c7f1', message: 'fix: 검색 결과 중복 제거', devicesPassed: 7, devicesTotal: 7, duration: '3m 11s', when: '3일 전' },
]

export default {
  name: 'CICDPipeline',
  data() {
    return {
      stages: JSON.parse(JSON.stringify(INITIAL_STAGES)),
      devices: JSON.parse(JSON.stringify(DEVICES)),
      logs: [],
      history: HISTORY,
      runNumber: 143,
      currentCommit: 'a3f8b2c',
      running: false,
      elapsedTime: '0.0',
      elapsedTimer: null,
      startedAt: null,
      finalStatus: null,
    }
  },
  computed: {
    successCount() { return this.history.filter(h => h.status === 'pass').length },
    avgDuration() {
      const nums = this.history.map(h => {
        const m = h.duration.match(/(\d+)m\s*(\d+)/)
        return m ? parseInt(m[1]) + parseInt(m[2]) / 60 : 0
      })
      return (nums.reduce((a, b) => a + b, 0) / nums.length).toFixed(1)
    },
  },
  methods: {
    async runPipeline() {
      this.reset()
      this.running = true
      this.startedAt = Date.now()
      this.elapsedTimer = setInterval(() => {
        this.elapsedTime = ((Date.now() - this.startedAt) / 1000).toFixed(1)
      }, 100)

      this.addLog('info', `━━━ Pipeline #${this.runNumber} 시작 ━━━`)
      this.addLog('info', `Branch: main · Commit: ${this.currentCommit}`)
      this.addLog('info', `Trigger: push to main`)
      await this.sleep(400)

      try {
        // 1. Checkout
        await this.runStage(0, 'actions/checkout@v4', [
          { l: 'run', m: 'git fetch origin main' },
          { l: 'run', m: 'git checkout a3f8b2c' },
          { l: 'success', m: 'Checkout complete (1.8s)' },
        ], '1.8s')

        // 2. Build iOS
        await this.runStage(1, 'Build iOS App', [
          { l: 'run', m: 'xcodebuild -scheme App -configuration Release' },
          { l: 'info', m: 'Compiling Swift sources...' },
          { l: 'info', m: 'Linking frameworks...' },
          { l: 'info', m: 'Signing app with certificate...' },
          { l: 'success', m: 'Build iOS App succeeded (1m 24s) · App.ipa generated' },
        ], '1m 24s')

        // 3. Build Android
        await this.runStage(2, 'Build Android App', [
          { l: 'run', m: './gradlew assembleRelease' },
          { l: 'info', m: 'Downloading dependencies...' },
          { l: 'info', m: 'Processing resources...' },
          { l: 'info', m: 'Signing APK...' },
          { l: 'success', m: 'Build Android App succeeded (1m 12s) · app-release.apk generated' },
        ], '1m 12s')

        // 4. Deploy to Device Farm
        this.setStageStatus(3, 'running')
        this.addLog('run', 'python scripts/deploy_to_farm.py --devices all')
        for (let i = 0; i < this.devices.length; i++) {
          this.devices[i].deployStatus = 'deploying'
          this.addLog('info', `[${this.devices[i].name}] Installing app...`)
          await this.sleep(300)
          this.devices[i].deployStatus = 'deployed'
          this.addLog('success', `[${this.devices[i].name}] Installed successfully`)
        }
        this.setStageStatus(3, 'done', '2m 18s')
        this.addLog('success', 'Deploy to Device Farm complete · 7/7 devices ready')
        await this.sleep(300)

        // 5. Run Tests (여기서 일부 디바이스는 실패)
        this.setStageStatus(4, 'running')
        this.addLog('run', 'pytest tests/ --device-matrix all --junit-xml=report.xml')
        this.addLog('info', 'Running Appium tests across 7 devices in parallel...')

        // 모든 디바이스 running 상태로
        this.devices.forEach(d => d.testStatus = 'running')

        // 각 디바이스 결과 (6개 성공, 1개 실패 — Galaxy S23)
        const results = [
          { idx: 0, pass: true, time: 320 },
          { idx: 1, pass: true, time: 290 },
          { idx: 2, pass: true, time: 310 },
          { idx: 3, pass: true, time: 280 },
          { idx: 4, pass: true, time: 300 },
          { idx: 5, pass: false, time: 180 }, // Galaxy S23 실패
          { idx: 6, pass: true, time: 295 },
        ]

        // 디바이스별 순서대로 결과 반영 (실제처럼 비동기 느낌)
        for (const r of results.sort(() => Math.random() - 0.5)) {
          await this.sleep(250)
          const d = this.devices[r.idx]
          if (r.pass) {
            d.testStatus = 'pass'
            d.testPassed = d.testTotal
            this.addLog('success', `[${d.name}] ${d.testPassed}/${d.testTotal} passed · ${(r.time/100).toFixed(1)}s`)
          } else {
            d.testStatus = 'fail'
            d.testPassed = 22
            this.addLog('error', `[${d.name}] ${d.testPassed}/${d.testTotal} passed · 2 failed`)
            this.addLog('error', `  └─ FAILED test_login_social_kakao.py::test_oauth_callback`)
            this.addLog('error', `  └─ FAILED test_payment.py::test_card_expiry_validation`)
          }
        }
        this.setStageStatus(4, 'fail', '5m 12s')
        this.addLog('error', 'Test stage completed with failures · 6/7 devices passed')
        await this.sleep(300)

        // 6. Send Slack Report (always 실행)
        await this.runStage(5, 'Send Slack Report', [
          { l: 'run', m: 'python scripts/notify_slack.py --report report.xml' },
          { l: 'info', m: 'Capturing failure screenshots from Galaxy S23...' },
          { l: 'info', m: 'Uploading screenshots to S3...' },
          { l: 'info', m: 'Posting to #qa-alerts channel...' },
          { l: 'success', m: 'Slack notification sent · 2 failures reported with screenshots' },
        ], '12s')

        this.finalStatus = 'fail'
        this.addLog('info', '━━━ Pipeline Finished ━━━')
        this.addLog('error', 'Overall: FAILED · Deployment blocked by quality gate')
      } finally {
        clearInterval(this.elapsedTimer)
        this.running = false
      }
    },
    async runStage(idx, _name, logList, duration) {
      this.setStageStatus(idx, 'running')
      for (const l of logList) {
        this.addLog(l.l, l.m)
        await this.sleep(l.l === 'info' ? 350 : 200)
      }
      this.setStageStatus(idx, 'done', duration)
      await this.sleep(200)
    },
    setStageStatus(idx, status, duration) {
      this.stages[idx].status = status
      if (duration) this.stages[idx].duration = duration
    },
    addLog(level, msg) {
      const d = new Date()
      const time = d.toTimeString().slice(0, 8)
      this.logs.push({ level, msg, time })
      this.$nextTick(() => {
        if (this.$refs.logsBody) this.$refs.logsBody.scrollTop = this.$refs.logsBody.scrollHeight
      })
    },
    reset() {
      this.stages = JSON.parse(JSON.stringify(INITIAL_STAGES))
      this.devices = JSON.parse(JSON.stringify(DEVICES))
      this.logs = []
      this.finalStatus = null
      this.elapsedTime = '0.0'
    },
    sleep(ms) { return new Promise(r => setTimeout(r, ms)) },
  },
}
</script>

<style scoped>
.cicd-page {
  padding: 100px 32px 60px; max-width: 1280px; margin: 0 auto;
  font-family: 'Pretendard Variable', Pretendard, sans-serif;
  user-select: none; -webkit-user-select: none;
}
.cicd-page * { font-family: inherit; }
.cicd-page .mono { font-family: 'JetBrains Mono', 'Menlo', monospace; }

/* 헤더 */
.cicd-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; gap: 20px; flex-wrap: wrap; }
.page-title { font-size: 24px; font-weight: 800; letter-spacing: -0.02em; }
.page-sub { font-size: 13px; color: var(--muted); margin-top: 6px; }
.cicd-header-right { display: flex; align-items: center; gap: 12px; }
.trigger-info { display: inline-flex; align-items: center; gap: 6px; background: var(--bg3); padding: 8px 12px; border-radius: 100px; font-size: 12px; color: var(--text-sub); font-weight: 500; }
.trigger-info strong { color: var(--text); font-weight: 700; }
.btn-run { display: inline-flex; align-items: center; gap: 7px; background: var(--primary); color: #fff; border: none; padding: 10px 18px; border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit; box-shadow: 0 4px 12px rgba(0,100,255,0.25); transition: all .15s; }
.btn-run:hover:not(:disabled) { background: var(--primary-hover); transform: translateY(-1px); }
.btn-run:disabled { opacity: .75; cursor: not-allowed; }
.spin-icon { display: inline-block; width: 10px; height: 10px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin .7s linear infinite; }
.spin-icon-sm { display: inline-block; width: 8px; height: 8px; border: 1.5px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin .7s linear infinite; }
.spin-icon-xs { display: inline-block; width: 7px; height: 7px; border: 1.5px solid currentColor; border-top-color: transparent; border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 요약 */
.summary-bar { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
.sb-item { display: flex; align-items: center; gap: 14px; background: #fff; border: 1px solid var(--border); border-radius: 14px; padding: 18px 20px; }
.sb-ic { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; flex-shrink: 0; }
.sb-blue { background: #DBEAFE; color: #1E40AF; }
.sb-green { background: #D1FAE5; color: #065F46; }
.sb-yellow { background: #FEF3C7; color: #92400E; }
.sb-purple { background: #F3E8FF; color: #6B21A8; }
.sb-n { font-size: 20px; font-weight: 800; font-family: 'Inter', sans-serif; letter-spacing: -0.02em; line-height: 1; }
.sb-l { font-size: 11px; color: var(--muted); margin-top: 4px; font-weight: 500; }

/* 메인 그리드 */
.main-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 20px; margin-bottom: 24px; }

/* 파이프라인 섹션 */
.pipe-section { background: #fff; border: 1px solid var(--border); border-radius: 16px; padding: 24px; }
.ps-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border); flex-wrap: wrap; gap: 10px; }
.ps-title { font-size: 14px; font-weight: 700; display: flex; align-items: center; letter-spacing: -0.01em; }
.ps-meta { display: flex; align-items: center; gap: 8px; }
.ps-branch { font-size: 11px; font-weight: 600; background: var(--bg3); padding: 4px 10px; border-radius: 100px; display: inline-flex; align-items: center; color: var(--text-sub); }
.ps-commit { font-size: 11px; color: var(--muted); background: var(--bg3); padding: 4px 10px; border-radius: 6px; }

.pipe-flow { display: flex; flex-direction: column; gap: 0; }
.stage-wrap { display: flex; flex-direction: column; align-items: stretch; }
.stage-card { background: var(--bg3); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; transition: all .25s; }
.stage-done { background: #F0FDF4; border-color: #86EFAC; }
.stage-running { background: #EFF6FF; border-color: #93C5FD; }
.stage-fail { background: #FEF2F2; border-color: #FCA5A5; }

.stage-head { display: flex; align-items: center; gap: 12px; }
.stage-ic { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; flex-shrink: 0; background: var(--bg4); color: var(--muted); }
.si-done { background: #10B981; color: #fff; }
.si-running { background: #0064FF; color: #fff; }
.si-fail { background: #EF4444; color: #fff; }
.stage-info { flex: 1; min-width: 0; }
.stage-name { font-size: 14px; font-weight: 700; color: var(--text); letter-spacing: -0.01em; }
.stage-sub { font-size: 11px; color: var(--muted); margin-top: 2px; font-family: 'JetBrains Mono', monospace; }
.stage-time { font-size: 12px; color: var(--muted); font-weight: 600; }
.stage-wait { opacity: 0.5; }
.stage-arrow { display: flex; justify-content: center; align-items: center; color: var(--faint); padding: 4px 0; }

/* 디바이스 그리드 (deploy/test 단계) */
.device-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,.5); }
.dev-chip { display: flex; align-items: center; gap: 5px; padding: 5px 8px; background: #fff; border-radius: 6px; font-size: 10.5px; font-weight: 600; color: var(--text-sub); }
.dev-chip .dc-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--muted); flex-shrink: 0; }
.dc-deploying .dc-dot { background: #0064FF; animation: pulse 1s infinite; }
.dc-deployed .dc-dot { background: #10B981; }
.dc-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
@keyframes pulse { 50% { opacity: 0.4; } }

.dev-result { background: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; display: flex; flex-direction: column; gap: 3px; transition: all .2s; }
.dr-pass { border-color: #86EFAC; background: #F0FDF4; }
.dr-fail { border-color: #FCA5A5; background: #FEF2F2; }
.dr-running { border-color: #93C5FD; background: #EFF6FF; }
.dr-head { display: flex; justify-content: space-between; align-items: center; }
.dr-name { font-size: 11px; font-weight: 700; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dr-mark { font-size: 11px; font-weight: 800; }
.dr-pass .dr-mark { color: #10B981; }
.dr-fail .dr-mark { color: #EF4444; }
.dr-running .dr-mark { color: #0064FF; }
.dr-stats { font-size: 10px; color: var(--muted); font-weight: 600; }

/* 최종 결과 */
.final-result { display: flex; align-items: center; gap: 14px; margin-top: 20px; padding: 18px 22px; border-radius: 12px; }
.fr-pass { background: #D1FAE5; border: 1px solid #86EFAC; }
.fr-fail { background: #FEE2E2; border: 1px solid #FCA5A5; }
.fr-ic { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 800; color: #fff; flex-shrink: 0; }
.fr-pass .fr-ic { background: #10B981; }
.fr-fail .fr-ic { background: #EF4444; }
.fr-body { flex: 1; min-width: 0; }
.fr-title { font-size: 15px; font-weight: 700; margin-bottom: 2px; letter-spacing: -0.01em; }
.fr-pass .fr-title { color: #065F46; }
.fr-fail .fr-title { color: #991B1B; }
.fr-sub { font-size: 12px; color: var(--text-sub); }
.btn-ghost { background: #fff; border: 1px solid var(--border2); padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit; }
.btn-ghost:hover { background: var(--bg3); }

/* 로그 섹션 */
.logs-section { background: #0F172A; color: #E2E8F0; border-radius: 16px; display: flex; flex-direction: column; min-height: 500px; max-height: 700px; font-family: 'JetBrains Mono', monospace; }
.logs-head { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #1E293B; }
.logs-title { font-size: 12px; font-weight: 700; display: flex; align-items: center; }
.logs-meta { font-size: 11px; color: #64748B; }
.logs-body { flex: 1; overflow-y: auto; padding: 12px 20px; }
.log-line { display: grid; grid-template-columns: 72px 16px 1fr; gap: 8px; align-items: start; padding: 3px 0; font-size: 11.5px; line-height: 1.5; }
.log-time { color: #475569; }
.log-arrow { font-weight: 700; }
.log-info .log-arrow { color: #64748B; }
.log-run .log-arrow { color: #06B6D4; }
.log-success .log-arrow { color: #10B981; }
.log-error .log-arrow { color: #F04452; }
.log-info .log-msg { color: #94A3B8; }
.log-run .log-msg { color: #67E8F9; }
.log-success .log-msg { color: #86EFAC; }
.log-error .log-msg { color: #FCA5A5; }
.log-empty { padding: 40px 20px; text-align: center; color: #475569; font-size: 12px; }

/* 히스토리 */
.history-section { background: #fff; border: 1px solid var(--border); border-radius: 16px; padding: 24px; margin-bottom: 24px; }
.hs-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.hs-title { font-size: 15px; font-weight: 700; letter-spacing: -0.01em; }
.hs-meta { font-size: 12px; color: var(--muted); }
.hs-list { display: flex; flex-direction: column; }
.hs-row { display: grid; grid-template-columns: 24px 54px 60px 1fr 110px 70px 70px; gap: 14px; align-items: center; padding: 12px 10px; border-bottom: 1px solid var(--border); font-size: 13px; transition: background .15s; cursor: pointer; }
.hs-row:last-child { border-bottom: none; }
.hs-row:hover { background: var(--bg3); border-radius: 8px; }
.hs-ic { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 800; color: #fff; }
.hsi-pass { background: #10B981; }
.hsi-fail { background: #EF4444; }
.hs-run { font-size: 12px; color: var(--muted); font-weight: 700; }
.hs-branch { font-size: 11px; background: var(--bg3); padding: 3px 8px; border-radius: 100px; color: var(--text-sub); font-weight: 600; text-align: center; }
.hs-commit { display: flex; align-items: center; gap: 10px; overflow: hidden; }
.hs-hash { font-size: 11px; color: var(--primary); background: var(--primary-dim); padding: 2px 6px; border-radius: 4px; font-weight: 700; flex-shrink: 0; }
.hs-msg { font-size: 13px; color: var(--text); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hs-devices { font-size: 11px; color: var(--text-sub); text-align: right; }
.hs-time { font-size: 11px; color: var(--muted); text-align: right; }
.hs-when { font-size: 11px; color: var(--muted); text-align: right; }

/* YAML */
.yaml-section { background: #fff; border: 1px solid var(--border); border-radius: 16px; padding: 24px; }
.ys-head { margin-bottom: 16px; }
.ys-title { font-size: 13px; font-weight: 700; display: flex; align-items: center; letter-spacing: -0.01em; }
.ys-sub { font-size: 12px; color: var(--muted); margin-top: 4px; margin-left: 20px; }
.yaml-code { background: #0F172A; color: #E2E8F0; padding: 20px 24px; border-radius: 12px; font-family: 'JetBrains Mono', monospace; font-size: 12px; line-height: 1.7; overflow-x: auto; user-select: text; -webkit-user-select: text; }
.yml-key { color: #67E8F9; }

@media (max-width: 1024px) {
  .main-grid { grid-template-columns: 1fr; }
  .summary-bar { grid-template-columns: repeat(2, 1fr); }
  .hs-row { grid-template-columns: 24px 50px 1fr 70px; }
  .hs-row > *:nth-child(3), .hs-row > *:nth-child(5), .hs-row > *:nth-child(6) { display: none; }
  .device-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>