from django.contrib import admin
from .models import Quiz, Question, Answer, Marks_Of_User, Discipline

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Marks_Of_User)
admin.site.register(Discipline)