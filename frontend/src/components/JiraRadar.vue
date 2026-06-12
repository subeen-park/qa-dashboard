<template>
  <div class="page">
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">정체 기준</span>
        <select v-model.number="riskThreshold" class="filter-select">
          <option v-for="d in [1,2,3,5,7,10,14]" :key="d" :value="d">{{ d }}일 이상</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">담당자</span>
        <select v-model="selectedAssignee" class="filter-select">
          <option value="">전체</option>
          <option v-for="a in allAssignees" :key="a">{{ a }}</option>
        </select>
      </div>
      <div class="filter-group">
        <span class="filter-label">업무유형</span>
        <select v-model="selectedType" class="filter-select">
          <option value="">전체</option>
          <option v-for="t in allTypes" :key="t">{{ t }}</option>
        </select>
      </div>
      <div class="filter-group" style="margin-left:auto">
        <label class="demo-toggle">
          <input type="checkbox" v-model="isDemo" />
          <span class="demo-label">데모 모드</span>
        </label>
      </div>
    </div>

    <!-- 메트릭 -->
    <div class="metrics">
      <div class="mc">
        <div class="mc-label">총 관리 대상</div>
        <div class="mc-val" style="color:var(--blue)">{{ displayData.length }}</div>
        <div class="mc-sub">미완료 티켓</div>
      </div>
      <div class="mc mc-clickable" @click="scrollTo('aging-section')">
        <div class="mc-label">⚠️ 정체 리스크 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--yellow)">{{ highRiskData.length }}</div>
        <div class="mc-sub">{{ riskThreshold }}일 이상 멈춤</div>
      </div>
      <div class="mc mc-clickable" @click="scrollTo('top10-section')">
        <div class="mc-label">🔥 병목 담당자 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--red)">{{ top10.length }}</div>
        <div class="mc-sub">Top 10 확인</div>
      </div>
      <div class="mc mc-clickable" @click="scrollTo('missing-section')">
        <div class="mc-label">📭 기한 누락 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--muted)">{{ missingDueData.length }}</div>
        <div class="mc-sub">Due date 없음</div>
      </div>
      <div class="mc mc-clickable" @click="scrollTo('overdue-section')">
        <div class="mc-label">🚨 기한 지연 <span class="mc-arrow">↓</span></div>
        <div class="mc-val" style="color:var(--red)">{{ overdueData.length }}</div>
        <div class="mc-sub">마감일 초과</div>
      </div>
    </div>

    <!-- Top 10 병목 담당자 -->
    <div class="section-title" id="top10-section">🏆 병목 담당자 Top 10</div>
    <div v-if="top10.length === 0" class="empty-card">정체 기간 {{ riskThreshold }}일 이상인 담당자가 없어요 ✓</div>
    <div v-else class="top10-grid">
      <div v-for="(item, i) in top10" :key="item.name"
        class="top10-card" :class="{selected: detailAssignee===item.name}"
        @click="toggleDetail(item.name)">
        <div class="top10-rank" :class="rankClass(i)">{{ i+1 }}</div>
        <div class="top10-info">
          <div class="top10-name">{{ item.name }}</div>
          <div class="top10-count">🚨 {{ item.count }}건 정체</div>
        </div>
        <div class="top10-bar">
          <div class="top10-fill" :style="{ width: (item.count / top10[0].count * 100) + '%' }"></div>
        </div>
        <div class="top10-arrow">{{ detailAssignee===item.name ? '▲' : '▼' }}</div>
      </div>
    </div>

    <!-- 상세 패널 -->
    <transition name="slide">
      <div v-if="detailAssignee" class="detail-panel">
        <div class="detail-header">
          <span>👤 {{ detailAssignee }} — 정체 티켓 {{ detailRows.length }}건</span>
          <button class="close-btn" @click="detailAssignee=null">✕</button>
        </div>
        <table class="data-table">
          <thead><tr><th style="width:90px">티켓번호</th><th>요약</th><th style="width:100px">현재상태</th><th style="width:80px">정체(일)</th><th style="width:60px">링크</th></tr></thead>
          <tbody>
            <tr v-for="r in detailRows" :key="r.티켓번호" class="data-row">
              <td class="cell-mono">{{ r.티켓번호 }}</td>
              <td class="cell-text">{{ r.요약 }}</td>
              <td><span class="s-chip" :class="stateClass(r.현재상태)">{{ r.현재상태 }}</span></td>
              <td><span class="aging-badge" :class="agingClass(r['정체기간(일)'])">{{ r['정체기간(일)'] }}일</span></td>
              <td><a :href="r.링크" target="_blank" class="link-btn">열기 ↗</a></td>
            </tr>
          </tbody>
        </table>
      </div>
    </transition>

    <div class="divider"></div>

    <!-- 탭 -->
    <div class="tabs">
      <div class="tab" :class="{on:activeTab==='aging'}" @click="activeTab='aging'">
        ⏳ 정체 티켓 <span class="tab-cnt">{{ filteredHighRisk.length }}</span>
      </div>
      <div class="tab" :class="{on:activeTab==='due'}" @click="activeTab='due'">
        🚨 일정 리스크 <span class="tab-cnt">{{ missingDueData.length + overdueData.length }}</span>
      </div>
    </div>

    <!-- 정체 탭 -->
    <div v-if="activeTab==='aging'" id="aging-section">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width:90px">티켓번호</th>
              <th style="width:80px">유형</th>
              <th>요약</th>
              <th style="width:90px">담당자</th>
              <th style="width:100px">현재상태</th>
              <th style="width:80px">정체(일)</th>
              <th style="width:60px">링크</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!filteredHighRisk.length">
              <td colspan="7" class="empty-state">정체 티켓이 없습니다 ✓</td>
            </tr>
            <tr v-for="r in filteredHighRisk" :key="r.티켓번호" class="data-row">
              <td class="cell-mono">{{ r.티켓번호 }}</td>
              <td><span class="type-chip">{{ r.업무유형 }}</span></td>
              <td class="cell-text">{{ r.요약 }}</td>
              <td class="cell-text muted">{{ r.담당자 }}</td>
              <td><span class="s-chip" :class="stateClass(r.현재상태)">{{ r.현재상태 }}</span></td>
              <td><span class="aging-badge" :class="agingClass(r['정체기간(일)'])">{{ r['정체기간(일)'] }}일</span></td>
              <td><a :href="r.링크" target="_blank" class="link-btn">열기 ↗</a></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 바 차트 -->
      <div class="chart-section">
        <div class="chart-title">📊 담당자별 정체 건수</div>
        <div class="bar-chart">
          <div v-for="item in assigneeChart" :key="item.name" class="bar-row">
            <div class="bar-label">{{ item.name }}</div>
            <div class="bar-track">
              <div class="bar-fill" :style="{width:(item.count/chartMax*100)+'%'}"></div>
              <span class="bar-count">{{ item.count }}건</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 일정 리스크 탭 -->
    <div v-if="activeTab==='due'">
      <div class="sub-section" id="missing-section">
        <div class="sub-title">📭 기한 누락 작업 <span class="sub-count">{{ missingDueData.length }}건</span></div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th style="width:90px">티켓번호</th><th>요약</th><th style="width:90px">담당자</th><th style="width:100px">현재상태</th><th style="width:60px">링크</th></tr></thead>
            <tbody>
              <tr v-if="!missingDueData.length"><td colspan="5" class="empty-state">누락된 티켓이 없습니다 ✓</td></tr>
              <tr v-for="r in missingDueData" :key="r.티켓번호" class="data-row">
                <td class="cell-mono">{{ r.티켓번호 }}</td>
                <td class="cell-text">{{ r.요약 }}</td>
                <td class="cell-text muted">{{ r.담당자 }}</td>
                <td><span class="s-chip" :class="stateClass(r.현재상태)">{{ r.현재상태 }}</span></td>
                <td><a :href="r.링크" target="_blank" class="link-btn">열기 ↗</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="sub-section" id="overdue-section">
        <div class="sub-title">🚨 기한 지연 작업 <span class="sub-count">{{ overdueData.length }}건</span></div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th style="width:90px">티켓번호</th><th>요약</th><th style="width:90px">담당자</th><th style="width:100px">기한</th><th style="width:80px">D+경과</th><th style="width:60px">링크</th></tr></thead>
            <tbody>
              <tr v-if="!overdueData.length"><td colspan="6" class="empty-state">지연된 티켓이 없습니다 ✓</td></tr>
              <tr v-for="r in overdueData" :key="r.티켓번호" class="data-row">
                <td class="cell-mono">{{ r.티켓번호 }}</td>
                <td class="cell-text">{{ r.요약 }}</td>
                <td class="cell-text muted">{{ r.담당자 }}</td>
                <td class="cell-mono" style="color:var(--red)">{{ r.기한 }}</td>
                <td><span class="aging-badge ag-high">{{ overdueDays(r.기한) }}일</span></td>
                <td><a :href="r.링크" target="_blank" class="link-btn">열기 ↗</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const MOCK = [
  {업무유형:'버그',티켓번호:'DEMO-101',요약:'[결제] 특정 환경에서 결제 버튼 미노출',담당자:'강대리',현재상태:'대기','정체기간(일)':15,기한:'2026-04-01',지연여부:'지연 됨 ❌',링크:'#'},
  {업무유형:'작업',티켓번호:'DEMO-102',요약:'[UI/UX] 메인 페이지 배너 리뉴얼',담당자:'이주임',현재상태:'진행 중','정체기간(일)':7,기한:'2026-06-15',지연여부:'정상',링크:'#'},
  {업무유형:'개선',티켓번호:'DEMO-103',요약:'[서버] API 응답 속도 최적화',담당자:'박팀장',현재상태:'확인/수정 중','정체기간(일)':5,기한:'누락 🚨',지연여부:'-',링크:'#'},
  {업무유형:'에픽',티켓번호:'DEMO-104',요약:'[신규] 2분기 시즌 패스 시스템',담당자:'김사원',현재상태:'접수 대기','정체기간(일)':3,기한:'2026-07-20',지연여부:'정상',링크:'#'},
  {업무유형:'버그',티켓번호:'DEMO-105',요약:'[AOS] 특정 단말기 앱 무한 로딩',담당자:'최주임',현재상태:'대기','정체기간(일)':12,기한:'2026-03-31',지연여부:'지연 됨 ❌',링크:'#'},
  {업무유형:'하위 작업',티켓번호:'DEMO-106',요약:'상점 아이템 아이콘 리소스 제작',담당자:'정대리',현재상태:'진행 중','정체기간(일)':8,기한:'2026-04-10',지연여부:'지연 됨 ❌',링크:'#'},
  {업무유형:'작업',티켓번호:'DEMO-107',요약:'[인프라] DB 서버 스토리지 증설',담당자:'홍팀장',현재상태:'확인/수정 중','정체기간(일)':4,기한:'누락 🚨',지연여부:'-',링크:'#'},
  {업무유형:'개선',티켓번호:'DEMO-108',요약:'[웹] 커뮤니티 게시판 검색 고도화',담당자:'박사원',현재상태:'진행 예정','정체기간(일)':6,기한:'2026-06-30',지연여부:'정상',링크:'#'},
  {업무유형:'버그',티켓번호:'DEMO-109',요약:'[iOS] 푸시 알림 간헐적 미발송',담당자:'최주임',현재상태:'대기','정체기간(일)':10,기한:'2026-04-05',지연여부:'지연 됨 ❌',링크:'#'},
  {업무유형:'작업',티켓번호:'DEMO-110',요약:'[기획] 랭킹 시스템 밸런스 조정안',담당자:'김사원',현재상태:'진행 중','정체기간(일)':2,기한:'2026-07-01',지연여부:'정상',링크:'#'},
  {업무유형:'버그',티켓번호:'DEMO-111',요약:'[결제] 환불 처리 지연 건 개선',담당자:'강대리',현재상태:'대기','정체기간(일)':9,기한:'2026-04-20',지연여부:'정상',링크:'#'},
  {업무유형:'에픽',티켓번호:'DEMO-112',요약:'신규 캐릭터 시스템 설계',담당자:'이주임',현재상태:'접수 대기','정체기간(일)':11,기한:'누락 🚨',지연여부:'-',링크:'#'},
]

