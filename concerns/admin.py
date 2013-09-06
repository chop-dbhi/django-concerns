from django.contrib import admin
from concerns.models import Concern

class ConcernAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'reporter', 'status', 'resolved', 'created')


admin.site.register(Concern, ConcernAdmin)
