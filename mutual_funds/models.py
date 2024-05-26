from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.dateparse import parse_date

from datahub.models import CustomJSONEncoder, Security
from users.models import User


class FundSecurity(models.Model):
    security = models.ForeignKey(
        Security,
        on_delete=models.CASCADE,
        related_name="fund_security",
        help_text="Reference to Security",
    )

    fund = models.ForeignKey(
        "Fund",
        on_delete=models.CASCADE,
        related_name="fund_security",
        help_text="Reference to Fund",
    )
    portfolio_date = models.DateTimeField()
    nature_name = models.CharField(max_length=500, null=True, blank=True)
    market_value = models.FloatField()
    corpus_per = models.FloatField()
    market_cap = models.CharField(max_length=500, null=True, blank=True)
    rating_market_cap = models.CharField(max_length=500, null=True, blank=True)
    scheme_code = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Fund Securities"


class Fund(models.Model):
    meta_title = models.CharField(max_length=500)
    meta_desc = models.TextField()
    meta_robots = models.CharField(max_length=500)
    amc = models.CharField(max_length=500)
    scheme_code = models.CharField(max_length=500)
    direct_scheme_code = models.CharField(max_length=500, null=True, blank=True)
    regular_search_id = models.CharField(max_length=500, null=True, blank=True)
    scheme_name = models.CharField(max_length=500)
    registrar_agent = models.CharField(max_length=500)
    search_id = models.CharField(max_length=500)
    min_investment_amount = models.PositiveIntegerField()
    fund_house = models.CharField(max_length=500)
    fund_manager = models.CharField(max_length=500)
    launch_date = models.DateField()
    mini_additional_investment = models.PositiveIntegerField()
    sip_multiplier = models.PositiveIntegerField()
    groww_rating = models.FloatField(null=True, blank=True)
    crisil_rating = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=500)
    rta_scheme_code = models.CharField(max_length=500)
    exit_load = models.CharField(max_length=500)
    sub_category = models.CharField(max_length=500)
    description = models.TextField()
    benchmark = models.CharField(max_length=500)
    benchmark_name = models.CharField(max_length=500)
    aum = models.FloatField()
    expense_ratio = models.CharField(max_length=500)
    super_category = models.CharField(max_length=500)
    sub_sub_category = models.CharField(max_length=500, null=True, blank=True)
    min_sip_investment = models.PositiveIntegerField()
    max_sip_investment = models.PositiveIntegerField()
    min_withdrawal = models.PositiveIntegerField()
    purchase_multiplier = models.PositiveIntegerField()
    available_for_investment = models.BooleanField()
    sip_allowed = models.BooleanField()
    lumpsum_allowed = models.BooleanField()
    doc_required = models.BooleanField()
    nav = models.FloatField()
    nav_date = models.DateField(null=True, blank=True)
    plan_type = models.CharField(max_length=500)
    scheme_type = models.CharField(max_length=500)
    video_url = models.URLField(null=True, blank=True)
    fund_news = models.TextField(null=True, blank=True)
    fund_events = models.TextField(null=True, blank=True)
    logo_url = models.URLField()
    sid_url = models.URLField()
    amc_page_url = models.URLField()
    isin = models.CharField(max_length=500)
    groww_scheme_code = models.CharField(max_length=500)
    stamp_duty = models.CharField(max_length=500)
    dividend = models.CharField(max_length=500, null=True, blank=True)
    closed_scheme = models.BooleanField()
    closed_date = models.DateField(null=True, blank=True)
    additional_details = models.TextField(null=True, blank=True)
    prod_code = models.CharField(max_length=500)
    stp_flag = models.BooleanField()
    swp_flag = models.BooleanField()
    switch_flag = models.BooleanField()
    redemption_amount_multiple = models.PositiveIntegerField(null=True, blank=True)
    redemption_qty_multiplier = models.PositiveIntegerField(null=True, blank=True)
    unique_groww_scheme_code = models.CharField(max_length=500, null=True, blank=True)
    swp_frequencies = models.CharField(max_length=500, null=True, blank=True)
    blocked_reason = models.TextField(null=True, blank=True)
    is_additional_check_req = models.BooleanField()
    sip_return = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    simple_return = models.JSONField(
        default=dict,
        encoder=CustomJSONEncoder,
    )
    lock_in = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    historic_exit_loads = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    historic_fund_expense = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    stpDetails = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    swpDetails = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    analysis = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    amc_info = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    category_info = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    stats = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    return_stats = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    fund_manager_details = models.JSONField(default=dict, encoder=CustomJSONEncoder)
    rta_details = models.JSONField(default=dict, encoder=CustomJSONEncoder)

    holdings = models.ManyToManyField(
        Security,
        through=FundSecurity,
        through_fields=("fund", "security"),
        help_text="Securities in this fund",
        blank=True,
    )

    def __str__(self):
        return self.scheme_name

    @classmethod
    def create_from_dict(cls, data):
        return cls.objects.create(
            meta_title=data.get("meta_title", ""),
            meta_desc=data.get("meta_desc", ""),
            meta_robots=data.get("meta_robots", ""),
            amc=data.get("amc", ""),
            scheme_code=data.get("scheme_code", ""),
            direct_scheme_code=data.get("direct_scheme_code"),
            regular_search_id=data.get("regular_search_id"),
            scheme_name=data.get("scheme_name", ""),
            registrar_agent=data.get("registrar_agent", ""),
            search_id=data.get("search_id", ""),
            min_investment_amount=data.get("min_investment_amount", 0),
            fund_house=data.get("fund_house", ""),
            fund_manager=data.get("fund_manager", ""),
            launch_date=(
                datetime.strptime(data.get("nav_date"), "%d-%B-%Y")
                if data.get("nav_date")
                else None
            ),
            mini_additional_investment=data.get("mini_additional_investment", 0),
            sip_multiplier=data.get("sip_multiplier", 1),
            groww_rating=data.get("groww_rating"),
            crisil_rating=data.get("crisil_rating"),
            category=data.get("category", ""),
            rta_scheme_code=data.get("rta_scheme_code", ""),
            exit_load=data.get("exit_load", ""),
            sub_category=data.get("sub_category", ""),
            description=data.get("description", ""),
            benchmark=data.get("benchmark", ""),
            benchmark_name=data.get("benchmark_name", ""),
            aum=data.get("aum", 0.0),
            expense_ratio=data.get("expense_ratio", "0.0"),
            super_category=data.get("super_category", ""),
            sub_sub_category=data.get("sub_sub_category"),
            min_sip_investment=data.get("min_sip_investment", 0),
            max_sip_investment=data.get("max_sip_investment", 0),
            min_withdrawal=data.get("min_withdrawal", 0),
            purchase_multiplier=data.get("purchase_multiplier", 1),
            available_for_investment=data.get("available_for_investment", False),
            sip_allowed=data.get("sip_allowed", False),
            lumpsum_allowed=data.get("lumpsum_allowed", False),
            doc_required=data.get("doc_required", False),
            nav=data.get("nav", 0.0),
            nav_date=(
                datetime.strptime(data.get("nav_date"), "%d-%B-%Y")
                if data.get("nav_date")
                else None
            ),
            plan_type=data.get("plan_type", ""),
            scheme_type=data.get("scheme_type", ""),
            video_url=data.get("video_url"),
            fund_news=data.get("fund_news"),
            fund_events=data.get("fund_events"),
            logo_url=data.get("logo_url", ""),
            sid_url=data.get("sid_url", ""),
            amc_page_url=data.get("amc_page_url", ""),
            isin=data.get("isin", ""),
            groww_scheme_code=data.get("groww_scheme_code", ""),
            stamp_duty=data.get("stamp_duty", ""),
            dividend=data.get("dividend"),
            closed_scheme=data.get("closed_scheme", False),
            closed_date=data.get("closed_date"),
            additional_details=data.get("additional_details"),
            prod_code=data.get("prod_code", ""),
            stp_flag=data.get("stp_flag", False),
            swp_flag=data.get("swp_flag", False),
            switch_flag=data.get("switch_flag", False),
            redemption_amount_multiple=data.get("redemption_amount_multiple"),
            redemption_qty_multiplier=data.get("redemption_qty_multiplier"),
            unique_groww_scheme_code=data.get("unique_groww_scheme_code"),
            swp_frequencies=data.get("swp_frequencies"),
            blocked_reason=data.get("blocked_reason"),
            is_additional_check_req=data.get("is_additional_check_req", False),
            sip_return=data.get("sip_return"),
            simple_return=data.get("simple_return"),
            lock_in=data.get("lock_in"),
            historic_exit_loads=data.get("historic_exit_loads"),
            historic_fund_expense=data.get("historic_fund_expense"),
            stpDetails=data.get("stpDetails"),
            swpDetails=data.get("swpDetails"),
            analysis=data.get("analysis"),
            amc_info=data.get("amc_info"),
            category_info=data.get("category_info"),
            stats=data.get("stats"),
            return_stats=data.get("return_stats"),
            fund_manager_details=data.get("fund_manager_details"),
            rta_details=data.get("rta_details"),
        )


