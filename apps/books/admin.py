from django.contrib import admin

# Register your models here.
from apps.books.models import Books


admin.site.register(Books)