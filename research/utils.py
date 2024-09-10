from datahub.models import Security


def calculate_eps(security_id):
    """
    EPS - Earning per share
    :param security_id:
    :return:
    """
    security = Security.objects.get(id=security_id)
