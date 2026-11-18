from django.contrib import admin
from .models import Skill, Review


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'exchange', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    list_select_related = ('owner',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('skill', 'author', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('skill__title', 'author__username', 'comment')
    list_select_related = ('skill', 'author')


admin.site.site_header = 'Campus SkillSwap Administration'
admin.site.site_title = 'Campus SkillSwap'
admin.site.index_title = 'Manage your campus community'
