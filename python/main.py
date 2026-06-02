import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from moneyforward import MoneyForwardAutomator
from models import ShiftRecord
from spreadsheet import fetch_from_gas, load_sample_data
from zst import ZSTAutomator

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

FRONTEND_PUBLIC = Path(__file__).parent.parent / "frontend" / "public"


def record_to_dict(r: ShiftRecord) -> dict:
    return {
        "staff_name": r.staff_name,
        "date": str(r.date),
        "start_time": r.start_time.strftime("%H:%M"),
        "end_time": r.end_time.strftime("%H:%M"),
        "break_minutes": r.break_minutes,
        "work_minutes": r.work_minutes,
        "note": r.note,
    }


def run_zst(records: list[ShiftRecord]) -> dict:
    url = os.getenv("ZST_URL", "")
    if not url:
        logger.warning("ZST_URL 未設定 → スキップ")
        return {"success": 0, "failed": 0, "skipped": True}

    result = {"success": 0, "failed": 0, "skipped": False}
    with ZSTAutomator(url, os.getenv("ZST_USER", ""), os.getenv("ZST_PASS", "")) as zst:
        for record in records:
            try:
                zst.input_shift(record)
                result["success"] += 1
            except Exception as e:
                logger.error(f"ZST 転記エラー: {record.staff_name} {record.date} - {e}")
                result["failed"] += 1
    return result


def run_moneyforward(records: list[ShiftRecord]) -> dict:
    url = os.getenv("MONEYFORWARD_URL", "")
    if not url:
        logger.warning("MONEYFORWARD_URL 未設定 → スキップ")
        return {"success": 0, "failed": 0, "skipped": True}

    result = {"success": 0, "failed": 0, "skipped": False}
    with MoneyForwardAutomator(url, os.getenv("MF_USER", ""), os.getenv("MF_PASS", "")) as mf:
        for record in records:
            try:
                mf.input_attendance(record)
                result["success"] += 1
            except Exception as e:
                logger.error(f"マネーフォワード転記エラー: {record.staff_name} {record.date} - {e}")
                result["failed"] += 1
    return result


def main():
    gas_endpoint = os.getenv("GAS_ENDPOINT", "")
    if gas_endpoint:
        logger.info("GAS エンドポイントからデータ取得")
        records = fetch_from_gas(gas_endpoint)
    else:
        logger.info("サンプルデータを使用 (GAS_ENDPOINT 未設定)")
        records = load_sample_data()

    logger.info(f"{len(records)} 件のシフトデータを取得")
    for r in records:
        logger.info(f"  {r.staff_name} {r.date} {r.start_time.strftime('%H:%M')}〜{r.end_time.strftime('%H:%M')}")

    result = {
        "timestamp": datetime.now().isoformat(),
        "total": len(records),
        "zst": run_zst(records),
        "moneyforward": run_moneyforward(records),
        "records": [record_to_dict(r) for r in records],
    }

    FRONTEND_PUBLIC.mkdir(parents=True, exist_ok=True)
    out_path = FRONTEND_PUBLIC / "last_run.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"結果を保存: {out_path}")

    zst = result["zst"]
    mf = result["moneyforward"]
    logger.info(
        f"完了 - ZST: {zst['success']}件成功/{zst['failed']}件失敗 | "
        f"マネーフォワード: {mf['success']}件成功/{mf['failed']}件失敗"
    )


if __name__ == "__main__":
    main()
