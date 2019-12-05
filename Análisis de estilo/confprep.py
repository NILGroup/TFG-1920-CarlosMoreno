# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 18:50:23 2019

@author: Carlos Moreno Morera
"""

TAGS_BREAKS_LINE = {'/p', '/div', 'br', 'br/'}
BREAK_LINE = {'\n', '\r'}

CHAR_ERROR = 3

FOWARD_LINE = '---------- Forwarded message ---------'

WEEK_PATTERN = '(lun\.|mar\.|mié\.|jue\.|vie\.|sáb\.|dom\.)'
DAYS_31_PAT = '(\d|((1|2)\d)|30|31)'
DAYS_30_PAT = '(\d|((1|2)\d)|30)'

MONTH_31_PAT = '(ene|mar|may|jul|ago|oct|dic)'
MONTH_30_PAT = '(abr|jun|sept|nov)'
#Leap years are not checked
FEB_PAT = '(\d|((1|2)\d))\sfeb'

DATE_31_PAT = DAYS_31_PAT + '\s' + MONTH_31_PAT
DATE_30_PAT = DAYS_30_PAT + '\s' + MONTH_30_PAT

MONTH_DAY_PAT = '(' + DATE_31_PAT + '|' + DATE_30_PAT + '|' + FEB_PAT + ')\.'
DATE_PAT = MONTH_DAY_PAT + '\s(20|19)\d\d'



BEGIN_PATTERN = 'El\s' + WEEK_PATTERN + ',\s' + DATE_PAT