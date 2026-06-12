import os, uuid, requests as req
from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# ── DB 연결 ───────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    """앱 시작 시 테이블 없으면 자동 생성"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id          TEXT PRIMARY KEY,
                    name        TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    pm          TEXT DEFAULT '',
                    end_date    TEXT DEFAULT '',
                    created_at  TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id          TEXT PRIMARY KEY,
                    project_id  TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    grp         TEXT DEFAULT '',
                    task        TEXT NOT NULL,
                    assignee    TEXT DEFAULT '',
                    start_date  TEXT DEFAULT '',
                    end_date    TEXT DEFAULT '',
                    progress    INTEGER DEFAULT 0,
                    note        TEXT DEFAULT '',
                    jira        TEXT DEFAULT '',
                    created_at  TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS webhook (
                    id      SERIAL PRIMARY KEY,
                    type    TEXT DEFAULT '',
                    token   TEXT DEFAULT '',
                    chat    TEXT DEFAULT '',
                    url     TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS logs (
                    id         SERIAL PRIMARY KEY,
                    log_type   TEXT DEFAULT '',
                    title      TEXT DEFAULT '',
                    detail     TEXT DEFAULT '',
                    created_at TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS task_snapshots (
                    id          SERIAL PRIMARY KEY,
                    project_id  TEXT NOT NULL,
                    snapshot    TEXT NOT NULL,
                    label       TEXT DEFAULT '',
                    created_at  TEXT DEFAULT ''
                );
            """)
        conn.commit()

# ── helpers ──────────────────────────────────────────────
def row_to_project(row):
    return {
        'id': row['id'], 'name': row['name'],
        'description': row['description'], 'pm': row['pm'],
        'endDate': row['end_date'], 'createdAt': row['created_at'],
    }

def row_to_task(row):
    return {
        'id': row['id'], 'group': row['grp'],
        'task': row['task'], 'assignee': row['assignee'],
        'startDate': row['start_date'], 'endDate': row['end_date'],
        'progress': row['progress'], 'note': row['note'],
        'jira': row['jira'],
    }

def diff_days(end_str):
    try:
        return (datetime.strptime(end_str, '%Y-%m-%d').date() - date.today()).days
    except:
        return None

def get_status(task):
    p = task.get('progress', 0) or 0
    d = diff_days(task.get('endDate', ''))
    if p >= 100:   return 'done'
    if d is None:  return 'pending'
    if d < 0:      return 'overdue'
    if d <= 7:     return 'risk'
    if p > 0:      return 'progress'
    return 'pending'

def calc_stats(project_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE project_id=%s", (project_id,))
            rows = cur.fetchall()
    tasks = [row_to_task(r) for r in rows]
    total = len(tasks)
    if total == 0:
        return {'total': 0, 'progress': 0, 'status': 'pending'}
    statuses = [get_status(t) for t in tasks]
    prog = round(sum(t['progress'] or 0 for t in tasks) / total)
    if 'overdue' in statuses: status = 'overdue'
    elif 'risk'  in statuses: status = 'risk'
    elif all(s == 'done' for s in statuses): status = 'done'
    elif any(s in ('done','progress') for s in statuses): status = 'progress'
    else: status = 'pending'
    return {'total': total, 'progress': prog, 'status': status}

def add_log(log_type, title, detail):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO logs (log_type,title,detail,created_at) VALUES (%s,%s,%s,%s)",
                (log_type, title, detail, datetime.now().strftime('%Y-%m-%d %H:%M'))
            )
            cur.execute("DELETE FROM logs WHERE id NOT IN (SELECT id FROM logs ORDER BY id DESC LIMIT 50)")
        conn.commit()

def build_message(task, project_name, trigger):
    emoji = {'done':'✅','progress':'🔵','risk':'⚠️','overdue':'🚨','pending':'⏳'}
    s = get_status(task)
    return (f"{emoji.get(s,'📋')} *[WBS 알림]* {trigger}\n\n"
            f"📁 프로젝트: {project_name}\n"
            f"📌 태스크: {task.get('task','')}\n"
            f"👤 담당자: {task.get('assignee','미지정')}\n"
            f"📂 그룹: {task.get('group','')}\n"
            f"📅 마감일: {task.get('endDate','')}\n"
            f"📊 진행률: {task.get('progress',0)}%")

def get_webhook_data():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM webhook ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
    return dict(row) if row else {}

def send_webhook(text):
    wh = get_webhook_data()
    if not wh.get('type'): return False, '웹훅 설정 없음'
    try:
        if wh['type'] == 'telegram':
            token, chat = wh.get('token',''), wh.get('chat','')
            if not token or not chat: return False, 'Token/Chat ID 없음'
            r = req.post(f"https://api.telegram.org/bot{token}/sendMessage",
                         json={'chat_id':chat,'text':text,'parse_mode':'Markdown'}, timeout=10)
        else:
            url = wh.get('url','')
            if not url: return False, 'Webhook URL 없음'
            r = req.post(url, json={'text':text}, timeout=10)
        return r.ok, r.text
    except Exception as e:
        return False, str(e)

# ── scheduler ─────────────────────────────────────────────
def daily_check():
    wh = get_webhook_data()
    if not wh.get('type'): return
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM projects")
            projects = cur.fetchall()
    for proj in projects:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM tasks WHERE project_id=%s", (proj['id'],))
                rows = cur.fetchall()
        for row in rows:
            t = row_to_task(row)
            if (t['progress'] or 0) >= 100: continue
            d = diff_days(t['endDate'])
            if d is None: continue
            if d == 7:
                ok, _ = send_webhook(build_message(t, proj['name'], 'D-7 마감 7일 전'))
                add_log('warning' if ok else 'error', f"D-7: {t['task']}", proj['name'])
            elif d == 1:
                ok, _ = send_webhook(build_message(t, proj['name'], '⚡ D-1 내일 마감'))
                add_log('warning' if ok else 'error', f"D-1: {t['task']}", proj['name'])
            elif d < 0:
                ok, _ = send_webhook(build_message(t, proj['name'], f'🚨 {abs(d)}일 초과'))
                add_log('error', f"지연: {t['task']}", f"{proj['name']} · {abs(d)}일 초과")

scheduler = BackgroundScheduler()
scheduler.add_job(daily_check, 'cron', hour=9, minute=0)
scheduler.start()

# ── projects ──────────────────────────────────────────────
@app.route('/api/projects', methods=['GET'])
def get_projects():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM projects ORDER BY created_at")
            rows = cur.fetchall()
    result = []
    for r in rows:
        p = row_to_project(r)
        result.append({**p, **calc_stats(p['id'])})
    return jsonify(result)

@app.route('/api/projects', methods=['POST'])
def create_project():
    d = request.json
    pid = str(uuid.uuid4())[:8]
    now = datetime.now().strftime('%Y-%m-%d')
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO projects (id,name,description,pm,end_date,created_at) VALUES (%s,%s,%s,%s,%s,%s)",
                (pid, d.get('name',''), d.get('description',''), d.get('pm',''), d.get('endDate',''), now)
            )
        conn.commit()
    return jsonify({'id':pid, **d, 'createdAt':now}), 201

@app.route('/api/projects/<pid>', methods=['GET'])
def get_project(pid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM projects WHERE id=%s", (pid,))
            row = cur.fetchone()
    if not row: return jsonify({'error':'not found'}), 404
    p = row_to_project(row)
    return jsonify({**p, **calc_stats(pid)})

@app.route('/api/projects/<pid>', methods=['PUT'])
def update_project(pid):
    d = request.json
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE projects SET name=%s,description=%s,pm=%s,end_date=%s WHERE id=%s",
                (d.get('name',''), d.get('description',''), d.get('pm',''), d.get('endDate',''), pid)
            )
        conn.commit()
    return jsonify({'ok': True})

@app.route('/api/projects/<pid>', methods=['DELETE'])
def delete_project(pid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM projects WHERE id=%s", (pid,))
        conn.commit()
    return jsonify({'ok': True})

# ── tasks ─────────────────────────────────────────────────
@app.route('/api/projects/<pid>/tasks', methods=['GET'])
def get_tasks(pid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE project_id=%s ORDER BY created_at", (pid,))
            rows = cur.fetchall()
    return jsonify([row_to_task(r) for r in rows])

@app.route('/api/projects/<pid>/tasks', methods=['POST'])
def create_task(pid):
    d = request.json
    tid = str(uuid.uuid4())[:8]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (id,project_id,grp,task,assignee,start_date,end_date,progress,note,jira,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (tid, pid, d.get('group',''), d.get('task',''), d.get('assignee',''),
                 d.get('startDate',''), d.get('endDate',''), d.get('progress',0),
                 d.get('note',''), d.get('jira',''), now)
            )
        conn.commit()
    return jsonify({**d, 'id': tid}), 201

@app.route('/api/projects/<pid>/tasks/<tid>', methods=['PUT'])
def update_task(pid, tid):
    d = request.json
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET grp=%s,task=%s,assignee=%s,start_date=%s,end_date=%s,progress=%s,note=%s,jira=%s WHERE id=%s AND project_id=%s",
                (d.get('group',''), d.get('task',''), d.get('assignee',''),
                 d.get('startDate',''), d.get('endDate',''), d.get('progress',0),
                 d.get('note',''), d.get('jira',''), tid, pid)
            )
        conn.commit()
    return jsonify({'ok': True})

@app.route('/api/projects/<pid>/tasks/<tid>', methods=['DELETE'])
def delete_task(pid, tid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id=%s AND project_id=%s", (tid, pid))
        conn.commit()
    return jsonify({'ok': True})

# ── snapshot helpers ──────────────────────────────────────
import json as _json

# 그룹명 정규화
GROUP_MAP = {
    '기획팀':'기획', '기획부':'기획',
    '디자인팀':'디자인',
    'be팀':'개발(BE)', '백엔드':'개발(BE)', 'backend':'개발(BE)',
    'fe팀':'개발(FE)', '프론트엔드':'개발(FE)', 'frontend':'개발(FE)',
    'android팀':'Android', '안드로이드':'Android',
    'ios팀':'iOS',
    'qa팀':'QA', '품질':'QA',
}
STANDARD_GROUPS = ['기획','디자인','개발(BE)','개발(FE)','Android','iOS','QA']

def normalize_group(g):
    if not g: return '기획'
    lower = g.strip().lower()
    if lower in GROUP_MAP: return GROUP_MAP[lower]
    for std in STANDARD_GROUPS:
        if lower in std.lower() or std.lower() in lower: return std
    return g.strip()

def save_snapshot(pid, label):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE project_id=%s ORDER BY created_at", (pid,))
            rows = cur.fetchall()
        tasks_data = [row_to_task(r) for r in rows]
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO task_snapshots (project_id, snapshot, label, created_at) VALUES (%s,%s,%s,%s)",
                (pid, _json.dumps(tasks_data, ensure_ascii=False), label, now)
            )
            # 최대 10개 스냅샷 유지
            cur.execute("""
                DELETE FROM task_snapshots WHERE id IN (
                    SELECT id FROM task_snapshots WHERE project_id=%s
                    ORDER BY id DESC OFFSET 10
                )
            """, (pid,))
        conn.commit()

@app.route('/api/projects/<pid>/snapshots/save', methods=['POST'])
def manual_save_snapshot(pid):
    try:
        save_snapshot(pid, f'수동 백업 ({datetime.now().strftime("%m/%d %H:%M")})')
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<pid>/snapshots', methods=['GET'])
def get_snapshots(pid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, label, created_at FROM task_snapshots WHERE project_id=%s ORDER BY id DESC", (pid,))
            rows = cur.fetchall()
    return jsonify([{'id': r['id'], 'label': r['label'], 'created_at': r['created_at']} for r in rows])

@app.route('/api/projects/<pid>/snapshots/<int:sid>/restore', methods=['POST'])
def restore_snapshot(pid, sid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT snapshot FROM task_snapshots WHERE id=%s AND project_id=%s", (sid, pid))
            row = cur.fetchone()
    if not row:
        return jsonify({'error': '스냅샷을 찾을 수 없습니다'}), 404
    tasks_data = _json.loads(row['snapshot'])
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE project_id=%s", (pid,))
            for t in tasks_data:
                tid = str(uuid.uuid4())[:8]
                cur.execute(
                    "INSERT INTO tasks (id,project_id,grp,task,assignee,start_date,end_date,progress,note,jira,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (tid, pid, t.get('group',''), t.get('task',''), t.get('assignee',''),
                     t.get('startDate',''), t.get('endDate',''), t.get('progress',0),
                     t.get('note',''), t.get('jira',''), now)
                )
        conn.commit()
    return jsonify({'ok': True, 'count': len(tasks_data)})

# ── excel upload ──────────────────────────────────────────
@app.route('/api/projects/<pid>/tasks/upload', methods=['POST'])
def upload_tasks_excel(pid):
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    file = request.files['file']
    try:
        import pandas as pd, io
        if file.filename.endswith('.csv'):
            try:    df_raw = pd.read_csv(file, encoding='utf-8', header=None)
            except: file.seek(0); df_raw = pd.read_csv(file, encoding='cp949', header=None)
        else:
            df_raw = pd.read_excel(file, header=None)
        df_raw = df_raw.fillna('')
        header_idx = next((i for i, row in df_raw.iterrows()
                          if any(k in ' '.join(str(x) for x in row.values).lower()
                                 for k in ['task','태스크','group'])), -1)
        if header_idx == -1:
            return jsonify({'error': '헤더 행을 찾을 수 없습니다'}), 400
        df = df_raw.iloc[header_idx+1:].copy()
        df.columns = df_raw.iloc[header_idx]
        def get_val(row, keys, default=''):
            for k in keys:
                for col in df.columns:
                    if str(col).strip().lower() == k.lower():
                        return str(row.get(col, default)).strip()
            return default
        count = 0
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_snapshot(pid, f'업로드 전 백업 ({datetime.now().strftime("%m/%d %H:%M")})')
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE project_id=%s", (pid,))
                for _, row in df.iterrows():
                    if not any(str(v).strip() for v in row.values): continue
                    t_name = get_val(row, ['Task','태스크명','태스크','작업명'])
                    s_name = get_val(row, ['Subtask','서브태스크','상세작업'])
                    if not t_name and not s_name: continue
                    task_name = f"[{t_name}] {s_name}" if t_name and s_name else (t_name or s_name)
                    jira_val  = get_val(row, ['Jira','지라','Link','링크'])
                    group_val = normalize_group(get_val(row, ['Team','Group','그룹','팀'], '기획'))
                    assignee  = get_val(row, ['Assignee','담당자'])
                    start_date= get_val(row, ['Start Date','시작일','시작']) or date.today().isoformat()
                    end_date  = get_val(row, ['End Date','마감일','종료일'])
                    prog_raw  = get_val(row, ['Progress','진행률','진척도'], '0').replace('%','')
                    try: progress = int(float(prog_raw)) if prog_raw else 0
                    except: progress = 0
                    note = get_val(row, ['Note','메모','비고'])
                    tid = str(uuid.uuid4())[:8]
                    cur.execute(
                        "INSERT INTO tasks (id,project_id,grp,task,assignee,start_date,end_date,progress,note,jira,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (tid, pid, group_val, task_name, assignee, start_date[:10],
                         end_date[:10] if end_date else '', progress, note, jira_val, now)
                    )
                    count += 1
            conn.commit()
        return jsonify({'ok': True, 'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<pid>/tasks/upload-sheets', methods=['POST'])
def upload_from_sheets(pid):
    csv_url = request.json.get('csv_url','')
    if not csv_url: return jsonify({'error':'csv_url 없음'}), 400
    try:
        import pandas as pd, io
        r = req.get(csv_url, timeout=15); r.raise_for_status()
        try:    df_raw = pd.read_csv(io.StringIO(r.content.decode('utf-8')), header=None)
        except: df_raw = pd.read_csv(io.StringIO(r.content.decode('cp949')), header=None)
        df_raw = df_raw.fillna('')
        header_idx = next((i for i, row in df_raw.iterrows()
                          if any(k in ' '.join(str(x) for x in row.values).lower()
                                 for k in ['task','태스크','group'])), -1)
        if header_idx == -1: return jsonify({'error':'헤더 행 없음'}), 400
        df = df_raw.iloc[header_idx+1:].copy()
        df.columns = df_raw.iloc[header_idx]
        def get_val(row, keys, default=''):
            for k in keys:
                for col in df.columns:
                    if str(col).strip().lower() == k.lower():
                        return str(row.get(col, default)).strip()
            return default
        count = 0
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_conn() as conn:
            with conn.cursor() as cur:
                for _, row in df.iterrows():
                    if not any(str(v).strip() for v in row.values): continue
                    t_name = get_val(row, ['Task','태스크명','태스크'])
                    s_name = get_val(row, ['Subtask','서브태스크'])
                    if not t_name and not s_name: continue
                    task_name = f"[{t_name}] {s_name}" if t_name and s_name else (t_name or s_name)
                    tid = str(uuid.uuid4())[:8]
                    end_date = get_val(row, ['End Date','마감일','종료일'])
                    prog_raw = get_val(row, ['Progress','진행률'], '0').replace('%','')
                    try: progress = int(float(prog_raw)) if prog_raw else 0
                    except: progress = 0
                    cur.execute(
                        "INSERT INTO tasks (id,project_id,grp,task,assignee,start_date,end_date,progress,note,jira,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (tid, pid,
                         normalize_group(get_val(row, ['Team','Group','그룹','팀'], '기획')),
                         task_name,
                         get_val(row, ['Assignee','담당자']),
                         get_val(row, ['Start Date','시작일']) or date.today().isoformat(),
                         end_date[:10] if end_date else '',
                         progress,
                         get_val(row, ['Note','메모','비고']),
                         get_val(row, ['Jira','지라','Link']),
                         now)
                    )
                    count += 1
            conn.commit()
        return jsonify({'ok': True, 'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── webhook / logs ────────────────────────────────────────
@app.route('/api/webhook', methods=['GET'])
def get_webhook():
    wh = get_webhook_data()
    return jsonify({**wh, 'token': '***' if wh.get('token') else ''})

@app.route('/api/webhook', methods=['POST'])
def save_webhook():
    d = request.json
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM webhook")
            cur.execute(
                "INSERT INTO webhook (type,token,chat,url) VALUES (%s,%s,%s,%s)",
                (d.get('type',''), d.get('token',''), d.get('chat',''), d.get('url',''))
            )
        conn.commit()
    return jsonify({'ok': True})

@app.route('/api/webhook/test', methods=['POST'])
def test_webhook():
    dummy = {'task':'[테스트] WBS Manager','group':'QA','assignee':'담당자1',
             'endDate':str(date.today()+timedelta(days=3)),'progress':0}
    ok, msg = send_webhook(build_message(dummy, 'Test', '테스트 메시지'))
    add_log('success' if ok else 'error', '테스트 전송', '성공' if ok else msg)
    return jsonify({'ok': ok, 'message': '전송 성공' if ok else msg})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT log_type as type, title, detail, created_at as time FROM logs ORDER BY id DESC LIMIT 50")
            rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/notify/now', methods=['POST'])
def notify_now():
    daily_check()
    return jsonify({'ok': True})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'ok': True})

# ── start ─────────────────────────────────────────────────
try:
    init_db()
    print("✅ DB 초기화 완료")
except Exception as e:
    print(f"⚠️ DB 초기화 실패: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)