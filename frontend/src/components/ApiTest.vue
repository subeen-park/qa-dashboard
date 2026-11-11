<template>
  <div class="api-page">
    <!-- 헤더 -->
    <div class="api-header">
      <div>
        <div class="api-eyebrow">API TEST</div>
        <h1 class="api-title">Postman Collection 기반 API 테스트</h1>
        <p class="api-sub">
          Postman Collection v2.1 JSON 업로드 → 순차 실행 → 상태코드·응답시간 Assertion 자동 검증.
        </p>
      </div>
      <div class="api-header-right">
        <input
          ref="fileInput"
          type="file"
          accept=".json,application/json"
          style="display:none"
          @change="handleFile"
        />
        <button class="btn-upload" @click="$refs.fileInput.click()">
          <span>↑</span> Collection 업로드
        </button>
      </div>
    </div>

    <!-- 요약 바 -->
    <div class="summary-bar">
      <div class="sb-item">
        <div class="sb-ic sb-blue">📄</div>
        <div>
          <div class="sb-val">{{ collections.length }}</div>
          <div class="sb-lab">업로드된 Collection</div>
        </div>
      </div>
      <div class="sb-item">
        <div class="sb-ic sb-green">✓</div>
        <div>
          <div class="sb-val">{{ totalPass }}</div>
          <div class="sb-lab">총 성공 요청</div>
        </div>
      </div>
      <div class="sb-item">
        <div class="sb-ic sb-red">✕</div>
        <div>
          <div class="sb-val">{{ totalFail }}</div>
          <div class="sb-lab">총 실패 요청</div>
        </div>
      </div>
      <div class="sb-item">
        <div class="sb-ic sb-yellow">⏱</div>
        <div>
          <div class="sb-val">{{ runs.length }}</div>
          <div class="sb-lab">누적 실행</div>
        </div>
      </div>
    </div>

    <!-- 메인 그리드 -->
    <div class="main-grid">
      <!-- 좌: Collection 리스트 -->
      <div class="panel">
        <div class="panel-head">
          <div class="panel-title">Collections</div>
          <div class="panel-sub">업로드된 Postman Collection</div>
        </div>
        <div class="coll-list">
          <div
            v-for="c in collections"
            :key="c.id"
            class="coll-item"
            :class="{ active: activeColl && activeColl.id === c.id }"
            @click="selectColl(c)"
          >
            <div class="coll-head">
              <div class="coll-name">{{ c.name }}</div>
              <button class="coll-del" @click.stop="confirmDelete(c)" title="삭제">🗑</button>
            </div>
            <div class="coll-meta">
              <span class="coll-count mono">{{ c.request_count }}개 요청</span>
              <span class="coll-date mono">{{ fmtDate(c.created_at) }}</span>
            </div>
          </div>
          <div v-if="collections.length === 0" class="empty-msg">
            <div style="font-size:28px;margin-bottom:8px;opacity:.4">📄</div>
            업로드된 Collection이 없어요.<br>
            상단 "Collection 업로드" 버튼으로 시작하세요.
          </div>
        </div>
      </div>

      <!-- 우: Collection 상세 + 실행 -->
      <div class="panel panel-wide">
        <div v-if="!activeColl" class="empty-placeholder">
          <div style="font-size:48px;opacity:.3">←</div>
          <div>왼쪽에서 Collection을 선택하세요</div>
        </div>

        <div v-else>
          <div class="panel-head">
            <div>
              <div class="panel-title">{{ activeColl.name }}</div>
              <div class="panel-sub">{{ activeColl.description || activeColl.request_count + '개 요청' }}</div>
            </div>
            <button class="btn-run" @click="runColl" :disabled="running">
              <span v-if="running" class="spin"></span>
              <span v-else>▶</span>
              {{ running ? '실행 중...' : 'Run All' }}
            </button>
          </div>

          <!-- Request 리스트 -->
          <div v-if="!currentRun" class="req-list">
            <div class="req-head">
              <span class="col-method">Method</span>
              <span class="col-name">Name</span>
              <span class="col-url">URL</span>
            </div>
            <div v-for="(r, i) in parsedRequests" :key="i" class="req-row">
              <span class="req-method" :class="'m-' + r.method.toLowerCase()">{{ r.method }}</span>
              <span class="req-name">{{ r.folder ? `${r.folder} / ${r.name}` : r.name }}</span>
              <span class="req-url mono">{{ r.url }}</span>
            </div>
          </div>

          <!-- 실행 결과 -->
          <div v-else class="run-result">
            <div class="result-summary">
              <div class="rs-pill" :class="'rs-' + currentRun.status">
                <span class="rs-dot"></span>
                {{ currentRun.status }}
              </div>
              <div class="rs-stats mono">
                총 <strong>{{ currentRun.total || 0 }}</strong> ·
                <span class="pass-text">성공 {{ currentRun.passed || 0 }}</span> ·
                <span class="fail-text">실패 {{ currentRun.failed || 0 }}</span>
              </div>
              <button class="btn-back" @click="currentRun = null">← 요청 목록</button>
            </div>

            <div class="result-table">
              <div class="rt-head">
                <span class="col-seq">#</span>
                <span class="col-status">상태</span>
                <span class="col-method">Method</span>
                <span class="col-name">Name</span>
                <span class="col-code">Code</span>
                <span class="col-dur">시간</span>
              </div>
              <div
                v-for="r in (currentRun.results || [])"
                :key="r.seq"
                class="rt-row"
                :class="{ 'row-fail': !r.pass }"
              >
                <span class="col-seq mono">{{ r.seq }}</span>
                <span class="col-status">
                  <span class="r-badge" :class="r.pass ? 'rb-pass' : 'rb-fail'">
                    {{ r.pass ? '✓' : '✕' }}
                  </span>
                </span>
                <span class="req-method" :class="'m-' + r.method.toLowerCase()">{{ r.method }}</span>
                <span class="col-name" :title="r.folder + ' / ' + r.name">
                  {{ r.name }}
                </span>
                <span class="col-code mono">
                  <span v-if="r.status_code" :class="statusClass(r.status_code)">{{ r.status_code }}</span>
                  <span v-else class="err">—</span>
                </span>
                <span class="col-dur mono">{{ r.duration_ms }}ms</span>
              </div>
              <div v-if="running && (!currentRun.results || currentRun.results.length === 0)" class="rt-waiting">
                실행 중... 결과를 기다리는 중
              </div>
            </div>

            <!-- 실패 요청 상세 -->
            <div v-if="failedResults.length > 0" class="fail-section">
              <div class="fs-title">❌ 실패한 요청 ({{ failedResults.length }})</div>
              <div v-for="r in failedResults" :key="r.seq" class="fs-item">
                <div class="fs-head">
                  <span class="req-method" :class="'m-' + r.method.toLowerCase()">{{ r.method }}</span>
                  <span class="fs-name">{{ r.name }}</span>
                </div>
                <div class="fs-meta mono">{{ r.url }}</div>
                <div v-if="r.error" class="fs-err">{{ r.error }}</div>
                <div v-else class="fs-err">HTTP {{ r.status_code }} (4xx/5xx)</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 최근 실행 이력 -->
    <div v-if="runs.length > 0" class="history-section">
      <div class="hs-head">
        <div class="hs-title">최근 실행 이력</div>
        <div class="hs-sub">최근 {{ runs.length }}회</div>
      </div>
      <div class="hs-list">
        <div
          v-for="r in runs"
          :key="r.id"
          class="hs-row"
          @click="loadRun(r.id)"
        >
          <span class="hs-ic" :class="'hsi-' + r.status">
            <span v-if="r.status === 'done' && r.failed === 0">✓</span>
            <span v-else-if="r.status === 'done'">✕</span>
            <span v-else-if="r.status === 'running'" class="spin-sm"></span>
            <span v-else>•</span>
          </span>
          <span class="hs-id mono">#{{ r.id }}</span>
          <span class="hs-coll">{{ r.collection_name }}</span>
          <span class="hs-stats mono">
            <span class="pass-text">{{ r.passed || 0 }}</span> /
            <span class="fail-text">{{ r.failed || 0 }}</span> /
            {{ r.total || 0 }}
          </span>
          <span class="hs-time mono">{{ fmtDate(r.started_at) }}</span>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 -->
    <div v-if="deleteTarget" class="confirm-overlay" @click.self="deleteTarget = null">
      <div class="confirm-box">
        <div class="cb-title">Collection 삭제</div>
        <div class="cb-msg">
          <strong>{{ deleteTarget.name }}</strong> 을 삭제하시겠어요?<br>
          연관된 실행 이력도 함께 삭제됩니다.
        </div>
        <div class="cb-actions">
          <button class="cb-btn cb-ghost" @click="deleteTarget = null">취소</button>
          <button class="cb-btn cb-danger" @click="doDelete">삭제</button>
        </div>
      </div>
    </div>

    <!-- 에러 토스트 -->
    <div v-if="toast" class="toast" :class="'toast-' + toast.type">{{ toast.msg }}</div>
  </div>
