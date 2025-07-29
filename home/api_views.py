from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Discipline, Quiz, Question, Answer, Marks_Of_User, UserStreak
from .serializers import (
    DisciplineSerializer, DisciplineListSerializer, DisciplineRoadmapSerializer,
    QuizSerializer, QuizListSerializer, QuizTakeSerializer,
    QuestionSerializer, AnswerSerializer,
    QuizSubmissionSerializer, UserScoreSerializer,
    UserProfileSerializer, UserStreakSerializer
)


class DisciplineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Discipline.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DisciplineListSerializer
        return DisciplineSerializer
    
    @action(detail=True, methods=['get'])
    def quizzes(self, request, pk=None):
        """Get all quizzes for a specific discipline"""
        discipline = self.get_object()
        quizzes = Quiz.objects.filter(discipline=discipline)
        serializer = QuizListSerializer(quizzes, many=True, context={'request': request})
        return Response(serializer.data)


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        elif self.action == 'take':
            return QuizTakeSerializer
        return QuizSerializer
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def take(self, request, pk=None):
        """Get quiz questions without revealing correct answers"""
        quiz = self.get_object()
        serializer = QuizTakeSerializer(quiz)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        """Submit quiz answers and calculate score"""
        quiz = self.get_object()
        submission_serializer = QuizSubmissionSerializer(data=request.data)
        
        if not submission_serializer.is_valid():
            return Response(
                submission_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        answers_data = submission_serializer.validated_data['answers']
        
        # Calculate score
        total_questions = quiz.question_set.count()
        if total_questions == 0:
            return Response(
                {'error': 'Quiz has no questions'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        correct_answers = 0
        results = []
        
        for question in quiz.question_set.all():
            question_id = str(question.id)
            user_answer_id = answers_data.get(question_id)
            
            if user_answer_id:
                try:
                    user_answer = Answer.objects.get(
                        id=user_answer_id, 
                        question=question
                    )
                    is_correct = user_answer.correct
                    if is_correct:
                        correct_answers += 1
                    
                    # Get the correct answer for response
                    correct_answer = Answer.objects.get(
                        question=question, 
                        correct=True
                    )
                    
                    results.append({
                        'question_id': question.id,
                        'question': question.content,
                        'user_answer_id': user_answer_id,
                        'user_answer': user_answer.content,
                        'correct_answer_id': correct_answer.id,
                        'correct_answer': correct_answer.content,
                        'is_correct': is_correct
                    })
                    
                except Answer.DoesNotExist:
                    results.append({
                        'question_id': question.id,
                        'question': question.content,
                        'user_answer_id': user_answer_id,
                        'user_answer': 'Invalid answer',
                        'is_correct': False,
                        'error': 'Invalid answer selected'
                    })
            else:
                # Question not answered
                correct_answer = Answer.objects.get(
                    question=question, 
                    correct=True
                )
                results.append({
                    'question_id': question.id,
                    'question': question.content,
                    'user_answer_id': None,
                    'user_answer': 'Not answered',
                    'correct_answer_id': correct_answer.id,
                    'correct_answer': correct_answer.content,
                    'is_correct': False
                })
        
        # Calculate percentage score
        score_percentage = (correct_answers / total_questions) * 100
        
        # Save or update user score and update streak
        with transaction.atomic():
            marks, created = Marks_Of_User.objects.update_or_create(
                quiz=quiz,
                user=request.user,
                defaults={'score': score_percentage}
            )
            
            # Update user streak
            streak, created = UserStreak.objects.get_or_create(user=request.user)
            streak.update_streak()
        
        return Response({
            'score': score_percentage,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'results': results,
            'passed': score_percentage >= 70  # You can adjust the passing score
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_scores(self, request):
        """Get current user's quiz scores"""
        scores = Marks_Of_User.objects.filter(user=request.user)
        serializer = UserScoreSerializer(scores, many=True)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminUser]  # Only admins can access full questions with answers


class AnswerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAdminUser]  # Only admins can access full answers


# User Profile endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user's profile information"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


# Roadmap endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def discipline_roadmap(request, discipline_id):
    """Get user's progress roadmap for a specific discipline"""
    try:
        discipline = Discipline.objects.get(id=discipline_id)
    except Discipline.DoesNotExist:
        return Response(
            {'error': 'Discipline not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = DisciplineRoadmapSerializer(discipline, context={'request': request})
    return Response(serializer.data)


# Streak endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_streak(request):
    """Get current user's streak information"""
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    serializer = UserStreakSerializer(streak)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_streak(request):
    """Manually update user's streak (for daily check-ins)"""
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    streak.update_streak()
    serializer = UserStreakSerializer(streak)
    return Response(serializer.data)