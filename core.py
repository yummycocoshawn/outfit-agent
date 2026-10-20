"""純邏輯:驗證模型輸出、清洗文字、重複穿搭比較、統計。不依賴 Discord,方便測試。"""
import json
import re
from collections import Counter
from datetime import datetime, timedelta

COLUMNS = ["日期時間", "上傳者", "穿搭名稱", "單品", "顏色", "風格", "適合溫度(°C)", "照片位置"]
STYLES = {"休閒", "正式", "運動", "街頭", "文青", "其他"}


def clean_text(value, limit=60):
    """去掉控制字元與 Excel 公式開頭字元,並限制長度。"""
    s = re.sub(r"[\x00-\x1f\x7f]", " ", str(value)).strip()
    # === DEFENSE 4 BEGIN: 以 = + - @ 開頭的文字不可被 Excel 當公式執行 ===
    s = s.lstrip("=+-@")
    # === DEFENSE 4 END ===
    return s[:limit]


def safe_filename(name):
    # === DEFENSE 3 BEGIN: 模型回傳的名稱變檔名前,移除路徑相關字元 ===
    s = clean_text(name, 20).replace("..", "")
    s = re.sub(r'[\\/:*?"<>|\s]+', "_", s)
    # === DEFENSE 3 END ===
    return s or "outfit"


def parse_model_output(raw):
    """從模型輸出擷取 JSON 並嚴格驗證;不合格就丟 ValueError。"""
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError("找不到 JSON")
    data = json.loads(m.group(0))
    if not isinstance(data, dict):
        raise ValueError("JSON 不是物件")
    if data.get("is_outfit") is False:
        return {"is_outfit": False, "name": "不是穿搭", "items": [], "colors": [],
                "style": "其他", "temp_min": None, "temp_max": None,
                "note": clean_text(data.get("note", "照片中沒有人穿搭"), 80)}
    items = data.get("items")
    colors = data.get("colors")
    if not isinstance(items, list) or not items or not all(isinstance(i, str) for i in items):
        raise ValueError("items 必須是非空字串陣列")
    if not isinstance(colors, list) or not all(isinstance(c, str) for c in colors):
        raise ValueError("colors 必須是字串陣列")
    tmin, tmax = data.get("temp_min"), data.get("temp_max")
    for t in (tmin, tmax):
        if isinstance(t, bool) or not isinstance(t, (int, float)) or not -20 <= t <= 50:
            raise ValueError("溫度必須是 -20~50 的數字")
    if tmin > tmax:
        tmin, tmax = tmax, tmin
    style = data.get("style")
    return {"is_outfit": True, "name": clean_text(data.get("name", "")) or "未命名穿搭",
            "items": [clean_text(i, 20) for i in items[:8]],
            "colors": [clean_text(c, 10) for c in colors[:5]],
            "style": style if style in STYLES else "其他",
            "temp_min": tmin, "temp_max": tmax, "note": ""}


def similarity(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def find_repeat(items, history, days=7, threshold=0.6, now=None):
    """在該使用者最近 days 天紀錄中,找單品重疊度 >= threshold 的穿搭。"""
    now = now or datetime.now()
    best = None
    for rec in history:
        if now - rec["time"] > timedelta(days=days):
            continue
        s = similarity(items, rec["items"])
        if s >= threshold and (best is None or s > best[0]):
            best = (s, rec)
    return best


def summarize(records):
    """records: [{'time','name','items','style'}] -> 統計 dict。"""
    items = Counter(i for r in records for i in r["items"])
    styles = Counter(r["style"] for r in records)
    return {"count": len(records), "top_items": items.most_common(3),
            "top_style": styles.most_common(1)[0] if styles else None}