</template>

<script>
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default {
  name: 'ApiTest',
  data() {
    return {
      collections: [],
      runs: [],
      activeColl: null,
      parsedRequests: [],
      currentRun: null,
      running: false,
      runPollTimer: null,
      deleteTarget: null,
      toast: null,
    }
  },
  computed: {
    totalPass() { return this.runs.reduce((s, r) => s + (r.passed || 0), 0) },
    totalFail() { return this.runs.reduce((s, r) => s + (r.failed || 0), 0) },
    failedResults() {
      if (!this.currentRun || !this.currentRun.results) return []
      return this.currentRun.results.filter(r => !r.pass)
    },
  },
  async mounted() {
    await this.loadCollections()
    await this.loadRuns()
  },
  beforeUnmount() {
    if (this.runPollTimer) clearInterval(this.runPollTimer)
  },
  methods: {
    async loadCollections() {
      try {
        const res = await fetch(`${API_BASE}/api/apitests/collections`)
        this.collections = await res.json()
      } catch (e) {
        this.showToast('error', 'Collection 로드 실패')
      }
    },
    async loadRuns() {
      try {
        const res = await fetch(`${API_BASE}/api/apitests/runs?limit=20`)
        this.runs = await res.json()
      } catch (e) {}
    },
    async handleFile(e) {
      const file = e.target.files[0]
      if (!file) return
      try {
        const text = await file.text()
        const json = JSON.parse(text)
        const res = await fetch(`${API_BASE}/api/apitests/collections`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ raw_json: json }),
        })
        if (!res.ok) {
          const err = await res.json()
          throw new Error(err.error || '업로드 실패')
        }
        const saved = await res.json()
        this.showToast('ok', `${saved.name} 업로드 완료 (${saved.request_count}개 요청)`)
        await this.loadCollections()
        this.selectColl(saved)
      } catch (err) {
        this.showToast('error', '업로드 실패: ' + err.message)
      } finally {
        e.target.value = ''
      }
    },
    async selectColl(c) {
      this.currentRun = null
      try {
        const res = await fetch(`${API_BASE}/api/apitests/collections/${c.id}`)
        const data = await res.json()
        this.activeColl = data
        this.parsedRequests = (data.parsed && data.parsed.requests) || []
      } catch (e) {
        this.showToast('error', '상세 로드 실패')
      }
    },
    async runColl() {
      if (!this.activeColl || this.running) return
      this.running = true
      try {
        const res = await fetch(`${API_BASE}/api/apitests/collections/${this.activeColl.id}/run`, {
          method: 'POST',
        })
        const data = await res.json()
        this.currentRun = { id: data.run_id, status: 'queued', results: [] }
        this.startPolling(data.run_id)
      } catch (e) {
        this.showToast('error', '실행 실패')
        this.running = false
      }
    },
    startPolling(runId) {
      if (this.runPollTimer) clearInterval(this.runPollTimer)
      this.runPollTimer = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE}/api/apitests/runs/${runId}`)
          const data = await res.json()
          this.currentRun = data
          if (data.status === 'done' || data.status === 'error') {
            clearInterval(this.runPollTimer)
            this.runPollTimer = null
            this.running = false
            await this.loadRuns()
          }
        } catch (e) {}
      }, 1500)
    },
    async loadRun(runId) {
      try {
        const res = await fetch(`${API_BASE}/api/apitests/runs/${runId}`)
        this.currentRun = await res.json()
        if (this.currentRun.collection_id && (!this.activeColl || this.activeColl.id !== this.currentRun.collection_id)) {
          const coll = this.collections.find(c => c.id === this.currentRun.collection_id)
          if (coll) await this.selectColl(coll)
        }
      } catch (e) {}
    },
    confirmDelete(c) {
      this.deleteTarget = c
    },
    async doDelete() {
      if (!this.deleteTarget) return
      try {
        await fetch(`${API_BASE}/api/apitests/collections/${this.deleteTarget.id}`, { method: 'DELETE' })
        if (this.activeColl && this.activeColl.id === this.deleteTarget.id) {
          this.activeColl = null
          this.currentRun = null
        }
        this.deleteTarget = null
        await this.loadCollections()
        await this.loadRuns()
      } catch (e) {
        this.showToast('error', '삭제 실패')
      }
    },
    fmtDate(iso) {
      if (!iso) return '-'
      const d = new Date(iso)
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      const hh = String(d.getHours()).padStart(2, '0')
      const mm = String(d.getMinutes()).padStart(2, '0')
      return `${m}/${day} ${hh}:${mm}`
    },
    statusClass(code) {
      if (code >= 500) return 'err'
      if (code >= 400) return 'warn'
      if (code >= 300) return 'info'
      return 'ok'
    },
    showToast(type, msg) {
      this.toast = { type, msg }
      setTimeout(() => { this.toast = null }, 3000)
    },
  },
}
</script>

<style scoped>
.api-page { padding: 92px 32px 60px; max-width: 1280px; margin: 0 auto; font-family: 'Pretendard Variable', Pretendard, sans-serif; }
.mono { font-family: 'JetBrains Mono', monospace; }

/* Header */
.api-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; gap: 20px; flex-wrap: wrap; }
.api-eyebrow { display: inline-block; font-size: 12px; font-weight: 700; color: #0064FF; letter-spacing: .12em; margin-bottom: 10px; }
.api-title { font-size: 26px; font-weight: 800; letter-spacing: -.03em; color: #0F172A; margin: 0 0 8px; }
.api-sub { font-size: 13.5px; line-height: 1.6; color: #64748B; margin: 0; max-width: 620px; }
.btn-upload { display: inline-flex; align-items: center; gap: 8px; background: #0064FF; color: #fff; border: none; padding: 10px 18px; border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit; box-shadow: 0 4px 12px rgba(0,100,255,.25); }
.btn-upload:hover { background: #0051d3; }

/* Summary bar */
.summary-bar { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 24px; }
.sb-item { display: flex; align-items: center; gap: 14px; background: #fff; border: 1px solid #E5E8EB; border-radius: 14px; padding: 18px 20px; }
.sb-ic { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; }
.sb-blue { background: #DBEAFE; color: #1E40AF; }
.sb-green { background: #D1FAE5; color: #065F46; }
.sb-red { background: #FEE2E2; color: #991B1B; }
.sb-yellow { background: #FEF3C7; color: #92400E; }
.sb-val { font-size: 22px; font-weight: 800; letter-spacing: -.02em; }
.sb-lab { font-size: 11px; color: #64748B; margin-top: 2px; font-weight: 500; }

/* Grid */
.main-grid { display: grid; grid-template-columns: 300px 1fr; gap: 16px; margin-bottom: 24px; }
.panel { background: #fff; border: 1px solid #E5E8EB; border-radius: 14px; overflow: hidden; }
.panel-wide { min-height: 400px; }
.panel-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid #E5E8EB; }
.panel-title { font-size: 14px; font-weight: 700; letter-spacing: -0.01em; }
.panel-sub { font-size: 11px; color: #64748B; margin-top: 2px; }

/* Collection list */
.coll-list { padding: 8px; max-height: 500px; overflow-y: auto; }
.coll-item { padding: 10px 12px; border-radius: 8px; cursor: pointer; margin-bottom: 4px; transition: background .12s; }
.coll-item:hover { background: #F1F5F9; }
.coll-item.active { background: #EFF6FF; border: 1px solid #BFDBFE; }
.coll-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.coll-name { font-size: 13px; font-weight: 700; color: #0F172A; }
.coll-del { background: transparent; border: none; cursor: pointer; font-size: 12px; color: #94A3B8; padding: 2px 4px; }
.coll-del:hover { color: #DC2626; }
.coll-meta { display: flex; justify-content: space-between; font-size: 11px; color: #64748B; }
.empty-msg { padding: 40px 20px; text-align: center; font-size: 12px; color: #94A3B8; line-height: 1.6; }
.empty-placeholder { padding: 80px 20px; text-align: center; font-size: 13px; color: #94A3B8; display: flex; flex-direction: column; align-items: center; gap: 12px; }

/* Run button */
.btn-run { display: inline-flex; align-items: center; gap: 7px; background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: #fff; border: none; padding: 9px 18px; border-radius: 9px; font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit; box-shadow: 0 3px 10px rgba(16,185,129,.3); }
.btn-run:disabled { opacity: .6; cursor: not-allowed; }
.btn-run:hover:not(:disabled) { transform: translateY(-1px); }
.spin { width: 11px; height: 11px; border: 2px solid rgba(255,255,255,.4); border-top-color: #fff; border-radius: 50%; animation: spin .7s linear infinite; display: inline-block; }
.spin-sm { width: 9px; height: 9px; border: 2px solid rgba(100,116,139,.3); border-top-color: #64748B; border-radius: 50%; animation: spin .7s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Request list */
.req-list { padding: 8px 16px 16px; max-height: 500px; overflow-y: auto; }
.req-head, .rt-head { display: grid; grid-template-columns: 70px 1fr 1.8fr; gap: 12px; padding: 8px 10px; font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: .05em; border-bottom: 1px solid #E5E8EB; }
.req-row { display: grid; grid-template-columns: 70px 1fr 1.8fr; gap: 12px; padding: 10px; align-items: center; border-bottom: 1px solid #F1F5F9; font-size: 12.5px; }
.req-method { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 800; padding: 3px 7px; border-radius: 4px; display: inline-block; text-align: center; letter-spacing: .02em; }
.m-get { background: #DBEAFE; color: #1E40AF; }
.m-post { background: #D1FAE5; color: #065F46; }
.m-put { background: #FEF3C7; color: #92400E; }
.m-patch { background: #FFEDD5; color: #9A3412; }
.m-delete { background: #FEE2E2; color: #991B1B; }
.req-name { font-size: 12.5px; color: #0F172A; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.req-url { font-size: 11px; color: #64748B; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Result */
.result-summary { display: flex; align-items: center; gap: 14px; padding: 14px 20px; border-bottom: 1px solid #E5E8EB; flex-wrap: wrap; }
.rs-pill { display: inline-flex; align-items: center; gap: 7px; padding: 5px 12px; border-radius: 100px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.rs-running { background: #DBEAFE; color: #1E40AF; }
.rs-done { background: #D1FAE5; color: #065F46; }
.rs-error, .rs-queued { background: #F1F5F9; color: #64748B; }
.rs-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.rs-running .rs-dot { animation: pulse 1.2s infinite; }
@keyframes pulse { 50% { opacity: .4; } }
.rs-stats { font-size: 12px; color: #334155; }
.pass-text { color: #059669; font-weight: 700; }
.fail-text { color: #DC2626; font-weight: 700; }
.btn-back { margin-left: auto; background: transparent; border: 1px solid #E5E8EB; padding: 6px 12px; border-radius: 7px; font-size: 12px; cursor: pointer; font-family: inherit; color: #64748B; }
.btn-back:hover { background: #F1F5F9; }

.result-table { padding: 8px 16px; max-height: 480px; overflow-y: auto; }
.rt-head { grid-template-columns: 40px 60px 70px 1fr 70px 70px; }
.rt-row { display: grid; grid-template-columns: 40px 60px 70px 1fr 70px 70px; gap: 12px; padding: 10px; align-items: center; font-size: 12.5px; border-bottom: 1px solid #F1F5F9; }
.rt-row.row-fail { background: #FEF2F2; }
.r-badge { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; font-size: 11px; font-weight: 800; }
.rb-pass { background: #10B981; color: #fff; }
.rb-fail { background: #EF4444; color: #fff; }
.col-seq, .col-code, .col-dur { font-size: 12px; color: #64748B; }
.col-code .ok { color: #059669; font-weight: 700; }
.col-code .info { color: #2563EB; font-weight: 700; }
.col-code .warn { color: #D97706; font-weight: 700; }
.col-code .err { color: #DC2626; font-weight: 700; }
.rt-waiting { padding: 30px; text-align: center; color: #94A3B8; font-size: 13px; }

.fail-section { padding: 16px 20px 24px; border-top: 1px solid #E5E8EB; background: #FAFBFC; }
.fs-title { font-size: 13px; font-weight: 700; color: #991B1B; margin-bottom: 12px; }
.fs-item { background: #fff; border: 1px solid #FCA5A5; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; }
.fs-head { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.fs-name { font-size: 12.5px; font-weight: 700; color: #0F172A; }
.fs-meta { font-size: 11px; color: #64748B; margin-bottom: 4px; word-break: break-all; }
.fs-err { font-size: 11.5px; color: #991B1B; font-family: 'JetBrains Mono', monospace; background: #FEF2F2; padding: 6px 8px; border-radius: 4px; }

/* History */
.history-section { background: #fff; border: 1px solid #E5E8EB; border-radius: 14px; padding: 20px; margin-bottom: 24px; }
.hs-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.hs-title { font-size: 14px; font-weight: 700; }
.hs-sub { font-size: 11px; color: #94A3B8; }
.hs-list { display: flex; flex-direction: column; }
.hs-row { display: grid; grid-template-columns: 24px 60px 1fr 160px 90px; gap: 12px; align-items: center; padding: 10px 8px; border-bottom: 1px solid #F1F5F9; cursor: pointer; font-size: 12.5px; transition: background .12s; }
.hs-row:hover { background: #F8FAFC; border-radius: 6px; }
.hs-ic { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 800; color: #fff; }
.hsi-done { background: #10B981; }
.hsi-running { background: #3B82F6; }
.hsi-error { background: #EF4444; }
.hsi-queued { background: #94A3B8; }
.hs-id { font-weight: 700; color: #64748B; }
.hs-coll { color: #0F172A; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hs-stats { font-size: 12px; color: #64748B; text-align: right; }
.hs-time { font-size: 11px; color: #94A3B8; text-align: right; }

/* Confirm modal */
.confirm-overlay { position: fixed; inset: 0; z-index: 1500; background: rgba(15,23,42,.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.confirm-box { background: #fff; border-radius: 14px; padding: 24px; max-width: 400px; width: 100%; box-shadow: 0 20px 50px rgba(0,0,0,.2); }
.cb-title { font-size: 16px; font-weight: 800; color: #0F172A; margin-bottom: 10px; }
.cb-msg { font-size: 13px; color: #334155; line-height: 1.6; margin-bottom: 20px; }
.cb-actions { display: flex; justify-content: flex-end; gap: 8px; }
.cb-btn { padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 700; border: none; cursor: pointer; font-family: inherit; }
.cb-ghost { background: #F1F5F9; color: #334155; }
.cb-danger { background: #EF4444; color: #fff; }

/* Toast */
.toast { position: fixed; top: 90px; right: 32px; background: #fff; border: 1px solid #E5E8EB; padding: 12px 18px; border-radius: 10px; font-size: 13px; font-weight: 600; box-shadow: 0 10px 30px rgba(0,0,0,.1); z-index: 2000; animation: slideIn .3s; }
.toast-ok { border-left: 3px solid #10B981; color: #065F46; }
.toast-error { border-left: 3px solid #EF4444; color: #991B1B; }
@keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }

@media (max-width: 900px) {
  .main-grid { grid-template-columns: 1fr; }
  .summary-bar { grid-template-columns: repeat(2,1fr); }
  .hs-row { grid-template-columns: 24px 50px 1fr 70px; }
  .hs-row > *:nth-child(4) { display: none; }
}
</style>