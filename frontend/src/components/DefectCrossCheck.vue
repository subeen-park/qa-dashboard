<template>
  <div class="defect-page">
    <!-- Header -->
    <div class="dp-header">
      <div>
        <div class="page-title">결함 트래커</div>
        <div class="page-sub">Jira × GitLab 교차 검증 — 릴리즈 범위를 자동으로 매칭합니다</div>
      </div>
      <div class="dp-header-right">
        <div class="demo-badge">
          <span class="dot"></span>
          데모 데이터
        </div>
        <select v-model="selectedVersion" class="version-select">
          <option v-for="v in versions" :key="v" :value="v">{{ v }}</option>
        </select>
        <button class="btn-sync" @click="syncData">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M1 7a6 6 0 0110-4.5M13 7a6 6 0 01-10 4.5M11 1v3h-3M3 13v-3h3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          재검증
        </button>
      </div>
    </div>

    <!-- 상단 요약 바 -->
    <div class="status-bar">
      <div class="sb-item sb-match" @click="scrollTo('matched')">
        <div class="sb-ic">✓</div>
        <div class="sb-txt">
          <div class="sb-n">{{ matched.length }}</div>
          <div class="sb-l">매칭됨</div>
        </div>
      </div>
      <div class="sb-divider"></div>
      <div class="sb-item sb-warn" :class="{active: missing.length > 0}" @click="scrollTo('missing')">
        <div class="sb-ic">⚠</div>
        <div class="sb-txt">
          <div class="sb-n">{{ missing.length }}</div>
          <div class="sb-l">누락</div>
        </div>
      </div>
      <div class="sb-divider"></div>
      <div class="sb-item sb-scope" :class="{active: outOfScope.length > 0}" @click="scrollTo('outscope')">
        <div class="sb-ic">⚠</div>
        <div class="sb-txt">
          <div class="sb-n">{{ outOfScope.length }}</div>
          <div class="sb-l">범위 외</div>
        </div>
      </div>
      <div class="sb-divider"></div>
      <div class="sb-item sb-err" :class="{active: statusMismatch.length > 0}" @click="scrollTo('mismatch')">
        <div class="sb-ic">✕</div>
        <div class="sb-txt">
          <div class="sb-n">{{ statusMismatch.length }}</div>
          <div class="sb-l">불일치</div>
        </div>
      </div>
      <div class="sb-right">
        <div class="sb-gate" :class="hasIssues ? 'gate-fail' : 'gate-pass'">
          <span class="gate-dot"></span>
          {{ hasIssues ? '배포 보류' : '배포 가능' }}
        </div>
      </div>
    </div>

    <!-- 상태 불일치 -->
    <div v-if="statusMismatch.length > 0" ref="mismatch" class="issue-section sect-err">
      <div class="is-head">
        <div class="is-head-left">
          <div class="is-badge badge-err">✕ 상태 불일치</div>
          <div class="is-title">배포 차단 — Jira는 완료인데 MR이 Draft</div>
        </div>
        <div class="is-count">{{ statusMismatch.length }}건</div>
      </div>
      <div class="pair-list">
        <div v-for="t in statusMismatch" :key="t.key" class="pair-row">
          <div class="pair-jira">
            <div class="p-head"><span class="p-src jira-src">Jira</span><span class="p-key mono">{{ t.key }}</span><span class="p-stat jc-done">{{ t.jiraStatus }}</span></div>
            <div class="p-title">{{ t.title }}</div>
            <div class="p-meta">{{ t.assignee }}</div>
          </div>
          <div class="pair-arrow">↔</div>
          <div class="pair-mr">
            <div class="p-head"><span class="p-src gitlab-src">GitLab</span><span class="p-key mono">!{{ getMR(t.key).iid }}</span><span class="p-stat mc-draft">{{ getMR(t.key).mrStatus }}</span></div>
            <div class="p-title">{{ getMR(t.key).title }}</div>
            <div class="p-meta">{{ getMR(t.key).author }}</div>
          </div>
          <div class="pair-action">
            <button class="btn-action" @click="openAction('mismatch', t)">담당자 확인</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 누락 -->
    <div v-if="missing.length > 0" ref="missing" class="issue-section sect-warn">
      <div class="is-head">
        <div class="is-head-left">
          <div class="is-badge badge-warn">⚠ 누락</div>
          <div class="is-title">Jira에만 존재 — MR이 아직 생성되지 않음</div>
        </div>
        <div class="is-count">{{ missing.length }}건</div>
      </div>
      <div class="single-list">
        <div v-for="t in missing" :key="t.key" class="single-row single-warn">
          <div class="s-left">
            <div class="s-head">
              <span class="s-src jira-src">Jira</span>
              <span class="s-key mono">{{ t.key }}</span>
              <span class="s-stat jc-done">{{ t.jiraStatus }}</span>
            </div>
            <div class="s-title">{{ t.title }}</div>
            <div class="s-meta">담당자 · {{ t.assignee }}</div>
          </div>
          <div class="s-note">MR 미생성</div>
          <button class="btn-action" @click="openAction('notify', t)">담당자에게 요청</button>
        </div>
      </div>
    </div>

    <!-- 범위 외 -->
    <div v-if="outOfScope.length > 0" ref="outscope" class="issue-section sect-scope">
      <div class="is-head">
        <div class="is-head-left">
          <div class="is-badge badge-scope">⚠ 범위 외</div>
          <div class="is-title">GitLab에만 존재 — Jira 티켓이 없는 MR</div>
        </div>
        <div class="is-count">{{ outOfScope.length }}건</div>
      </div>
      <div class="single-list">
        <div v-for="m in outOfScope" :key="m.iid" class="single-row single-scope">
          <div class="s-left">
            <div class="s-head">
              <span class="s-src gitlab-src">GitLab</span>
              <span class="s-key mono">!{{ m.iid }}</span>
              <span class="s-stat mc-merged">{{ m.mrStatus }}</span>
            </div>
            <div class="s-title">{{ m.title }}</div>
            <div class="s-meta">작성자 · {{ m.author }}</div>
          </div>
          <div class="s-note">Jira 티켓 없음</div>
          <button class="btn-action" @click="openAction('scope', m)">범위 확인</button>
        </div>
      </div>
    </div>

    <!-- 매칭됨 (접힘) -->
    <div ref="matched" class="issue-section sect-match" :class="{collapsed: !showMatched}">
      <div class="is-head" @click="showMatched = !showMatched" style="cursor:pointer">
        <div class="is-head-left">
          <div class="is-badge badge-match">✓ 매칭됨</div>
          <div class="is-title">정상 — Jira ↔ MR 완전 일치</div>
        </div>
        <div class="is-right">
          <div class="is-count count-ok">{{ matched.length }}건</div>
          <div class="toggle-icon">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" :style="{transform: showMatched ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform .2s'}">
              <path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </div>
      <div v-if="showMatched" class="pair-list">
        <div v-for="t in matched" :key="t.key" class="pair-row pair-row-ok">
          <div class="pair-jira">
            <div class="p-head"><span class="p-src jira-src">Jira</span><span class="p-key mono">{{ t.key }}</span><span class="p-stat jc-done">{{ t.jiraStatus }}</span></div>
            <div class="p-title">{{ t.title }}</div>
            <div class="p-meta">{{ t.assignee }}</div>
          </div>
          <div class="pair-arrow pa-ok">✓</div>
          <div class="pair-mr">
            <div class="p-head"><span class="p-src gitlab-src">GitLab</span><span class="p-key mono">!{{ getMR(t.key).iid }}</span><span class="p-stat mc-merged">{{ getMR(t.key).mrStatus }}</span></div>
            <div class="p-title">{{ getMR(t.key).title }}</div>
            <div class="p-meta">{{ getMR(t.key).author }}</div>
          </div>
          <div class="pair-action"></div>
        </div>
      </div>
    </div>

    <!-- 어떻게 작동 -->
    <div class="how-section">
      <div class="how-title">어떻게 작동하나요?</div>
      <div class="how-flow">
        <div class="hf-step">
          <div class="hf-num">01</div>
          <div class="hf-body">
            <div class="hf-t">Jira에서 티켓 수집</div>
            <div class="hf-d"><code>fixVersion = "{{ selectedVersion }}"</code> JQL로 조회</div>
          </div>
        </div>
        <div class="hf-arrow">→</div>
        <div class="hf-step">
          <div class="hf-num">02</div>
          <div class="hf-body">
            <div class="hf-t">GitLab MR 수집</div>
            <div class="hf-d"><code>release/{{ selectedVersion }}</code> 브랜치 MR 조회</div>
          </div>
        </div>
        <div class="hf-arrow">→</div>
        <div class="hf-step">
          <div class="hf-num">03</div>
          <div class="hf-body">
            <div class="hf-t">Jira 키 추출</div>
            <div class="hf-d">MR 제목·브랜치·커밋에서 <code>/[A-Z]+-\d+/</code> 매칭</div>
          </div>
        </div>
        <div class="hf-arrow">→</div>
        <div class="hf-step">
          <div class="hf-num">04</div>
          <div class="hf-body">
            <div class="hf-t">교차 검증 분류</div>
            <div class="hf-d">매칭·누락·범위외·불일치 4가지로 자동 분류</div>
          </div>
        </div>
      </div>
      <div class="how-foot">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0;margin-top:2px"><circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M7 4v3M7 10v.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        <div><strong>데모 환경 안내</strong> — 공개 저장소에 토큰을 노출할 수 없어 모의 데이터로 UI를 시연합니다. 실제 Jira REST API / GitLab API 호출 모듈이 설계되어 있으며, <code>.env</code>에 토큰만 세팅하면 실 데이터로 전환됩니다.</div>
      </div>
    </div>

    <!-- 액션 모달 -->
    <div v-if="actionModal.show" class="action-overlay" @click.self="closeAction">
      <div class="action-modal">
        <div class="am-head">
          <div class="am-icon" :class="'ai-' + actionModal.type">
            <svg v-if="actionModal.type === 'notify'" width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M14 6a5 5 0 10-10 0c0 5-2 6-2 6h14s-2-1-2-6M7 15a2 2 0 004 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else-if="actionModal.type === 'scope'" width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="7" stroke="currentColor" stroke-width="1.8"/><path d="M6 9l2 2 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 2a7 7 0 100 14A7 7 0 009 2zM9 6v3M9 12v.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          </div>
          <div class="am-head-txt">
            <div class="am-title">{{ actionModal.title }}</div>
            <div class="am-sub">{{ actionModal.subtitle }}</div>
          </div>
        </div>

        <div class="am-target">
          <div class="am-target-row">
            <div class="am-target-key mono">{{ actionModal.key }}</div>
            <div class="am-target-title">{{ actionModal.ticketTitle }}</div>
          </div>
          <div class="am-target-meta">담당자 · {{ actionModal.assignee }}</div>
        </div>

        <div class="am-body">
          <div class="am-section-title">실행 액션</div>
          <div class="am-actions-list">
            <div v-for="(a, i) in actionModal.actions" :key="i" class="am-action-item">
              <div class="am-action-check">✓</div>
              <div class="am-action-text">
                <div class="am-action-name">{{ a.name }}</div>
                <div class="am-action-desc">{{ a.desc }}</div>
              </div>
            </div>
          </div>
          <div class="am-note">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style="flex-shrink:0;margin-top:2px"><circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1.2"/><path d="M6 3.5v3M6 8.5v.01" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            <span>데모 환경 — 실제 액션은 실행되지 않습니다. 연동 설정 시 자동으로 트리거됩니다.</span>
          </div>
        </div>

        <div class="am-footer">
          <button class="am-btn am-btn-ghost" @click="closeAction">취소</button>
          <button class="am-btn am-btn-primary" @click="executeAction">{{ actionModal.ctaLabel }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const MOCK_DATA = {
  'v2.4.0': {
    jira: [
      { key: 'FEAT-101', title: '소셜 로그인 개선', jiraStatus: 'Done', assignee: '박수빈' },
      { key: 'FEAT-102', title: '결제 플로우 리뉴얼', jiraStatus: 'Done', assignee: '김민지' },
      { key: 'FEAT-103', title: '푸시 알림 설정 추가', jiraStatus: 'Done', assignee: '한지원' },
      { key: 'BUG-204', title: '검색 결과 중복 노출', jiraStatus: 'Done', assignee: '박수빈' },
      { key: 'BUG-209', title: '마이페이지 응답 지연', jiraStatus: 'In Review', assignee: '정하늘' },
      { key: 'FEAT-111', title: '다크 모드 지원', jiraStatus: 'Done', assignee: '김민지' },
      { key: 'FEAT-115', title: '프로필 이미지 업로드', jiraStatus: 'Done', assignee: '한지원' },
    ],
    gitlab: [
      { iid: 231, title: '[FEAT-101] 소셜 로그인 Google OAuth 추가', jiraKey: 'FEAT-101', mrStatus: 'merged', author: '박수빈' },
      { iid: 232, title: '[FEAT-102] 결제 플로우 신규 디자인 적용', jiraKey: 'FEAT-102', mrStatus: 'merged', author: '김민지' },
      { iid: 234, title: 'BUG-204 검색 중복 제거 로직', jiraKey: 'BUG-204', mrStatus: 'merged', author: '박수빈' },
      { iid: 236, title: '[FEAT-111] 다크 모드 테마 토큰', jiraKey: 'FEAT-111', mrStatus: 'merged', author: '김민지' },
      { iid: 237, title: '[FEAT-115] 프로필 이미지 CDN 업로드', jiraKey: 'FEAT-115', mrStatus: 'draft', author: '한지원' },
      { iid: 238, title: 'hotfix: 로그 레벨 조정', jiraKey: null, mrStatus: 'merged', author: '정하늘' },
      { iid: 239, title: 'chore: 의존성 업그레이드', jiraKey: null, mrStatus: 'merged', author: '박수빈' },
    ],
  },
  'v2.3.0': {
    jira: [
      { key: 'FEAT-095', title: '회원가입 플로우 간소화', jiraStatus: 'Done', assignee: '박수빈' },
      { key: 'BUG-198', title: '세션 만료 처리 오류', jiraStatus: 'Done', assignee: '정하늘' },
      { key: 'FEAT-098', title: '검색 자동완성', jiraStatus: 'Done', assignee: '김민지' },
    ],
    gitlab: [
      { iid: 220, title: '[FEAT-095] 회원가입 단계 축소', jiraKey: 'FEAT-095', mrStatus: 'merged', author: '박수빈' },
      { iid: 221, title: '[BUG-198] 세션 리프레시 토큰 처리', jiraKey: 'BUG-198', mrStatus: 'merged', author: '정하늘' },
      { iid: 222, title: '[FEAT-098] 검색 자동완성 API 연동', jiraKey: 'FEAT-098', mrStatus: 'merged', author: '김민지' },
    ],
  },
}

export default {
  name: 'DefectCrossCheck',
  data() {
    return {
      versions: ['v2.4.0', 'v2.3.0'],
      selectedVersion: 'v2.4.0',
      showMatched: false,
      actionModal: {
        show: false,
        type: '',
        title: '',
        subtitle: '',
        ctaLabel: '',
        key: '',
        ticketTitle: '',
        assignee: '',
        actions: [],
      },
    }
  },
  computed: {
    rawData() { return MOCK_DATA[this.selectedVersion] || { jira: [], gitlab: [] } },
    matched() {
      const mrKeys = new Set(this.rawData.gitlab.filter(m => m.jiraKey).map(m => m.jiraKey))
      return this.rawData.jira.filter(t => {
        if (!mrKeys.has(t.key)) return false
        const mr = this.rawData.gitlab.find(m => m.jiraKey === t.key)
        if (t.jiraStatus === 'Done' && mr && mr.mrStatus === 'draft') return false
        return true
      })
    },
    missing() {
      const mrKeys = new Set(this.rawData.gitlab.filter(m => m.jiraKey).map(m => m.jiraKey))
      return this.rawData.jira.filter(t => !mrKeys.has(t.key))
    },
    outOfScope() {
      const jiraKeys = new Set(this.rawData.jira.map(t => t.key))
      return this.rawData.gitlab.filter(m => !m.jiraKey || !jiraKeys.has(m.jiraKey))
    },
    statusMismatch() {
      return this.rawData.jira.filter(t => {
        const mr = this.rawData.gitlab.find(m => m.jiraKey === t.key)
        return t.jiraStatus === 'Done' && mr && mr.mrStatus === 'draft'
      })
    },
    hasIssues() {
      return this.missing.length + this.outOfScope.length + this.statusMismatch.length > 0
    },
  },
  methods: {
    syncData() {},
    getMR(jiraKey) { return this.rawData.gitlab.find(m => m.jiraKey === jiraKey) || {} },
    scrollTo(ref) {
      const el = this.$refs[ref]
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    },
    openAction(type, item) {
      if (type === 'notify') {
        this.actionModal = {
          show: true, type: 'notify',
          title: '담당자에게 MR 생성 요청',
          subtitle: 'Slack · 이메일로 자동 알림을 발송합니다',
          ctaLabel: '요청 보내기',
          key: item.key, ticketTitle: item.title, assignee: item.assignee,
          actions: [
            { name: 'Slack DM 발송', desc: '담당자 Slack 계정으로 직접 메시지 전송' },
            { name: '이메일 알림', desc: '담당자 이메일로 티켓 요약 및 MR 생성 요청 발송' },
            { name: 'Jira 코멘트 추가', desc: '해당 티켓에 MR 생성 요청 자동 코멘트 작성' },
            { name: 'Slack #qa-alerts 채널 공지', desc: 'QA 알림 채널에 누락 티켓 공유' },
          ],
        }
      } else if (type === 'scope') {
        this.actionModal = {
          show: true, type: 'scope',
          title: '범위 외 MR 확인',
          subtitle: 'Jira 티켓 없이 머지된 MR의 범위를 확정합니다',
          ctaLabel: '범위 확정',
          key: '!' + item.iid, ticketTitle: item.title, assignee: item.author,
          actions: [
            { name: 'Jira 티켓 자동 생성', desc: 'MR 내용 기반으로 Jira 티켓 신규 생성 및 매칭' },
            { name: '범위 외 승인', desc: '핫픽스 · chore 등 범위 외 작업으로 공식 승인' },
            { name: '릴리즈 노트 자동 추가', desc: 'MR 제목을 릴리즈 노트에 반영' },
            { name: 'QA 담당자에게 통보', desc: '추가 테스트 필요 여부 확인 요청' },
          ],
        }
      } else if (type === 'mismatch') {
        this.actionModal = {
          show: true, type: 'mismatch',
          title: '상태 불일치 해결',
          subtitle: 'Jira는 완료인데 MR이 Draft인 상태입니다',
          ctaLabel: 'MR 완료 요청',
          key: item.key, ticketTitle: item.title, assignee: item.assignee,
          actions: [
            { name: '담당자에게 MR 완료 요청', desc: 'Slack DM으로 MR Draft 해제 및 리뷰 요청' },
            { name: '배포 게이트 블록 등록', desc: '해당 티켓 미해결 시 배포 자동 차단' },
            { name: 'Jira 상태 되돌리기 제안', desc: 'MR이 Draft인 경우 Jira를 In Progress로 복원 제안' },
            { name: '릴리즈 매니저에게 보고', desc: '배포 리스크로 분류하여 자동 보고' },
          ],
        }
      }
    },
    closeAction() { this.actionModal.show = false },
    executeAction() { this.actionModal.show = false },
  },
}
</script>

<style scoped>
.defect-page {
  padding: 100px 32px 60px; max-width: 1240px; margin: 0 auto;
  user-select: none; -webkit-user-select: none;
  font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  letter-spacing: -0.01em;
}
.defect-page * { font-family: inherit; }
.defect-page .mono, .defect-page code { font-family: 'JetBrains Mono', 'Menlo', monospace; }

/* 헤더 */
.dp-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; gap: 20px; flex-wrap: wrap; }
.dp-header-right { display: flex; align-items: center; gap: 10px; }
.demo-badge { display: inline-flex; align-items: center; gap: 6px; background: #FEF3C7; color: #92400E; padding: 6px 12px; border-radius: 100px; font-size: 12px; font-weight: 600; }
.demo-badge .dot { width: 6px; height: 6px; border-radius: 50%; background: #F59E0B; }
.version-select { background: #fff; border: 1px solid var(--border2); border-radius: 10px; padding: 8px 14px; font-size: 14px; font-weight: 600; color: var(--text); font-family: inherit; cursor: pointer; outline: none; }
.btn-sync { display: inline-flex; align-items: center; gap: 6px; background: var(--primary); color: #fff; border: none; padding: 9px 16px; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; box-shadow: 0 4px 12px rgba(0,100,255,0.2); }
.btn-sync:hover { background: var(--primary-hover); }

/* 상단 요약 바 */
.status-bar { display: flex; align-items: center; gap: 0; background: #fff; border: 1px solid var(--border); border-radius: 14px; padding: 18px 24px; margin-bottom: 28px; }
.sb-item { display: flex; align-items: center; gap: 12px; padding: 4px 16px; flex: 1; cursor: pointer; transition: all .15s; border-radius: 8px; }
.sb-item:first-child { padding-left: 0; }
.sb-item:hover { background: var(--bg3); }
.sb-divider { width: 1px; height: 36px; background: var(--border); }
.sb-ic { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; flex-shrink: 0; background: #F1F5F9; color: #94A3B8; }
.sb-match .sb-ic { background: #D1FAE5; color: #059669; }
.sb-warn.active .sb-ic { background: #FEF3C7; color: #D97706; }
.sb-scope.active .sb-ic { background: #FFEDD5; color: #EA580C; }
.sb-err.active .sb-ic { background: #FEE2E2; color: #DC2626; }
.sb-n { font-size: 22px; font-weight: 800; font-family: 'Inter', sans-serif; line-height: 1; color: var(--text); letter-spacing: -.02em; }
.sb-l { font-size: 12px; color: var(--muted); margin-top: 3px; font-weight: 500; }
.sb-right { margin-left: 16px; padding-left: 20px; border-left: 1px solid var(--border); }
.sb-gate { display: inline-flex; align-items: center; gap: 8px; padding: 10px 18px; border-radius: 10px; font-size: 13px; font-weight: 700; letter-spacing: -.01em; }
.gate-pass { background: #D1FAE5; color: #065F46; }
.gate-fail { background: #FEE2E2; color: #991B1B; }
.gate-dot { width: 7px; height: 7px; border-radius: 50%; }
.gate-pass .gate-dot { background: #10B981; }
.gate-fail .gate-dot { background: #EF4444; }

/* 섹션 공통 */
.issue-section { background: #fff; border: 1px solid var(--border); border-radius: 14px; margin-bottom: 16px; overflow: hidden; }
.sect-err { border-color: #FECACA; }
.sect-warn { border-color: #FDE68A; }
.sect-scope { border-color: #FED7AA; }
.sect-match { border-color: var(--border); }
.is-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 22px; border-bottom: 1px solid var(--border); }
.sect-match.collapsed .is-head { border-bottom: none; }
.is-head-left { display: flex; align-items: center; gap: 14px; }
.is-badge { font-size: 12px; font-weight: 700; padding: 5px 12px; border-radius: 7px; display: inline-flex; align-items: center; gap: 5px; letter-spacing: -0.01em; }
.badge-err { background: #FEE2E2; color: #991B1B; }
.badge-warn { background: #FEF3C7; color: #92400E; }
.badge-scope { background: #FFEDD5; color: #9A3412; }
.badge-match { background: #D1FAE5; color: #065F46; }
.is-title { font-size: 14px; font-weight: 600; color: var(--text); letter-spacing: -0.01em; }
.is-count { font-size: 13px; font-weight: 700; color: var(--text-sub); padding: 5px 12px; background: var(--bg3); border-radius: 100px; }
.count-ok { background: #F0FDF4; color: #15803D; }
.is-right { display: flex; align-items: center; gap: 10px; }
.toggle-icon { color: var(--muted); display: flex; align-items: center; justify-content: center; padding: 4px; }

/* 매칭 짝 */
.pair-list { padding: 8px 12px; }
.pair-row { display: grid; grid-template-columns: 1fr 36px 1fr 110px; gap: 10px; align-items: stretch; padding: 12px; border-radius: 10px; transition: background .15s; }
.pair-row:hover { background: #FAFBFC; }
.pair-row-ok { opacity: .85; }
.pair-row-ok:hover { opacity: 1; }
.pair-jira, .pair-mr { background: #FAFBFC; border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px; min-width: 0; }
.pair-arrow { display: flex; align-items: center; justify-content: center; font-size: 16px; color: #CBD5E1; font-weight: 700; }
.pa-ok { color: #10B981; }
.p-head { display: flex; align-items: center; gap: 7px; margin-bottom: 6px; }
.p-src { font-size: 9px; font-weight: 800; padding: 2px 5px; border-radius: 3px; letter-spacing: 0.03em; text-transform: uppercase; }
.jira-src { background: #E6EFFC; color: #0052CC; }
.gitlab-src { background: #FEE3D4; color: #C04A0F; }
.p-key { font-size: 11px; font-weight: 700; color: var(--text-sub); }
.p-stat { font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.jc-done, .mc-merged { background: #D1FAE5; color: #065F46; }
.jc-in { background: #DBEAFE; color: #1E40AF; }
.mc-draft { background: #FEE2E2; color: #991B1B; }
.p-title { font-size: 13.5px; color: var(--text); font-weight: 600; margin-bottom: 4px; line-height: 1.4; letter-spacing: -0.01em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.p-meta { font-size: 11px; color: var(--muted); }
.pair-action { display: flex; align-items: center; justify-content: flex-end; }
.btn-action { background: #fff; border: 1px solid var(--border2); border-radius: 8px; padding: 7px 12px; font-size: 12px; font-weight: 600; color: var(--text); cursor: pointer; font-family: inherit; white-space: nowrap; transition: all .15s; }
.btn-action:hover { background: var(--primary); border-color: var(--primary); color: #fff; }

/* 단일 행 */
.single-list { padding: 8px 12px; }
.single-row { display: grid; grid-template-columns: 1fr auto auto; gap: 16px; align-items: center; padding: 14px 16px; border-radius: 10px; margin-bottom: 4px; transition: all .15s; }
.single-warn { background: #fff; border-left: 3px solid #F59E0B; }
.single-warn:hover { background: #FFFBEB; }
.single-scope { background: #fff; border-left: 3px solid #F97316; }
.single-scope:hover { background: #FFF7ED; }
.s-head { display: flex; align-items: center; gap: 7px; margin-bottom: 5px; }
.s-src { font-size: 9px; font-weight: 800; padding: 2px 5px; border-radius: 3px; letter-spacing: 0.03em; text-transform: uppercase; }
.s-src.jira-src { background: #E6EFFC; color: #0052CC; }
.s-src.gitlab-src { background: #FEE3D4; color: #C04A0F; }
.s-key { font-size: 11px; font-weight: 700; color: var(--text-sub); }
.s-stat { font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.s-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 3px; letter-spacing: -0.01em; }
.s-meta { font-size: 11px; color: var(--muted); }
.s-note { font-size: 12px; color: var(--muted); font-weight: 500; }

/* 어떻게 작동 */
.how-section { background: #fff; border: 1px solid var(--border); border-radius: 14px; padding: 28px; margin-top: 32px; }
.how-title { font-size: 15px; font-weight: 700; margin-bottom: 20px; letter-spacing: -0.01em; }
.how-flow { display: flex; align-items: stretch; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.hf-step { flex: 1; min-width: 180px; background: var(--bg3); border-radius: 12px; padding: 16px 18px; }
.hf-num { font-size: 10px; font-weight: 800; color: var(--primary); font-family: 'JetBrains Mono', monospace; letter-spacing: .08em; margin-bottom: 8px; }
.hf-t { font-size: 13px; font-weight: 700; color: var(--text); margin-bottom: 6px; letter-spacing: -0.01em; }
.hf-d { font-size: 11px; color: var(--text-sub); line-height: 1.55; }
.hf-d code { background: #fff; border: 1px solid var(--border); padding: 1px 5px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--primary); }
.hf-arrow { display: flex; align-items: center; justify-content: center; font-size: 16px; color: #CBD5E1; width: 20px; }
.how-foot { display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 10px; font-size: 12px; color: #1E40AF; line-height: 1.6; }
.how-foot strong { color: #1E3A8A; font-weight: 700; }
.how-foot code { background: #fff; padding: 1px 5px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--primary); }

/* 액션 모달 */
.action-overlay { position: fixed; inset: 0; z-index: 500; background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; user-select: none; -webkit-user-select: none; }
.action-modal { background: #fff; border-radius: 18px; width: 100%; max-width: 540px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.2); font-family: 'Pretendard Variable', Pretendard, sans-serif; }
.am-head { display: flex; align-items: flex-start; gap: 14px; padding: 24px 24px 16px; }
.am-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ai-notify { background: #FEF3C7; color: #D97706; }
.ai-scope { background: #FFEDD5; color: #EA580C; }
.ai-mismatch { background: #FEE2E2; color: #DC2626; }
.am-head-txt { flex: 1; min-width: 0; }
.am-title { font-size: 17px; font-weight: 700; color: var(--text); margin-bottom: 4px; letter-spacing: -0.02em; }
.am-sub { font-size: 13px; color: var(--muted); line-height: 1.5; }
.am-target { margin: 0 24px 20px; padding: 14px 16px; background: #F8FAFC; border: 1px solid var(--border); border-radius: 10px; }
.am-target-row { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.am-target-key { font-size: 11px; font-weight: 700; color: var(--primary); flex-shrink: 0; }
.am-target-title { font-size: 13.5px; font-weight: 600; color: var(--text); letter-spacing: -0.01em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.am-target-meta { font-size: 11px; color: var(--muted); }
.am-body { padding: 0 24px 20px; }
.am-section-title { font-size: 11px; font-weight: 700; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 12px; }
.am-actions-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
.am-action-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 14px; background: #F8FAFC; border: 1px solid var(--border); border-radius: 10px; }
.am-action-check { width: 20px; height: 20px; border-radius: 50%; background: #D1FAE5; color: #059669; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; margin-top: 2px; }
.am-action-text { flex: 1; min-width: 0; }
.am-action-name { font-size: 13.5px; font-weight: 600; color: var(--text); margin-bottom: 3px; letter-spacing: -0.01em; }
.am-action-desc { font-size: 12px; color: var(--text-sub); line-height: 1.5; }
.am-note { display: flex; align-items: flex-start; gap: 8px; padding: 10px 14px; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; font-size: 12px; color: #1E40AF; line-height: 1.5; }
.am-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 24px 20px; border-top: 1px solid var(--border); }
.am-btn { padding: 10px 20px; border-radius: 10px; font-size: 14px; font-weight: 600; border: none; cursor: pointer; font-family: inherit; letter-spacing: -0.01em; transition: all .15s; }
.am-btn-ghost { background: #F1F5F9; color: var(--text); }
.am-btn-ghost:hover { background: #E2E8F0; }
.am-btn-primary { background: var(--primary); color: #fff; box-shadow: 0 4px 12px rgba(0,100,255,0.25); }
.am-btn-primary:hover { background: var(--primary-hover); }

@media (max-width: 900px) {
  .status-bar { flex-wrap: wrap; }
  .sb-right { margin-left: 0; padding-left: 0; border-left: none; width: 100%; margin-top: 10px; }
  .pair-row { grid-template-columns: 1fr; gap: 8px; }
  .pair-arrow { display: none; }
  .single-row { grid-template-columns: 1fr; gap: 10px; }
  .how-flow { flex-direction: column; }
  .hf-arrow { transform: rotate(90deg); }
}
</style>