export default {
  name: 'JiraRadar',
  data() {
    return {
      isDemo: true, riskThreshold: 3,
      selectedAssignee: '', selectedType: '',
      activeTab: 'aging', detailAssignee: null,
    }
  },
  computed: {
    displayData() { return MOCK },
    allAssignees() { return [...new Set(this.displayData.map(r=>r.담당자))].sort() },
    allTypes()     { return [...new Set(this.displayData.map(r=>r.업무유형))].sort() },
    highRiskData() { return this.displayData.filter(r => r['정체기간(일)'] >= this.riskThreshold) },
    filteredHighRisk() {
      let d = this.highRiskData
      if (this.selectedAssignee) d = d.filter(r => r.담당자 === this.selectedAssignee)
      if (this.selectedType)     d = d.filter(r => r.업무유형 === this.selectedType)
      return d.sort((a,b) => b['정체기간(일)'] - a['정체기간(일)'])
    },
    missingDueData() { return this.displayData.filter(r => r.기한 === '누락 🚨') },
    overdueData()    { return this.displayData.filter(r => r.지연여부 === '지연 됨 ❌') },
    top10() {
      const counts = {}
      this.highRiskData.forEach(r => { counts[r.담당자] = (counts[r.담당자]||0)+1 })
      return Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,10).map(([name,count])=>({name,count}))
    },
    detailRows() {
      if (!this.detailAssignee) return []
      return this.highRiskData.filter(r=>r.담당자===this.detailAssignee).sort((a,b)=>b['정체기간(일)']-a['정체기간(일)'])
    },
    assigneeChart() {
      const d = this.selectedAssignee
        ? this.filteredHighRisk
        : this.highRiskData
      const counts = {}
      d.forEach(r => { counts[r.담당자] = (counts[r.담당자]||0)+1 })
      return Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,8).map(([name,count])=>({name,count}))
    },
    chartMax() { return Math.max(...this.assigneeChart.map(c=>c.count), 1) },
  },
  methods: {
    scrollTo(id) {
      const tabMap = { 'aging-section':'aging', 'top10-section':'aging', 'missing-section':'due', 'overdue-section':'due' }
      this.activeTab = tabMap[id] || 'aging'
      this.$nextTick(() => {
        setTimeout(() => {
          const el = document.getElementById(id)
          if (el) el.scrollIntoView({ behavior:'smooth', block:'start' })
        }, 80)
      })
    },
    toggleDetail(name) { this.detailAssignee = this.detailAssignee===name ? null : name },
    rankClass(i)    { return i===0?'rank-1':i===1?'rank-2':i===2?'rank-3':'' },
    stateClass(s) {
      if (s==='진행 중')       return 'sc-progress'
      if (s==='대기')          return 'sc-wait'
      if (s.includes('수정'))  return 'sc-fix'
      if (s.includes('예정'))  return 'sc-plan'
      return 'sc-other'
    },
    agingClass(d) {
      if (d >= 10) return 'ag-high'
      if (d >= 5)  return 'ag-mid'
      return 'ag-low'
    },
    overdueDays(due) {
      if (!due || due === '누락 🚨') return 0
      const diff = Math.floor((new Date() - new Date(due)) / 86400000)
      return diff > 0 ? diff : 0
    },
  }
}
</script>

