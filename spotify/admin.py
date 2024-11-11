from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import SavedWrap

# Get the default User model
User = get_user_model()

# Register the SavedWrap model with custom admin
@admin.register(SavedWrap)
class SavedWrapAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_with_spotify_indicator', 'time_range_label', 'created_at')
    
    # Method to display the user name with "(Spotify)" indicator
    def user_with_spotify_indicator(self, obj):
        return f"{obj.user.username} (Spotify)"
    
    user_with_spotify_indicator.short_description = "User"

# Define a custom admin class for the User model
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email_with_spotify_indicator', 'username', 'first_name', 'last_name', 'is_staff')
    
    def email_with_spotify_indicator(self, obj):
        # Check if the user has at least one saved wrap
        if SavedWrap.objects.filter(user=obj).exists():
            return f"{obj.email} (Spotify)"
        return obj.email
    
    email_with_spotify_indicator.short_description = "Email"

# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
