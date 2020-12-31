import hashlib
import random
from io import BytesIO

from PIL import Image, ImageFont
from PIL.ImageDraw import ImageDraw
from LibrarySystem import settings

from django.shortcuts import render, HttpResponse, redirect
from library.models import Student, Book, Borrow
# Create your views here.

def getHome(request):
    return render(request, "home.html")

def register(request):

        if request.method == 'GET':
            return render(request, 'register.html')

        else:

            received_code = request.POST.get('code')
            stored_code = request.session.get('verify_code')

            username = str(request.POST.get('username')).lower()

            if Student.objects.filter(username=username).exists():
                return render(request, 'register.html', {'msg': 'Username already exists, try another one'})

            if received_code != stored_code:
                return render(request, 'register.html', {'msg': 'Verify Code is wrong, try again.'})
            else:

                password = request.POST.get('password')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                studentID = request.POST.get('student_id')
                major = request.POST.get('major')
                gender = request.POST.get('gender')
                photo = request.FILES.get('photo')

                student = Student()
                student.first_name = first_name
                student.last_name = last_name
                student.studentID = studentID
                student.username = username
                student.password = password
                student.major = major
                student.gender = gender
                student.photo = photo
                student.save()

                # return render(request, 'login.html', {'success':'Account created. Please login.'})
                request.session['success'] = 'Account created. Please login.'

                response = redirect('/login')

                return response


def login(request):
    if request.method == 'GET':

        if request.session.has_key('success'):
            success = request.session['success']
            del request.session['success']
            return render(request, 'login.html', {'success':success})

        else:
            return render(request, 'login.html')

    else:
        username = str(request.POST.get('username')).lower()
        password = request.POST.get('password')

        try:
            student = Student.objects.get(username=username, password=password)

        except:
            return render(request, 'login.html', {'msg': "Username or password is incorrect, try again."})

        else:
            request.session['username'] = username
            response = redirect('/student/dashboard')
            # response.set_cookie('token', user.user_token)
            return response

def logout(request):
    if request.session.has_key('username'):
        del request.session['username']
    return redirect('/login')

def getCode(request):
    mode = 'RGB'
    size = (200,100)
    red = get_color()
    green = get_color()
    blue = get_color()
    color = (red,green,blue)
    image = Image.new(mode=mode, size=size, color=color)
    imagefont = ImageFont.truetype(settings.FONT_PATH,80)
    imageDraw = ImageDraw(image)

    verify_code = generate_code()
    request.session['verify_code'] = verify_code

    for i in range(4):
        fill = (get_color(),get_color(),get_color())
        imageDraw.text(xy=(50*i, 0), text=verify_code[i], font=imagefont,fill=fill)


    for i in range(200):
        fill = (get_color(),get_color(),get_color())
        xy = (random.randrange(201),random.randrange(101))
        imageDraw.point(xy=xy,fill=fill)


    fp = BytesIO()
    image.save(fp,'png')
    return HttpResponse(fp.getvalue(), content_type='image/png')

def get_color():
    return random.randrange(256)

def generate_code():
    source = 'qwrtyutiyuiopasdffghjghjlzxcbvvbnm132447686780IUHVOINJZWAE'
    code = ''
    for i in range(4):
        code += random.choice(source)

    return code

def dashboard(request):
    if request.session.has_key('username'):
        username = request.session['username']
        student = Student.objects.get(username=username)
        return render(request, 'student/dashboard.html', {'student': student})

    else:
        return redirect('/login')

def stu_booklist(request):
    booklist = Book.objects.all()
    return render(request,'student/booklist.html',{'booklist':booklist})

def stu_showbook(request, id):
    book = Book.objects.get(id=id)
    return render(request,'student/showbook.html',{'book':book})

