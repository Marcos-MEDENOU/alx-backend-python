from django.contrib import admin
from django.utils.html import format_html
from .models import Message, Notification, MessageHistory


class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    extra = 0
    readonly_fields = ('edited_at', 'content')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_edited', 'is_read')
    list_filter = ('is_read', 'is_edited', 'timestamp')
    search_fields = ('content', 'sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'
    list_select_related = ('sender', 'receiver')
    inlines = [MessageHistoryInline]
    readonly_fields = ('timestamp', 'edited_at', 'is_edited')
    fieldsets = (
        (None, {
            'fields': ('sender', 'receiver', 'content')
        }),
        ('Status', {
            'fields': ('is_read', 'is_edited', 'timestamp', 'edited_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'receiver')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message__content')
    date_hierarchy = 'created_at'
    list_select_related = ('user', 'message')

    def message_preview(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            obj.message.get_absolute_url(),
            f"Message from {obj.message.sender} ({obj.message.timestamp})"
        )
    message_preview.short_description = 'Message'


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'edited_at', 'content_preview')
    list_filter = ('edited_at',)
    search_fields = ('message__content', 'content')
    date_hierarchy = 'edited_at'
    readonly_fields = ('message', 'content', 'edited_at')

    def content_preview(self, obj):
        return f"{obj.content[:50]}..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
