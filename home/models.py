from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Discipline(models.Model):
    name = models.CharField(max_length=50, verbose_name="Denumirea disciplinei")
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name
         
    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Discipline'
    
class Quiz(models.Model):
    title = models.CharField(max_length=100)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizuri'
        
class Question(models.Model):
    content = models.CharField(max_length=200, verbose_name="Întebarea")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name="Quiz'ul la care se referă")
    
    def __str__(self):
        return self.content
    
    def get_answers(self):
        return self.answer_set.all()
    
    class Meta:
        verbose_name = 'Întrebarea'
        verbose_name_plural = 'Întrebări'
    
class Answer(models.Model):
    content = models.CharField(max_length=600)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Întrebarea: {self.question.content}, Răspunsul: {self.content}, Corect: {self.correct}"
    
    class Meta:
        verbose_name = 'Răspuns'
        verbose_name_plural = 'Răspunsuri'
    
class Marks_Of_User(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.quiz)
    
    class Meta:
        verbose_name = 'Scorul'
        verbose_name_plural = 'Scoruri'
        unique_together = ['quiz', 'user']


class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Current: {self.current_streak} days"
    
    def update_streak(self):
        """Update user streak based on quiz completion"""
        today = timezone.now().date()
        
        if self.last_active_date is None:
            # First time activity
            self.current_streak = 1
            self.last_active_date = today
        elif self.last_active_date == today:
            # Already active today, no change
            return
        elif self.last_active_date == today - timezone.timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
            self.last_active_date = today
        else:
            # Streak broken
            self.current_streak = 1
            self.last_active_date = today
        
        # Update longest streak
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.save()
    
    class Meta:
        verbose_name = 'User Streak'
        verbose_name_plural = 'User Streaks'
