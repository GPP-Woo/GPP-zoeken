from django_filters.rest_framework import FilterSet, filters

from woo_search.search_index.constants import ResultTypeChoices, SortChoices


class SearchFilterSet(FilterSet):
    query = filters.CharFilter()
    page = filters.NumberFilter()
    page_size = filters.NumberFilter()
    sort = filters.ChoiceFilter(choices=SortChoices.choices)
    registratiedatum_vanaf = filters.DateTimeFilter()
    registratiedatum_tot = filters.DateTimeFilter()
    laatst_gewijzigd_datum_vanaf = filters.DateTimeFilter()
    laatst_gewijzigd_datum_tot = filters.DateTimeFilter()
    resultType = filters.ChoiceFilter(
        choices=ResultTypeChoices.choices,
    )
    informatie_categorieen = filters.CharFilter()
    publishers = filters.CharFilter()
