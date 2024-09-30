from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationForSecurity(PageNumberPagination):
    page_size = 500
