"""
Scopul fisierului este sa gestioneze si sa incadreze zilele dintr o luna in anumite saptamani
S1: 1-7
S2: 8-14
S3: 15-21
S4: 22-28
S5: 29+ (pana la 30/31)
"""
import calendar
from datetime import date, datetime

def get_week_label(day):
    if 1<=day<=7:
        return "S1"
    elif 8<=day<=14:
        return "S2"
    elif 15<=day<=21:
        return "S3"
    elif 22<=day<=28:
        return "S4"
    else:
        return "S5"

def adjust_day_for_month(year, month, day):
    last_day = calendar.monthrange(year, month)[1]
    return min(day, last_day)

def get_filename(year, month):
    return f"{year}-{month:02d}_Buget.xlsx"


