def is_market_close_today() -> bool:
    return False
    # local_tz = ZoneInfo(settings.TIME_ZONE)
    # today = datetime.datetime.now().astimezone(local_tz).date()
    # if today.weekday() in [5, 6]:
    #     return True
    #
    # holiday_exists = Holiday.objects.filter(trading_date=today).exists()
    # if holiday_exists:
    #     return True
    #
    # return False
