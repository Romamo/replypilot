import requests
from bs4 import BeautifulSoup
from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter

from accounts.models import Account
from apps.detector import Detector
from apps.models import App


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = 'name', 'autogenerate', 'autoreview', 'state', 'account'
    # search_fields = ('name', 'id')
    readonly_fields_add = 'name', 'packageName', 'num_reviews', 'classify', 'limit_replies'
    readonly_fields_change = 'url', 'account', 'packageName', 'num_reviews', 'classify', 'limit_replies'
    list_filter = 'state', ('account', RelatedOnlyFieldListFilter),

    # def get_fieldsets(self, request, obj=None):
    #     if obj is None:
    #         return [(None, {"fields": ['url', 'account', 'keywords', 'state']})]
    #     return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return self.readonly_fields_change if obj else self.readonly_fields_add

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(account__user=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.packageName:
            m = Detector.parse(obj.url)
            response = requests.get(obj.url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # meta_tag = soup.find('meta', property='og:image')
                # if meta_tag:
                #     self.icon = meta_tag['content']
                meta_tag = soup.find('meta', property='og:title')
                if meta_tag:
                    obj.name = meta_tag['content'].split(' - ')[0]

            obj.packageName = m.id
        super().save_model(request, obj, form, change)

    # def get_object(self, request, object_id, from_field=None):
    #     return super(AppAdmin, self).get_object(request, object_id, from_field)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if request.user.is_superuser is False and db_field.name == 'account':
            kwargs['queryset'] = Account.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
