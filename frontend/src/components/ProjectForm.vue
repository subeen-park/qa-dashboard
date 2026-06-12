<template>
  <div v-if="modelValue" class="overlay" @click.self="close">
    <div class="modal">
      <div class="modal-title">{{ editProject ? 'WBS 수정' : '새 WBS 등록' }}</div>

      <div class="field">
        <label>프로젝트명 * <span class="char-count" :class="form.name.length > 35 ? 'over' : ''">{{ form.name.length }}/35</span></label>
        <input v-model="form.name" placeholder="예: 신규 캐릭터 출시 v1.0" :maxlength="35" :class="{error: errors.name}" />
        <span v-if="errors.name" class="err-msg">{{ errors.name }}</span>
      </div>

      <div class="field">
        <label>설명 *</label>
        <input v-model="form.description" placeholder="프로젝트 간단 설명" :class="{error: errors.description}" />
        <span v-if="errors.description" class="err-msg">{{ errors.description }}</span>
      </div>

      <div class="row2">
        <div class="field">
          <label>담당 PM *</label>
          <input v-model="form.pm" placeholder="예: 박수빈" :class="{error: errors.pm}" />
          <span v-if="errors.pm" class="err-msg">{{ errors.pm }}</span>
        </div>
        <div class="field">
          <label>마감일 *</label>
          <input type="date" v-model="form.endDate" :class="{error: errors.endDate}" />
          <span v-if="errors.endDate" class="err-msg">{{ errors.endDate }}</span>
        </div>
      </div>

      <div class="modal-actions">
        <button v-if="editProject" class="btn btn-danger" @click="remove">삭제</button>
        <div style="flex:1"></div>
        <button class="btn btn-ghost" @click="close">취소</button>
        <button class="btn btn-primary" @click="submit">{{ editProject ? '저장' : '등록' }}</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProjectForm',
  props: { modelValue: Boolean, editProject: Object },
  emits: ['update:modelValue', 'save', 'delete'],
  data() { return { form: { name:'', description:'', pm:'', endDate:'' }, errors: {} } },
  watch: {
    editProject(val) {
      this.form = val ? {...val} : { name:'', description:'', pm:'', endDate:'' }
      this.errors = {}
    },
    modelValue(v) {
      if (v && !this.editProject) {
        this.form = { name:'', description:'', pm:'', endDate:'' }
        this.errors = {}
      }
    }
  },
  methods: {
    close() { this.$emit('update:modelValue', false) },
    validate() {
      const e = {}
      if (!this.form.name.trim())        e.name = '프로젝트명을 입력하세요'
      if (this.form.name.length > 35)    e.name = '35자 이내로 입력하세요'
      if (!this.form.description.trim()) e.description = '설명을 입력하세요'
      if (!this.form.pm.trim())          e.pm = '담당 PM을 입력하세요'
      if (!this.form.endDate)            e.endDate = '마감일을 선택하세요'
      this.errors = e
      return Object.keys(e).length === 0
    },
    submit() {
      if (!this.validate()) return
      this.$emit('save', { ...this.form, id: this.editProject?.id })
    },
    remove() {
      if (!confirm('이 WBS를 삭제하시겠습니까?\n(포함된 태스크도 모두 삭제됩니다)')) return
      this.$emit('delete', this.editProject.id)
    }
  }
}
</script>

<style scoped>
.overlay{ position:fixed; inset:0; background:rgba(0,0,0,.6); z-index:200; display:flex; align-items:center; justify-content:center }
.modal  { background:var(--bg2); border:1px solid var(--border2); border-radius:12px; padding:24px; width:480px; max-width:90vw }
.modal-title{ font-size:16px; font-weight:600; margin-bottom:18px }
.field  { margin-bottom:14px }
.field label{ display:flex; align-items:center; justify-content:space-between; font-size:11px; color:var(--muted); margin-bottom:5px }
.char-count { font-size:11px; color:var(--muted) }
.char-count.over { color:var(--red) }
.field input{ width:100%; background:var(--bg3); border:1px solid var(--border2); border-radius:6px; padding:8px 10px; color:var(--text); font-size:13px; font-family:inherit; outline:none; transition:border-color .15s }
.field input:focus{ border-color:var(--amber) }
.field input.error{ border-color:var(--red) }
.err-msg { font-size:11px; color:var(--red); margin-top:3px; display:block }
.row2  { display:grid; grid-template-columns:1fr 1fr; gap:10px }
.modal-actions{ display:flex; align-items:center; gap:8px; margin-top:20px }
.btn   { display:inline-flex; align-items:center; padding:7px 16px; border-radius:7px; font-size:13px; cursor:pointer; border:none; font-family:inherit; font-weight:500 }
.btn-primary{ background:var(--amber); color:#0a0800 }.btn-primary:hover{ background:#f0b85a }
.btn-ghost  { background:transparent; color:var(--muted); border:1px solid var(--border2) }.btn-ghost:hover{ background:var(--bg3) }
.btn-danger { background:transparent; color:var(--red); border:1px solid var(--red-dim) }.btn-danger:hover{ background:var(--red-dim) }
</style>