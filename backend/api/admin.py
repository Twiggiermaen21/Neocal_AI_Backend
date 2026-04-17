from django.contrib import admin
from django.utils import timezone
from .models import UserApproval


@admin.register(UserApproval)
class UserApprovalAdmin(admin.ModelAdmin):
    list_display = ("user", "username", "email", "email_confirmed", "is_active", "approved_by", "approved_at", "created_at")
    list_filter = ("email_confirmed", "user__is_active")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("approved_by", "approved_at", "created_at")
    actions = ("approve_users", "revoke_users")

    def username(self, obj):
        return obj.user.username

    def email(self, obj):
        return obj.user.email

    def is_active(self, obj):
        return obj.user.is_active
    is_active.boolean = True

    @admin.action(description="Zatwierdź wybranych użytkowników (aktywuj konto)")
    def approve_users(self, request, queryset):
        count = 0
        for approval in queryset.select_related("user"):
            if not approval.user.is_active:
                approval.user.is_active = True
                approval.user.save(update_fields=["is_active"])
                approval.approved_by = request.user
                approval.approved_at = timezone.now()
                approval.save(update_fields=["approved_by", "approved_at"])
                count += 1
        self.message_user(request, f"Zatwierdzono {count} użytkowników.")

    @admin.action(description="Cofnij aktywację wybranych użytkowników")
    def revoke_users(self, request, queryset):
        count = 0
        for approval in queryset.select_related("user"):
            if approval.user.is_active:
                approval.user.is_active = False
                approval.user.save(update_fields=["is_active"])
                approval.approved_by = None
                approval.approved_at = None
                approval.save(update_fields=["approved_by", "approved_at"])
                count += 1
        self.message_user(request, f"Cofnięto aktywację {count} użytkowników.")
