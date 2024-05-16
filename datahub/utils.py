from datahub.models import GeneralInfo


def get_general_info_obj():
    general_info = GeneralInfo.objects.last()
    return GeneralInfo() if general_info is None else general_info
