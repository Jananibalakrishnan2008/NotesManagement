from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'is_favorite', 'created_at', 'updated_at')
    list_filter = ('category', 'is_favorite', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)

