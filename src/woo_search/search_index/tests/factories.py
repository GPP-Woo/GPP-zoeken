import factory


class PublisherFactory(factory.Factory):
    uuid = factory.Faker("uuid4", cast_to=str)
    naam = factory.Faker("company")

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
    creatiedatum = factory.Faker(
        "past_date",
    )
    registratiedatum = factory.Faker("past_datetime")
    laatst_gewijzigd_datum = factory.Faker("past_datetime")

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = dict
