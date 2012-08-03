from manager.models import Exercise, ExerciseComment, ExerciseCategory
from django.contrib import admin

class ExerciseCommentInline(admin.TabularInline): #admin.StackedInline
    model = ExerciseComment
    extra = 1

class ExerciseAdmin(admin.ModelAdmin):
    #fields = ['name',]
    
    inlines = [ExerciseCommentInline]


    
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(ExerciseCategory)