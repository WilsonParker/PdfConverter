# 설치가 필요할 수 있습니다: pip install python-dateutil
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta


class DateUtil:

    # 날짜 추가
    def addYearsToDate(self, date: str, year: str):
        # '30년'에서 숫자 30만 추출
        years_to_add = int(re.findall(r'\d+', year)[0])

        date_obj = datetime.strptime(date, "%Y-%m-%d")
        new_date = date_obj + relativedelta(years=years_to_add)

        return new_date.strftime("%Y-%m-%d")
