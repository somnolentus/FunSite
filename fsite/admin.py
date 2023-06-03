from django.contrib import admin
from .models import Advertisment, Category, Subscriber, Comment, Profile
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.
admin.site.register(Category)
admin.site.register(Subscriber)
admin.site.register(Comment)
admin.site.register(Profile)


class AdvertismentAdmin(SummernoteModelAdmin):
    summernote_fields = ('body',)


admin.site.register(Advertisment, AdvertismentAdmin)
