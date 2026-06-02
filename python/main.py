import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from models import StaffShift
from spreadsheet import fetch_from_gas, load_sample_data
from zst import ZSTAutomator
from moneyforward import MoneyForwardAutomator, generate_csv
from shift_mapper import SHIFT_LABEL, SHIFT_COLOR

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / 'frontend' / 'public'


def staff_to_dict(s: StaffShift) -> dict:
    return {
        'name': s.name,
        'furigana': s.furigana,
        'year': s.year,
        'month': s.month,
        'shifts': s.shifts,
        'shift_labels': [SHIFT_LABEL.get(c, c) for c in s.shifts],
        'shift_colors': [SHIFT_COLOR.get(c, '#edf2f7') for c in s.shifts],
    }


def run_zst(staff_list: list[StaffShift]) -> dict:
    url = os.getenv('ZST_URL', '')
    if not url:
        logger.warning('ZST_URL 未設定 → スキップ')
        return {'success': 0, 'failed': 0, 'skipped': True, 'message': 'ZST_URL を .env に設定してください'}

    result = {'success': 0, 'failed': 0, 'skipped': False, 'message': ''}
    with ZSTAutomator(url, os.getenv('ZST_USER', ''), os.getenv('ZST_PASS', '')) as zst:
        for staff in staff_list:
            try:
                done = zst.input_staff_shifts(staff)
                result['success'] += done
                logger.info(f'ZST: {staff.name} → {done}日分入力')
            except NotImplementedError as e:
                result['skipped'] = True
                result['message'] = str(e)
                break
            except Exception as e:
                logger.error(f'ZST エラー ({staff.name}): {e}')
                result['failed'] += 1
    return result


def run_moneyforward(staff_list: list[StaffShift]) -> dict:
    url = os.getenv('MONEYFORWARD_URL', '')

    # CSVは常に生成（URLが未設定でも確認用に出力）
    csv_content = generate_csv(staff_list)
    csv_path = OUTPUT_DIR / 'moneyforward_shift.csv'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path.write_text(csv_content, encoding='utf-8-sig')
    logger.info(f'マネーフォワード用CSV生成: {csv_path}')

    if not url:
        logger.warning('MONEYFORWARD_URL 未設定 → CSV生成のみ実行')
        return {'success': 0, 'failed': 0, 'skipped': True, 'message': 'CSV生成済み。MONEYFORWARD_URL を設定するとアップロードも自動化できます'}

    result = {'success': 0, 'failed': 0, 'skipped': False, 'message': ''}
    try:
        year = staff_list[0].year if staff_list else datetime.now().year
        month = staff_list[0].month if staff_list else datetime.now().month
        with MoneyForwardAutomator(url, os.getenv('MF_USER', ''), os.getenv('MF_PASS', '')) as mf:
            mf.upload_csv(csv_content, year, month)
        result['success'] = len(staff_list)
    except NotImplementedError as e:
        result['skipped'] = True
        result['message'] = str(e)
    except Exception as e:
        logger.error(f'マネーフォワードエラー: {e}')
        result['failed'] = 1
        result['message'] = str(e)
    return result


def main():
    gas_endpoint = os.getenv('GAS_ENDPOINT', '')
    if gas_endpoint:
        logger.info('GAS からデータ取得')
        staff_list = fetch_from_gas(gas_endpoint)
    else:
        logger.info('サンプルデータ使用 (GAS_ENDPOINT 未設定)')
        staff_list = load_sample_data()

    logger.info(f'{len(staff_list)} 名のシフトデータ取得')
    for s in staff_list:
        preview = ' '.join(s.shifts[:7])
        logger.info(f'  {s.name}: {preview} ...')

    result = {
        'timestamp': datetime.now().isoformat(),
        'year': staff_list[0].year if staff_list else 0,
        'month': staff_list[0].month if staff_list else 0,
        'staff_count': len(staff_list),
        'day_count': len(staff_list[0].shifts) if staff_list else 0,
        'zst': run_zst(staff_list),
        'moneyforward': run_moneyforward(staff_list),
        'staff': [staff_to_dict(s) for s in staff_list],
    }

    out = OUTPUT_DIR / 'last_run.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info(f'結果保存: {out}')


if __name__ == '__main__':
    main()
