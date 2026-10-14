<template>
  <div v-if="show" class="runner-overlay" @click.self="close">
    <div class="runner-modal">
      <!-- 헤더 -->
      <div class="rm-header">
        <div class="rm-head-left">
          <div class="rm-live-dot"></div>
          <div>
            <div class="rm-title">{{ currentScenario.name }}</div>
            <div class="rm-sub">{{ currentScenario.description }}</div>
          </div>
        </div>
        <div class="rm-head-right">
          <div class="rm-status" :class="'rs-'+status">
            <span v-if="status==='running'" class="rs-spin"></span>
            <span v-else-if="status==='pass'">✓</span>
            <span v-else-if="status==='fail'">✕</span>
            {{ statusLabel }}
          </div>
          <button class="rm-close" @click="close">✕</button>
        </div>
      </div>

      <div class="rm-body">
        <!-- 좌측: 가상 브라우저 -->
        <div class="rm-browser">
          <div class="browser-chrome">
            <div class="chrome-btns">
              <span class="cb-dot cb-red"></span>
              <span class="cb-dot cb-yellow"></span>
              <span class="cb-dot cb-green"></span>
            </div>
            <div class="chrome-url">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style="margin-right:6px"><path d="M4 5V3a2 2 0 014 0v2M3 5h6v5H3V5z" stroke="currentColor" stroke-width="1.3"/></svg>
              <span class="url-text">{{ currentPage.url }}</span>
            </div>
          </div>

          <div class="browser-viewport">
            <!-- 로그인 페이지 -->
            <div v-if="currentPage.type==='login'" class="demo-page">
              <div class="dp-brand">
                <div class="dp-logo">QA</div>
                <div class="dp-site">Demo Service</div>
              </div>
              <h2 class="dp-title">로그인</h2>
              <div class="dp-form">
                <label class="dp-label">이메일</label>
                <div class="dp-input" :class="{focused: focusField==='email'}">
                  {{ inputs.email }}<span v-if="focusField==='email'" class="cursor">|</span>
                </div>
                <label class="dp-label">비밀번호</label>
                <div class="dp-input" :class="{focused: focusField==='password'}">
                  {{ '•'.repeat(inputs.password.length) }}<span v-if="focusField==='password'" class="cursor">|</span>
                </div>
                <button class="dp-btn" :class="{clicking: clickTarget==='loginBtn'}">
                  로그인
                </button>
              </div>
              <div v-if="pageSuccess" class="dp-success">
                <div class="dp-success-ic">✓</div>
                로그인 성공 — 대시보드로 이동
              </div>
            </div>

            <!-- 회원가입 페이지 -->
            <div v-else-if="currentPage.type==='signup'" class="demo-page">
              <div class="dp-brand">
                <div class="dp-logo">QA</div>
                <div class="dp-site">Demo Service</div>
              </div>
              <h2 class="dp-title">회원가입</h2>
              <div class="dp-form">
                <label class="dp-label">이름</label>
                <div class="dp-input" :class="{focused: focusField==='name'}">
                  {{ inputs.name }}<span v-if="focusField==='name'" class="cursor">|</span>
                </div>
                <label class="dp-label">이메일</label>
                <div class="dp-input" :class="{focused: focusField==='email'}">
                  {{ inputs.email }}<span v-if="focusField==='email'" class="cursor">|</span>
                </div>
                <label class="dp-label">비밀번호</label>
                <div class="dp-input" :class="{focused: focusField==='password'}">
                  {{ '•'.repeat(inputs.password.length) }}<span v-if="focusField==='password'" class="cursor">|</span>
                </div>
                <div class="dp-check" :class="{checked: inputs.agreed, clicking: clickTarget==='agreeBox'}">
                  <div class="dp-check-box">
                    <span v-if="inputs.agreed">✓</span>
                  </div>
                  <span>이용약관에 동의합니다</span>
                </div>
                <button class="dp-btn" :class="{clicking: clickTarget==='signupBtn'}">
                  가입하기
                </button>
              </div>
              <div v-if="pageSuccess" class="dp-success">
                <div class="dp-success-ic">✓</div>
                회원가입 완료 — 환영합니다
              </div>
            </div>

            <!-- 결제 페이지 -->
            <div v-else-if="currentPage.type==='payment'" class="demo-page demo-payment">
              <div class="dp-brand">
                <div class="dp-logo">QA</div>
                <div class="dp-site">Demo Service</div>
              </div>
              <h2 class="dp-title">결제하기</h2>
              <div class="pay-cart">
                <div class="cart-item">
                  <div class="cart-name">QA Hub Pro Plan</div>
                  <div class="cart-price">₩29,000</div>
                </div>
              </div>
              <div class="dp-form">
                <label class="dp-label">카드 번호</label>
                <div class="dp-input" :class="{focused: focusField==='cardNumber'}">
                  {{ inputs.cardNumber }}<span v-if="focusField==='cardNumber'" class="cursor">|</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
                  <div>
                    <label class="dp-label">유효기간</label>
                    <div class="dp-input" :class="{focused: focusField==='cardExpiry'}">
                      {{ inputs.cardExpiry }}<span v-if="focusField==='cardExpiry'" class="cursor">|</span>
                    </div>
                  </div>
                  <div>
                    <label class="dp-label">CVC</label>
                    <div class="dp-input" :class="{focused: focusField==='cardCvc'}">
                      {{ inputs.cardCvc }}<span v-if="focusField==='cardCvc'" class="cursor">|</span>
                    </div>
                  </div>
                </div>
                <button class="dp-btn dp-pay-btn" :class="{clicking: clickTarget==='payBtn'}">
                  ₩29,000 결제하기
                </button>
              </div>
              <div v-if="pageSuccess" class="dp-success">
                <div class="dp-success-ic">✓</div>
                결제 완료 — 영수증이 이메일로 발송됨
              </div>
            </div>

            <!-- 로딩 화면 -->
            <div v-if="loading" class="loading-overlay">
              <div class="loading-spinner"></div>
              <div class="loading-text">페이지 이동 중...</div>
            </div>
          </div>
        </div>

        <!-- 우측: 실시간 로그 -->
        <div class="rm-logs">
          <div class="logs-head">
            <div class="logs-title">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style="margin-right:5px"><path d="M3 2v8l3-2 3 2V2z" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>
              Playwright Logs
            </div>
            <div class="logs-meta mono">{{ elapsedTime }}s</div>
          </div>
          <div class="logs-body" ref="logsBody">
            <div v-for="(log, i) in logs" :key="i" class="log-line" :class="'log-'+log.level">
              <span class="log-time mono">{{ log.time }}</span>
              <span class="log-icon">
                <span v-if="log.level==='info'">›</span>
                <span v-else-if="log.level==='action'">▸</span>
                <span v-else-if="log.level==='success'">✓</span>
                <span v-else-if="log.level==='error'">✕</span>
              </span>
              <span class="log-msg">{{ log.msg }}</span>
            </div>
          </div>
          <div v-if="finalResult" class="logs-footer" :class="'lf-'+finalResult.status">
            <div class="lf-top">
              <div class="lf-ic">{{ finalResult.status==='pass' ? '✓' : '✕' }}</div>
              <div class="lf-txt">
                <div class="lf-label">{{ finalResult.status==='pass' ? 'All Scenarios Passed' : 'Test Failed' }}</div>
                <div class="lf-sub">{{ finalResult.passCount }}/{{ finalResult.total }} 통과 · {{ elapsedTime }}s</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 하단 컨트롤 -->
      <div class="rm-footer">
        <div class="scenario-tabs">
          <div v-for="(s, i) in scenarios" :key="s.name"
            class="st-pill" :class="{active: scenarioIndex===i, done: s.result}"
            @click="jumpTo(i)">
            <span class="st-num">{{ (i+1).toString().padStart(2, '0') }}</span>
            {{ s.name }}
            <span v-if="s.result==='pass'" class="st-mark pass">✓</span>
            <span v-else-if="s.result==='fail'" class="st-mark fail">✕</span>
          </div>
        </div>
        <div class="rm-actions">
          <button v-if="status==='idle' || status==='pass' || status==='fail'" class="btn-replay" @click="replay">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 6a4 4 0 017-2.5M10 6a4 4 0 01-7 2.5M9 1v3H6M3 11V8h3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
            다시 실행
          </button>
          <button v-if="status==='running'" class="btn-stop" @click="stop">정지</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AutomationRunner',
  props: {
    show: { type: Boolean, default: false },
  },
  emits: ['close'],
  data() {
    return {
      status: 'idle', // idle / running / pass / fail
      scenarioIndex: 0,
      scenarios: [
        {
          name: '로그인 테스트',
          description: '이메일/비밀번호로 로그인하고 성공 응답을 확인합니다',
          pages: [
            { type: 'login', url: 'https://demo.qa-hub.app/login' }
          ],
          steps: [
            { kind: 'navigate', url: 'https://demo.qa-hub.app/login', log: 'page.goto("https://demo.qa-hub.app/login")' },
            { kind: 'wait', ms: 400, log: 'await page.waitForLoadState("networkidle")' },
            { kind: 'type', field: 'email', text: 'test@qa-hub.app', log: 'await page.fill("input#email", "test@qa-hub.app")' },
            { kind: 'type', field: 'password', text: 'Password123!', log: 'await page.fill("input#password", "Password123!")' },
            { kind: 'click', target: 'loginBtn', log: 'await page.click("button[type=\\"submit\\"]")' },
            { kind: 'wait', ms: 600, log: 'await page.waitForURL("**/dashboard")' },
            { kind: 'success', log: 'expect(page.url()).toContain("/dashboard") ✓' },
          ],
          result: null,
        },
        {
          name: '회원가입 테스트',
          description: '신규 사용자 가입 플로우 전체를 검증합니다',
          pages: [
            { type: 'signup', url: 'https://demo.qa-hub.app/signup' }
          ],
          steps: [
            { kind: 'navigate', url: 'https://demo.qa-hub.app/signup', log: 'page.goto("https://demo.qa-hub.app/signup")' },
            { kind: 'wait', ms: 400, log: 'await page.waitForLoadState("networkidle")' },
            { kind: 'type', field: 'name', text: '박수빈', log: 'await page.fill("input#name", "박수빈")' },
            { kind: 'type', field: 'email', text: 'new.user@qa-hub.app', log: 'await page.fill("input#email", "new.user@qa-hub.app")' },
            { kind: 'type', field: 'password', text: 'SecurePass!2026', log: 'await page.fill("input#password", "SecurePass!2026")' },
            { kind: 'check', target: 'agreeBox', log: 'await page.check("input#agree-terms")' },
            { kind: 'click', target: 'signupBtn', log: 'await page.click("button#signup-submit")' },
            { kind: 'wait', ms: 700, log: 'await page.waitForSelector(".welcome-message")' },
            { kind: 'success', log: 'expect(page.locator(".welcome-message")).toBeVisible() ✓' },
          ],
          result: null,
        },
        {
          name: '결제 플로우 테스트',
          description: 'Pro 플랜 결제 전체 흐름을 자동화합니다',
          pages: [
            { type: 'payment', url: 'https://demo.qa-hub.app/checkout' }
          ],
          steps: [
            { kind: 'navigate', url: 'https://demo.qa-hub.app/checkout', log: 'page.goto("https://demo.qa-hub.app/checkout")' },
            { kind: 'wait', ms: 400, log: 'await page.waitForLoadState("networkidle")' },
            { kind: 'type', field: 'cardNumber', text: '4242 4242 4242 4242', log: 'await page.fill("input#card-number", "4242 4242 4242 4242")' },
            { kind: 'type', field: 'cardExpiry', text: '12/28', log: 'await page.fill("input#card-expiry", "12/28")' },
            { kind: 'type', field: 'cardCvc', text: '123', log: 'await page.fill("input#card-cvc", "123")' },
            { kind: 'click', target: 'payBtn', log: 'await page.click("button#pay-submit")' },
            { kind: 'wait', ms: 900, log: 'await page.waitForResponse(res => res.url().includes("/api/payment"))' },
            { kind: 'success', log: 'expect(response.status()).toBe(200) ✓ · 결제 승인 완료' },
          ],
          result: null,
        },
      ],
      currentPage: { type: 'login', url: 'https://demo.qa-hub.app/login' },
      inputs: { email: '', password: '', name: '', cardNumber: '', cardExpiry: '', cardCvc: '', agreed: false },
      focusField: null,
      clickTarget: null,
      loading: false,
      pageSuccess: false,
      logs: [],
      startedAt: null,
      elapsedTime: '0.0',
      elapsedTimer: null,
      finalResult: null,
      stopped: false,
    }
  },
  computed: {
    currentScenario() { return this.scenarios[this.scenarioIndex] || this.scenarios[0] },
    statusLabel() {
      return ({ idle: 'Ready', running: 'Running', pass: 'Passed', fail: 'Failed' })[this.status]
    },
  },
  watch: {
    show(v) {
      if (v) this.start()
    },
  },
  methods: {
    close() {
      this.stop()
      this.$emit('close')
    },
    reset() {
      this.scenarios.forEach(s => s.result = null)
      this.scenarioIndex = 0
      this.resetScenario()
      this.logs = []
      this.finalResult = null
      this.stopped = false
    },
    resetScenario() {
      this.inputs = { email: '', password: '', name: '', cardNumber: '', cardExpiry: '', cardCvc: '', agreed: false }
      this.focusField = null
      this.clickTarget = null
      this.loading = false
      this.pageSuccess = false
    },
    async start() {
      this.reset()
      this.status = 'running'
      this.startedAt = Date.now()
      this.elapsedTimer = setInterval(() => {
        this.elapsedTime = ((Date.now() - this.startedAt) / 1000).toFixed(1)
      }, 100)

      for (let i = 0; i < this.scenarios.length; i++) {
        if (this.stopped) break
        this.scenarioIndex = i
        this.resetScenario()
        this.currentPage = this.scenarios[i].pages[0]
        this.addLog('info', `━━━ ${this.scenarios[i].name} 시작 ━━━`)
        await this.sleep(300)
        const passed = await this.runScenario(this.scenarios[i])
        this.scenarios[i].result = passed ? 'pass' : 'fail'
        this.addLog(passed ? 'success' : 'error', passed ? 'Scenario PASSED' : 'Scenario FAILED')
        if (!passed) break
        await this.sleep(500)
      }

      clearInterval(this.elapsedTimer)
      const passCount = this.scenarios.filter(s => s.result === 'pass').length
      const total = this.scenarios.length
      const allPassed = passCount === total
      this.status = allPassed ? 'pass' : 'fail'
      this.finalResult = { status: this.status, passCount, total }
    },
    async runScenario(scenario) {
      for (const step of scenario.steps) {
        if (this.stopped) return false
        await this.runStep(step)
      }
      return true
    },
    async runStep(step) {
      this.addLog('action', step.log)
      if (step.kind === 'navigate') {
        this.loading = true
        await this.sleep(400)
        this.loading = false
      } else if (step.kind === 'wait') {
        await this.sleep(step.ms)
      } else if (step.kind === 'type') {
        this.focusField = step.field
        await this.sleep(150)
        for (const ch of step.text) {
          if (this.stopped) return
          this.inputs[step.field] += ch
          await this.sleep(45 + Math.random() * 40)
        }
        await this.sleep(150)
        this.focusField = null
      } else if (step.kind === 'check') {
        this.clickTarget = step.target
        await this.sleep(150)
        this.inputs.agreed = true
        await this.sleep(100)
        this.clickTarget = null
      } else if (step.kind === 'click') {
        this.clickTarget = step.target
        await this.sleep(200)
        this.clickTarget = null
      } else if (step.kind === 'success') {
        this.addLog('success', step.log)
        this.pageSuccess = true
        await this.sleep(500)
      }
    },
    addLog(level, msg) {
      const d = new Date()
      const time = d.toTimeString().slice(0, 8)
      this.logs.push({ level, msg, time })
      this.$nextTick(() => {
        if (this.$refs.logsBody) this.$refs.logsBody.scrollTop = this.$refs.logsBody.scrollHeight
      })
    },
    sleep(ms) { return new Promise(r => setTimeout(r, ms)) },
    stop() {
      this.stopped = true
      if (this.elapsedTimer) clearInterval(this.elapsedTimer)
    },
    replay() {
      this.start()
    },
    jumpTo(i) {
      // 완료된 시나리오만 되돌아보기 가능
      if (this.status === 'running') return
      if (!this.scenarios[i].result) return
      this.scenarioIndex = i
      this.resetScenario()
      this.currentPage = this.scenarios[i].pages[0]
      this.pageSuccess = true
      // 모든 input 채워진 상태로
      const sc = this.scenarios[i]
      for (const step of sc.steps) {
        if (step.kind === 'type') this.inputs[step.field] = step.text
        if (step.kind === 'check') this.inputs.agreed = true
      }
    },
  },
}
</script>

