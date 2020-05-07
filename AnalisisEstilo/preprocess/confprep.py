# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 18:50:23 2019

@author: Carlos Moreno Morera
"""

TAGS_BREAKS_LINE = {'/p', '/div', 'br', 'br/', 'div', 'p'}
TAGS_FORMAT_TEXT = {'b', '/b', 'strong', '/strong', 'i', '/i', 'em', '/em',
                    'u', '/u', 's', '/s', 'del', '/del'}
TAGS_LIST = {'ul', 'ol', 'li'}
SPECIAL_CHAR = {'*', '-', '.', ' '}
SPECIAL_HTML_CHAR = {'<' : '&lt;', '>' : '&gt;', '&' : '&amp;', '"': '&quot;',
                     "'" : '&#39;'}

CHAR_ERROR = 3

FORWARD_LINE = '---------- Forwarded message ---------'
FORWARD_LINE_ES = '--------- Mensaje reenviado ----------'

WEEK_PATTERN = r'(?:lun|mar|mié|jue|vie|sáb|dom)\.'
DAYS_31_PAT = r'(?:(?:[12]?\d)|30|31)'
DAYS_30_PAT = r'(?:(?:[12]?\d)|30)'

MONTH_31_PAT = r'(?:ene|mar|may|jul|ago|oct|dic)'
MONTH_30_PAT = r'(?:abr|jun|sept|nov)'
#Leap years are not checked
FEB_PAT = r'(?:[12]?\d)\sfeb'

DATE_31_PAT = DAYS_31_PAT + r'\s' + MONTH_31_PAT
DATE_30_PAT = DAYS_30_PAT + r'\s' + MONTH_30_PAT

MONTH_DAY_PAT = r'(?:' + DATE_31_PAT + r'|' + DATE_30_PAT + r'|' + FEB_PAT + r')\.'
DATE_PAT = MONTH_DAY_PAT + r'\s(?:20|19)\d\d'

TIME_PAT = r'(?:(?:1?\d)|2[0-3]):[0-5]\d'

MOMENT_PAT = r'El\s' + WEEK_PATTERN + r',\s' + DATE_PAT + r'\s(?:a\slas\s)?' + TIME_PAT

EMAIL_PAT = r'[^@]+@[\w.-]+\.[a-zA-Z]{2,6}>?\)?'

REPLY_PATTERN = MOMENT_PAT + r',\s' + EMAIL_PAT + r'\s+escribió:'

MONTH_31_PAT2 = r'(?:enero|marzo|mayo|julio|agosto|octubre|diciembre)'
MONTH_30_PAT2 = r'(?:abril|junio|septiembre|noviembre)'

#Leap years are not checked
FEB_PAT2 = r'(?:[12]?\d)\sde\sfebrero'
DATE_31_PAT2 = DAYS_31_PAT + r'\sde\s' + MONTH_31_PAT2
DATE_30_PAT2 = DAYS_30_PAT + r'\sde\s' + MONTH_30_PAT2

MONTH_DAY_PAT2 = r'(?:' + DATE_31_PAT2 + r'|' + DATE_30_PAT2 + r'|' + FEB_PAT2 + r')\.'
DATE_PAT2 = MONTH_DAY_PAT2 + r'\sde\s(?:20|19)\d\d'

REPLY_PATTERN2 = r'El\s' + DATE_PAT2 + r',\s' + TIME_PAT + EMAIL_PAT + r'\s+escribió:'