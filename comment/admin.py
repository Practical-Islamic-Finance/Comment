from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from comment.models import (
    Comment, Flag, FlagInstance, Reaction, ReactionInstance, Follower, BlockedUser, BlockedUserHistory
)


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'posted', 'edited', 'content_type', 'user', 'email', 'urlhash', 'view_content_object')
    search_fields = ('content',)

    def view_content_object(self, obj):
        # Get the admin URL for the content object associated with this comment
        content_type = obj.content_type
        content_object = obj.content_object
        if content_object:
            if content_type.model == 'stock':
                # Here 'stock' should be the model name of your Stock model
                object_url = reverse('stock_details', args=(content_object.ticker,))
            elif content_type.model == 'crypto':
                # And 'crypto' should be the model name of your Crypto model
                object_url = reverse('crypto_details', args=(content_object.slug,))
            else:
                return "Invalid asset type"

            return format_html('<a href="{}" target="_blank">View Asset</a>', object_url)
        return "No associated asset"

    view_content_object.short_description = "View Asset"

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
        'blocked_user__user__username', 'blocked_user__email', 'blocker__username', 'blocker__email', 'state',  'date'
    )


admin.site.register(Comment, CommentModelAdmin)
admin.site.register(Reaction, ReactionModelAdmin)
admin.site.register(Flag, FlagModelAdmin)
admin.site.register(Follower, FollowerModelAdmin)
admin.site.register(BlockedUser, BlockedUserModelAdmin)
admin.site.register(BlockedUserHistory, BlockedUserHistoryModelAdmin)
