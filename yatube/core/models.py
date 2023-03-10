from django.db import models


class CreatedModel(models.Model):
    """Abstract model. Add create date."""
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True
