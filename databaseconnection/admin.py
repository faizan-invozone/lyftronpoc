from django.contrib import admin
from .models import DatabaseConnecion, Integration


@admin.register(DatabaseConnecion)
class DatabaseConnectionAdmin(admin.ModelAdmin):
    pass


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    pass
