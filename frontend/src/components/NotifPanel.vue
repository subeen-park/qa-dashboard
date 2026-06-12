<!-- NotifPanel.vue -->
<template>
  <div class="notif-grid">
    <div>
      <div class="notif-card">
        <h3>웹훅 설정</h3>
        <div class="field"><label>메신저</label>
          <select v-model="form.type" @change="form.token='';form.chat='';form.url=''">
            <option value="telegram">Telegram</option><option value="slack">Slack</option>
            <option value="teams">Microsoft Teams</option><option value="custom">Custom</option>
          </select>
        </div>
        <template v-if="form.type==='telegram'">
          <div class="field"><label>Bot Token</label><input type="password" v-model="form.token" placeholder="123456789:AABBccdd..."/></div>
          <div class="field"><label>Chat ID</label><input v-model="form.chat" placeholder="-1001234567890"/></div>
        </template>
        <template v-else>
          <div class="field"><label>Webhook URL</label><input v-model="form.url" :placeholder="urlPh"/></div>
        </template>
        <div class="btn-row">
          <button class="btn btn-primary" style="flex:1" @click="save">저장</button>
          <button class="btn btn-ghost" @click="test" :disabled="testing">{{ testing?'전송 중...':'테스트' }}</button>
        </div>
        <div class="help">{{ helpText }}</div>
      </div>
      <div class="notif-card" style="margin-top:12px">
        <h3>알림 규칙</h3>
        <div class="rule-list">
          <div class="rule-item" v-for="r in rules" :key="r.key">
            <div class="rule-info"><span style="font-size:16px">{{ r.icon }}</span><div><div style="font-weight:500;font-size:13px">{{ r.label }}</div><div style="font-size:11px;color:var(--muted)">{{ r.sub }}</div></div></div>
            <label class="toggle"><input type="checkbox" v-model="r.on"><span class="ts"></span></label>
          </div>
        </div>
      </div>
    </div>
    <div>
      <div class="notif-card">
        <h3>예정 알림</h3>
        <div v-if="!alerts.length" class="empty-state">예정된 알림 없음</div>
        <div v-for="a in alerts" :key="a.task.id" class="alert-item" :class="a.d<=1?'a-1d':'a-7d'">
          <div style="flex:1"><div style="font-size:13px;font-weight:500">{{ a.task.task }}</div><div style="font-size:11px;color:var(--muted);margin-top:2px">{{ a.task.group }} · {{ a.task.assignee||'미지정' }} · {{ a.task.endDate }}</div></div>
          <span class="ab" :class="a.d<=1?'ab-1d':'ab-7d'">{{ a.d===0?'오늘':a.d===1?'내일':`D-${a.d}` }}</span>
        </div>
      </div>
      <div class="log-card">
        <div class="log-head">최근 발송 로그</div>
        <div v-if="!logs.length" class="empty-state" style="padding:20px">기록 없음</div>
        <div v-for="l in logs.slice(0,8)" :key="l.time" class="log-item">
          <div class="log-icon" :class="{'li-ok':l.type==='success','li-err':l.type==='error','li-warn':l.type==='warning'}">{{ l.type==='success'?'✓':l.type==='error'?'✕':'!' }}</div>
          <div><div style="font-size:13px;font-weight:500">{{ l.title }}</div><div style="font-size:11px;color:var(--muted)">{{ l.detail }} · {{ l.time }}</div></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { api } from '../api/index.js'
