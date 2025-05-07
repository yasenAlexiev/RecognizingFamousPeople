from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import FamousPerson

class FamousPersonAdminForm(forms.ModelForm):
    class Meta:
        model = FamousPerson
        fields = '__all__'
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }

@admin.register(FamousPerson)
class FamousPersonAdmin(admin.ModelAdmin):
    form = FamousPersonAdminForm
    list_display = ('name', 'difficulty', 'created_at', 'gender', 'skin_color', 'image_preview')
    list_filter = ('difficulty', 'gender', 'skin_color')
    search_fields = ('name',)
    ordering = ('name',)
    actions = ['delete_selected', 'edit_selected']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div style="position: relative;">'
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />'
                '<a href="{}" style="position: absolute; top: -10px; right: -10px; background: #ff4444; color: white; border-radius: 50%; width: 20px; height: 20px; text-align: center; line-height: 20px; text-decoration: none;">×</a>'
                '</div>',
                obj.image.url, f'/admin/members/famousperson/{obj.id}/change/'
            )
        return "No Image"
    image_preview.short_description = 'Image Preview'

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'difficulty', 'gender', 'skin_color')
        }),
        ('Image', {
            'fields': ('image',),
            'classes': ('wide',),
            'description': 'Upload a square image for best results. You can change the image by uploading a new one.'
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.image:
            form.base_fields['image'].help_text = format_html(
                '<div style="margin: 10px 0;">'
                '<strong>Current Image:</strong><br>'
                '<img src="{}" style="max-width: 200px; margin: 10px 0; border-radius: 5px;" /><br>'
                'To change the image, upload a new one below.'
                '</div>',
                obj.image.url
            )
        return form
