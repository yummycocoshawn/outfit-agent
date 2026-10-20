"""Excel 讀寫與照片存放。所有使用者共用同一份 xlsx,以『上傳者』欄區分。"""
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook

from core import COLUMNS, clean_text

SEP = "、"


class Store:
    def __init__(self, data_dir):
        self.dir = Path(data_dir)
        self.photos = self.dir / "photos"
        self.photos.mkdir(parents=True, exist_ok=True)
        self.xlsx = self.dir / "outfits.xlsx"
        if not self.xlsx.exists():
            wb = Workbook()
            wb.active.append(COLUMNS)
            wb.save(self.xlsx)

    def add(self, user, rec, photo_path):
        wb = load_workbook(self.xlsx)
        wb.active.append([
            rec["time"].strftime("%Y-%m-%d %H:%M:%S"), clean_text(user, 40), rec["name"],
            SEP.join(rec["items"]), SEP.join(rec["colors"]), rec["style"],
            "" if rec["temp_min"] is None else f'{rec["temp_min"]}~{rec["temp_max"]}',
            str(photo_path)])
        wb.save(self.xlsx)

    def records(self, user):
        ws = load_workbook(self.xlsx).active
        out = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[1] != clean_text(user, 40) or row[2] == "不是穿搭":
                continue
            out.append({"time": datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"),
                        "name": row[2], "items": row[3].split(SEP), "style": row[5]})
        return out

    def delete_last(self, user):
        wb = load_workbook(self.xlsx)
        ws = wb.active
        for idx in range(ws.max_row, 1, -1):
            if ws.cell(idx, 2).value == clean_text(user, 40):
                name = ws.cell(idx, 3).value
                ws.delete_rows(idx)
                wb.save(self.xlsx)
                return name
        return None
