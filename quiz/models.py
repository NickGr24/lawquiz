from django.db import models

class Quiz(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        verbose_name_plural = "Quizzes"
        

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL)
    question_text = models.CharField(max_length=255)
    
    
class Answer(models.Model):
    
    