<style scoped>
.page { padding:20px 24px }

.filter-bar { display:flex; align-items:center; gap:12px; flex-wrap:wrap; background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:12px 16px; margin-bottom:16px }
.filter-label { font-size:11px; color:var(--muted); white-space:nowrap }
.filter-group { display:flex; align-items:center; gap:8px }
.filter-select { background:var(--bg3); border:1px solid var(--border2); border-radius:6px; padding:5px 8px; color:var(--text); font-size:12px; outline:none }
.demo-toggle { display:flex; align-items:center; gap:6px; cursor:pointer; font-size:12px }
.demo-toggle input { accent-color:var(--amber) }
.demo-label { color:var(--muted) }

.metrics { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-bottom:20px }
.mc      { background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:14px 16px }
.mc-label{ font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; margin-bottom:4px; display:flex; align-items:center; gap:4px }
.mc-val  { font-size:24px; font-weight:600; font-family:'DM Mono',monospace }
.mc-sub  { font-size:11px; color:var(--muted); margin-top:3px }
.mc-arrow{ font-size:10px }
.mc-clickable { cursor:pointer; transition:all .15s; user-select:none }
.mc-clickable:hover { filter:brightness(.96); transform:translateY(-1px) }

.section-title { font-size:13px; font-weight:600; color:var(--text); margin-bottom:10px; scroll-margin-top:80px }
.empty-card { background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:24px; text-align:center; color:var(--muted); font-size:13px; margin-bottom:16px }

