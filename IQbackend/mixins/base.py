import uuid
from django.db import models


class UUIDCreatedUpdatedMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, 
        editable=False
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        abstract = True