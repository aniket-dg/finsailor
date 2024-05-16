import datetime

from celery import shared_task

from combo_investment.celery import BaseTaskWithRetry
from datahub.models import Security
from news.models import StockEvent
from scrapper.views import NSEScrapper


@shared_task(base=BaseTaskWithRetry)
def load_upcoming_nse_events():
    nse = NSEScrapper()
    events, status = nse.get_upcoming_events()

    if not events:
        return

    symbol_to_event_data = {}
    for event in events:
        symbol = event.get("symbol")
        symbol_to_event_data[symbol] = event

    securities = Security.objects.filter(symbol__in=symbol_to_event_data.keys())

    for sec in securities:
        event = symbol_to_event_data.get(sec.symbol)
        event_date = datetime.datetime.strptime(event.get("date"), "%d-%b-%Y")
        StockEvent.objects.get_or_create(
            date=event_date,
            company=event.get("company"),
            security_id=sec.id,
            defaults={"purpose": event.get("purpose"), "details": event.get("bm_desc")},
        )