.top10-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin-bottom:16px }
.top10-card { background:var(--bg2); border:1px solid var(--border); border-radius:8px; padding:12px; cursor:pointer; transition:all .15s; display:flex; flex-direction:column; gap:6px }
.top10-card:hover  { border-color:var(--amber) }
.top10-card.selected { border-color:var(--amber); background:var(--bg3) }
.top10-rank  { font-size:20px; font-weight:700; font-family:'DM Mono',monospace; color:var(--muted) }
.rank-1 { color:#f59e0b }
.rank-2 { color:#94a3b8 }
.rank-3 { color:#b45309 }
.top10-info  { flex:1 }
.top10-name  { font-size:13px; font-weight:500; color:var(--text) }
.top10-count { font-size:11px; color:var(--red); margin-top:2px }
.top10-bar   { height:4px; background:var(--bg4); border-radius:2px; overflow:hidden }
.top10-fill  { height:100%; background:var(--red); border-radius:2px; transition:width .3s }
.top10-arrow { font-size:10px; color:var(--muted); text-align:right }

.detail-panel { background:var(--bg2); border:1px solid var(--amber); border-radius:10px; margin-bottom:16px; overflow:hidden }
.detail-header { display:flex; align-items:center; justify-content:space-between; padding:10px 14px; background:var(--amber-dim); border-bottom:1px solid var(--border); font-size:13px; font-weight:600 }
.close-btn { background:none; border:none; color:var(--muted); cursor:pointer; font-size:14px }
.close-btn:hover { color:var(--text) }

.slide-enter-active, .slide-leave-active { transition:all .2s }
.slide-enter-from, .slide-leave-to { opacity:0; transform:translateY(-8px) }

.divider { border:none; border-top:1px solid var(--border); margin:16px 0 }

.tabs  { display:flex; gap:2px; background:var(--bg2); border:1px solid var(--border); border-radius:8px; padding:3px; width:fit-content; margin-bottom:14px }
.tab   { padding:6px 16px; border-radius:6px; cursor:pointer; font-size:13px; color:var(--muted); transition:all .15s; display:flex; align-items:center; gap:6px }
.tab.on{ background:var(--bg4); color:var(--text) }
.tab-cnt { background:var(--bg3); color:var(--muted); font-size:11px; padding:1px 6px; border-radius:10px; font-family:'DM Mono',monospace }
.tab.on .tab-cnt { background:var(--bg2); color:var(--text) }

.table-wrap { background:var(--bg2); border:1px solid var(--border); border-radius:10px; overflow:hidden; margin-bottom:16px }
.data-table { width:100%; border-collapse:collapse }
.data-table th { background:var(--bg3); padding:9px 12px; text-align:left; font-size:11px; font-weight:600; color:var(--muted); border-bottom:1px solid var(--border); white-space:nowrap }
.data-table td { padding:9px 12px; border-bottom:1px solid var(--border); vertical-align:middle }
.data-table tr:last-child td { border-bottom:none }
.data-row:hover td { background:var(--bg3) }
.cell-text { font-size:13px; color:var(--text) }
.cell-mono { font-size:12px; font-family:'DM Mono',monospace }
.muted { color:var(--muted) }
.empty-state { text-align:center; padding:30px; color:var(--muted); font-size:13px }
.link-btn { color:var(--blue); text-decoration:none; font-size:12px; font-weight:500 }
.link-btn:hover { text-decoration:underline }

.type-chip { display:inline-block; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600; background:var(--bg4); color:var(--muted) }
.s-chip { display:inline-block; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:600 }
.sc-progress { background:var(--blue-dim); color:var(--blue) }
.sc-wait     { background:var(--bg4); color:var(--muted) }
.sc-fix      { background:var(--yellow-dim); color:var(--yellow) }
.sc-plan     { background:var(--green-dim); color:var(--green) }
.sc-other    { background:var(--bg4); color:var(--muted) }

.aging-badge { display:inline-block; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:600; font-family:'DM Mono',monospace }
.ag-high { background:var(--red-dim); color:var(--red) }
.ag-mid  { background:var(--yellow-dim); color:var(--yellow) }
.ag-low  { background:var(--green-dim); color:var(--green) }

.chart-section { background:var(--bg2); border:1px solid var(--border); border-radius:10px; padding:16px; margin-bottom:16px }
.chart-title   { font-size:13px; font-weight:600; margin-bottom:14px; color:var(--text) }
.bar-chart { display:flex; flex-direction:column; gap:10px }
.bar-row   { display:flex; align-items:center; gap:10px }
.bar-label { width:72px; font-size:12px; color:var(--muted); text-align:right; flex-shrink:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.bar-track { flex:1; height:20px; background:var(--bg4); border-radius:5px; overflow:hidden; position:relative }
.bar-fill  { height:100%; background:var(--amber); border-radius:5px; transition:width .4s }
.bar-count { position:absolute; right:8px; top:50%; transform:translateY(-50%); font-size:11px; font-family:'DM Mono',monospace; color:var(--text) }

.sub-section { margin-bottom:16px; scroll-margin-top:80px }
.sub-title   { font-size:13px; font-weight:600; margin-bottom:8px; color:var(--text); display:flex; align-items:center; gap:8px }
.sub-count   { background:var(--bg4); color:var(--muted); font-size:11px; padding:2px 8px; border-radius:10px; font-weight:400 }

@media(max-width:900px) { .metrics{grid-template-columns:repeat(3,1fr)} .top10-grid{grid-template-columns:repeat(2,1fr)} }
</style>