import { diffDays } from '../utils.js'
export default {
  name:'NotifPanel', props:{tasks:Array,logs:Array}, emits:['toast','reload-logs'],
  data(){ return{
    form:{type:'telegram',token:'',chat:'',url:''},
    testing:false,
    rules:[
      {key:'d7',icon:'📅',label:'마감 7일 전',sub:'D-7 자동 알림',on:true},
      {key:'d1',icon:'⚡',label:'마감 1일 전',sub:'D-1 긴급 알림',on:true},
      {key:'over',icon:'🚨',label:'마감 초과',sub:'지연 매일 리마인드',on:true},
    ]
  }},
  computed:{
    alerts(){ return this.tasks.filter(t=>{ if(!t.endDate||parseInt(t.progress||0)>=100)return false; const d=diffDays(t.endDate); return d!==null&&d>=0&&d<=7 }).map(t=>({task:t,d:diffDays(t.endDate)})).sort((a,b)=>a.d-b.d) },
    urlPh(){ return{slack:'https://hooks.slack.com/services/...',teams:'https://outlook.office.com/webhook/...',custom:'https://your-webhook.com'}[this.form.type]||'' },
    helpText(){ return{telegram:'① @BotFather에서 봇 생성\n② Chat ID 확인 후 입력',slack:'Slack → Incoming Webhooks에서 URL 발급',teams:'Teams 채널 → 커넥터 → Incoming Webhook',custom:'POST {"text":"메시지"} JSON 전송'}[this.form.type]||'' }
  },
  async mounted(){ try{ const wh=await api.getWebhook(); this.form={...this.form,...wh,token:''} }catch{} },
  methods:{
    async save(){ await api.saveWebhook(this.form); this.$emit('toast',{msg:'웹훅 저장됨',type:'ok'}) },
    async test(){ this.testing=true; try{ const r=await api.testWebhook(); this.$emit('toast',{msg:r.ok?'테스트 전송 성공 ✓':`실패: ${r.message}`,type:r.ok?'ok':'err'}); this.$emit('reload-logs') }finally{this.testing=false} }
  }
}
</script>
<style scoped>
.notif-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.notif-card{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:16px}
.notif-card h3{font-size:13px;font-weight:500;margin-bottom:12px}
.field{margin-bottom:10px}.field label{display:block;font-size:11px;color:var(--muted);margin-bottom:4px}
.field input,.field select{width:100%;background:var(--bg3);border:1px solid var(--border2);border-radius:6px;padding:7px 10px;color:var(--text);font-size:13px;font-family:inherit;outline:none}
.field input:focus,.field select:focus{border-color:var(--amber)}.field select option{background:var(--bg2)}
.btn-row{display:flex;gap:8px;margin-top:6px}
.btn{display:inline-flex;align-items:center;padding:7px 14px;border-radius:7px;font-size:13px;cursor:pointer;border:none;font-family:inherit;font-weight:500}
.btn-primary{background:var(--amber);color:#0a0800}.btn-primary:hover{background:#f0b85a}
.btn-ghost{background:transparent;color:var(--muted);border:1px solid var(--border2)}.btn-ghost:hover{background:var(--bg3);color:var(--text)}
.btn:disabled{opacity:.5;cursor:not-allowed}
.help{font-size:11px;color:var(--muted);margin-top:10px;white-space:pre-line;line-height:1.6}
.rule-list{display:flex;flex-direction:column;gap:8px}
.rule-item{display:flex;align-items:center;justify-content:space-between;background:var(--bg3);border-radius:7px;padding:10px 12px}
.rule-info{display:flex;align-items:center;gap:10px}
.toggle{position:relative;width:36px;height:20px;cursor:pointer}.toggle input{display:none}
.ts{position:absolute;inset:0;background:var(--bg4);border-radius:999px;transition:.2s}
.toggle input:checked+.ts{background:var(--amber)}
.ts::after{content:'';position:absolute;width:14px;height:14px;background:white;border-radius:50%;top:3px;left:3px;transition:.2s}
.toggle input:checked+.ts::after{left:19px}
.alert-item{display:flex;align-items:center;gap:10px;background:var(--bg3);border-radius:7px;padding:10px 12px;border-left:3px solid transparent;margin-bottom:6px}
.a-7d{border-color:var(--yellow)}.a-1d{border-color:var(--red)}
.ab{font-size:11px;font-weight:500;padding:2px 8px;border-radius:4px;white-space:nowrap}
.ab-7d{background:var(--yellow-dim);color:var(--yellow)}.ab-1d{background:var(--red-dim);color:var(--red)}
.log-card{background:var(--bg2);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-top:14px}
.log-head{background:var(--bg3);padding:9px 14px;border-bottom:1px solid var(--border);font-size:11px;font-weight:500;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.log-item{padding:10px 14px;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:10px}
.log-item:last-child{border-bottom:none}
.log-icon{width:26px;height:26px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0}
.li-ok{background:var(--green-dim)}.li-err{background:var(--red-dim)}.li-warn{background:var(--yellow-dim)}
.empty-state{text-align:center;padding:16px;color:var(--muted);font-size:12px}
@media(max-width:900px){.notif-grid{grid-template-columns:1fr}}
</style>
