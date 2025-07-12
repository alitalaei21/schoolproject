from django.contrib import admin

# Register your models here.
# courses/admin.py

from django.contrib import admin
from .models import Course, Section, Video

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1

class SectionInline(admin.StackedInline):
    model = Section
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'is_vip_only', 'student_count']
    inlines = [SectionInline]

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    inlines = [VideoInline]

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'order']
