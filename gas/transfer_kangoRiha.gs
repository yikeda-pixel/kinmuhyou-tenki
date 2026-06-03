/**
 * 転記スクリプト
 * ソース: Sheet1のコピー の「看護、リハ割合」の右横データ
 * 転記先: まとめシート の「入力2」の下
 *
 * 実行方法: GASエディタでこの関数を選択して「実行」ボタンを押す
 */

const SOURCE_SS_ID = '1XAfXTdRCLCO6a_2z6F5TDVwhEUhQb6pv1L3od5Es3Xg';
const SOURCE_SHEET_GID = 823389167;
const DEST_SS_ID = '1XLOwfIxkVyzZBNp8ZIjg9eYqotKJIegg3GMgS8wigBo';
const DEST_SHEET_GID = 1791869002;

function transferKangoRihaData() {
  // ソーススプレッドシートを開く
  const sourceSS = SpreadsheetApp.openById(SOURCE_SS_ID);
  const sourceSheet = getSheetByGid(sourceSS, SOURCE_SHEET_GID);
  if (!sourceSheet) {
    throw new Error('ソースシートが見つかりません (GID: ' + SOURCE_SHEET_GID + ')');
  }

  // 「看護、リハ割合」セルを探す
  const sourceData = sourceSheet.getDataRange().getValues();
  let targetRow = -1;
  let targetCol = -1;

  for (let r = 0; r < sourceData.length; r++) {
    for (let c = 0; c < sourceData[r].length; c++) {
      const cell = String(sourceData[r][c]).trim();
      if (cell === '看護、リハ割合' || cell === '看護・リハ割合' || cell.includes('看護') && cell.includes('リハ')) {
        targetRow = r;
        targetCol = c;
        break;
      }
    }
    if (targetRow !== -1) break;
  }

  if (targetRow === -1) {
    throw new Error('"看護、リハ割合" が見つかりません。シートの内容を確認してください。');
  }

  Logger.log('「看護、リハ割合」発見: 行=' + (targetRow + 1) + ', 列=' + (targetCol + 1));

  // 同じ行の右側データを取得（空のセルまで）
  const rowData = sourceData[targetRow];
  const extractedData = [];
  for (let c = targetCol + 1; c < rowData.length; c++) {
    extractedData.push(rowData[c]);
  }

  // 末尾の空セルを除去
  while (extractedData.length > 0 && extractedData[extractedData.length - 1] === '') {
    extractedData.pop();
  }

  Logger.log('取得データ: ' + JSON.stringify(extractedData));

  if (extractedData.length === 0) {
    throw new Error('"看護、リハ割合" の右にデータがありません。');
  }

  // 転記先スプレッドシートを開く
  const destSS = SpreadsheetApp.openById(DEST_SS_ID);
  const destSheet = getSheetByGid(destSS, DEST_SHEET_GID);
  if (!destSheet) {
    throw new Error('転記先シートが見つかりません (GID: ' + DEST_SHEET_GID + ')');
  }

  // 「入力2」セルを探す
  const destData = destSheet.getDataRange().getValues();
  let destRow = -1;
  let destCol = -1;

  for (let r = 0; r < destData.length; r++) {
    for (let c = 0; c < destData[r].length; c++) {
      if (String(destData[r][c]).trim() === '入力2') {
        destRow = r;
        destCol = c;
        break;
      }
    }
    if (destRow !== -1) break;
  }

  if (destRow === -1) {
    throw new Error('"入力2" が転記先シートに見つかりません。');
  }

  Logger.log('「入力2」発見: 行=' + (destRow + 1) + ', 列=' + (destCol + 1));

  // 「入力2」の1行下にデータを書き込む（上書き）
  const writeRow = destRow + 2; // 1-indexed
  const writeCol = destCol + 1; // 1-indexed

  const targetRange = destSheet.getRange(writeRow, writeCol, 1, extractedData.length);
  targetRange.setValues([extractedData]);

  Logger.log('転記完了: ' + writeRow + '行目, ' + writeCol + '列目から ' + extractedData.length + '列分');
  SpreadsheetApp.flush();

  Logger.log('✅ 転記が完了しました。');
}

/**
 * シートIDからシートオブジェクトを取得する
 */
function getSheetByGid(spreadsheet, gid) {
  const sheets = spreadsheet.getSheets();
  for (const sheet of sheets) {
    if (sheet.getSheetId() === gid) {
      return sheet;
    }
  }
  return null;
}
