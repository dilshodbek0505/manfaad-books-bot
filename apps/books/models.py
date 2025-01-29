from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from apps.common.models import BaseModel


def validate_mp3(value):
    formats=[".mp3",".aac",".ogg",".flac",".alac",".wav",".aiff",".dsd",".pcm",".m4a",".ape",".wv",".raw",".oga",".mogg",".mmf",".movpkg",".m4p",".m4b",".aa"]
    if not any(value.name.lower().endswith(i) for i in formats):
        raise ValidationError('Only MP3 files are allowed.')
    
def validate_pdf(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError('Only PDF files are allowed.')

class Books(models.Model):
    author_name = models.CharField(max_length=128, verbose_name=("Author full name"))
    name = models.CharField(max_length=248, verbose_name=("Book name"))
    desc = models.TextField(verbose_name=("Books description"), null=True,blank=True)
    audio = models.FileField(upload_to='files/audios/',verbose_name='Audio book',validators=[validate_mp3])
    book = models.FileField(upload_to='files/books/',verbose_name='book',validators=[validate_pdf])

    def __str__(self):
        return f"{self.author_name} | {self.name}"
    

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")


class Books_population(models.Model):
    telegram_id = models.BigIntegerField(verbose_name='Telegram user id')
    book = models.ForeignKey(Books ,on_delete=models.deletion.CASCADE, related_name='related_entries', verbose_name='Book_id')

    def __str__(self):
        return f"{self.telegram_id} | {self.book.name}"
    

    class Meta:
        verbose_name = _("Book_population")
        verbose_name_plural = _("Books_population")
