<template>
  <div class="page">
    <!-- 필터 바 -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">플랫폼</span>
        <div class="seg-btns">
          <button v-for="p in PLATFORMS" :key="p"
            class="seg-btn" :class="{on: platform===p}" @click="platform=p">{{ p }}</button>
        </div>
      </div>
      <div class="filter-group">
        <span class="filter-label">버전</span>
        <div class="seg-btns">
          <button v-for="v in versions" :key="v"
            class="seg-btn" :class="{on: version===v}" @click="version=v">{{ v }}</button>
        </div>
      </div>
      <div class="filter-group" style="margin-left:auto">
        <div class="search-wrap">
          <span style="color:var(--muted);font-size:13px">⌕</span>
          <input v-model="search" placeholder="담당자, 티켓, 작업명 검색..." />
        </div>
      </div>
      <div class="filter-group">
        <label class="demo-toggle">
          <input type="checkbox" v-model="isDemo" />
          <span class="demo-label">데모 모드</span>
        </label>
      </div>
    </div>

    <!-- 메트릭 -->
    <div class="metrics">
      <div class="mc">
        <div class="mc-label">전체 (머지 제외)</div>
        <div class="mc-val" style="color:var(--blue)">{{ unmergedTotal }}</div>
      </div>
      <div class="mc mc-clickable" @click="activeTab='미빌드'">
        <div class="mc-label">미빌드 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--muted)">{{ byStatus('미빌드').length }}</div>
        <div class="mc-sub">등록 독려 필요</div>
      </div>
      <div class="mc mc-clickable" @click="activeTab='빌드완료'">
        <div class="mc-label">빌드완료 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--blue)">{{ byStatus('빌드완료').length }}</div>
        <div class="mc-sub">MR 생성 필요</div>
      </div>
      <div class="mc mc-clickable" @click="activeTab='머지요청완료'">
        <div class="mc-label">머지요청완료 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--yellow)">{{ byStatus('머지요청완료').length }}</div>
        <div class="mc-sub">최종 승인 대기</div>
      </div>
      <div class="mc mc-clickable" @click="activeTab='머지 완료'">
        <div class="mc-label">머지완료 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--green)">{{ byStatus('머지 완료').length }}</div>
        <div class="mc-sub">배포 준비 완료</div>
      </div>
    </div>

    <!-- 탭 -->
    <div class="tabs">
      <div v-for="t in TABS" :key="t.key"
        class="tab" :class="{on: activeTab===t.key}" @click="activeTab=t.key">
        {{ t.label }} <span class="tab-cnt">{{ tabCount(t.key) }}</span>
      </div>
    </div>

    <!-- 테이블 -->
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th style="width:110px">담당자</th>
            <th style="width:110px">티켓</th>
            <th>작업명</th>
            <th style="width:120px">현 상태</th>
            <th style="width:90px">빌드</th>
            <th style="width:100px">등록일</th>
            <th style="width:80px">Jira</th>
            <th style="width:80px">GitLab</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="!tabData.length">
            <tr><td colspan="8" class="empty-state">해당하는 티켓이 없습니다</td></tr>
          </template>
          <tr v-else-if="activeTab!=='all'" class="risk-row">
            <td colspan="8">
              <span class="risk-chip">
                우선 확인: {{ topAssignee.name }} ({{ topAssignee.count }}건 보유)
              </span>
            </td>
          </tr>
          <tr v-for="row in filteredData" :key="row.티켓" class="data-row">
            <td class="cell-text muted">{{ row.담당자 }}</td>
            <td class="cell-mono">{{ row.티켓 }}</td>
            <td class="cell-text">{{ row.작업명 }}</td>
            <td><span class="status-chip" :class="statusClass(row['현 상태'])">{{ row['현 상태'] }}</span></td>
            <td><span class="build-chip" :class="buildClass(row['빌드 상태'])">{{ row['빌드 상태'] }}</span></td>
            <td class="cell-mono muted">{{ fmtDate(row['등록 일자']) }}</td>
            <td>
              <a v-if="row['Jira 링크'] && row['Jira 링크']!=='#'" :href="row['Jira 링크']" target="_blank" class="link-btn">보기 ↗</a>
              <span v-else class="muted cell-text">-</span>
            </td>
            <td>
              <a v-if="row['GitLab MR'] && row['GitLab MR']!=='#' && row['GitLab MR']!==''" :href="row['GitLab MR']" target="_blank" class="link-btn">열기 ↗</a>
              <span v-else class="muted cell-text">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
