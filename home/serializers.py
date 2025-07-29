from rest_framework import serializers
from .models import Discipline, Quiz, Question, Answer, Marks_Of_User
from django.contrib.auth.models import User


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'content', 'correct']


class AnswerWithoutCorrectSerializer(serializers.ModelSerializer):
    """Serializer for answers without revealing the correct flag (for quizzes)"""
    class Meta:
        model = Answer
        fields = ['id', 'content']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(source='answer_set', many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'content', 'quiz', 'answers']


class QuestionWithoutCorrectSerializer(serializers.ModelSerializer):
    """Serializer for questions without revealing correct answers (for taking quizzes)"""
    answers = AnswerWithoutCorrectSerializer(source='answer_set', many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'content', 'answers']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(source='question_set', many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'discipline', 'slug', 'questions', 'question_count']
    
    def get_question_count(self, obj):
        return obj.question_set.count()


class QuizListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing quizzes without questions"""
    question_count = serializers.SerializerMethodField()
    user_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'discipline', 'slug', 'question_count', 'user_score']
    
    def get_question_count(self, obj):
        return obj.question_set.count()
    
    def get_user_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                mark = Marks_Of_User.objects.get(quiz=obj, user=request.user)
                return mark.score
            except Marks_Of_User.DoesNotExist:
                return None
        return None


class QuizTakeSerializer(serializers.ModelSerializer):
    """Serializer for taking a quiz (without correct answers)"""
    questions = QuestionWithoutCorrectSerializer(source='question_set', many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'questions', 'question_count']
    
    def get_question_count(self, obj):
        return obj.question_set.count()


class DisciplineSerializer(serializers.ModelSerializer):
    quizzes = QuizListSerializer(source='quiz_set', many=True, read_only=True)
    quiz_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Discipline
        fields = ['id', 'name', 'slug', 'quizzes', 'quiz_count']
    
    def get_quiz_count(self, obj):
        return obj.quiz_set.count()


class DisciplineListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing disciplines without quizzes"""
    quiz_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Discipline
        fields = ['id', 'name', 'slug', 'quiz_count']
    
    def get_quiz_count(self, obj):
        return obj.quiz_set.count()


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for quiz submission"""
    answers = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Dictionary with question_id as key and answer_id as value"
    )


class UserScoreSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    discipline_name = serializers.CharField(source='quiz.discipline.name', read_only=True)
    
    class Meta:
        model = Marks_Of_User
        fields = ['id', 'quiz', 'quiz_title', 'discipline_name', 'score']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']