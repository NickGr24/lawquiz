from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz
from datetime import datetime, timedelta

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
    score = models.FloatField()  # Score as decimal (e.g., 0.85 for 85%)
    completed = models.BooleanField(default=False)  # True if score >= 70%
    completed_at = models.DateTimeField(auto_now_add=True)  # Changed to auto_now_add for creation time
    updated_at = models.DateTimeField(auto_now=True)  # Track when the record was last updated
    
    def save(self, *args, **kwargs):
        # Automatically set completed status based on score (70% threshold)
        self.completed = self.score >= 70.0
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}%"
    
    class Meta:
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
        unique_together = ['quiz', 'user']
        ordering = ['-completed_at']


class UserProfile(models.Model):
    """Extended user profile to store timezone and other preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    timezone = models.CharField(
        max_length=50, 
        default='UTC',
        help_text="User's timezone (e.g., 'America/New_York', 'Europe/London')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.timezone}"
    
    def get_user_timezone(self):
        """Get timezone object for this user"""
        try:
            return pytz.timezone(self.timezone)
        except pytz.UnknownTimeZoneError:
            return pytz.UTC
    
    def get_user_today(self):
        """Get today's date in user's timezone"""
        user_tz = self.get_user_timezone()
        return timezone.now().astimezone(user_tz).date()
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create user profile with default timezone"""
        profile, created = cls.objects.get_or_create(
            user=user,
            defaults={'timezone': 'UTC'}
        )
        return profile
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Current: {self.current_streak} days"
    
    def update_streak(self, user_timezone=None):
        """
        Update user streak based on quiz completion with timezone awareness
        
        Args:
            user_timezone: Optional timezone to use. If None, will get from user profile
        """
        # Get user's timezone-aware today
        if user_timezone:
            user_tz = user_timezone
        else:
            try:
                profile = UserProfile.objects.get(user=self.user)
                user_tz = profile.get_user_timezone()
            except UserProfile.DoesNotExist:
                # Create profile with default timezone
                profile = UserProfile.get_or_create_for_user(self.user)
                user_tz = profile.get_user_timezone()
        
        # Get today in user's timezone
        user_now = timezone.now().astimezone(user_tz)
        today = user_now.date()
        
        if self.last_active_date is None:
            # First time activity
            self.current_streak = 1
            self.last_active_date = today
        elif self.last_active_date == today:
            # Already active today, no change needed
            return False  # Return False to indicate no update was made
        elif self.last_active_date == today - timedelta(days=1):
            # Consecutive day - increment streak
            self.current_streak += 1
            self.last_active_date = today
        else:
            # Streak broken - reset to 1
            self.current_streak = 1
            self.last_active_date = today
        
        # Update longest streak if necessary
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.save()
        return True  # Return True to indicate streak was updated
    
    @classmethod
    def update_streak_for_user(cls, user, user_timezone=None):
        """
        Class method to update streak for a user, creating the streak object if it doesn't exist
        
        Args:
            user: User object
            user_timezone: Optional timezone to use
            
        Returns:
            tuple: (UserStreak object, bool indicating if streak was updated)
        """
        streak, created = cls.objects.get_or_create(user=user)
        
        if created:
            # New streak object, this counts as first activity
            updated = streak.update_streak(user_timezone)
            return streak, True
        else:
            # Existing streak, update if needed
            updated = streak.update_streak(user_timezone)
            return streak, updated
    
    class Meta:
        verbose_name = 'User Streak'
        verbose_name_plural = 'User Streaks'
