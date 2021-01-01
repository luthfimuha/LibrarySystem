
import random
from io import BytesIO

from PIL import Image, ImageFont
from PIL.ImageDraw import ImageDraw
from LibrarySystem import settings

import pandas as pd
from datetime import date, timedelta

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel

from django.db import connection
from django.core.paginator import Paginator

from django.db.models import Count

from django.shortcuts import render, HttpResponse, redirect
from library.models import Student, Book, Borrow
# Create your views here.

def getHome(request):
    return render(request, "home.html")

def register(request):

    if request.method == 'GET':
        return render(request, 'student/register.html')

    else:

        received_code = request.POST.get('code')
        stored_code = request.session.get('verify_code')

        username = str(request.POST.get('username')).lower()

        if Student.objects.filter(username=username).exists():
            return render(request, 'student/register.html', {'msg': 'Username already exists, try another one'})

        if received_code != stored_code:
            return render(request, 'student/register.html', {'msg': 'Verify Code is wrong, try again.'})
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
            return render(request, 'student/login.html', {'success':success})

        else:
            return render(request, 'student/login.html')

    else:
        username = str(request.POST.get('username')).lower()
        password = request.POST.get('password')

        try:
            student = Student.objects.get(username=username, password=password)

        except:
            return render(request, 'student/login.html', {'msg': "Username or password is incorrect, try again."})

        else:
            request.session['username'] = username
            response = redirect('/student/dashboard')
            return response

def logout(request):
    if request.session.has_key('username'):
        del request.session['username']
    return redirect('/')

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
        book_loans = Borrow.objects.filter(student=student)
        total_loan = book_loans.count()
        unreturned = book_loans.filter(status="Not returned").count()

        return render(request, 'student/dashboard.html', {'student': student, 'total_loan':total_loan, 'unreturned':unreturned})


    else:
        return redirect('/login')

def stu_booklist(request):
    username = request.session['username']
    student = Student.objects.get(username=username)
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword', "")
    if keyword != "":
        books = Book.objects.filter(name__icontains=keyword)
    else:
        books = Book.objects.all()
    paginator = Paginator(books,10)
    booklist = paginator.page(page)
    return render(request,'student/booklist.html',{'booklist':booklist, 'student':student})

