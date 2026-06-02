from dataclasses import dataclass


@dataclass
class StaffShift:
    name: str        # 氏名 (例: 池田優(代表）)
    furigana: str    # フリガナ (例: イケダユウ)
    year: int
    month: int
    shifts: list[str]  # shifts[0]=1日, shifts[29]=30日  記号: 日/前/後/オン/休オ/公/希/有/欠/研

    def get(self, day: int) -> str:
        """1始まりの日を指定してシフト記号を取得"""
        idx = day - 1
        if 0 <= idx < len(self.shifts):
            return self.shifts[idx]
        return ''