const PLATFORMS = ['iOS', 'Android', 'AndroidTV']
const VERSIONS  = ['v.8.24.0', 'v.8.23.0', 'v.8.22.0']
const STATUSES  = ['머지 완료','머지요청완료','미빌드','빌드완료','검증 중 (오류)']
const JOBS      = ['크래시 해결','UI 간격 조정','로직 수정','신규 팝업 작업','API 연동 최적화']
const NAMES     = Array.from({length:14}, (_,i) => `담당자_${String(i+1).padStart(2,'0')}`)

const TABS = [
  { key:'all',     label:'전체 현황' },
  { key:'미빌드',  label:'미빌드' },
  { key:'빌드완료',label:'빌드완료' },
  { key:'머지요청완료', label:'머지요청완료' },
  { key:'머지 완료', label:'머지완료' },
]

function seededRand(seed) {
  let s = seed.split('').reduce((a,c) => a + c.charCodeAt(0), 0)
  return () => { s = (s * 1664525 + 1013904223) & 0xffffffff; return Math.abs(s) / 0x7fffffff }
}

function getMockData(platform, version) {
  const rand = seededRand(version + platform)
  const pick = arr => arr[Math.floor(rand() * arr.length)]
  const today = new Date()
  return Array.from({length:50}, (_,i) => {
    const status = pick(STATUSES)
    const d = new Date(today); d.setDate(d.getDate() - Math.floor(rand()*60+1))
    return {
      담당자: pick(NAMES), 티켓: `SOOPKR-${19000+i+1}`,
      작업명: `[${pick(JOBS)}] ${i+1}차 작업`,
      '현 상태': status,
      '빌드 상태': ['머지 완료','머지요청완료','빌드완료'].includes(status) ? '성공'
                  : status.includes('오류') ? 'failed' : '-',
      '등록 일자': d,
      'Jira 링크': '#',
      'GitLab MR': ['머지 완료','머지요청완료','검증 중 (오류)'].includes(status) ? '#' : '',
    }
  })
}

export default {
  name: 'MergeTracker',
  data() {
    return {
      isDemo: true, platform: 'iOS', version: 'v.8.24.0',
      search: '', activeTab: 'all',
      PLATFORMS, TABS,
    }
  },
  computed: {
    versions() { return VERSIONS },
    allData()   { return getMockData(this.platform, this.version) },
    byStatusFn() { return s => this.allData.filter(r => r['현 상태'] === s) },
    unmergedTotal() { return this.allData.filter(r => r['현 상태'] !== '머지 완료').length },
    tabData() {
      if (this.activeTab === 'all') return this.allData
      return this.byStatus(this.activeTab)
    },
    filteredData() {
      if (!this.search) return this.tabData
      const q = this.search.toLowerCase()
      return this.tabData.filter(r =>
        r.담당자.toLowerCase().includes(q) ||
        r.티켓.toLowerCase().includes(q) ||
        r.작업명.toLowerCase().includes(q)
      )
    },
    topAssignee() {
      const counts = {}
      this.tabData.forEach(r => { counts[r.담당자] = (counts[r.담당자]||0)+1 })
      const name = Object.entries(counts).sort((a,b)=>b[1]-a[1])[0]?.[0] || '-'
      return { name, count: counts[name]||0 }
    },
  },
  methods: {
    byStatus(s) { return this.allData.filter(r => r['현 상태'] === s) },
    tabCount(key) {
      if (key==='all') return this.allData.length
      return this.byStatus(key).length
    },
    fmtDate(d) {
      if (!d) return '-'
      const dt = new Date(d)
      return `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}`
    },
    statusClass(s) {
      if (s==='머지 완료')      return 'sc-done'
      if (s==='머지요청완료')   return 'sc-ready'
      if (s==='빌드완료')       return 'sc-build'
      if (s==='미빌드')         return 'sc-none'
      if (s.includes('오류'))   return 'sc-err'
      return ''
    },
    buildClass(b) {
      if (b==='성공')  return 'bc-ok'
      if (b==='failed') return 'bc-fail'
      return 'bc-none'
    },
  }
}
</script>

