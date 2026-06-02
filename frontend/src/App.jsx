import { useState, useEffect } from 'react'

const BASE = import.meta.env.BASE_URL

const styles = {
  root: { fontFamily: 'system-ui, "Hiragino Sans", sans-serif', maxWidth: 960, margin: '0 auto', padding: '2rem 1rem', color: '#1a202c' },
  h1: { fontSize: '1.5rem', fontWeight: 700, borderBottom: '2px solid #e2e8f0', paddingBottom: '0.75rem', marginBottom: '1.5rem' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '2rem' },
  card: { border: '1px solid #e2e8f0', borderRadius: 8, padding: '1rem 1.25rem', background: '#fff' },
  cardLabel: { fontSize: '0.8rem', color: '#718096', marginBottom: '0.25rem' },
  cardValue: { fontSize: '1.4rem', fontWeight: 700 },
  badge: (color) => ({ display: 'inline-block', padding: '0.1rem 0.5rem', borderRadius: 4, fontSize: '0.75rem', background: color === 'green' ? '#c6f6d5' : color === 'red' ? '#fed7d7' : '#e2e8f0', color: color === 'green' ? '#276749' : color === 'red' ? '#c53030' : '#4a5568', marginLeft: '0.4rem' }),
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' },
  th: { padding: '0.6rem 0.75rem', textAlign: 'left', background: '#f7fafc', borderBottom: '2px solid #e2e8f0', whiteSpace: 'nowrap' },
  td: { padding: '0.6rem 0.75rem', borderBottom: '1px solid #edf2f7' },
  meta: { color: '#718096', fontSize: '0.8rem', marginBottom: '1rem' },
  error: { background: '#fff5f5', border: '1px solid #fc8181', borderRadius: 8, padding: '1rem', marginBottom: '1.5rem' },
}

function StatusBadge({ result }) {
  if (result.skipped) return <span style={styles.badge('gray')}>スキップ</span>
  if (result.failed > 0) return <span style={styles.badge('red')}>エラーあり</span>
  return <span style={styles.badge('green')}>成功</span>
}

function SummaryCard({ title, result }) {
  return (
    <div style={styles.card}>
      <div style={styles.cardLabel}>
        {title} <StatusBadge result={result} />
      </div>
      <div style={styles.cardValue}>
        {result.skipped ? '－' : `${result.success} 件`}
      </div>
      {!result.skipped && result.failed > 0 && (
        <div style={{ fontSize: '0.8rem', color: '#e53e3e', marginTop: '0.25rem' }}>
          {result.failed} 件失敗
        </div>
      )}
    </div>
  )
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

  return (
    <div style={styles.root}>
      <h1 style={styles.h1}>勤務表転記システム</h1>

      {error && (
        <div style={styles.error}>
          {error} — <code>python main.py</code> を実行して結果ファイルを生成してください。
        </div>
      )}

      {data && (
        <>
          <div style={styles.grid}>
            <div style={styles.card}>
              <div style={styles.cardLabel}>取得レコード数</div>
              <div style={styles.cardValue}>{data.total} 件</div>
            </div>
            <SummaryCard title="ZST" result={data.zst} />
            <SummaryCard title="マネーフォワード勤怠" result={data.moneyforward} />
          </div>

          <p style={styles.meta}>
            最終実行: {new Date(data.timestamp).toLocaleString('ja-JP')}
          </p>

          <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem' }}>シフトデータ</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={styles.table}>
              <thead>
                <tr>
                  {['スタッフ名', '日付', '出勤', '退勤', '休憩(分)', '実働(分)', '備考'].map(h => (
                    <th key={h} style={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.records.map((r, i) => (
                  <tr key={i}>
                    <td style={styles.td}>{r.staff_name}</td>
                    <td style={styles.td}>{r.date}</td>
                    <td style={styles.td}>{r.start_time}</td>
                    <td style={styles.td}>{r.end_time}</td>
                    <td style={styles.td}>{r.break_minutes}</td>
                    <td style={styles.td}>{r.work_minutes}</td>
                    <td style={styles.td}>{r.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
