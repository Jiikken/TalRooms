import re

from app.services.date import get_today_date_ymd, get_today_date_dmy


def test_get_today_date_ymd():
    date = get_today_date_ymd()
    assert re.match(r'^\d{4}-\d{2}-\d{2}$', date) is not None
    assert len(date) == 10

def test_get_today_date_dmy():
    date = get_today_date_dmy()
    assert re.match(r'^\d{2}.\d{2}.\d{4}$', date) is not None
    assert len(date) == 10