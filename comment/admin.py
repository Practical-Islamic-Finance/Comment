from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Exists, OuterRef

from comment.models import (
    Comment, Flag, FlagInstance, Reaction, ReactionInstance, Follower, BlockedUser, BlockedUserHistory
)


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'has_replies_boolean', 'posted', 'edited', 'user', 'email', 'view_content_object')
    search_fields = ('content',)

    def view_content_object(self, obj):
        content_object = obj.content_object
        if content_object:
            asset_name = getattr(content_object, 'name', 'No Name')

            # Determine the URL based on the asset_class name.
            asset_class_name = getattr(content_object, 'asset_class', None)
            if asset_class_name and asset_class_name.name.lower() == 'stock':
                object_url = reverse('stock_details', args=(content_object.ticker,))
            elif asset_class_name and asset_class_name.name.lower() == 'crypto':
                object_url = reverse('crypto_details', args=(content_object.slug,))
            else:
                return "Invalid asset type"

            # Return the link with the asset name
            return format_html('<a href="{}" target="_blank">{}</a>', object_url, asset_name)

        return "No associated asset"

    view_content_object.short_description = "View Asset"
    view_content_object.admin_order_field = 'object_id'

    def get_queryset(self, request):
        # Annotate the queryset with information about replies for sorting
        queryset = super().get_queryset(request)
        # This annotation checks for the existence of child comments
        queryset = queryset.annotate(has_replies_annotation=Exists(Comment.objects.filter(parent=OuterRef('pk'))))
        return queryset

    def has_replies(self, obj):
        if obj.parent is not None and obj.email == 'adelaboalanien@gmail.com':
            # Directly return the dash without setting .boolean = True
            return format_html('-')
        # Otherwise, perform the check and return True or False
        return Comment.objects.filter(parent=obj).exists()

    has_replies.short_description = 'Replied To'

    # Instead of setting .boolean = True globally, handle it in the method
    def has_replies_boolean(self, obj):
        result = self.has_replies(obj)
        if isinstance(result, bool):
            return result
        return None

    has_replies_boolean.boolean = True
    has_replies_boolean.short_description = 'Replied To'

    # Use the new annotation for sorting in the admin
    has_replies_boolean.admin_order_field = 'has_replies_annotation'

    class Meta:
        model = Comment


class InlineReactionInstance(admin.TabularInline):
    model = ReactionInstance
    extra = 0
    readonly_fields = ['user', 'reaction', 'reaction_type', 'date_reacted']


class ReactionModelAdmin(admin.ModelAdmin):
    list_display = ('comment', 'likes', 'dislikes')
    readonly_fields = list_display
    search_fields = ('comment__content',)
    inlines = [InlineReactionInstance]


class InlineFlagInstance(admin.TabularInline):
    model = FlagInstance
    extra = 0
    readonly_fields = ['user', 'flag', 'reason', 'info', 'date_flagged']


class FlagModelAdmin(admin.ModelAdmin):
    list_display = ('comment', 'moderator', 'state', 'count', 'comment_author')
    readonly_fields = list_display
    search_fields = ('comment__content',)
    inlines = [InlineFlagInstance]


class FollowerModelAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'content_type', 'content_object')
    readonly_fields = list_display
    search_fields = ('email',)


class BlockedUserModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'blocked')
    search_fields = ('user__username', 'email')


class BlockedUserHistoryModelAdmin(admin.ModelAdmin):
    list_display = ('blocked_user', 'blocker', 'reason', 'state', 'date')
    search_fields = (
        'blocked_user__user__username', 'blocked_user__email', 'blocker__username', 'blocker__email', 'state', 'date'
    )


admin.site.register(Comment, CommentModelAdmin)
admin.site.register(Reaction, ReactionModelAdmin)
admin.site.register(Flag, FlagModelAdmin)
admin.site.register(Follower, FollowerModelAdmin)
admin.site.register(BlockedUser, BlockedUserModelAdmin)
admin.site.register(BlockedUserHistory, BlockedUserHistoryModelAdmin)
