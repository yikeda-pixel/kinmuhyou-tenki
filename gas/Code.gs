/**
 * GAS Web App: 勤務希望シートを解析してJSONで返す
 *
 * シートの形式（1行目がヘッダー）:
 *   行0: [年(2026), フリガナ, 先月勤務, 1, 2, ..., 30, -, 公休, ...]
 *   行1: [月(6),   空,      空,       月, 火, ..., 火, -, ...]
 *   行2+: スタッフ行 or セクションヘッダ行
 *
 * デプロイ手順:
 *   1. このスクリプトを勤務希望スプレッドシートのGASエディタに貼り付け
 *   2. 「デプロイ」→「新しいデプロイ」→「ウェブアプリ」
 *   3. アクセスできるユーザー:「全員」に設定
 *   4. デプロイ後のURLを python/.env の GAS_ENDPOINT に設定
 */

const DAY_START_COL = 3; // D列（インデックス3）から日付列が始まる

function doGet(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const values = sheet.getDataRange().getValues();

  if (values.length < 2) {
    return jsonResponse({ success: true, year: 0, month: 0, dayCount: 0, data: [] });
  }

  const year = Number(values[0][0]) || new Date().getFullYear();
  const month = Number(values[1][0]) || new Date().getMonth() + 1;
  const dayCount = detectDayCount(values[0]);

  // 集計行のラベル（スタッフ行と区別するため）
  const SUMMARY_LABELS = new Set(['公', '公休', '希望', '有給', 'オン', '休オ', '日勤', '午前', '午後', '欠勤', '研修']);

  const records = [];

  for (let r = 2; r < values.length; r++) {
    const row = values[r];
    const name = String(row[0] || '').trim();
    const furigana = String(row[1] || '').trim();

    // スタッフ行の条件: 名前があり、フリガナがあり、集計ラベルでない
    if (!name || !furigana || SUMMARY_LABELS.has(name)) continue;

    // 各日のシフト記号を配列で取得
    const shifts = [];
    for (let d = 0; d < dayCount; d++) {
      const cell = row[DAY_START_COL + d];
      shifts.push(cell !== null && cell !== undefined ? String(cell).trim() : '');
    }

    records.push({ name, furigana, year, month, shifts });
  }

  return jsonResponse({ success: true, year, month, dayCount, data: records });
}

/**
 * ヘッダー行から日数を検出する (1〜31 の連続する数値を数える)
 */
function detectDayCount(headerRow) {
  let count = 0;
  for (let i = DAY_START_COL; i < headerRow.length; i++) {
    const v = headerRow[i];
    if (typeof v === 'number' && v >= 1 && v <= 31) {
      count++;
    } else if (count > 0) {
      break; // 日付列が終わった
    }
  }
  return count > 0 ? count : 30;
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