class FundTransaction(models.Model):
    external = models.BooleanField()
    remark = models.CharField(max_length=255)
    user_account_id = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=50)
    scheme_code = models.CharField(max_length=20)
    units = models.FloatField()
    folio_number = models.CharField(max_length=50)
    transaction_amount = models.DecimalField(decimal_places=5, max_digits=10, default=0)
    transaction_price = models.DecimalField(decimal_places=5, max_digits=10, default=0)
    transaction_type = models.CharField(max_length=50)
    transaction_status = models.CharField(max_length=50)
    transaction_time = models.DateTimeField()
    transaction_date = models.DateField()
    purchase_date = models.DateTimeField()
    hidden = models.BooleanField()
    transaction_source = models.CharField(max_length=50)
    transaction_sub_type = models.CharField(max_length=50)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fund_transactions",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = (("user_account_id", "transaction_id"),)

    @classmethod
    def create_from_dict(cls, data):
        transaction_time = datetime.strptime(
            data.get("transaction_time"), "%Y-%m-%dT%H:%M:%S"
        )
        transaction_date = datetime.strptime(
            data.get("transaction_date"), "%d %b %Y"
        ).date()
        purchase_date = datetime.strptime(
            data.get("purchase_date"), "%Y-%m-%dT%H:%M:%S"
        )

        return cls.objects.create(
            external=data.get("external", False),
            remark=data.get("remark", ""),
            user_account_id=data.get("user_account_id", ""),
            transaction_id=data.get("transaction_id", ""),
            scheme_code=data.get("scheme_code", ""),
            units=data.get("units", 0.0),
            folio_number=data.get("folio_number", ""),
            transaction_amount=data.get("transaction_amount", 0.0),
            transaction_price=data.get("transaction_price", 0.0),
            transaction_type=transaction_time,
            transaction_status=data.get("transaction_status", ""),
            transaction_time=data.get("transaction_time"),
            transaction_date=transaction_date,
            purchase_date=purchase_date,
            hidden=data.get("hidden", False),
            transaction_source=data.get("transaction_source", ""),
            transaction_sub_type=data.get("transaction_sub_type", ""),
        )


