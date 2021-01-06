from django.contrib import admin
from .models import SqlDialect, SourceDatatype, TargetDatatype, DatatypeMapping


@admin.register(SqlDialect)
class SqlDialectAdmin(admin.ModelAdmin):
    pass


@admin.register(SourceDatatype)
class SourceDatatypeAdmin(admin.ModelAdmin):
    pass


@admin.register(TargetDatatype)
class TargetDatatypeAdmin(admin.ModelAdmin):
    pass


@admin.register(DatatypeMapping)
class DatatypeMappingAdmin(admin.ModelAdmin):
    pass
