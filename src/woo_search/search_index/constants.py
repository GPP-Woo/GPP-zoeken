from django.db import models
from django.utils.translation import gettext_lazy as _

DOCUMENT_ATTACHMENT_PIPELINE_ID = "document_attachment"


class ResultTypeChoices(models.TextChoices):
    publication = "publication", _("Publication")
    document = "document", _("Document")
    topic = "topic", _("Topic")


class SortChoices(models.TextChoices):
    relevance = "relevance", _("Relevance")
    chronological = "chronological", _("Chronological")
