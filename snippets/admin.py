from django.contrib import admin
from .models import Snippet, AuditRecord


class SnippetAdmin(admin.ModelAdmin):
    readonly_fields = ("highlighted",)


class AuditRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_name', 'object_id', 'action', 'timestamp')
    list_filter = ('action', 'model_name')
    search_fields = ('user__username', 'model_name', 'object_id')


admin.site.register(Snippet, SnippetAdmin)
admin.site.register(AuditRecord, AuditRecordAdmin)
