from django.contrib import admin

# Register your models here.
from apps.books.models import Books,Books_population


admin.site.register(Books)
admin.site.register(Books_population)