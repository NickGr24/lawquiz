from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db import transaction, models

from .models import Discipline, Quiz, Question, Answer, Marks_Of_User, UserStreak, UserProfile
from .serializers import (
    DisciplineSerializer, DisciplineListSerializer, DisciplineRoadmapSerializer,
    QuizSerializer, QuizListSerializer, QuizTakeSerializer,
    QuestionSerializer, AnswerSerializer,
    QuizSubmissionSerializer, UserScoreSerializer,
    UserDetailSerializer, UserStreakSerializer, UserProfileSerializer,
    UserProgressSerializer, UserProgressCreateSerializer
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
            
            # Update user streak with timezone awareness
            # Get user's timezone from request headers or profile
            user_timezone_str = request.headers.get('X-User-Timezone')
            user_timezone = None
            
            if user_timezone_str:
                try:
                    import pytz
                    user_timezone = pytz.timezone(user_timezone_str)
                    # Also update user profile if different
                    profile = UserProfile.get_or_create_for_user(request.user)
                    if profile.timezone != user_timezone_str:
                        profile.timezone = user_timezone_str
                        profile.save()
                except Exception:
                    user_timezone = None
            
            # Update streak using the class method
            streak, streak_updated = UserStreak.update_streak_for_user(
                request.user, 
                user_timezone
            )
        
        return Response({
            'score': score_percentage,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'results': results,
            'passed': score_percentage >= 70,  # You can adjust the passing score
            'streak_info': {
                'current_streak': streak.current_streak,
                'longest_streak': streak.longest_streak,
                'streak_updated': streak_updated,
                'last_active_date': streak.last_active_date.isoformat() if streak.last_active_date else None
            }
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


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user quiz progress.
    Allows users to save and retrieve their quiz progress.
    """
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only return progress for the authenticated user"""
        return Marks_Of_User.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return UserProgressCreateSerializer
        return UserProgressSerializer
    
    def perform_create(self, serializer):
        """Ensure the progress is saved for the authenticated user"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Ensure user can only update their own progress"""
        if serializer.instance.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update your own progress.")
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get user's progress summary"""
        progress_records = self.get_queryset()
        total_completed = progress_records.filter(completed=True).count()
        total_attempted = progress_records.count()
        
        # Calculate overall average score
        scores = progress_records.values_list('score', flat=True)
        average_score = round(sum(scores) / len(scores), 2) if scores else 0
        
        # Get discipline breakdown
        from django.db.models import Count, Avg
        discipline_stats = (
            progress_records
            .values('quiz__discipline__name', 'quiz__discipline__id')
            .annotate(
                total_quizzes=Count('id'),
                completed_quizzes=Count('id', filter=models.Q(completed=True)),
                avg_score=Avg('score')
            )
            .order_by('quiz__discipline__name')
        )
        
        return Response({
            'total_quizzes_attempted': total_attempted,
            'total_quizzes_completed': total_completed,
            'overall_average_score': average_score,
            'completion_percentage': round((total_completed / total_attempted * 100), 2) if total_attempted > 0 else 0,
            'discipline_breakdown': list(discipline_stats)
        })
    
    @action(detail=False, methods=['get'])
    def by_discipline(self, request, discipline_id=None):
        """Get user's progress for a specific discipline"""
        discipline_id = request.query_params.get('discipline_id')
        if not discipline_id:
            return Response(
                {'error': 'discipline_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            discipline_id = int(discipline_id)
        except ValueError:
            return Response(
                {'error': 'discipline_id must be a valid integer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        progress_records = self.get_queryset().filter(quiz__discipline__id=discipline_id)
        serializer = self.get_serializer(progress_records, many=True)
        return Response(serializer.data)


# User Profile endpoint
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update current user's profile information"""
    if request.method == 'GET':
        # Ensure user has a profile
        UserProfile.get_or_create_for_user(request.user)
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        # Update user timezone or other profile info
        profile = UserProfile.get_or_create_for_user(request.user)
        
        # Handle timezone update
        timezone_data = request.data.get('timezone')
        if timezone_data:
            try:
                import pytz
                # Validate timezone
                pytz.timezone(timezone_data)
                profile.timezone = timezone_data
                profile.save()
            except pytz.UnknownTimeZoneError:
                return Response(
                    {'error': 'Invalid timezone provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Return updated profile
        serializer = UserDetailSerializer(request.user)
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
    """Get current user's streak information with timezone awareness"""
    # Get or create user profile for timezone info
    profile = UserProfile.get_or_create_for_user(request.user)
    
    # Get or create streak
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    
    # Get today in user's timezone for additional info
    user_today = profile.get_user_today()
    
    serializer = UserStreakSerializer(streak)
    data = serializer.data
    
    # Add timezone-aware information
    data.update({
        'user_timezone': profile.timezone,
        'user_today': user_today.isoformat(),
        'quiz_completed_today': streak.last_active_date == user_today if streak.last_active_date else False
    })
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_streak(request):
    """Manually update user's streak (for daily check-ins) with timezone support"""
    # Get user's timezone from request or profile
    user_timezone_str = request.data.get('timezone') or request.headers.get('X-User-Timezone')
    user_timezone = None
    
    if user_timezone_str:
        try:
            import pytz
            user_timezone = pytz.timezone(user_timezone_str)
            # Update user profile if different
            profile = UserProfile.get_or_create_for_user(request.user)
            if profile.timezone != user_timezone_str:
                profile.timezone = user_timezone_str
                profile.save()
        except Exception:
            user_timezone = None
    
    # Update streak using the enhanced class method
    streak, streak_updated = UserStreak.update_streak_for_user(request.user, user_timezone)
    
    serializer = UserStreakSerializer(streak)
    data = serializer.data
    data['streak_updated'] = streak_updated
    
    return Response(data)