from django.contrib import admin

from accounts.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'state']
    # search_fields = ('name', 'id')
    # raw_id_fields = 'user',
    readonly_fields = 'user',
    list_filter = 'state',

    # def get_fieldsets(self, request, obj=None):
    #     if obj is None:
    #         return super().get_fieldsets(request, obj)
    #     return (
    #     (None, {
    #         'fields': ('name', 'state')
    #     }),
    # )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return self.readonly_fields

    def get_list_display(self, request, obj=None):
        if request.user.is_superuser:
            return self.list_display + ['user']
        return self.list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)
