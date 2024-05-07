from django import forms
from .models import Quiz, Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quiz'].queryset = Quiz.objects.all()
        
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'discipline']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content', 'correct']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = 'Answer'
        self.fields['correct'].label = 'Is Correct Answer?'
