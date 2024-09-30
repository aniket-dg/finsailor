from json import JSONEncoder

from django.db import models
from django.db.models import QuerySet, F
from django.utils.translation import gettext_lazy as _
from bsedata.bse import BSE
import datetime
import decimal

from industries.models import BasicIndustry
from django.db.models import Func, Value, CharField


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)


class JSONExtractPathText(Func):
    function = "jsonb_extract_path_text"
    template = "%(function)s(%(expressions)s)"

    def __init__(self, expression, *paths, **extra):
        paths = [expression] + list(paths)
        super().__init__(*paths, output_field=CharField(), **extra)


class SecurityCache(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)


class SecurityQuerySet(QuerySet):
    def with_related(self):
        return self.select_related("basic_industry__industry__sector__macro_sector")

    def with_close_price(self, date):
        return self.annotate(
            last_price=JSONExtractPathText(
                F("historical_price_info"), Value(date), Value("lastPrice")
            )
        ).values("symbol", "last_price", "market_cap", "free_float_market_cap")


class SecurityManager(models.Manager):
    def get_queryset(self):
        return SecurityQuerySet(self.model, using=self._db).with_related()

    def with_close_price(self, date):
        return SecurityQuerySet(self.model, using=self._db).with_close_price(date=date)


class Security(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    isin = models.CharField(max_length=100, null=True, blank=True)
    scrip_code = models.CharField(max_length=100, null=True, blank=True)
    symbol = models.CharField(max_length=100, unique=True)
    last_updated_price = models.DecimalField(
        decimal_places=10, null=True, blank=True, max_digits=30
    )
    market_cap = models.DecimalField(
        decimal_places=10, null=True, blank=True, max_digits=30
    )
    free_float_market_cap = models.DecimalField(
        decimal_places=10, null=True, blank=True, max_digits=30
    )
    price_modified_datetime = models.DateTimeField(blank=True, null=True)
    basic_industry = models.ForeignKey(
        BasicIndustry, on_delete=models.SET_NULL, null=True, blank=True
    )
    historical_price_info = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    trade_info = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    security_info = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    metadata = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    base_security = models.BooleanField(default=True)

    objects = models.Manager()
    select_related = SecurityManager()

    def __str__(self):
        return f"Security - {self.name}"


class ExchangeType(models.TextChoices):
    BSE = ("BSE", _("Bombay Stock Exchange"))
    NSE = ("NSE", _("National Stock Exchange"))


class Exchange(models.Model):
    name = models.CharField(
        choices=ExchangeType.choices, max_length=50, default=ExchangeType.BSE
    )


class Broker(models.Model):
    name = models.CharField(max_length=50)


class GeneralInfo(models.Model):
    tradebook_last_uploaded = models.DateField(null=True, blank=True)


class Parameter(models.Model):
    name = models.CharField(max_length=100)
    time = models.TimeField(null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)


class StockIndex(models.Model):
    key = models.CharField(max_length=100)
    index = models.CharField(max_length=100)
    indexSymbol = models.CharField(max_length=100)
    last = models.CharField(max_length=100, null=True, blank=True)
    variation = models.CharField(max_length=100, null=True, blank=True)
    percentChange = models.CharField(max_length=100, null=True, blank=True)
    open = models.CharField(max_length=100, null=True, blank=True)
    high = models.CharField(max_length=100, null=True, blank=True)
    low = models.CharField(max_length=100, null=True, blank=True)
    previousClose = models.CharField(max_length=100, null=True, blank=True)
    yearHigh = models.CharField(max_length=100, null=True, blank=True)
    yearLow = models.CharField(max_length=100, null=True, blank=True)
    indicativeClose = models.CharField(max_length=100, null=True, blank=True)
    pe = models.CharField(max_length=100, null=True, blank=True)
    pb = models.CharField(max_length=100, null=True, blank=True)
    dy = models.CharField(max_length=100, null=True, blank=True)
    declines = models.CharField(max_length=100, null=True, blank=True)
    advances = models.CharField(max_length=100, null=True, blank=True)
    unchanged = models.CharField(max_length=100, null=True, blank=True)
    perChange365d = models.CharField(null=True, blank=True)
    date365dAgo = models.CharField(max_length=200, null=True, blank=True)
    chart365dPath = models.CharField(max_length=200, null=True, blank=True)
    date30dAgo = models.CharField(max_length=200, null=True, blank=True)
    perChange30d = models.CharField(max_length=100, null=True, blank=True)
    chart30dPath = models.CharField(max_length=200, null=True, blank=True)
    chartTodayPath = models.CharField(max_length=200, null=True, blank=True)
    previousDay = models.CharField(max_length=100, null=True, blank=True)
    oneWeekAgo = models.CharField(max_length=100, null=True, blank=True)
    oneMonthAgo = models.CharField(max_length=100, null=True, blank=True)
    oneYearAgo = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        unique_together = ["index", "date", "time"]

    def get_empty_object(self):
        new_stock_index = self
        fields_to_update_none = [
            "pk",
            "variation",
            "percentChange",
            "previousClose",
            "yearHigh",
            "yearLow",
            "indicativeClose",
            "pe",
            "pb",
            "dy",
            "declines",
            "unchanged",
            "perChange356d",
            "day365dAgo",
            "chart365dPath",
            "date30dAgo",
            "perChange30d",
            "chart30dPath",
            "chartTodayPath",
            "previousDay",
            "oneWeekAgo",
            "oneMonthAgo",
            "oneYearAgo",
        ]
        for field in fields_to_update_none:
            setattr(new_stock_index, field, None)

        return new_stock_index

    @classmethod
    def update_or_create_from_dict(cls, data):
        obj, created = cls.objects.update_or_create(
            key=data.get("key"),
            index=data.get("index"),
            indexSymbol=data.get("indexSymbol"),
            date=data.get("date"),
            time=data.get("time"),
            defaults={
                "last": data.get("last"),
                "variation": data.get("variation"),
                "percentChange": data.get("percentChange"),
                "open": data.get("open"),
                "high": data.get("high"),
                "low": data.get("low"),
                "previousClose": data.get("previousClose"),
                "yearHigh": data.get("yearHigh"),
                "yearLow": data.get("yearLow"),
                "indicativeClose": data.get("indicativeClose"),
                "pe": data.get("pe"),
                "pb": data.get("pb"),
                "dy": data.get("dy"),
                "declines": data.get("declines"),
                "advances": data.get("advances"),
                "unchanged": data.get("unchanged"),
                "perChange365d": data.get("perChange365d"),
                "date365dAgo": data.get("date365dAgo"),
                "chart365dPath": data.get("chart365dPath"),
                "date30dAgo": data.get("date30dAgo"),
                "perChange30d": data.get("perChange30d"),
                "chart30dPath": data.get("chart30dPath"),
                "chartTodayPath": data.get("chartTodayPath"),
                "previousDay": data.get("previousDay"),
                "oneWeekAgo": data.get("oneWeekAgo"),
                "oneMonthAgo": data.get("oneMonthAgo"),
                "oneYearAgo": data.get("oneYearAgo"),
            },
        )
        return obj, created

    def __str__(self):
        return f"{self.indexSymbol} - {self.date} - {self.time.strftime('%I:%M %p')}"


class TodayStockIndex(models.Model):
    stocks_indices = models.ManyToManyField(
        StockIndex, related_name="todays_stock_index", null=True, blank=True
    )
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    historical_dates_info = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    date_30_day_ago = models.DateField(null=True, blank=True)
    date_365_day_ago = models.DateField(null=True, blank=True)


class Holiday(models.Model):
    trading_date = models.DateField()
    weekday = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    sr_no = models.IntegerField()

    def __str__(self):
        return f"Hoiliday - {self.trading_date}"


class TodaysMacroSectorPerformance(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, encoder=CustomJSONEncoder)

    def __str__(self):
        return f"TodaysMacroSectorPerformance - {self.datetime}"


class CorporateAction(models.Model):
    symbol = models.CharField(max_length=20)
    series = models.CharField(max_length=10)
    ind = models.CharField(max_length=10, blank=True, null=True)
    face_val = models.DecimalField(max_digits=10, decimal_places=2)
    subject = models.CharField(max_length=255)
    ex_date = models.DateField()
    rec_date = models.DateField(blank=True, null=True)
    bc_start_date = models.DateField(blank=True, null=True)
    bc_end_date = models.DateField(blank=True, null=True)
    nd_start_date = models.DateField(blank=True, null=True)
    comp = models.CharField(max_length=255)
    isin = models.CharField(max_length=12)
    nd_end_date = models.DateField(blank=True, null=True)
    ca_broadcast_date = models.DateField(blank=True, null=True)

    @classmethod
    def create_from_dict(cls, data):
        def parse_date(date_str):
            if date_str and date_str != "-":
                return datetime.datetime.strptime(date_str, "%d-%b-%Y").date()
            return None

        # Convert dictionary to model instance
        return cls.objects.create(
            symbol=data.get("symbol"),
            series=data.get("series"),
            ind=data.get("ind") if data.get("ind") != "-" else None,
            face_val=data.get("faceVal"),
            subject=data.get("subject"),
            ex_date=parse_date(data.get("exDate")),
            rec_date=parse_date(data.get("recDate")),
            bc_start_date=parse_date(data.get("bcStartDate")),
            bc_end_date=parse_date(data.get("bcEndDate")),
            nd_start_date=parse_date(data.get("ndStartDate")),
            comp=data.get("comp"),
            isin=data.get("isin"),
            nd_end_date=parse_date(data.get("ndEndDate")),
            ca_broadcast_date=parse_date(data.get("caBroadcastDate")),
        )
