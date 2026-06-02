import { useState, useEffect } from 'react'

const BASE = import.meta.env.BASE_URL

const s = {
  root:      { fontFamily: 'system-ui,"Hiragino Sans",sans-serif', fontSize: '14px', color: '#1a202c', padding: '1.5rem', maxWidth: '100%' },
  h1:        { fontSize: '1.25rem', fontWeight: 700, borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem', marginBottom: '1rem' },
  cards:     { display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.5rem' },
  card:      { border: '1px solid #e2e8f0', borderRadius: 8, padding: '0.75rem 1rem', minWidth: 180 },
  cardLabel: { fontSize: '0.75rem', color: '#718096' },
  cardVal:   { fontSize: '1.25rem', fontWeight: 700, marginTop: 2 },
  badge:     (ok) => ({ display:'inline-block', padding:'1px 6px', borderRadius:3, fontSize:'0.7rem', marginLeft:4, background: ok ? '#c6f6d5' : '#fed7d7', color: ok ? '#276749' : '#c53030' }),
  meta:      { color:'#718096', fontSize:'0.75rem', marginBottom:'1rem' },
  tableWrap: { overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: 8 },
  table:     { borderCollapse: 'collapse', fontSize: '12px', width: '100%' },
  th:        { padding: '6px 4px', background: '#f7fafc', borderBottom: '2px solid #e2e8f0', borderRight: '1px solid #e2e8f0', whiteSpace: 'nowrap', textAlign: 'center', minWidth: 28 },
  thName:    { padding: '6px 8px', background: '#f7fafc', borderBottom: '2px solid #e2e8f0', borderRight: '1px solid #e2e8f0', textAlign: 'left', minWidth: 120, position: 'sticky', left: 0, zIndex: 1 },
  tdName:    { padding: '5px 8px', borderBottom: '1px solid #edf2f7', borderRight: '2px solid #e2e8f0', whiteSpace: 'nowrap', position: 'sticky', left: 0, background: '#fff', zIndex: 1 },
  td:        { padding: '3px 2px', borderBottom: '1px solid #edf2f7', borderRight: '1px solid #edf2f7', textAlign: 'center' },
  chip:      (color) => ({ display:'inline-block', padding:'2px 4px', borderRadius:3, background: color, fontSize:'11px', fontWeight:600, color:'#fff', minWidth:22, textShadow:'0 1px 1px rgba(0,0,0,0.3)' }),
  error:     { background:'#fff5f5', border:'1px solid #fc8181', borderRadius:8, padding:'1rem', marginBottom:'1rem' },
  info:      { background:'#ebf8ff', border:'1px solid #90cdf4', borderRadius:8, padding:'0.75rem 1rem', marginBottom:'1rem', fontSize:'0.85rem' },
}

const WEEKDAY = ['月','火','水','木','金','土','日']

function getWeekday(year, month, day) {
  return WEEKDAY[new Date(year, month - 1, day).getDay() === 0 ? 6 : new Date(year, month - 1, day).getDay() - 1]
}

function isHoliday(year, month, day) {
  const wd = new Date(year, month - 1, day).getDay()
  return wd === 0 || wd === 6
}

function StatusBadge({ r }) {
  if (r.skipped) return <span style={s.badge(false)}>スキップ</span>
  if (r.failed > 0) return <span style={s.badge(false)}>エラー</span>
  return <span style={s.badge(true)}>成功</span>
}

export default function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${BASE}last_run.json`)
      .then(r => { if (!r.ok) throw new Error('データなし'); return r.json() })
      .then(setData)
      .catch(e => setError(e.message))
  }, [])

  if (error) return (
    <div style={s.root}>
      <h1 style={s.h1}>勤務表転記システム</h1>
      <div style={s.error}>
        {error} — <code>python main.py</code> を実行してください
      </div>
    </div>
  )

  if (!data) return <div style={s.root}>読み込み中...</div>

  const { year, month, staff_count, day_count, zst, moneyforward, staff } = data
  const days = Array.from({ length: day_count }, (_, i) => i + 1)

  return (
    <div style={s.root}>
      <h1 style={s.h1}>勤務表転記システム — {year}年{month}月</h1>

      {/* サマリーカード */}
      <div style={s.cards}>
        <div style={s.card}>
          <div style={s.cardLabel}>スタッフ数</div>
          <div style={s.cardVal}>{staff_count} 名</div>
        </div>
        <div style={s.card}>
          <div style={s.cardLabel}>ZST <StatusBadge r={zst} /></div>
          <div style={s.cardVal}>{zst.skipped ? '－' : `${zst.success}件`}</div>
          {zst.message && <div style={{ fontSize:'0.7rem', color:'#718096', marginTop:2 }}>{zst.message}</div>}
        </div>
        <div style={s.card}>
          <div style={s.cardLabel}>マネーフォワード勤怠 <StatusBadge r={moneyforward} /></div>
          <div style={s.cardVal}>{moneyforward.skipped ? 'CSV生成済' : `${moneyforward.success}件`}</div>
          {moneyforward.message && <div style={{ fontSize:'0.7rem', color:'#718096', marginTop:2 }}>{moneyforward.message}</div>}
        </div>
      </div>

      <p style={s.meta}>最終実行: {new Date(data.timestamp).toLocaleString('ja-JP')}</p>

      {moneyforward.skipped && (
        <div style={s.info}>
          マネーフォワード用CSV (<code>frontend/public/moneyforward_shift.csv</code>) を生成しました。
          マネーフォワード → シフト管理 →「CSVで一括更新」から手動でアップロードできます。
        </div>
      )}

      {/* シフトマトリクス表 */}
      <div style={s.tableWrap}>
        <table style={s.table}>
          <thead>
            <tr>
              <th style={s.thName}>氏名</th>
              {days.map(d => (
                <th key={d} style={{ ...s.th, color: isHoliday(year, month, d) ? '#e53e3e' : undefined }}>
                  <div>{d}</div>
                  <div style={{ fontSize: 10 }}>{getWeekday(year, month, d)}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {staff && staff.map((person, i) => (
              <tr key={i}>
                <td style={s.tdName}>
                  <div style={{ fontWeight: 600 }}>{person.name}</div>
                  <div style={{ fontSize: 11, color: '#a0aec0' }}>{person.furigana}</div>
                </td>
                {person.shifts.map((code, d) => (
                  <td key={d} style={s.td}>
                    {code ? (
                      <span style={s.chip(person.shift_colors[d])} title={person.shift_labels[d]}>
                        {code}
                      </span>
                    ) : null}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 凡例 */}
      <div style={{ marginTop: '1rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem', fontSize: '12px' }}>
        {[
          ['日', '#4299e1', '日勤'], ['前', '#48bb78', '午前'], ['後', '#ed8936', '午後'],
          ['オン', '#9f7aea', 'オンコール'], ['休オ', '#b794f4', '休みオンコール'],
          ['公', '#a0aec0', '公休'], ['希', '#f6ad55', '希望休'], ['有', '#68d391', '有給'],
          ['欠', '#fc8181', '欠勤'], ['研', '#76e4f7', '研修'],
        ].map(([code, color, label]) => (
          <span key={code} style={{ display:'flex', alignItems:'center', gap:4 }}>
            <span style={s.chip(color)}>{code}</span>
            <span style={{ color: '#718096' }}>{label}</span>
          </span>
        ))}
      </div>
    </div>
  )
}
