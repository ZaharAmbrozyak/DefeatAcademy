from django.shortcuts import render

from .models import Course, Test

# Create your views here.
def index(request):
    return render(request, 'academy/index.html')

def courses(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'academy/courses.html', context)

def course(request, course_id):
    course = Course.objects.get(id=course_id)
    tests  = course.test_set.all()
    context = {'course': course, 'tests': tests}
    return render(request, 'academy/course.html', context)

def test(request, course_id, test_id):
    test = Test.objects.get(id=test_id, course__id=course_id)

    context = {'test': test}

    return render(request, 'academy/test.html', context)