<template>
  <div class="farm-page">
    <!-- Header -->
    <section class="farm-header">
      <div class="fh-inner">
        <div class="fh-left">
          <div class="fh-eyebrow">Device Farm</div>
          <h1 class="fh-title">7대의 디바이스가<br>24/7 자동 테스트 중</h1>
          <p class="fh-sub">
            iOS · Android · Tablet 전체 플랫폼의 실제 디바이스를 상시 연결하여,
            머지 즉시 자동 테스트를 돌리고 미러링으로 실시간 상황을 확인합니다.
          </p>
        </div>
        <div class="fh-right">
          <div class="stat-tile">
            <div class="st-icon" style="background:#DBEAFE;color:#1E40AF">📱</div>
            <div>
              <div class="st-val">7</div>
              <div class="st-lab">연결 디바이스</div>
            </div>
          </div>
          <div class="stat-tile">
            <div class="st-icon" style="background:#D1FAE5;color:#065F46">⚡</div>
            <div>
              <div class="st-val mono">{{ runningCount }}</div>
              <div class="st-lab">실행 중</div>
            </div>
          </div>
          <div class="stat-tile">
            <div class="st-icon" style="background:#F0FDF4;color:#059669">✓</div>
            <div>
              <div class="st-val mono">{{ idleCount }}</div>
              <div class="st-lab">대기</div>
            </div>
          </div>
          <div class="stat-tile">
            <div class="st-icon" style="background:#FEE2E2;color:#991B1B">×</div>
            <div>
              <div class="st-val mono">{{ offlineCount }}</div>
              <div class="st-lab">오프라인</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Toolbar -->
    <section class="farm-toolbar">
      <div class="ft-inner">
        <div class="ft-tabs">
          <button
            v-for="t in tabs" :key="t.k"
            class="ft-tab" :class="{active: tab===t.k}"
            @click="tab=t.k"
          >
            {{ t.label }}
            <span class="ft-count">{{ t.count }}</span>
          </button>
        </div>
        <div class="ft-right">
          <div class="ft-search">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.5"/>
              <path d="M9.5 9.5l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <input v-model="query" placeholder="디바이스 검색..." />
          </div>
          <button class="ft-btn" @click="refresh">
            <span :class="{spinning: refreshing}">↻</span>
            새로고침
          </button>
        </div>
      </div>
    </section>

    <!-- Device Grid -->
    <section class="farm-grid-section">
      <div class="fg-inner">
        <div class="dev-grid">
          <div
            v-for="d in filteredDevices" :key="d.id"
            class="dev-card"
            :class="['dev-'+d.status]"
          >
            <!-- 상단 상태 바 -->
            <div class="dc-top">
              <div class="dc-platform">
                <span class="plat-badge" :class="'plat-'+d.platform">
                  {{ d.platform === 'ios' ? 'iOS' : d.platform === 'android' ? 'Android' : 'iPadOS' }}
                </span>
                <span class="dc-os mono">{{ d.os }}</span>
              </div>
              <div class="dc-status">
                <span class="status-dot" :class="'sd-'+d.status"></span>
                <span class="status-label">
                  {{ d.status === 'running' ? '실행 중' : d.status === 'idle' ? '대기' : '오프라인' }}
                </span>
              </div>
            </div>

            <!-- 디바이스 뷰 -->
            <div class="dc-phone">
              <div class="phone-frame" :class="'frame-'+d.platform">
                <div class="phone-screen">
                  <!-- 실행 중 -->
                  <div v-if="d.status === 'running'" class="screen-running">
                    <div class="sr-app-header">
                      <div class="sr-time mono">{{ clock }}</div>
                      <div class="sr-icons">
                        <span>●●●</span>
                        <span>📶</span>
                        <span>🔋</span>
                      </div>
                    </div>
                    <div class="sr-content">
                      <div class="sr-badge">
                        <span class="sr-rec"></span>
                        REC
                      </div>
                      <div class="sr-test-name">{{ d.currentTest }}</div>
                      <div class="sr-fake-ui">
                        <div class="fake-row" v-for="n in 4" :key="n"></div>
                        <div class="fake-btn" :class="{active: cursorOn}"></div>
                        <div class="fake-row" v-for="n in 2" :key="n"></div>
                      </div>
                      <div v-if="cursorOn" class="sr-cursor" :style="{left: cursorX+'%', top: cursorY+'%'}"></div>
                    </div>
                  </div>
                  <!-- 대기 -->
                  <div v-else-if="d.status === 'idle'" class="screen-idle">
                    <div class="idle-time mono">{{ clock }}</div>
                    <div class="idle-icon">💤</div>
                    <div class="idle-label">Ready</div>
                  </div>
                  <!-- 오프라인 -->
                  <div v-else class="screen-offline">
                    <div class="off-icon">⊘</div>
                    <div class="off-label">Offline</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 디바이스 정보 -->
            <div class="dc-info">
              <div class="dc-name">{{ d.name }}</div>
              <div class="dc-meta mono">{{ d.model }} · {{ d.serial }}</div>
            </div>

            <!-- 메트릭 -->
            <div class="dc-metrics">
              <div class="metric">
                <div class="m-label">배터리</div>
                <div class="m-bar">
                  <div class="m-fill" :style="{width: d.battery+'%', background: batteryColor(d.battery)}"></div>
                </div>
                <div class="m-val mono">{{ d.battery }}%</div>
              </div>
              <div class="metric">
                <div class="m-label">가동 시간</div>
                <div class="m-val mono m-single">{{ d.uptime }}</div>
              </div>
            </div>

            <!-- 현재 상태 상세 -->
            <div v-if="d.status === 'running'" class="dc-current">
              <div class="cur-label">현재 실행</div>
              <div class="cur-test mono">{{ d.currentTest }}</div>
              <div class="cur-progress">
                <div class="cp-fill" :style="{width: d.progress+'%'}"></div>
              </div>
              <div class="cur-foot">
                <span class="mono">{{ d.progress }}%</span>
                <span class="mono">{{ d.elapsed }}</span>
              </div>
            </div>
            <div v-else-if="d.status === 'idle'" class="dc-lastrun">
              <div class="cur-label">마지막 실행</div>
              <div class="lr-row">
                <span class="lr-dot" :class="d.lastResult === 'pass' ? 'lr-pass' : 'lr-fail'"></span>
                <span class="lr-name mono">{{ d.lastTest }}</span>
                <span class="lr-time mono">{{ d.lastTime }}</span>
              </div>
            </div>
            <div v-else class="dc-offline-note">
              <div class="offn-icon">⚠</div>
              <div>
                <div class="offn-title">연결 끊김</div>
                <div class="offn-sub mono">{{ d.offlineReason }}</div>
              </div>
            </div>

            <!-- Actions -->
            <div class="dc-actions">
              <button class="dca-btn dca-primary" @click="openMirror(d)" :disabled="d.status==='offline'">
                미러링 보기
              </button>
              <button class="dca-btn dca-ghost" @click="openDetail(d)">
                상세
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Mirror Modal -->
    <div v-if="mirrorDev" class="modal-overlay" @click.self="mirrorDev=null">
      <div class="mirror-modal">
        <div class="mm-head">
          <div class="mm-title">
            <span class="mm-dot" :class="'sd-'+mirrorDev.status"></span>
            {{ mirrorDev.name }} 미러링
          </div>
          <button class="mm-close" @click="mirrorDev=null">×</button>
        </div>
        <div class="mm-body">
          <div class="mm-phone">
            <div class="phone-frame-large" :class="'frame-'+mirrorDev.platform">
              <div class="phone-screen-large">
                <div v-if="mirrorDev.status === 'running'" class="screen-running screen-large">
                  <div class="sr-app-header">
                    <div class="sr-time mono">{{ clock }}</div>
                    <div class="sr-icons"><span>●●●</span><span>📶</span><span>🔋</span></div>
                  </div>
                  <div class="sr-content">
                    <div class="sr-badge"><span class="sr-rec"></span> REC</div>
                    <div class="sr-test-name">{{ mirrorDev.currentTest }}</div>
                    <div class="sr-fake-ui" style="scale:1.4;margin-top:30px">
                      <div class="fake-row" v-for="n in 4" :key="n"></div>
                      <div class="fake-btn" :class="{active: cursorOn}"></div>
                      <div class="fake-row" v-for="n in 2" :key="n"></div>
                    </div>
                  </div>
                </div>
                <div v-else class="screen-idle">
                  <div class="idle-time mono">{{ clock }}</div>
                  <div class="idle-icon">💤</div>
                  <div class="idle-label">Ready for test</div>
                </div>
              </div>
            </div>
          </div>
          <div class="mm-side">
            <div class="mms-section">
              <div class="mms-h">디바이스 정보</div>
              <div class="mms-row"><span>모델</span><span class="mono">{{ mirrorDev.model }}</span></div>
              <div class="mms-row"><span>OS</span><span class="mono">{{ mirrorDev.os }}</span></div>
              <div class="mms-row"><span>시리얼</span><span class="mono">{{ mirrorDev.serial }}</span></div>
              <div class="mms-row"><span>배터리</span><span class="mono">{{ mirrorDev.battery }}%</span></div>
              <div class="mms-row"><span>가동 시간</span><span class="mono">{{ mirrorDev.uptime }}</span></div>
            </div>
            <div v-if="mirrorDev.status==='running'" class="mms-section">
              <div class="mms-h">실행 로그</div>
              <div class="mms-log mono">
                <div v-for="(l, i) in mirrorLogs" :key="i" class="log-line">
                  <span class="ll-time">{{ l.t }}</span>
                  <span class="ll-text">{{ l.m }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="detailDev" class="modal-overlay" @click.self="detailDev=null">
      <div class="detail-modal">
        <div class="mm-head">
          <div class="mm-title">
            {{ detailDev.name }} · 최근 실행 이력
          </div>
          <button class="mm-close" @click="detailDev=null">×</button>
        </div>
        <div class="dm-body">
          <div class="dm-stats">
            <div class="dm-stat">
              <div class="dms-val mono">{{ detailDev.stats.total }}</div>
              <div class="dms-lab">총 실행</div>
            </div>
            <div class="dm-stat">
              <div class="dms-val mono" style="color:var(--green)">{{ detailDev.stats.passed }}</div>
              <div class="dms-lab">성공</div>
            </div>
            <div class="dm-stat">
              <div class="dms-val mono" style="color:var(--red)">{{ detailDev.stats.failed }}</div>
              <div class="dms-lab">실패</div>
            </div>
            <div class="dm-stat">
              <div class="dms-val mono">{{ detailDev.stats.rate }}%</div>
              <div class="dms-lab">성공률</div>
            </div>
          </div>
          <div class="dm-history">
            <div class="dmh-head">
              <div>테스트</div>
              <div>결과</div>
              <div>소요</div>
              <div>실행 시각</div>
            </div>
            <div class="dmh-row" v-for="(h, i) in detailDev.history" :key="i">
              <div class="mono dmh-name">{{ h.name }}</div>
              <div><span class="res-chip" :class="'rc-'+h.result">{{ h.result === 'pass' ? '성공' : '실패' }}</span></div>
              <div class="mono">{{ h.dur }}</div>
              <div class="mono dmh-time">{{ h.at }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const DEVICES = [
  {
    id: 'ip14', name: 'iPhone 14', model: 'A2882', serial: 'F2L...4X9',
    platform: 'ios', os: 'iOS 17.5', status: 'running',
    battery: 72, uptime: '14h 32m',
    currentTest: 'test_login_flow.py', progress: 68, elapsed: '00:48',
    lastTest: '', lastResult: '', lastTime: '',
    offlineReason: '',
    stats: { total: 1240, passed: 1198, failed: 42, rate: 96.6 },
    history: [
      { name: 'test_login_flow.py', result: 'pass', dur: '1m 12s', at: '17:08' },
      { name: 'test_payment_card.py', result: 'pass', dur: '2m 04s', at: '16:52' },
      { name: 'test_signup_email.py', result: 'fail', dur: '0m 48s', at: '16:30' },
      { name: 'test_push_notification.py', result: 'pass', dur: '1m 36s', at: '16:12' },
    ],
  },
  {
    id: 'ip15p', name: 'iPhone 15 Pro', model: 'A3101', serial: 'G8N...2K1',
    platform: 'ios', os: 'iOS 18.0', status: 'idle',
    battery: 94, uptime: '2d 06h',
    currentTest: '', progress: 0, elapsed: '',
    lastTest: 'test_video_playback.py', lastResult: 'pass', lastTime: '방금 전',
    offlineReason: '',
    stats: { total: 980, passed: 952, failed: 28, rate: 97.1 },
    history: [
      { name: 'test_video_playback.py', result: 'pass', dur: '3m 20s', at: '17:12' },
      { name: 'test_streaming_quality.py', result: 'pass', dur: '2m 48s', at: '16:40' },
      { name: 'test_chat_message.py', result: 'pass', dur: '1m 10s', at: '16:18' },
      { name: 'test_profile_edit.py', result: 'pass', dur: '0m 56s', at: '15:52' },
    ],
  },
  {
    id: 'ipad', name: 'iPad Air (5세대)', model: 'A2588', serial: 'DMP...9H3',
    platform: 'ipad', os: 'iPadOS 17.4', status: 'idle',
    battery: 100, uptime: '12h 08m',
    currentTest: '', progress: 0, elapsed: '',
    lastTest: 'test_landscape_mode.py', lastResult: 'pass', lastTime: '12분 전',
    offlineReason: '',
    stats: { total: 620, passed: 614, failed: 6, rate: 99.0 },
    history: [
      { name: 'test_landscape_mode.py', result: 'pass', dur: '1m 48s', at: '17:00' },
      { name: 'test_split_view.py', result: 'pass', dur: '2m 12s', at: '16:28' },
      { name: 'test_apple_pencil.py', result: 'pass', dur: '1m 24s', at: '15:50' },
    ],
  },
  {
    id: 'px7', name: 'Pixel 7', model: 'GVU6C', serial: '38241...',
    platform: 'android', os: 'Android 14', status: 'running',
    battery: 68, uptime: '1d 18h',
    currentTest: 'test_payment_flow.py', progress: 42, elapsed: '00:32',
    lastTest: '', lastResult: '', lastTime: '',
    offlineReason: '',
    stats: { total: 1512, passed: 1456, failed: 56, rate: 96.3 },
    history: [
      { name: 'test_payment_flow.py', result: 'pass', dur: '2m 10s', at: '17:04' },
      { name: 'test_fingerprint_auth.py', result: 'pass', dur: '0m 42s', at: '16:35' },
      { name: 'test_notification_permission.py', result: 'fail', dur: '1m 18s', at: '16:08' },
    ],
  },
  {
    id: 'px8', name: 'Pixel 8', model: 'GKWS6', serial: '41082...',
    platform: 'android', os: 'Android 15', status: 'idle',
    battery: 92, uptime: '08h 44m',
    currentTest: '', progress: 0, elapsed: '',
    lastTest: 'test_dark_mode.py', lastResult: 'pass', lastTime: '3분 전',
    offlineReason: '',
    stats: { total: 1120, passed: 1092, failed: 28, rate: 97.5 },
    history: [
      { name: 'test_dark_mode.py', result: 'pass', dur: '0m 52s', at: '17:13' },
      { name: 'test_biometric_login.py', result: 'pass', dur: '1m 24s', at: '16:50' },
      { name: 'test_push_action.py', result: 'pass', dur: '2m 02s', at: '16:20' },
    ],
  },
  {
    id: 'gs23', name: 'Galaxy S23', model: 'SM-S911N', serial: 'R58T...',
    platform: 'android', os: 'Android 14', status: 'running',
    battery: 54, uptime: '3d 02h',
    currentTest: 'test_login_social_kakao.py', progress: 86, elapsed: '01:12',
    lastTest: '', lastResult: '', lastTime: '',
    offlineReason: '',
    stats: { total: 1780, passed: 1702, failed: 78, rate: 95.6 },
    history: [
      { name: 'test_login_social_kakao.py', result: 'fail', dur: '1m 24s', at: '17:10' },
      { name: 'test_payment.py', result: 'fail', dur: '0m 56s', at: '16:48' },
      { name: 'test_profile_image.py', result: 'pass', dur: '1m 32s', at: '16:20' },
      { name: 'test_bluetooth_pairing.py', result: 'pass', dur: '2m 08s', at: '15:52' },
    ],
  },
  {
    id: 'gs24', name: 'Galaxy S24', model: 'SM-S921N', serial: 'R9MX...',
    platform: 'android', os: 'Android 15', status: 'offline',
    battery: 0, uptime: '-',
    currentTest: '', progress: 0, elapsed: '',
    lastTest: '', lastResult: '', lastTime: '',
    offlineReason: 'USB 연결 끊김 (14:22)',
    stats: { total: 892, passed: 864, failed: 28, rate: 96.9 },
    history: [
      { name: 'test_edge_panel.py', result: 'pass', dur: '1m 12s', at: '어제 14:20' },
      { name: 'test_s_pen.py', result: 'pass', dur: '2m 44s', at: '어제 13:52' },
    ],
  },
]

const MIRROR_LOGS = [
  { t: '17:12:04', m: '>>> pytest tests/test_login_social_kakao.py' },
  { t: '17:12:04', m: 'collecting ... collected 1 item' },
  { t: '17:12:05', m: 'driver = webdriver.Remote(appium_url, caps)' },
  { t: '17:12:06', m: 'driver.find_element(By.ID, "btn_kakao_login").click()' },
  { t: '17:12:08', m: 'WebDriverWait(driver, 10).until(EC.visibility_of(...))' },
  { t: '17:12:10', m: 'driver.find_element(By.ID, "input_email").send_keys(...)' },
  { t: '17:12:12', m: 'driver.find_element(By.ID, "btn_confirm").click()' },
]

export default {
  name: 'DeviceFarm',
  data() {
    return {
      tab: 'all',
      query: '',
      devices: DEVICES,
      refreshing: false,
      mirrorDev: null,
      detailDev: null,
      cursorX: 50,
      cursorY: 50,
      cursorOn: true,
      cursorTimer: null,
      clock: '',
      clockTimer: null,
      mirrorLogs: MIRROR_LOGS,
    }
  },
  computed: {
    runningCount() { return this.devices.filter(d => d.status === 'running').length },
    idleCount() { return this.devices.filter(d => d.status === 'idle').length },
    offlineCount() { return this.devices.filter(d => d.status === 'offline').length },
    tabs() {
      return [
        { k: 'all', label: '전체', count: this.devices.length },
        { k: 'ios', label: 'iOS', count: this.devices.filter(d => d.platform === 'ios').length },
        { k: 'android', label: 'Android', count: this.devices.filter(d => d.platform === 'android').length },
        { k: 'ipad', label: 'Tablet', count: this.devices.filter(d => d.platform === 'ipad').length },
      ]
    },
    filteredDevices() {
      let list = this.devices
      if (this.tab !== 'all') list = list.filter(d => d.platform === this.tab)
      if (this.query) {
        const q = this.query.toLowerCase()
        list = list.filter(d =>
          d.name.toLowerCase().includes(q) ||
          d.model.toLowerCase().includes(q) ||
          d.os.toLowerCase().includes(q)
        )
      }
      return list
    },
  },
  mounted() {
    this.updateClock()
    this.clockTimer = setInterval(this.updateClock, 1000)
    this.cursorTimer = setInterval(this.animateCursor, 1200)
  },
  beforeUnmount() {
    if (this.clockTimer) clearInterval(this.clockTimer)
    if (this.cursorTimer) clearInterval(this.cursorTimer)
  },
  methods: {
    updateClock() {
      const d = new Date()
      this.clock = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0')
    },
    animateCursor() {
      this.cursorOn = false
      setTimeout(() => {
        this.cursorX = 20 + Math.random() * 60
        this.cursorY = 30 + Math.random() * 50
        this.cursorOn = true
      }, 200)
    },
    batteryColor(b) {
      if (b >= 60) return '#06C755'
      if (b >= 30) return '#FFB800'
      return '#F04452'
    },
    refresh() {
      this.refreshing = true
      setTimeout(() => { this.refreshing = false }, 800)
    },
    openMirror(d) {
      if (d.status === 'offline') return
      this.mirrorDev = d
    },
    openDetail(d) {
      this.detailDev = d
    },
  },
}
</script>

<style scoped>
.farm-page {
  padding-top: 68px;
  min-height: 100vh;
  background: #fafbfc;
  user-select: none;
  -webkit-user-select: none;
}
.mono { font-family: 'JetBrains Mono', monospace }

/* Header */
.farm-header {
  padding: 56px 32px 40px;
  background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
  border-bottom: 1px solid #E5E8EB;
}
.fh-inner {
  max-width: 1240px; margin: 0 auto;
  display: grid; grid-template-columns: 1.3fr 1fr;
  gap: 48px; align-items: center;
}
.fh-eyebrow {
  display: inline-block;
  font-size: 13px; font-weight: 700;
  color: #0064FF; letter-spacing: .1em;
  text-transform: uppercase; margin-bottom: 14px;
}
.fh-title {
  font-size: 40px; font-weight: 900;
  line-height: 1.2; letter-spacing: -.04em;
  color: #0F172A; margin-bottom: 16px;
  word-break: keep-all;
}
.fh-sub {
  font-size: 15px; line-height: 1.75;
  color: #334155; word-break: keep-all;
}
.fh-right {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
}
.stat-tile {
  background: #fff; border: 1px solid #E5E8EB;
  border-radius: 12px; padding: 16px 18px;
  display: flex; align-items: center; gap: 12px;
}
.st-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.st-val { font-size: 22px; font-weight: 800; letter-spacing: -.03em; color: #0F172A; }
.st-lab { font-size: 12px; color: #64748B; font-weight: 500; margin-top: 2px; }

/* Toolbar */
.farm-toolbar {
  background: #fff; border-bottom: 1px solid #E5E8EB;
  padding: 16px 32px; position: sticky; top: 68px; z-index: 20;
}
.ft-inner {
  max-width: 1240px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between; gap: 20px;
  flex-wrap: wrap;
}
.ft-tabs { display: flex; gap: 4px }
.ft-tab {
  background: transparent; border: none; cursor: pointer;
  padding: 8px 14px; font-size: 14px; font-weight: 600;
  color: #64748B; border-radius: 8px; font-family: inherit;
  display: flex; align-items: center; gap: 8px;
}
.ft-tab:hover { background: #f6f7f9; color: #0F172A }
.ft-tab.active { background: #e5f0ff; color: #0064FF }
.ft-count {
  background: rgba(100,116,139,.1); color: #64748B;
  font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 10px; font-family: 'JetBrains Mono', monospace;
}
.ft-tab.active .ft-count { background: rgba(0,100,255,.15); color: #0064FF }

.ft-right { display: flex; align-items: center; gap: 10px }
.ft-search {
  display: flex; align-items: center; gap: 8px;
  background: #f6f7f9; border: 1px solid #E5E8EB;
  padding: 8px 12px; border-radius: 8px;
  color: #64748B; min-width: 220px;
}
.ft-search input {
  border: none; background: transparent; outline: none;
  font-size: 13px; color: #0F172A; font-family: inherit; flex: 1;
}
.ft-btn {
  background: #fff; border: 1px solid #E5E8EB;
  padding: 8px 14px; border-radius: 8px; font-size: 13px;
  font-weight: 600; cursor: pointer; color: #334155;
  font-family: inherit; display: flex; align-items: center; gap: 6px;
}
.ft-btn:hover { background: #f6f7f9 }
.spinning { display: inline-block; animation: spin 0.8s linear infinite }
@keyframes spin { to { transform: rotate(360deg) } }

/* Grid */
.farm-grid-section { padding: 32px }
.fg-inner { max-width: 1240px; margin: 0 auto }
.dev-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;
}

/* Device Card */
.dev-card {
  background: #fff; border: 1px solid #E5E8EB;
  border-radius: 16px; padding: 20px;
  transition: all .2s; position: relative;
}
.dev-card:hover { border-color: #D1D6DB; box-shadow: 0 4px 16px rgba(15,23,42,.06) }
.dev-running { border-color: rgba(0,100,255,.2); background: linear-gradient(180deg, #fff 0%, #fafcff 100%) }
.dev-offline { opacity: .72 }

.dc-top {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.dc-platform { display: flex; align-items: center; gap: 8px }
.plat-badge {
  font-size: 11px; font-weight: 700; padding: 3px 8px;
  border-radius: 5px; letter-spacing: -.01em;
}
.plat-ios { background: #F1F5F9; color: #1E293B }
.plat-android { background: #ECFDF5; color: #065F46 }
.plat-ipad { background: #FEF3C7; color: #92400E }
.dc-os { font-size: 11px; color: #64748B }

.dc-status { display: flex; align-items: center; gap: 6px }
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
}
.sd-running { background: #0064FF; box-shadow: 0 0 8px #0064FF; animation: pulse 1.5s infinite }
.sd-idle { background: #06C755 }
.sd-offline { background: #CBD5E1 }
@keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: .4 } }
.status-label { font-size: 11px; font-weight: 700; color: #64748B }

/* Phone Frame */
.dc-phone {
  display: flex; justify-content: center; margin: 12px 0 16px;
}
.phone-frame {
  width: 140px; height: 220px;
  background: #1a1a1a; border-radius: 24px;
  padding: 6px; position: relative;
  box-shadow: 0 4px 12px rgba(0,0,0,.15);
}
.frame-ipad { width: 180px; height: 220px; border-radius: 16px }
.phone-frame::before {
  content: ''; position: absolute;
  top: 10px; left: 50%; transform: translateX(-50%);
  width: 36px; height: 4px; background: #333;
  border-radius: 4px;
}
.frame-ipad::before { display: none }
.phone-screen {
  width: 100%; height: 100%; background: #000;
  border-radius: 18px; overflow: hidden;
  position: relative;
}
.frame-ipad .phone-screen { border-radius: 10px }

.screen-running {
  width: 100%; height: 100%; padding: 10px 8px;
  display: flex; flex-direction: column;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}
.sr-app-header {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 8px; color: #fff; margin-bottom: 8px;
}
.sr-time { font-weight: 700 }
.sr-icons { display: flex; gap: 3px; font-size: 7px }
.sr-content { flex: 1; position: relative }
.sr-badge {
  display: inline-flex; align-items: center; gap: 3px;
  background: rgba(240,68,82,.2); color: #FF6B6B;
  font-size: 7px; font-weight: 800;
  padding: 2px 6px; border-radius: 4px;
  margin-bottom: 6px;
}
.sr-rec {
  width: 5px; height: 5px; border-radius: 50%;
  background: #FF6B6B; animation: pulse 1s infinite;
}
.sr-test-name {
  font-size: 7px; color: #94A3B8;
  font-family: 'JetBrains Mono', monospace;
  margin-bottom: 10px; word-break: break-all;
}
.sr-fake-ui {
  display: flex; flex-direction: column; gap: 4px;
}
.fake-row {
  height: 6px; background: rgba(255,255,255,.08);
  border-radius: 2px;
}
.fake-btn {
  height: 14px; background: rgba(0,100,255,.3);
  border-radius: 3px; margin: 4px 0;
  transition: all .2s;
}
.fake-btn.active { background: #0064FF; box-shadow: 0 0 8px rgba(0,100,255,.6) }
.sr-cursor {
  position: absolute; width: 10px; height: 10px;
  border-radius: 50%; background: rgba(255,255,255,.6);
  border: 1.5px solid #fff; pointer-events: none;
  transition: all .3s ease;
}

.screen-idle {
  width: 100%; height: 100%;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px;
}
.idle-time { color: #fff; font-size: 20px; font-weight: 700 }
.idle-icon { font-size: 22px; opacity: .6 }
.idle-label { color: #64748B; font-size: 10px; font-weight: 600 }

.screen-offline {
  width: 100%; height: 100%; background: #0a0a0a;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 6px;
}
.off-icon { font-size: 32px; color: #333 }
.off-label { color: #555; font-size: 10px; font-weight: 600 }

/* Info */
.dc-info { margin-bottom: 14px }
.dc-name {
  font-size: 15px; font-weight: 800;
  color: #0F172A; letter-spacing: -.02em;
  margin-bottom: 2px;
}
.dc-meta { font-size: 11px; color: #64748B }

/* Metrics */
.dc-metrics {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
  padding: 12px 0; border-top: 1px solid #f1f3f5; border-bottom: 1px solid #f1f3f5;
  margin-bottom: 12px;
}
.metric { display: flex; flex-direction: column; gap: 4px }
.m-label { font-size: 10px; color: #64748B; font-weight: 600 }
.m-bar {
  height: 4px; background: #f1f3f5; border-radius: 2px; overflow: hidden;
}
.m-fill { height: 100%; transition: width .3s }
.m-val { font-size: 11px; color: #0F172A; font-weight: 700 }
.m-single { margin-top: 2px }

/* Current state */
.dc-current, .dc-lastrun, .dc-offline-note {
  background: #f9fafc; border-radius: 8px;
  padding: 10px 12px; margin-bottom: 12px;
}
.cur-label {
  font-size: 10px; color: #64748B; font-weight: 700;
  letter-spacing: .05em; text-transform: uppercase;
  margin-bottom: 4px;
}
.cur-test {
  font-size: 11px; color: #0064FF; font-weight: 700;
  margin-bottom: 8px; word-break: break-all;
}
.cur-progress {
  height: 4px; background: rgba(0,100,255,.1);
  border-radius: 2px; overflow: hidden; margin-bottom: 6px;
}
.cp-fill { height: 100%; background: #0064FF; transition: width .3s }
.cur-foot {
  display: flex; justify-content: space-between;
  font-size: 10px; color: #64748B; font-weight: 600;
}
.lr-row {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px;
}
.lr-dot { width: 6px; height: 6px; border-radius: 50% }
.lr-pass { background: #06C755 }
.lr-fail { background: #F04452 }
.lr-name { color: #0F172A; font-weight: 600; flex: 1; word-break: break-all }
.lr-time { color: #64748B }

.dc-offline-note {
  display: flex; align-items: center; gap: 10px;
  background: #FEF2F2;
}
.offn-icon { color: #DC2626; font-size: 18px }
.offn-title { font-size: 12px; font-weight: 700; color: #991B1B }
.offn-sub { font-size: 10px; color: #991B1B; opacity: .7; margin-top: 2px }

/* Actions */
.dc-actions { display: flex; gap: 8px }
.dca-btn {
  flex: 1; padding: 10px 12px; border-radius: 8px;
  font-size: 12px; font-weight: 700; cursor: pointer;
  border: none; font-family: inherit; transition: all .15s;
}
.dca-primary { background: #0064FF; color: #fff }
.dca-primary:hover:not(:disabled) { background: #0051d3 }
.dca-primary:disabled { background: #CBD5E1; cursor: not-allowed }
.dca-ghost { background: #f6f7f9; color: #334155 }
.dca-ghost:hover { background: #eef0f3 }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(15,23,42,.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  padding: 20px; animation: fadeIn .2s;
}
@keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }

.mirror-modal, .detail-modal {
  background: #fff; border-radius: 16px;
  max-width: 920px; width: 100%;
  max-height: 90vh; overflow: hidden;
  display: flex; flex-direction: column;
  animation: slideUp .25s;
}
.detail-modal { max-width: 760px }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px) } to { opacity: 1; transform: translateY(0) } }

.mm-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px; border-bottom: 1px solid #E5E8EB;
}
.mm-title {
  font-size: 16px; font-weight: 800; color: #0F172A;
  display: flex; align-items: center; gap: 8px;
}
.mm-dot { width: 8px; height: 8px; border-radius: 50% }
.mm-close {
  background: #f6f7f9; border: none; width: 32px; height: 32px;
  border-radius: 8px; font-size: 20px; cursor: pointer; color: #64748B;
  display: flex; align-items: center; justify-content: center;
}
.mm-close:hover { background: #eef0f3; color: #0F172A }

.mm-body {
  display: grid; grid-template-columns: 1fr 1.1fr; gap: 24px;
  padding: 24px; overflow-y: auto;
}
.mm-phone { display: flex; align-items: center; justify-content: center }
.phone-frame-large {
  width: 220px; height: 440px; background: #1a1a1a;
  border-radius: 36px; padding: 8px; position: relative;
  box-shadow: 0 10px 40px rgba(0,0,0,.2);
}
.frame-ipad.phone-frame-large { width: 300px; height: 400px; border-radius: 24px }
.phone-frame-large::before {
  content: ''; position: absolute;
  top: 14px; left: 50%; transform: translateX(-50%);
  width: 56px; height: 6px; background: #333; border-radius: 6px;
}
.phone-screen-large {
  width: 100%; height: 100%; background: #000;
  border-radius: 28px; overflow: hidden; position: relative;
}
.screen-large { padding: 20px 14px }
.screen-large .sr-app-header { font-size: 11px; margin-bottom: 14px }
.screen-large .sr-icons { font-size: 10px }
.screen-large .sr-badge { font-size: 10px; padding: 4px 10px }
.screen-large .sr-test-name { font-size: 10px; margin-bottom: 20px }

.mm-side { display: flex; flex-direction: column; gap: 16px }
.mms-section {
  background: #f9fafc; border-radius: 10px; padding: 16px;
}
.mms-h {
  font-size: 12px; font-weight: 800; color: #0F172A;
  margin-bottom: 10px; letter-spacing: -.01em;
}
.mms-row {
  display: flex; justify-content: space-between;
  padding: 6px 0; font-size: 13px;
  border-bottom: 1px solid #eef0f3;
}
.mms-row:last-child { border-bottom: none }
.mms-row span:first-child { color: #64748B }
.mms-row span:last-child { color: #0F172A; font-weight: 600 }

.mms-log {
  background: #0F172A; border-radius: 8px;
  padding: 12px; max-height: 240px; overflow-y: auto;
  font-size: 11px; line-height: 1.6;
}
.log-line { display: flex; gap: 10px; margin-bottom: 2px }
.ll-time { color: #64748B; flex-shrink: 0 }
.ll-text { color: #CBD5E1 }

/* Detail Modal */
.dm-body { padding: 24px; overflow-y: auto }
.dm-stats {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
  margin-bottom: 20px;
}
.dm-stat {
  background: #f9fafc; border-radius: 10px;
  padding: 14px; text-align: center;
}
.dms-val {
  font-size: 24px; font-weight: 800; color: #0F172A;
  letter-spacing: -.03em; margin-bottom: 4px;
}
.dms-lab { font-size: 11px; color: #64748B; font-weight: 600 }

.dm-history {
  border: 1px solid #E5E8EB; border-radius: 10px;
  overflow: hidden;
}
.dmh-head {
  display: grid; grid-template-columns: 2fr 1fr 1fr 1.2fr;
  padding: 10px 16px; background: #f9fafc;
  font-size: 11px; font-weight: 700; color: #64748B;
  text-transform: uppercase; letter-spacing: .05em;
  border-bottom: 1px solid #E5E8EB;
}
.dmh-row {
  display: grid; grid-template-columns: 2fr 1fr 1fr 1.2fr;
  padding: 12px 16px; align-items: center;
  font-size: 13px; border-bottom: 1px solid #f1f3f5;
}
.dmh-row:last-child { border-bottom: none }
.dmh-name { color: #0F172A; font-size: 12px }
.dmh-time { color: #64748B; font-size: 12px }

.res-chip {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 11px; font-weight: 700;
}
.rc-pass { background: #D1FAE5; color: #065F46 }
.rc-fail { background: #FEE2E2; color: #991B1B }

@media (max-width: 1024px) {
  .dev-grid { grid-template-columns: repeat(2, 1fr) }
  .fh-inner { grid-template-columns: 1fr }
  .mm-body { grid-template-columns: 1fr }
}
@media (max-width: 640px) {
  .dev-grid { grid-template-columns: 1fr }
  .fh-right { grid-template-columns: 1fr 1fr }
  .ft-inner { flex-direction: column; align-items: stretch }
  .ft-search { min-width: 0 }
  .dm-stats { grid-template-columns: repeat(2, 1fr) }
  .farm-header { padding: 32px 20px 24px }
  .fh-title { font-size: 28px }
  .farm-grid-section { padding: 20px }
}
</style>