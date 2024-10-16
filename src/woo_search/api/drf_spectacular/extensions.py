from drf_spectacular.contrib.django_filters import DjangoFilterExtension

from woo_search.api.utils import underscore_to_camel


class CamelizeFilterExtension(DjangoFilterExtension):
    priority = 1

    def get_schema_operation_parameters(
        self, auto_schema, *args, **kwargs
    ):  # pragma: no cover
        """
        camelize query parameters
        """
        parameters = super().get_schema_operation_parameters(
            auto_schema, *args, **kwargs
        )
        for parameter in parameters:
            parameter["name"] = underscore_to_camel(parameter["name"])
        return parameters
