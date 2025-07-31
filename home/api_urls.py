from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .api_views import (
    DisciplineViewSet,
    QuizViewSet,
    QuestionViewSet,
    AnswerViewSet,
    UserProgressViewSet,
    user_profile,
    discipline_roadmap,
    user_streak,
    update_streak,
)

# Create DRF router
router = DefaultRouter()
router.register(r'disciplines', DisciplineViewSet, basename='discipline')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'answers', AnswerViewSet, basename='answer')
router.register(r'user-progress', UserProgressViewSet, basename='user-progress')

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User endpoints
    path('me/', user_profile, name='user_profile'),
    
    # Roadmap endpoint
    path('roadmap/<int:discipline_id>/', discipline_roadmap, name='discipline_roadmap'),
    
    # Streak endpoints
    path('streak/', user_streak, name='user_streak'),
    path('streak/update/', update_streak, name='update_streak'),
    
    # API endpoints
    path('', include(router.urls)),
]