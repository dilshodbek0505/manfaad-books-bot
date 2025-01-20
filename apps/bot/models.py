from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel

# Create your models here.
class BotAdmin(BaseModel):
    telegram_id = models.CharField(max_length=128, verbose_name=_("Telegram ID of the bot admin"))

    def __str__(self):
        return f"{self.telegram_id}"