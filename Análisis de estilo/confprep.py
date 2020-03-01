# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 18:50:23 2019

@author: Carlos Moreno Morera
"""

TAGS_BREAKS_LINE = {'/p', '/div', 'br', 'br/'}
TAGS_FORMAT_TEXT = {'b', '/b', 'strong', '/strong', 'i', '/i', 'em', '/em',
                    'u', '/u', 's', '/s', 'del', '/del'}
TAGS_LIST = {'ul', 'ol', 'li'}
SPECIAL_CHAR = {'*', '-', '.', ' '}

CHAR_ERROR = 3

FOWARD_LINE = '---------- Forwarded message ---------'

CSV_COL = ['id', 'threadId', 'to', 'cc', 'bcc', 'from', 'depth', 'date', 'subject', 
               'bodyBase64Plain', 'bodyBase64Html', 'plainEncoding', 'charLength']

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

REPLY_PATTERN = MOMENT_PAT + r',\s' + EMAIL_PAT + r'\sescribió:'