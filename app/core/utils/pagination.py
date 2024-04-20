from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        next_page_number = None
        previous_page_number = None

        if self.page.has_next():
            next_page_number = self.page.next_page_number()

        if self.page.has_previous():
            previous_page_number = self.page.previous_page_number()

        return Response({
            'next': next_page_number,
            'previous': previous_page_number,
            'count': self.page.paginator.count,
            'results': data
        })