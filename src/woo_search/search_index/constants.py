from django.db import models
from django.utils.translation import gettext_lazy as _


class ResultTypeChoices(models.TextChoices):
    all = "*", _("All")
    publication = "publication", _("Publication")
    document = "document", _("Document")


class SortChoices(models.TextChoices):
    relevance = "relevance", _("Relevance")
    chronological = "chronological", _("Chronological")
