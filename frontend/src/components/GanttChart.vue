<template>
  <div>
    <div class="gantt-nav">
      <div class="period-btns">
        <button v-for="p in PERIODS" :key="p.key"
          class="period-btn" :class="{on: period===p.key}" @click="setPeriod(p.key)">
          {{ p.label }}
        </button>
      </div>
      <div class="nav-center">
        <button class="nav-btn" @click="prev">← 이전</button>
        <span class="range">{{ rangeLabel }}</span>
        <button class="nav-btn" @click="next">다음 →</button>
      </div>
      <button class="nav-btn" @click="goToday">오늘</button>
    </div>

    <div class="gantt-wrap">
      <div v-if="!tasks.length" class="empty-state">태스크가 없습니다</div>
      <div v-else class="gantt-scroll-outer">
        <!-- 고정 레이블 영역 + 스크롤 영역 -->
        <div class="gantt-inner">
          <!-- 헤더 -->
          <div class="g-row g-header">
            <div class="g-label-head">태스크</div>
            <div class="g-dates-head">
              <!-- 년/월 표시 행 -->
              <div class="g-month-row">
                <div v-for="m in monthGroups" :key="m.label"
                  class="g-month-cell"
                  :style="{ width: (m.count * CW) + 'px', minWidth: (m.count * CW) + 'px' }">
                  {{ m.label }}
                </div>
              </div>
              <!-- 날짜 행 -->
              <div class="g-day-row">
                <div v-for="(d,i) in dates" :key="d"
                  class="g-day-head"
                  :style="{ width: CW+'px', minWidth: CW+'px' }"
                  :class="{ today: d===todayStr, weekend: isWeekend(d) }">
                  <span class="day-num">{{ fmtDay(d) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 태스크 행 -->
          <div v-for="t in tasks" :key="t.id" class="g-row">
            <div class="g-label">
              <span class="gb" :style="groupStyle(t.group)">{{ t.group }}</span>
              <span class="g-task-name">{{ t.task }}</span>
            </div>
            <div class="g-dates-body">
              <template v-for="(d,i) in dates" :key="d">
                <div v-if="isStart(t,i)"
                  class="g-bar-cell"
                  :style="{ width: barW(t)+'px', minWidth: barW(t)+'px' }">
                  <div class="g-bar" :style="groupStyle(t.group)">{{ t.task }}</div>
                </div>
                <div v-else-if="!inBar(t,i)"
                  class="g-empty"
                  :style="{ width: CW+'px', minWidth: CW+'px' }"
                  :class="{ today: d===todayStr, weekend: isWeekend(d) }">
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { today, getStatus } from '../utils.js'

const PERIODS = [
  { key:'week',  label:'1주일', days:7  },
  { key:'month', label:'1개월', days:30 },
  { key:'all',   label:'전체',  days:0  },
]

const GROUP_PALETTE = {
  '기획':     { bg:'#dbeafe', color:'#1e40af', border:'#93c5fd' },
  '기획팀':   { bg:'#dbeafe', color:'#1e40af', border:'#93c5fd' },
  '디자인':   { bg:'#ede9fe', color:'#5b21b6', border:'#c4b5fd' },
  '디자인팀': { bg:'#ede9fe', color:'#5b21b6', border:'#c4b5fd' },
  '개발(BE)': { bg:'#dcfce7', color:'#166534', border:'#86efac' },
  '개발(FE)': { bg:'#fef9c3', color:'#854d0e', border:'#fde047' },
  'Android':  { bg:'#ffedd5', color:'#9a3412', border:'#fdba74' },
  'iOS':      { bg:'#cffafe', color:'#155e75', border:'#67e8f9' },
  'QA':       { bg:'#fce7f3', color:'#9d174d', border:'#f9a8d4' },
  'QA팀':     { bg:'#fce7f3', color:'#9d174d', border:'#f9a8d4' },
}
const DEFAULT_PALETTE = { bg:'#f1f5f9', color:'#475569', border:'#cbd5e1' }

// 그룹 이름에서 가장 유사한 팔레트 찾기
function getPalette(group) {
  if (!group) return DEFAULT_PALETTE
  if (GROUP_PALETTE[group]) return GROUP_PALETTE[group]
  // 부분 매칭
  const key = Object.keys(GROUP_PALETTE).find(k => group.includes(k) || k.includes(group))
  return key ? GROUP_PALETTE[key] : DEFAULT_PALETTE
}

export default {
  name: 'GanttChart',
  props: { tasks: { type:Array, default:()=>[] } },
  data() {
    return { period:'month', offset:0, todayStr:today(), PERIODS, CW:28 }
  },
  computed: {
    days() {
      if (this.period==='week')  return 7
      if (this.period==='month') return 30
      if (!this.tasks.length) return 30
      const starts = this.tasks.map(t=>t.startDate).filter(Boolean)
      const ends   = this.tasks.map(t=>t.endDate).filter(Boolean)
      if (!starts.length||!ends.length) return 30
      const minD = starts.reduce((a,b)=>a<b?a:b)
      const maxD = ends.reduce((a,b)=>a>b?a:b)
      return Math.max(Math.round((new Date(maxD)-new Date(minD))/86400000)+1, 7)
    },
    startDt() {
      if (this.period==='all' && this.tasks.length) {
        const starts = this.tasks.map(t=>t.startDate).filter(Boolean)
        if (starts.length) {
          const min = starts.reduce((a,b)=>a<b?a:b)
          const d = new Date(min); d.setDate(d.getDate()+this.offset*this.days)
          return d.toISOString().slice(0,10)
        }
      }
      const d = new Date(); d.setDate(d.getDate()+this.offset*this.days)
      return d.toISOString().slice(0,10)
    },
    dates() {
      return Array.from({length:this.days},(_,i)=>{
        const d = new Date(this.startDt); d.setDate(d.getDate()+i)
        return d.toISOString().slice(0,10)
      })
    },
    rangeLabel() {
      if (!this.dates.length) return ''
      const s = this.dates[0]
      const e = this.dates[this.dates.length-1]
      return `${s.slice(0,7).replace('-','/')} ${s.slice(8)} ~ ${e.slice(0,7).replace('-','/')} ${e.slice(8)}`
    },
    // 년/월 그룹핑
    monthGroups() {
      const groups = []
      let cur = null
      this.dates.forEach(d => {
        const label = `${new Date(d).getFullYear()}년 ${new Date(d).getMonth()+1}월`
        if (!cur || cur.label !== label) {
          cur = { label, count: 1 }
          groups.push(cur)
        } else {
          cur.count++
        }
      })
      return groups
    },
  },
  methods: {
    setPeriod(p) { this.period=p; this.offset=0 },
    prev()    { this.offset-- },
    next()    { this.offset++ },
    goToday() { this.offset=0 },
    isWeekend(d) { const day=new Date(d).getDay(); return day===0||day===6 },
    fmtDay(d)  { return new Date(d).getDate() },
    si(t) { return Math.max(0,Math.round((new Date(t.startDate||this.dates[0])-new Date(this.dates[0]))/86400000)) },
    ei(t) { return Math.min(this.days-1,Math.round((new Date(t.endDate||this.dates[this.days-1])-new Date(this.dates[0]))/86400000)) },
    isStart(t,i) { return i===this.si(t)&&i<=this.ei(t) },
    inBar(t,i)   { return i>this.si(t)&&i<=this.ei(t) },
    barW(t)      { return Math.max(1,this.ei(t)-this.si(t)+1)*this.CW },
    groupStyle(group) {
      const p = getPalette(group)
      return { background:p.bg, color:p.color, border:`1px solid ${p.border}` }
    },
  }
}
</script>

<style scoped>
.gantt-nav{display:flex;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
.period-btns{display:flex;gap:4px}
.period-btn{padding:4px 12px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-size:12px;cursor:pointer;font-family:inherit;transition:all .15s}
.period-btn.on{background:var(--bg4);color:var(--text);border-color:var(--border)}
.nav-center{display:flex;align-items:center;gap:8px;flex:1;justify-content:center}
.nav-btn{padding:4px 10px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--muted);font-size:12px;cursor:pointer;font-family:inherit}
.nav-btn:hover{background:var(--bg3);color:var(--text)}
.range{font-size:12px;color:var(--muted);min-width:200px;text-align:center}

.gantt-wrap{background:var(--bg2);border:1px solid var(--border);border-radius:10px;overflow:hidden}
.gantt-scroll-outer{overflow-x:auto}
.gantt-inner{min-width:max-content}

/* 헤더 */
.g-header{display:flex;border-bottom:1px solid var(--border);background:var(--bg3)}
.g-label-head{width:180px;min-width:180px;border-right:1px solid var(--border);padding:0 10px;font-size:11px;color:var(--muted);display:flex;align-items:flex-end;padding-bottom:6px}
.g-dates-head{display:flex;flex-direction:column;flex:1}

/* 년/월 행 */
.g-month-row{display:flex;border-bottom:1px solid var(--border)}
.g-month-cell{font-size:10px;font-weight:600;color:var(--text);padding:4px 0;text-align:center;border-right:1px solid var(--border);background:var(--bg3)}

/* 날짜 행 */
.g-day-row{display:flex}
.g-day-head{border-right:1px solid var(--border);display:flex;align-items:center;justify-content:center;padding:5px 0}
.g-day-head.today{background:rgba(245,158,11,.15)}
.g-day-head.weekend .day-num{color:var(--red);font-weight:600}
.day-num{font-size:10px;color:var(--muted)}
.g-day-head.today .day-num{color:var(--amber);font-weight:700}

/* 태스크 행 */
.g-row{display:flex;border-bottom:1px solid var(--border);min-height:36px;align-items:stretch}
.g-row:last-child{border-bottom:none}
.g-label{width:180px;min-width:180px;border-right:1px solid var(--border);padding:7px 10px;display:flex;align-items:center;gap:6px;overflow:hidden}
.g-task-name{font-size:11px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.g-dates-body{display:flex;align-items:center}

/* 빈 셀 */
.g-empty{border-right:1px solid var(--border);height:36px;flex-shrink:0}
.g-empty.today{background:rgba(245,158,11,.06)}
.g-empty.weekend{background:rgba(239,68,68,.04)}

/* 바 셀 */
.g-bar-cell{display:flex;align-items:center;padding:8px 3px;flex-shrink:0}
.g-bar{height:20px;border-radius:4px;display:flex;align-items:center;padding:0 8px;font-size:10px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:100%}

/* 그룹 뱃지 */
.gb{display:inline-block;padding:1px 6px;border-radius:4px;font-size:9px;font-weight:600;flex-shrink:0;white-space:nowrap}

.empty-state{text-align:center;padding:40px;color:var(--muted);font-size:13px}
</style>