class SIPDetails(models.Model):
    has_active_sip = models.BooleanField()
    active_sip_count = models.IntegerField()


class FundInvestmentFolio(models.Model):
    folio_number = models.CharField(max_length=255)
    units = models.FloatField()
    amount_invested = models.FloatField()
    average_nav = models.FloatField()
    xirr = models.FloatField(null=True, blank=True)
    portfolio_source = models.CharField(max_length=255)
    folio_type = models.CharField(max_length=1)
    first_unrealised_purchase_date = models.DateField(null=True, blank=True)
    current_value = models.FloatField()
    sip_details = models.OneToOneField(SIPDetails, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="fund_investment_folios")


class FundInvestment(models.Model):
    fund = models.ForeignKey(
        Fund,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="investments",
    )
    avg_nav = models.DecimalField(
        blank=True, decimal_places=5, max_digits=10, null=True
    )
    units = models.DecimalField(decimal_places=5, max_digits=10, default=0)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount_invested = models.DecimalField(decimal_places=5, max_digits=10, default=0)
    folios = models.ManyToManyField(FundInvestmentFolio, blank=True, related_name="fund_investments")
    isin = models.CharField(max_length=100, null=True, blank=True)
    current_value = models.DecimalField(decimal_places=5, max_digits=10, default=0)
    xirr = models.CharField(max_length=100, null=True, blank=True)
    transactions = models.ManyToManyField(
        FundTransaction, related_name="fund_investments"
    )

    def __str__(self):
        return f""