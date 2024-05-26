from datahub.models import GeneralInfo, Security


def get_general_info_obj():
    general_info = GeneralInfo.objects.last()
    return GeneralInfo() if general_info is None else general_info


def get_all_securities():
    return Security.objects.filter(security_info__tradingStatus="Active")