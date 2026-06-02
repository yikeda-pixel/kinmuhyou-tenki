from dataclasses import dataclass
from datetime import date, time


@dataclass
class ShiftRecord:
    staff_name: str
    date: date
    start_time: time
    end_time: time
    break_minutes: int
    note: str = ""

    @property
    def work_minutes(self) -> int:
        start = self.start_time.hour * 60 + self.start_time.minute
        end = self.end_time.hour * 60 + self.end_time.minute
        return end - start - self.break_minutes