def stu_borrow(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        username = request.session['username']

        book = Book.objects.get(id=book_id)
        student = Student.objects.get(username=username)

        book.stock = book.stock - 1
        book.save()

        today = date.today()
        borrowed_date = today.strftime("%Y-%m-%d")

        next_week = date.today() + timedelta(days=7)

        due_date = next_week.strftime("%Y-%m-%d")

        borrow = Borrow()
        borrow.borrowed_date = borrowed_date
        borrow.due_date = due_date
        borrow.book = book
        borrow.student = student
        borrow.status = 'Not returned'
        borrow.save()

    return redirect('/student/booklist')

def stu_return(request):
    if request.method == 'POST':
        borrow_id = request.POST.get('borrow_id')
        borrow = Borrow.objects.get(id=borrow_id)

        borrow.status = 'Returned'
        borrow.book.stock = borrow.book.stock + 1
        borrow.book.save()

        borrow.save()

        return redirect('/student/history')



def stu_showbook(request):

    username = request.session['username']
    student = Student.objects.get(username=username)
    id = request.GET.get('id')
    book = Book.objects.get(id=id)

    query = str(Book.objects.all().query)
    bookrec = pd.read_sql_query(query, connection)
    tfv = TfidfVectorizer(min_df=0, max_features=None,
                          strip_accents='unicode', analyzer='word',
                          ngram_range=(1, 3), stop_words='english')

    # Filling NaNs with empty string
    bookrec['desc'] = bookrec['desc'].fillna('')
    # Filling the TF IDF on the 'description'
    tfv_matrix = tfv.fit_transform(bookrec['desc'])
    cosine_sim = sigmoid_kernel(tfv_matrix, tfv_matrix)
    # Reverse mapping of indices and book titles
    indices = pd.Series(bookrec.index, index=bookrec['id']).drop_duplicates()

    def recommendation(id, cosine_sim=cosine_sim):
        bid = []
        bname = []
        bdesc = []
        bauth = []
        bpd = []
        btype = []
        bstock = []

        # Get the index corresponding to the book name
        idx = indices[id]

        # Get the pairwise similarity scores
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the books
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Scores of the 3 most similar books
        sim_scores = sim_scores[1:4]

        # Book indices
        book_indices = [i[0] for i in sim_scores]

        for ind in book_indices:
            bid.append(list(bookrec.id)[ind])
            bname.append(list(bookrec.name)[ind])
            bdesc.append(list(bookrec.desc)[ind])
            bauth.append(list(bookrec.author)[ind])
            bpd.append(list(bookrec.pub_date)[ind])
            btype.append(list(bookrec.type)[ind])
            bstock.append(list(bookrec.stock)[ind])

        return bid

    recommendation(book.id)

    similarbooks = []

    for id in recommendation(book.id):
        similarbooks.append(Book.objects.get(id=id))

    return render(request,'student/showbook.html',{'book':book, 'similarbooks':similarbooks, 'student':student})


def stu_history(request):
    username = request.session['username']
    student = Student.objects.get(username=username)
    borrowlist = Borrow.objects.filter(student=student)

    return render(request,'student/history.html',{'borrowlist':borrowlist,'student':student})


def admin_login(request):
    return render(request, 'admin/admin_login.html')

def admin_logout(request):
    if request.session.has_key('admin'):
        del request.session['admin']

    return redirect('/')


def admin_dashboard(request):
    # Chart 1, Book By Category

    chart1_label = []
    chart1_data = []
    book_types = Book.objects.values('type').distinct()
    for type in book_types:
        chart1_label.append(type['type'])

    for label in chart1_label:
        chart1_data.append(Book.objects.filter(type=label).count())

    # Chart 2, Top 3 Most Loaned Book

    top3_books = Book.objects.annotate(num_loan=Count('borrow')).order_by('-num_loan')[:3]

    # Chart 3, Number of Loan by Day

    chart3_label = []
    chart3_data = []

    loan_dates = Borrow.objects.values('borrowed_date').distinct()

    for date in loan_dates:
        chart3_label.append(str(date['borrowed_date']))

    for label in chart3_label:
        chart3_data.append(Borrow.objects.filter(borrowed_date=label).count())

    print(loan_dates)
    print(chart3_label)
    print(chart3_data)

    context = {
        'chart1_label': chart1_label,
        'chart1_data': chart1_data,
        'top3_books': top3_books,
        'chart3_label': chart3_label,
        'chart3_data': chart3_data,
    }

    if request.session.has_key('admin'):

        return render(request, 'admin/dashboard.html', context=context)



    else:
        if request.method == 'POST':
            username = str(request.POST.get('username')).lower()
            password = request.POST.get('password')

            if username == 'admin' and password == 'admin':
                request.session['admin'] = 'Ok'
                return render(request, 'admin/dashboard.html',context=context)

            else:
                return render(request, 'admin/admin_login.html',
                              {'msg': "Username or password is incorrect, try again."})

        else:
            return redirect('/admin/login')

def admin_booklist(request):
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword',"")
    if keyword != "":
        books = Book.objects.filter(name__icontains=keyword)
    else:
        books = Book.objects.all()
    paginator = Paginator(books, 10)
    booklist = paginator.page(page)
    return render(request,'admin/booklist.html',{'booklist':booklist})

def admin_studentlist(request):
    studentlist = Student.objects.all()
    return render(request, 'admin/studentlist.html', {'studentlist': studentlist})

def admin_borrowlist(request):
    borrowlist = Borrow.objects.all()
    return render(request,'admin/borrowlist.html',{'borrowlist':borrowlist})

def admin_updatebook(request):
    if request.method == 'GET':
        book_id = request.GET.get('id')
        book = Book.objects.get(id=book_id)
        return render(request,'admin/updatebook.html', {'book':book})

def admin_addbook(request):
    if request.method == 'GET':
        return render(request, 'admin/addbook.html')
    else:

        book = Book()
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        author = request.POST.get('author')
        pub_date = request.POST.get('pub_date')
        type = request.POST.get('type')
        stock = request.POST.get('stock')
        cover = request.FILES.get('cover')

        book.name = name
        book.desc = desc
        book.author = author
        book.pub_date = pub_date
        book.type = type
        book.stock = stock
        book.cover = cover
        book.save()

        return redirect('/admin/booklist')


def admin_saveupdate(request):
    if request.method == "POST":
        id = request.POST.get('id')
        book = Book.objects.get(id=id)

        name = request.POST.get('name')
        desc = request.POST.get('desc')
        author = request.POST.get('author')
        pub_date = request.POST.get('pub_date')
        type = request.POST.get('type')
        stock = request.POST.get('stock')
        cover = request.FILES.get('cover')


        book.name = name
        book.desc = desc
        book.author = author
        if pub_date != "":
            book.pub_date = pub_date
        book.type = type
        book.stock = stock

        if cover != None:
            book.cover = cover

        book.save()

        return redirect('/admin/booklist')













