from typing import Any

import factory
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.test.factories import ServiceFactory as _ServiceFactory


class NestedPublisherFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    naam = factory.Faker("company")

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = dict


class NestedInformationCategoryFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    naam = factory.Faker("sentence", nb_words=3)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = dict


class NestedTopicFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    officiele_titel = factory.Faker("sentence", nb_words=3)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = dict


class IndexDocumentFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    publicatie = factory.Faker("uuid4", cast_to=str)
    publisher = factory.SubFactory(NestedPublisherFactory)
    identifiers = factory.LazyFunction(list)
    officiele_titel = factory.Faker("sentence", nb_words=6)
    verkorte_titel = factory.Faker("sentence", nb_words=3)
    omschrijving = factory.Faker("paragraph")
    creatiedatum = factory.Faker("past_date")
    # stay within the search query decay offset to avoid decay affecting the score
    registratiedatum = factory.Faker("past_datetime", start_date="-5d")
    gepubliceerd_op = factory.Faker("past_datetime", start_date="-5d")
    laatst_gewijzigd_datum = factory.Faker("past_datetime")
    # document fields
    download_url = ""
    file_size = None

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = dict

    @factory.post_generation
    def informatie_categorieen(
        self: dict[str, Any],  # pyright: ignore[reportGeneralTypeIssues]
        create,
        extracted,
        **kwargs,
    ):
        if extracted:
            self["informatie_categorieen"] = extracted
        else:
            size = kwargs.pop("size", 1)
            categories = NestedInformationCategoryFactory.create_batch(size, **kwargs)
            self["informatie_categorieen"] = categories

    @factory.post_generation
    def onderwerpen(
        self: dict[str, Any],  # pyright: ignore[reportGeneralTypeIssues]
        create,
        extracted,
        **kwargs,
    ):
        if extracted:
            self["onderwerpen"] = extracted
        else:
            self["onderwerpen"] = []


class IndexPublicationFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    identifiers = factory.LazyFunction(list)
    publisher = factory.SubFactory(NestedPublisherFactory)
    officiele_titel = factory.Faker("sentence", nb_words=6)
    verkorte_titel = factory.Faker("sentence", nb_words=3)
    omschrijving = factory.Faker("paragraph")
    # stay within the search query decay offset to avoid decay affecting the score
    registratiedatum = factory.Faker("past_datetime", start_date="-5d")
    gepubliceerd_op = factory.Faker("past_datetime", start_date="-5d")
    laatst_gewijzigd_datum = factory.Faker("past_datetime")
    datum_begin_geldigheid = factory.Faker("past_datetime")
    datum_einde_geldigheid = factory.Faker("past_datetime")

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = dict

    @factory.post_generation
    def informatie_categorieen(
        self: dict[str, Any],  # pyright: ignore[reportGeneralTypeIssues]
        create,
        extracted,
        **kwargs,
    ):
        if extracted:
            self["informatie_categorieen"] = extracted
        else:
            size = kwargs.pop("size", 1)
            categories = NestedInformationCategoryFactory.create_batch(size, **kwargs)
            self["informatie_categorieen"] = categories

    @factory.post_generation
    def onderwerpen(
        self: dict[str, Any],  # pyright: ignore[reportGeneralTypeIssues]
        create,
        extracted,
        **kwargs,
    ):
        if extracted:
            self["onderwerpen"] = extracted
        else:
            self["onderwerpen"] = []


class IndexTopicFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    officiele_titel = factory.Faker("sentence", nb_words=6)
    omschrijving = factory.Faker("paragraph")
    # stay within the search query decay offset to avoid decay affecting the score
    registratiedatum = factory.Faker("past_datetime", start_date="-5d")
    laatst_gewijzigd_datum = factory.Faker("past_datetime")

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = dict


class ServiceFactory(_ServiceFactory):
    class Params:  # type: ignore
        for_download_url_mock_service = factory.Trait(
            label="download-url-mock",
            api_root="http://localhost/",
            api_type=APITypes.orc,
            auth_type=AuthTypes.api_key,
            header_key="Authorization",
            header_value="Token insecure",
        )
