from django.contrib import admin
from django.contrib.admin import SimpleListFilter, RelatedOnlyFieldListFilter
from django.db.models import Q
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from reviews.models import Review


class ChangedFilter(SimpleListFilter):
    title = 'changed'
    parameter_name = 'changed'

    def lookups(self, request, model_admin):
        return (
            ('changed', 'Changed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'changed':
            return queryset.exclude(lastModifiedChanged__isnull=True)
        return queryset


class ThumbsFilter(SimpleListFilter):
    title = 'thumbs'
    parameter_name = 'thumbs'

    def lookups(self, request, model_admin):
        return (
            ('thumbs', 'With thumbs'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'thumbs':
            return queryset.filter(Q(thumbsUpCount__gt=0)|Q(thumbsDownCount__gt=0))
        return queryset


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['textCalculated',
                    # 'length',
                    'reply', 'reviewerLanguage', 'starRatingCalculated', 'thumbs', 'state',
                    'lastModified', 'replied', 'cost', 'reason']
    search_fields = 'uuid', 'text', 'originalText', 'reply', 'author'
    raw_id_fields = 'app',
    list_filter = 'state', ('app', RelatedOnlyFieldListFilter), ThumbsFilter, ChangedFilter, 'starRating', \
                  'reviewerLanguage'
    readonly_fields = 'originalText', 'uuid', 'app', 'author', 'text', 'lastModified', 'starRating', 'reviewerLanguage', \
                      'androidOsVersion', 'appVersionCode', 'appVersionName', 'device', 'reason', 'state', 'replied'
    fieldsets = (
        (None, {
            'fields': ('author', 'starRating', 'reviewerLanguage', 'text', 'reply', 'replied', 'state', 'reason')
        }),
        ('Advanced options', {
            # 'classes': ('collapse',),
            'fields': ('originalText', 'uuid', 'appVersionCode', 'appVersionName', 'device', 'androidOsVersion', 'app'),
        }),
    )
    actions = ['approve', 'review', 'clear']
    ordering = '-replied', '-lastModified'

    def length(self, review):
        return len(review.text)

    def get_list_display(self, request, obj=None):
        if request.user.is_superuser:
            return self.list_display + ['app']
        return self.list_display

    def clear(self, request, queryset):
        queryset.filter(state__in=[Review.State.NEW,
                                   Review.State.GENERATED,
                                   Review.State.READY,
                                   Review.State.COMPLETE,
                                   Review.State.ERROR])\
            .update(reply='', state=Review.State.NEW, reason='')
    clear.short_description = "Clear replies"

    def approve(self, request, queryset):
        queryset.filter(state=Review.State.NEW).update(state=Review.State.APPROVED)
    approve.short_description = "Mark to generate reply"

    def review(self, request, queryset):
        queryset.filter(state=Review.State.GENERATED).update(state=Review.State.READY)
    review.short_description = "Mark to send reply"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(app__account__user=request.user)

    def starRatingCalculated(self, review):
        if review.starRatingChanged:
            return f"{review.starRating} → {review.starRatingChanged}"
        return review.starRating
    starRatingCalculated.short_description = "Stars"

    def textCalculated(self, review):
        if review.textChanged:
            return mark_safe(f"{review.text}<br/>→<br/>{review.textChanged}")
        return review.text
    textCalculated.short_description = "Text"

    def thumbs(self, review):
        if review.thumbsUpCount or review.thumbsDownCount:
            return format_html(
                f'<div style="white-space:nowrap">{review.thumbsUpCount} 👍 {review.thumbsDownCount} 👎</div>'
            )
        return ''
    thumbs.short_description = "thumbs"
    thumbs.admin_order_field = 'thumbsUpCount'
