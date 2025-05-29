from rest_framework import filters


class NameSearchFilter(filters.SearchFilter):
    search_param = 'name'