<style scoped>
.page { padding:20px 24px }

.filter-bar { display:flex; align-items:center; gap:16px; flex-wrap:wrap; background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:12px 16px; margin-bottom:16px }
.filter-label { font-size:11px; color:var(--muted); margin-right:6px }
.filter-group { display:flex; align-items:center; gap:6px }
.seg-btns { display:flex; gap:3px }
.seg-btn  { padding:4px 12px; border-radius:6px; border:1px solid var(--border2); background:transparent; color:var(--muted); font-size:12px; cursor:pointer; font-family:inherit; transition:all .15s }
.seg-btn.on { background:var(--bg4); color:var(--text); border-color:var(--border) }

.search-wrap { display:flex; align-items:center; gap:6px; background:var(--bg3); border:1px solid var(--border2); border-radius:7px; padding:5px 10px }
.search-wrap input { background:transparent; border:none; outline:none; color:var(--text); font-size:12px; width:200px; font-family:inherit }
.search-wrap input::placeholder { color:var(--muted) }

.demo-toggle { display:flex; align-items:center; gap:6px; cursor:pointer; font-size:12px }
.demo-toggle input { accent-color:var(--amber) }
.demo-label { color:var(--muted) }

.metrics { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-bottom:16px }
.mc      { background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:14px 16px }
.mc-label{ font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px }
.mc-val  { font-size:24px; font-family:'DM Mono',monospace; font-weight:600 }
.mc-sub  { font-size:11px; color:var(--muted); margin-top:3px }
.mc-arrow{ font-size:11px }
.mc-clickable { cursor:pointer; transition:all .15s; user-select:none }
.mc-clickable:hover { filter:brightness(.95) }
.mc-clickable:active { transform:scale(.98) }

.tabs  { display:flex; gap:2px; background:var(--bg2); border:1px solid var(--border); border-radius:8px; padding:3px; width:fit-content; margin-bottom:14px }
.tab   { padding:5px 14px; border-radius:6px; cursor:pointer; font-size:13px; color:var(--muted); transition:all .15s; display:flex; align-items:center; gap:6px }
.tab.on{ background:var(--bg4); color:var(--text) }
.tab-cnt { background:var(--bg3); color:var(--muted); font-size:11px; padding:1px 6px; border-radius:10px; font-family:'DM Mono',monospace }
.tab.on .tab-cnt { background:var(--bg2); color:var(--text) }

.table-wrap { background:var(--bg2); border:1px solid var(--border); border-radius:10px; overflow:hidden }
.data-table { width:100%; border-collapse:collapse }
.data-table th { background:var(--bg3); padding:9px 12px; text-align:left; font-size:11px; font-weight:600; color:var(--muted); border-bottom:1px solid var(--border); white-space:nowrap }
.data-table td { padding:9px 12px; border-bottom:1px solid var(--border); vertical-align:middle }
.data-table tr:last-child td { border-bottom:none }
.data-row:hover td { background:var(--bg3) }
.risk-row td { background:var(--bg3); padding:8px 12px }
.risk-chip { font-size:12px; font-weight:600; color:var(--amber) }

.cell-text { font-size:13px; color:var(--text) }
.cell-mono { font-size:12px; font-family:'DM Mono',monospace; color:var(--text) }
.muted { color:var(--muted) }
.empty-state { text-align:center; padding:40px; color:var(--muted); font-size:13px }

.status-chip { display:inline-block; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:600; white-space:nowrap }
.sc-done  { background:var(--green-dim); color:var(--green) }
.sc-ready { background:var(--yellow-dim); color:var(--yellow) }
.sc-build { background:var(--blue-dim); color:var(--blue) }
.sc-none  { background:var(--bg4); color:var(--muted) }
.sc-err   { background:var(--red-dim); color:var(--red) }

.build-chip { display:inline-block; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:600 }
.bc-ok   { background:var(--green-dim); color:var(--green) }
.bc-fail { background:var(--red-dim); color:var(--red) }
.bc-none { background:var(--bg4); color:var(--muted) }

.link-btn { color:var(--blue); text-decoration:none; font-size:12px; font-weight:500 }
.link-btn:hover { text-decoration:underline }

@media(max-width:900px) { .metrics { grid-template-columns:repeat(3,1fr) } }
</style>