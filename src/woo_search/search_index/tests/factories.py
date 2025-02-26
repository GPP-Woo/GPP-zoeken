from typing import Any

import factory


class PublisherFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    naam = factory.Faker("company")

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = dict


class InformationCategoryFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    naam = factory.Faker("sentence", nb_words=3)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = dict


class IndexDocumentFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    publicatie = factory.Faker("uuid4", cast_to=str)
    publisher = factory.SubFactory(PublisherFactory)
    identifier = factory.Sequence(lambda n: f"identifier-{n}")
    officiele_titel = factory.Faker("sentence", nb_words=6)
    verkorte_titel = factory.Faker("sentence", nb_words=3)
    omschrijving = factory.Faker("paragraph")
    creatiedatum = factory.Faker("past_date")
    # stay within the search query decay offset to avoid decay affecting the score
    registratiedatum = factory.Faker("past_datetime", start_date="-5d")
    laatst_gewijzigd_datum = factory.Faker("past_datetime")

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
            categories = InformationCategoryFactory.create_batch(size, **kwargs)
            self["informatie_categorieen"] = categories


class IndexPublicationFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    publisher = factory.SubFactory(PublisherFactory)
    officiele_titel = factory.Faker("sentence", nb_words=6)
    verkorte_titel = factory.Faker("sentence", nb_words=3)
    omschrijving = factory.Faker("paragraph")
    # stay within the search query decay offset to avoid decay affecting the score
    registratiedatum = factory.Faker("past_datetime", start_date="-5d")
    laatst_gewijzigd_datum = factory.Faker("past_datetime")

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
            categories = InformationCategoryFactory.create_batch(size, **kwargs)
            self["informatie_categorieen"] = categories
