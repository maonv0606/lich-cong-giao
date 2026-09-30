#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Catholic Calendar (.ics) Generator for iOS & Android
Tạo file lịch iCalendar (.ics) cho người Công Giáo với đầy đủ bài đọc, bậc lễ và thông báo nhắc nhở.
"""

import os
import re
import uuid
from datetime import datetime, date, timedelta, timezone

# ==============================================================================
# CẤU HÌNH NHẮC NHỞ (ALARMS / REMINDERS)
# ==============================================================================
# 1. Nhắc trước vào buổi tối hôm trước (khoảng 20:00) đối với Lễ Trọng, Lễ Kính, Lễ Buộc, Chúa Nhật
REMIND_EVENING_BEFORE = True

# 2. Nhắc vào buổi sáng ngày lễ (khoảng 07:00 sáng)
REMIND_MORNING_OF_FEAST = True

# 3. Có bật chuông nhắc nhở cho ngày thường (chỉ có bài đọc, không có lễ) không?
# Mặc định False để tránh reo chuông liên tục mỗi ngày gây phiền.
REMIND_ORDINARY_DAYS = False

# Tên bộ lịch hiển thị trên iPhone/Android
CALENDAR_NAME = "Lịch Phụng Vụ Công Giáo"
CALENDAR_DESC = "Lịch các ngày Lễ Trọng, Lễ Kính, Lễ Nhớ và Bài Đọc Lời Chúa"

# ==============================================================================
# BẢNG THUẬT NGỮ PHỤNG VỤ
# ==============================================================================
LITURGICAL_COLORS = {
    "(Tr)": "Trắng (Lễ Chúa, Đức Mẹ, Thiên Thần, Các Thánh không tử đạo)",
    "(Đ)": "Đỏ (Lễ Chúa Thánh Thần, Cuộc Khổ Nạn, Các Thánh Tử Đạo, Tông Đồ)",
    "(X)": "Xanh (Mùa Thường Niên)",
    "(Tm)": "Tím (Mùa Vọng, Mùa Chay, Cầu hồn)",
    "(H)": "Hồng (Chúa Nhật Vui Mùa Vọng / Mùa Chay)"
}

SCRIPTURE_BOOKS = [
    "St", "Xh", "Lv", "Ds", "Đnl", "Gs", "Thp", "Rút", "1 Sm", "2 Sm", "1 V", "2 V",
    "1 Sb", "2 Sb", "Er", "Nkm", "Tb", "Gđt", "Et", "1 Mcb", "2 Mcb", "G", "Tv",
    "Cn", "Gv", "Dc", "Kn", "Hc", "Is", "Gr", "Ac", "Br", "Ed", "Đn", "Hs", "Ge",
    "Am", "Ob", "Yn", "Mk", "Nm", "Hk", "Xp", "Hg", "Zc", "Ml",
    "Mt", "Mc", "Lc", "Ga", "Cv", "Rm", "1 Cr", "2 Cr", "Gl", "Ep", "Pl", "Cl",
    "1 Tx", "2 Tx", "1 Tm", "2 Tm", "Tt", "Plm", "Dt", "Gcb", "1 Pr", "2 Pr",
    "1 Ga", "2 Ga", "3 Ga", "Gđ", "Kh"
]

def is_scripture_line(line: str) -> bool:
    line_clean = line.strip()
    if not line_clean:
        return False
    if line_clean.startswith("Sách bài đọc"):
        return True
    if re.match(r'^\d+,\s*\d+', line_clean):
        return True
    for book in SCRIPTURE_BOOKS:
        if re.search(r'\b' + re.escape(book) + r'\s+\d+', line_clean):
            return True
    return False

def clean_reading(text: str) -> str:
    t = text.strip()
    return re.sub(r'[;,]+$', '', t).strip()

def escape_ics_text(text: str) -> str:
    """Escape text for iCalendar RFC 5545 format."""
    text = text.replace('\\', '\\\\')
    text = text.replace(';', r'\;')
    text = text.replace(',', r'\,')
    text = text.replace('\r\n', r'\n').replace('\r', r'\n').replace('\n', r'\n')
    return text

def fold_ics_line(line: str, limit: int = 75) -> str:
    """Fold lines longer than 75 bytes as required by RFC 5545."""
    if len(line.encode('utf-8')) <= limit:
        return line
    
    parts = []
    current_bytes = bytearray()
    
    for ch in line:
        ch_bytes = ch.encode('utf-8')
        if len(current_bytes) + len(ch_bytes) > limit:
            parts.append(current_bytes.decode('utf-8'))
            current_bytes = bytearray(b' ' + ch_bytes)
        else:
            current_bytes.extend(ch_bytes)
            
    if current_bytes:
        parts.append(current_bytes.decode('utf-8'))
        
    return '\r\n'.join(parts)

def parse_catholic_data(file_path_or_text: str, is_file: bool = True):
    if is_file:
        with open(file_path_or_text, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = file_path_or_text

    date_regex = re.compile(r"^(\d{1,2}/\d{1,2}/\d{4})\s*$", re.MULTILINE)
    matches = list(date_regex.finditer(content))
    days = []

    for i, match in enumerate(matches):
        date_str = match.group(1).strip()
        d_start = match.end()
        d_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        
        block = content[d_start:d_end].strip()
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        
        day_of_week = ""
        content_lines = []
        
        if lines and any(dow in lines[0] for dow in ["Thứ", "Chủ Nhật"]):
            day_of_week = lines[0]
            content_lines = lines[1:]
        else:
            content_lines = lines

        # Skip empty days
        if not content_lines:
            continue
            
        days.append({
            "date_str": date_str,
            "day_of_week": day_of_week,
            "raw_lines": content_lines
        })

    return days

def parse_event_details(entry: dict) -> dict:
    d, m, y = map(int, entry["date_str"].split("/"))
    event_date = date(y, m, d)
    day_of_week = entry["day_of_week"]
    raw_lines = entry["raw_lines"]

    rank = None
    colors = []
    color_explanations = []
    readings = []
    titles = []
    notes = []

    for line_str in raw_lines:
        line_str = line_str.strip()
        if not line_str:
            continue
        
        # Rank detection
        if re.search(r'Lễ\s+trọng\s*\.?\s*Lễ\s+buộc', line_str, re.IGNORECASE):
            rank = "LỄ TRỌNG (LỄ BUỘC)"
            continue
        elif re.search(r'Lễ\s+trọng', line_str, re.IGNORECASE):
            rank = "LỄ TRỌNG"
            continue
        elif re.search(r'Lễ\s+kính', line_str, re.IGNORECASE):
            rank = "Lễ kính"
            continue
        elif re.search(r'Lễ\s+nhớ', line_str, re.IGNORECASE):
            rank = "Lễ nhớ"
            continue
        
        # Color codes
        for c_code, c_desc in LITURGICAL_COLORS.items():
            if c_code in line_str:
                if c_code not in colors:
                    colors.append(c_code)
                    color_explanations.append(f"{c_code}: {c_desc}")

        # Scripture or notes or titles
        if is_scripture_line(line_str):
            readings.append(line_str)
        elif line_str in ["(Tr)", "(Đ)", "(X)", "(Tm)", "(H)"]:
            pass
        elif any(line_str.startswith(kw) for kw in ["Không cử hành", "Bổn mạng", "Kỷ niệm", "Hết năm phụng vụ", "MÙA VỌNG", "Thánh vịnh"]):
            notes.append(line_str)
        else:
            titles.append(line_str)

    # Determine if this day is an actual feast or Sunday (filter out ordinary weekdays)
    full_text = " ".join(raw_lines).lower()
    keywords = ["thánh", "đức mẹ", "đức trinh nữ", "thiên thần", "cung hiến", "tử đạo", "fatima", "các đẳng", "cầu cho các tín hữu", "hài đồng", "giáng sinh", "thánh gia", "tô-ma", "bổn mạng"]
    has_sacred = any(k in full_text for k in keywords)
    is_sunday = "chủ nhật" in day_of_week.lower() or "chúa nhật" in full_text
    
    is_actual_feast = is_sunday or bool(rank) or has_sacred
    if not is_actual_feast:
        return None  # Bỏ ngày thường, chỉ giữ ngày lễ!

    # Determine main title (prioritize saint/celebration line)
    main_title = ""
    for t in titles:
        t_clean = re.sub(r'^\([TrĐXmH]+\)\s*', '', t).strip()
        t_clean = re.sub(r'\s*\([TrĐXmH]+\)$', '', t_clean).strip()
        if any(k in t.lower() for k in keywords) or "chúa nhật" in t.lower():
            main_title = t_clean
            break
            
    if not main_title and titles:
        main_title = re.sub(r'^\([TrĐXmH]+\)\s*', '', titles[0]).strip()
        main_title = re.sub(r'\s*\([TrĐXmH]+\)$', '', main_title).strip()
        
    if not main_title:
        main_title = f"{day_of_week} ({entry['date_str']})"

    # Summary building
    summary_parts = []
    is_solemnity = rank and "TRỌNG" in rank.upper()
    is_feast = rank == "Lễ kính"
    is_memorial = rank == "Lễ nhớ" or ("Thánh " in main_title and not rank and not is_sunday)

    if rank:
        if is_solemnity:
            summary_parts.append(f"[{rank}]")
        elif is_feast:
            summary_parts.append("[Lễ kính]")
        elif is_memorial and not is_sunday:
            summary_parts.append("[Lễ nhớ]")
    elif is_memorial and not is_sunday:
        summary_parts.append("[Lễ nhớ]")

    summary_parts.append(main_title)
    summary = " ".join(summary_parts)

    # Description building
    desc_lines = []
    if rank:
        desc_lines.append(f"✦ Bậc lễ: {rank}")
    
    if color_explanations:
        desc_lines.append("✦ Màu áo phụng vụ:")
        for ce in color_explanations:
            desc_lines.append(f"   {ce}")
            
    if notes:
        desc_lines.append("✦ Ghi chú phụng vụ:")
        for n in notes:
            desc_lines.append(f"   • {n}")

    if len(titles) > 1:
        desc_lines.append("✦ Các lễ / ý chỉ khác:")
        for t in titles[1:]:
            desc_lines.append(f"   • {t}")

    clean_readings_list = [clean_reading(r) for r in readings if clean_reading(r)]
    if clean_readings_list:
        desc_lines.append("✦ Lời Chúa trong Thánh lễ:")
        for r in clean_readings_list:
            desc_lines.append(f"   • {r}")

    description = "\n".join(desc_lines)

    # Alarm criteria
    needs_alarm = True

    return {
        "date": event_date,
        "date_str": entry["date_str"],
        "day_of_week": day_of_week,
        "summary": summary,
        "clean_title": main_title,
        "description": description,
        "rank": rank,
        "colors": colors,
        "readings": clean_readings_list,
        "notes": notes,
        "is_solemnity": is_solemnity,
        "is_feast": is_feast,
        "is_sunday": is_sunday,
        "is_actual_feast": is_actual_feast,
        "needs_alarm": needs_alarm
    }

def generate_ics(events, output_filename="catholic_calendar.ics"):
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Catholic Calendar Vietnam//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_ics_text(CALENDAR_NAME)}",
        f"X-WR-CALDESC:{escape_ics_text(CALENDAR_DESC)}",
        "X-WR-TIMEZONE:Asia/Ho_Chi_Minh",
        "X-PUBLISHED-TTL:P1D",
        "REFRESH-INTERVAL;VALUE=DURATION:P1D"
    ]

    for ev in events:
        start_date_str = ev["date"].strftime("%Y%m%d")
        end_date = ev["date"] + timedelta(days=1)
        end_date_str = end_date.strftime("%Y%m%d")
        
        uid = f"catholic-{start_date_str}-{uuid.uuid4().hex[:8]}@phungvu.vn"
        
        event_lines = [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART;VALUE=DATE:{start_date_str}",
            f"DTEND;VALUE=DATE:{end_date_str}",
            f"SUMMARY:{escape_ics_text(ev['summary'])}",
            f"DESCRIPTION:{escape_ics_text(ev['description'])}",
            "STATUS:CONFIRMED",
            "TRANSP:TRANSPARENT"
        ]

        # Alarms
        if ev["needs_alarm"]:
            # Nhắc trước tối hôm trước (20:00) cho Lễ Trọng, Buộc, Kính, Chúa Nhật
            if REMIND_EVENING_BEFORE and (ev["is_solemnity"] or ev["is_feast"] or ev["is_sunday"]):
                event_lines.extend([
                    "BEGIN:VALARM",
                    "ACTION:DISPLAY",
                    f"DESCRIPTION:Ngày mai: {escape_ics_text(ev['summary'])}",
                    "TRIGGER:-P1D",  # iOS & Google Calendar default to 1 day before
                    "END:VALARM"
                ])
            
            # Nhắc sáng ngày lễ (07:00)
            if REMIND_MORNING_OF_FEAST:
                event_lines.extend([
                    "BEGIN:VALARM",
                    "ACTION:DISPLAY",
                    f"DESCRIPTION:Hôm nay: {escape_ics_text(ev['summary'])}",
                    "TRIGGER;RELATED=START:PT7H",  # 7:00 AM on the day
                    "END:VALARM"
                ])

        event_lines.append("END:VEVENT")

        # Fold lines and add
        for el in event_lines:
            lines.append(fold_ics_line(el))

    lines.append("END:VCALENDAR")

    final_ics_content = "\r\n".join(lines) + "\r\n"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_ics_content)
        
    print(f"Đã tạo thành công file: {output_filename}")
    print(f"Tổng số sự kiện ngày lễ: {len(events)}")
    return output_filename

def main():
    import sys
    input_file = "raw_calendar_data.txt"
    output_file = "catholic_calendar_2026.ics"

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Không tìm thấy file: {input_file}")
        return

    print(f"Đang đọc dữ liệu từ: {input_file}...")
    raw_days = parse_catholic_data(input_file)
    parsed_events = [parse_event_details(d) for d in raw_days]
    feasts_only = [ev for ev in parsed_events if ev is not None]
    
    # Chỉ lấy Lễ Buộc & Lễ Trọng vào file ICS (loại bỏ Chúa Nhật thường và Lễ nhớ/kính)
    solemnities_only = [
        ev for ev in feasts_only 
        if ev.get("is_solemnity") or (ev.get("rank") and ("TRỌNG" in ev["rank"].upper() or "BUỘC" in ev["rank"].upper()))
    ]
    generate_ics(solemnities_only, output_file)

if __name__ == "__main__":
    main()
