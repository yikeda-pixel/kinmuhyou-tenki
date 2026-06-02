/**
 * GAS Web App エントリーポイント
 * スプレッドシートのデータを JSON で返す
 *
 * デプロイ手順:
 *   1. このスクリプトを勤務表スプレッドシートに紐付ける
 *   2. 「デプロイ」→「新しいデプロイ」→「ウェブアプリ」
 *   3. 「アクセスできるユーザー」を「全員」に設定
 *   4. デプロイ URL を python/.env の GAS_ENDPOINT に設定
 *
 * スプレッドシートの列構成 (1行目がヘッダー):
 *   スタッフ名 | 日付 | 出勤時間 | 退勤時間 | 休憩(分) | 備考
 */
function doGet(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getDataRange().getValues();

  if (data.length < 2) {
    return jsonResponse({ success: true, data: [] });
  }

  const headers = data[0];
  const rows = data.slice(1).filter(row => row[0] !== '');

  const records = rows.map(row => {
    const obj = {};
    headers.forEach((header, i) => {
      const val = row[i];
      if (val instanceof Date) {
        obj[header] = Utilities.formatDate(val, 'Asia/Tokyo', 'yyyy/MM/dd');
      } else if (typeof val === 'number' && header === '出勤時間' || header === '退勤時間') {
        // シリアル値を HH:MM に変換
        const totalMin = Math.round(val * 24 * 60);
        const h = Math.floor(totalMin / 60).toString().padStart(2, '0');
        const m = (totalMin % 60).toString().padStart(2, '0');
        obj[header] = `${h}:${m}`;
      } else {
        obj[header] = val;
      }
    });
    return obj;
  });

  return jsonResponse({ success: true, data: records });
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
