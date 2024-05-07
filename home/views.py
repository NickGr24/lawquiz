from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from .models import Discipline, Quiz, Question, Answer
from .forms import QuestionForm, AnswerForm, QuizForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse

def home(request):
    disciplines = Discipline.objects.all()
    return render(request, 'home.html', {'disciplines': disciplines})

@login_required
def quizzes_by_discipline(request, discipline_id):
    discipline = get_object_or_404(Discipline, id=discipline_id)
    quizzes = Quiz.objects.filter(discipline=discipline)
    context = {
            'discipline': discipline,
            'quizzes': quizzes,
            }
    return render(request, 'quizzes_by_discipline.html', context)

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    total_questions = questions.count()
    question_number = int(request.session.get('question_number', 1))
    
    if request.method == 'POST':
        # Обработка ответа пользователя
        selected_answer_id = request.POST.get('selected_answer_id')
        question = get_object_or_404(Question, id=request.POST.get('question_id'))
        correct_answer_id = question.answer_set.filter(correct=True).first().id
        
        # Проверяем, правильный ли был ответ и обновляем счет
        score = request.session.get('score', 0)
        if selected_answer_id == str(correct_answer_id):
            score += 1
        request.session['score'] = score

        # Переходим к следующему вопросу
        question_number += 1
        request.session['question_number'] = question_number

        # Проверяем, есть ли еще вопросы
        if question_number <= total_questions:
            # Перенаправляем пользователя на страницу следующего вопроса
            return redirect('take_quiz', quiz_id=quiz_id)
        else:
            # Если вопросы закончились, перенаправляем на страницу результатов
            percentage = (score / total_questions) * 100
            rounded_percentage = int(percentage)
            
            # Удаление данных из сессии
            del request.session['question_number']
            del request.session['score']

            return render(request, 'quiz_results.html', {'score': score, 'total_questions': total_questions, 'percentage': rounded_percentage})

    # Если пользователь уже прошел все вопросы, перенаправляем на страницу результатов
    if question_number > total_questions:
        return redirect('quiz_results', quiz_id=quiz_id)

    # Получаем текущий вопрос для отображения
    current_question = questions[question_number - 1]
    
    context = {
        'quiz': quiz,
        'current_question': current_question,
        'question_number': question_number,
        'total_questions': total_questions
    }

    return render(request, 'take_quiz.html', context)


@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    score = request.session.get('score', 0)
    total_questions = request.session.get('total_questions', 0)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    ques_number = request.session.get('question_number')
    if 'score' in request.session:
        del request.session['score']
    if 'total_questions' in request.session:
        del request.session['total_questions']
    print(total_questions)
    print(score)
    request.session['question_number'] = 1
    print(ques_number)
    
    context = {
            'quiz': quiz,
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage
    }
    return render(request, 'quiz_results.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Log in the user
                login(request, user)
                return redirect('home')  # Redirect to the home page after successful login
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