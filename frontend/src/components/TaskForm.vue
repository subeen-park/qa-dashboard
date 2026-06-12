<template>
  <div v-if="modelValue" class="overlay" @click.self="$emit('update:modelValue',false)">
    <div class="modal">
      <div class="modal-title">{{ editTask ? '태스크 수정' : '태스크 추가' }}</div>
      
      <div class="form-grid">
        <div class="field"><label>그룹</label><select v-model="form.group"><option v-for="g in GROUPS" :key="g">{{ g }}</option></select></div>
        <div class="field" style="grid-column:span 3"><label>태스크명 *</label><input v-model="form.task" placeholder="예: 신규 캐릭터 API 개발"/></div>
        <div class="field"><label>담당자</label><input v-model="form.assignee" placeholder="예: 개발자1"/></div>
        <div class="field"><label>시작일</label><input type="date" v-model="form.startDate"/></div>
        <div class="field"><label>마감일</label><input type="date" v-model="form.endDate"/></div>
        <div class="field"><label>진행률(%)</label><input type="number" v-model.number="form.progress" min="0" max="100"/></div>
        <div class="field" style="grid-column:1/-1"><label>Jira Link</label><input v-model="form.jira" placeholder="Jira 티켓 번호 또는 URL을 입력하세요"/></div>
        <div class="field" style="grid-column:1/-1"><label>메모</label><input v-model="form.note" placeholder="추가 설명 (선택)"/></div>
      </div>

      <div class="modal-actions">
        <button v-if="editTask" class="btn btn-danger" @click="remove">삭제</button>
        <div style="flex:1"></div>
        <button class="btn btn-ghost" @click="$emit('update:modelValue',false)">취소</button>
        <button class="btn btn-primary" @click="submit">저장</button>
      </div>
    </div>
  </div>
</template>

<script>
import { today, addDays, GROUPS, normalizeGroup } from '../utils.js'

const def = () => ({ group:'기획', task:'', assignee:'', startDate:today(), endDate:addDays(today(),14), progress:0, note:'', jira:'' })

export default {
  name:'TaskForm', 
  props:{ modelValue:Boolean, editTask:Object, projectId:String }, 
  emits:['update:modelValue','save','delete'],
  data(){ return{ form:def(), GROUPS } },
  watch:{
    editTask(v){ this.form = v ? {...v} : def() },
    modelValue(v){ if(v && !this.editTask) this.form = def() }
  },
  methods:{
    submit() { 
      if(!this.form.task.trim()) { alert('태스크명을 입력해주세요.'); return }
      if(!this.form.endDate) { alert('마감일을 입력해주세요.'); return }
      this.$emit('save', { ...this.form, id: this.editTask?.id }) 
    },
    remove() { 
      if(confirm('이 태스크를 정말 삭제하시겠습니까?')) {
        this.$emit('delete', this.editTask.id) 
      }
    }
  }
}
</script>

<style scoped>
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:200;display:flex;align-items:center;justify-content:center}
.modal{background:var(--bg2);border:1px solid var(--border2);border-radius:12px;padding:32px;width:560px;max-width:90vw}
.modal-title{font-size:18px;font-weight:600;margin-bottom:24px;color:var(--text)}
.form-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.field label{display:block;font-size:12px;color:var(--muted);margin-bottom:6px}
.field input,.field select{width:100%;background:var(--bg3);border:1px solid var(--border2);border-radius:6px;padding:10px 14px;color:var(--text);font-size:14px;font-family:inherit;outline:none; transition: border-color 0.2s;}
.field input:focus,.field select:focus{border-color:var(--amber)}
.field select option{background:var(--bg2)}

.modal-actions{display:flex;align-items:center;gap:8px;margin-top:24px}
.btn{display:inline-flex;align-items:center;padding:10px 18px;border-radius:8px;font-size:14px;cursor:pointer;border:none;font-family:inherit;font-weight:500; transition:all 0.15s;}
.btn-primary{background:var(--amber);color:#0a0800}.btn-primary:hover{background:#f0b85a}
.btn-ghost{background:transparent;color:var(--muted);border:1px solid var(--border2)}.btn-ghost:hover{background:var(--bg3);color:var(--text)}
.btn-danger{background:transparent;color:var(--red);border:1px solid var(--red-dim)}
.btn-danger:hover{background:var(--red-dim); color:var(--text)}
</style>