from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from .models import Discipline, Quiz, Question, Answer, Marks_Of_User
from .forms import QuestionForm, AnswerForm, QuizForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError

def home(request):
    disciplines = Discipline.objects.all()
    return render(request, 'home.html', {'disciplines': disciplines})


@login_required
def quizzes_by_discipline(request, discipline_id):
    discipline = get_object_or_404(Discipline, id=discipline_id)
    quizzes = Quiz.objects.filter(discipline=discipline)

    # Fetch the user's completed quizzes
    completed_quizzes = Marks_Of_User.objects.filter(user=request.user).values_list('quiz_id', flat=True)

    # Prepare quizzes with status
    quizzes_with_status = []
    for quiz in quizzes:
        status = "Пройден" if quiz.id in completed_quizzes else "Не пройден"
        quizzes_with_status.append({'quiz': quiz, 'status': status})
    print(f"Completed quizzes for user {request.user.id}: {completed_quizzes}")

    context = {
        'discipline': discipline,
        'quizzes_with_status': quizzes_with_status,
    }
    return render(request, 'quizzes_by_discipline.html', context)

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    total_questions = questions.count()

    # Initialize session data if it doesn't exist
    if 'question_number' not in request.session:
        request.session['question_number'] = 1
        request.session['user_answers'] = []
        request.session['score'] = 0

    question_number = request.session['question_number']

    # Handle POST request (answer submission)
    if request.method == 'POST':
        if question_number > total_questions:
            return redirect('quiz_results', quiz_id=quiz_id)  # Prevent redundant submission

        selected_answer_id = request.POST.get('selected_answer_id')
        current_question = questions[question_number - 1]
        correct_answer = current_question.answer_set.filter(correct=True).first()

        # Append or update user answers
        user_answers = request.session['user_answers']
        user_answers.append({
            'question_id': current_question.id,
            'selected': int(selected_answer_id) if selected_answer_id else None,
            'correct': correct_answer.id
        })
        request.session['user_answers'] = user_answers

        # Update score
        if selected_answer_id and int(selected_answer_id) == correct_answer.id:
            request.session['score'] += 1

        # Increment question number
        request.session['question_number'] += 1

        # Redirect to results page if quiz is completed
        if request.session['question_number'] > total_questions:
            return redirect('quiz_results', quiz_id=quiz_id)

        return redirect('take_quiz', quiz_id=quiz_id)

    # Handle GET request
    if question_number > total_questions:
        return redirect('quiz_results', quiz_id=quiz_id)

    current_question = questions[question_number - 1]

    # Debugging: Print session state
    print(f"Session Data during quiz: {dict(request.session.items())}")

    context = {
        'quiz': quiz,
        'current_question': current_question,
        'question_number': question_number,
        'total_questions': total_questions,
    }
    return render(request, 'take_quiz.html', context)



@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Check for session data
    user_answers = request.session.get('user_answers', [])
    score = request.session.get('score', 0)
    question_number = request.session.get('question_number', 0)

    if question_number <= 0 or not user_answers:
        return redirect('take_quiz', quiz_id=quiz_id)  # Redirect if session data is incomplete

    total_questions = len(user_answers)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0

    # Get all questions related to the quiz
    question_ids = [ans['question_id'] for ans in user_answers]
    questions = Question.objects.filter(id__in=question_ids)

    # Clear session data after completion
    request.session.pop('question_number', None)
    request.session.pop('user_answers', None)
    request.session.pop('score', None)

    context = {
        'quiz': quiz,
        'score': score,
        'total_questions': total_questions,
        'percentage': percentage,
        'questions': questions,
        'user_answers': user_answers,
    }
    return render(request, 'quiz_results.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  
    else:
        form = UserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home') 

@login_required
def get_quizzes(request):
    if request.method == 'POST' and request.is_ajax():
        discipline_id = request.POST.get('discipline_id')  # Получаем id выбранной дисциплины
        if discipline_id:
            # Получаем все квизы, относящиеся к выбранной дисциплине
            quizzes = Quiz.objects.filter(discipline_id=discipline_id)
            # Создаем список квизов в формате JSON
            quizzes_list = [{'id': quiz.id, 'title': quiz.title} for quiz in quizzes]
            return JsonResponse({'quizzes': quizzes_list})
        else:
            return JsonResponse({'error': 'Invalid discipline id'})
    else:
        return JsonResponse({'error': 'Invalid request'})
    
@login_required
def add_question(request):
    disciplines = Discipline.objects.all()
    form = QuestionForm()

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            discipline_id = form.cleaned_data['discipline']
            quiz_id = form.cleaned_data['quiz']
            question_text = form.cleaned_data['content']
            correct_answer_index = int(form.cleaned_data['correct_answer'])

            # Получаем объекты дисциплины и квиза
            discipline = get_object_or_404(Discipline, id=discipline_id)
            quiz = get_object_or_404(Quiz, id=quiz_id)

            # Создаем объект вопроса
            question = Question.objects.create(quiz=quiz, content=question_text)

            # Создаем объекты ответов
            for i in range(1, 6):
                answer_text = form.cleaned_data.get(f'answer{i}', None)
                if answer_text:
                    is_correct = (i == correct_answer_index)
                    Answer.objects.create(question=question, content=answer_text, correct=is_correct)

            return redirect('question_added_successfully')  # Перенаправляем на страницу успешного добавления

    return render(request, 'add_questions.html', {'form': form, 'disciplines': disciplines})