<style scoped>
.runner-overlay {
  position: fixed; inset: 0; z-index: 500;
  background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
  font-family: 'Pretendard Variable', Pretendard, sans-serif;
  user-select: none; -webkit-user-select: none;
}
.runner-modal {
  background: #fff; border-radius: 16px; overflow: hidden;
  width: 100%; max-width: 1100px; height: 85vh; max-height: 760px;
  display: flex; flex-direction: column;
  box-shadow: 0 24px 70px rgba(0,0,0,0.3);
}

.rm-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 24px; border-bottom: 1px solid #E5E8EB;
}
.rm-head-left { display: flex; align-items: center; gap: 12px; }
.rm-live-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: #06C755; box-shadow: 0 0 10px #06C755;
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 50% { opacity: .4; } }
.rm-title { font-size: 15px; font-weight: 700; letter-spacing: -0.02em; }
.rm-sub { font-size: 12px; color: #64748B; margin-top: 2px; }
.rm-head-right { display: flex; align-items: center; gap: 10px; }
.rm-status {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 100px;
  font-size: 12px; font-weight: 700;
}
.rs-idle { background: #F1F5F9; color: #475569; }
.rs-running { background: #DBEAFE; color: #1E40AF; }
.rs-pass { background: #D1FAE5; color: #065F46; }
.rs-fail { background: #FEE2E2; color: #991B1B; }
.rs-spin {
  display: inline-block; width: 10px; height: 10px;
  border: 2px solid currentColor; border-top-color: transparent;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.rm-close {
  background: transparent; border: none; cursor: pointer;
  width: 32px; height: 32px; border-radius: 8px;
  color: #64748B; font-size: 14px;
}
.rm-close:hover { background: #F1F5F9; }

.rm-body { flex: 1; display: grid; grid-template-columns: 1.3fr 1fr; min-height: 0; }

/* 가상 브라우저 */
.rm-browser { background: #F6F7F9; display: flex; flex-direction: column; min-height: 0; }
.browser-chrome {
  background: #E5E8EB; padding: 10px 14px;
  display: flex; align-items: center; gap: 12px;
  border-bottom: 1px solid #D1D5DB;
}
.chrome-btns { display: flex; gap: 6px; }
.cb-dot { width: 10px; height: 10px; border-radius: 50%; }
.cb-red { background: #FF5F57; }
.cb-yellow { background: #FFBD2E; }
.cb-green { background: #28C840; }
.chrome-url {
  flex: 1; background: #fff; border-radius: 6px;
  padding: 6px 12px; font-size: 12px; color: #64748B;
  display: flex; align-items: center;
  font-family: 'JetBrains Mono', monospace;
}
.url-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.browser-viewport {
  flex: 1; overflow-y: auto;
  padding: 40px 32px; position: relative;
  background: #fff;
}

.demo-page { max-width: 400px; margin: 0 auto; }
.dp-brand {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 32px; justify-content: center;
}
.dp-logo {
  background: linear-gradient(135deg, #0064FF, #06B6D4);
  color: #fff; width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px; font-weight: 800; font-size: 12px;
}
.dp-site { font-size: 15px; font-weight: 700; letter-spacing: -0.02em; }
.dp-title {
  font-size: 24px; font-weight: 800; letter-spacing: -0.03em;
  text-align: center; margin-bottom: 28px;
}
.dp-form { display: flex; flex-direction: column; gap: 14px; }
.dp-label { font-size: 12px; font-weight: 600; color: #475569; margin-bottom: -8px; }
.dp-input {
  background: #F6F7F9; border: 1.5px solid #E5E8EB;
  border-radius: 10px; padding: 11px 14px;
  font-size: 14px; color: #0F172A; min-height: 42px;
  font-family: 'JetBrains Mono', monospace;
  display: flex; align-items: center;
  transition: all .15s;
}
.dp-input.focused {
  border-color: #0064FF; background: #fff;
  box-shadow: 0 0 0 3px rgba(0,100,255,0.1);
}
.cursor { display: inline-block; width: 1px; background: #0064FF; height: 16px; margin-left: 1px; animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0; } }

.dp-btn {
  background: #0064FF; color: #fff; border: none;
  padding: 13px; border-radius: 10px;
  font-size: 14px; font-weight: 700; cursor: pointer;
  margin-top: 8px; transition: all .1s;
  font-family: inherit;
}
.dp-btn.clicking {
  transform: scale(0.97);
  box-shadow: 0 0 0 4px rgba(0,100,255,0.3);
}
.dp-pay-btn { background: #06C755; }
.dp-pay-btn.clicking { box-shadow: 0 0 0 4px rgba(6,199,85,0.3); }

.dp-check { display: flex; align-items: center; gap: 10px; margin-top: 6px; font-size: 13px; color: #475569; cursor: pointer; }
.dp-check.clicking { background: #EFF6FF; border-radius: 6px; padding: 4px 6px; margin: 6px -6px 0; }
.dp-check-box {
  width: 18px; height: 18px; border: 1.5px solid #CBD5E1;
  border-radius: 4px; display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 11px; font-weight: 700;
  transition: all .15s;
}
.dp-check.checked .dp-check-box { background: #0064FF; border-color: #0064FF; }

.dp-success {
  margin-top: 24px; padding: 16px;
  background: #D1FAE5; border: 1px solid #86EFAC;
  border-radius: 10px; display: flex; align-items: center; gap: 10px;
  font-size: 13px; font-weight: 600; color: #065F46;
  animation: slideDown .3s ease;
}
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.dp-success-ic {
  width: 24px; height: 24px; border-radius: 50%;
  background: #065F46; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 800;
}

.pay-cart {
  background: #F6F7F9; border-radius: 10px;
  padding: 14px 16px; margin-bottom: 20px;
  display: flex; justify-content: space-between; align-items: center;
}
.cart-name { font-size: 13px; font-weight: 600; }
.cart-price { font-size: 15px; font-weight: 800; color: #06C755; font-family: 'Inter', sans-serif; }

/* 로딩 */
.loading-overlay {
  position: absolute; inset: 0;
  background: rgba(255,255,255,0.9);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px;
}
.loading-spinner {
  width: 32px; height: 32px;
  border: 3px solid #E5E8EB; border-top-color: #0064FF;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.loading-text { font-size: 12px; color: #64748B; font-weight: 500; }

/* 로그 패널 */
.rm-logs {
  background: #0F172A; color: #E2E8F0;
  display: flex; flex-direction: column; min-height: 0;
  font-family: 'JetBrains Mono', monospace;
}
.logs-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 20px; border-bottom: 1px solid #1E293B;
}
.logs-title { font-size: 12px; font-weight: 700; display: flex; align-items: center; }
.logs-meta { font-size: 11px; color: #64748B; }

.logs-body { flex: 1; overflow-y: auto; padding: 12px 20px; }
.log-line {
  display: grid; grid-template-columns: 72px 16px 1fr;
  gap: 8px; align-items: start;
  padding: 4px 0; font-size: 11.5px; line-height: 1.5;
}
.log-time { color: #475569; }
.log-icon { font-weight: 700; }
.log-info .log-icon { color: #64748B; }
.log-action .log-icon { color: #0064FF; }
.log-success .log-icon { color: #06C755; }
.log-error .log-icon { color: #F04452; }
.log-info .log-msg { color: #94A3B8; }
.log-action .log-msg { color: #CBD5E1; }
.log-success .log-msg { color: #86EFAC; }
.log-error .log-msg { color: #FCA5A5; }

.logs-footer { padding: 16px 20px; border-top: 1px solid #1E293B; }
.lf-top { display: flex; align-items: center; gap: 12px; }
.lf-ic {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 800;
}
.lf-pass .lf-ic { background: #065F46; color: #86EFAC; }
.lf-fail .lf-ic { background: #991B1B; color: #FCA5A5; }
.lf-label { font-size: 13px; font-weight: 700; margin-bottom: 2px; }
.lf-pass .lf-label { color: #86EFAC; }
.lf-fail .lf-label { color: #FCA5A5; }
.lf-sub { font-size: 11px; color: #94A3B8; }

/* 하단 */
.rm-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 20px; border-top: 1px solid #E5E8EB; background: #F6F7F9;
  gap: 12px; flex-wrap: wrap;
}
.scenario-tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.st-pill {
  display: flex; align-items: center; gap: 7px;
  background: #fff; border: 1px solid #D1D5DB;
  padding: 7px 13px; border-radius: 100px;
  font-size: 12px; font-weight: 600; color: #475569;
  cursor: pointer; transition: all .15s;
}
.st-pill:hover { border-color: #0064FF; }
.st-pill.active { background: #0064FF; color: #fff; border-color: #0064FF; }
.st-pill.done { border-color: #06C755; }
.st-num { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #94A3B8; }
.st-pill.active .st-num { color: rgba(255,255,255,0.7); }
.st-mark { font-size: 10px; font-weight: 800; }
.st-mark.pass { color: #06C755; }
.st-pill.active .st-mark.pass { color: #86EFAC; }
.st-mark.fail { color: #F04452; }

.rm-actions { display: flex; gap: 8px; }
.btn-replay, .btn-stop {
  display: inline-flex; align-items: center; gap: 6px;
  background: #fff; border: 1px solid #D1D5DB;
  padding: 8px 16px; border-radius: 8px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  font-family: inherit;
}
.btn-replay:hover { background: #0064FF; color: #fff; border-color: #0064FF; }
.btn-stop { color: #F04452; border-color: #FCA5A5; }
.btn-stop:hover { background: #F04452; color: #fff; }

@media (max-width: 900px) {
  .runner-modal { height: 95vh; }
  .rm-body { grid-template-columns: 1fr; grid-template-rows: 1fr 1fr; }
  .rm-logs { max-height: 300px; }
}
</style>