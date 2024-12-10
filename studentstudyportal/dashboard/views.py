from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from django.views import generic
 # Ensure you import your Notes model
from . models import Notes
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'dashboard/home.html')  # Ensure you return the correct template


@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=form.cleaned_data['title'], description=form.cleaned_data['description'])
            notes.save()
            messages.success(request, f"Notes Added from {request.user.username} Successfully!")
    else:
        form = NotesForm()

    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)

@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model= Notes

@login_required
def homework(request):
    if request.method=='POST':
        form=HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished=request.Post['is_finished']
                if finished=='on':
                    finished=True
                else:
                    finished=False
            except:
                finished=False

            homeworks=Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished
            )
            homeworks.save()
            messages.success(request,f'Homework Added from {request.user.username}!!')
    else:
        form=HomeworkForm()
    homework=Homework.objects.filter(user=request.user)
    if len(homework)==0:
        homework_done=True
    else:
        homework_done=False
    
    context={'homeworks':homework,'homeworks_done':homework_done,'form':form}
    return render(request,'dashboard/homework.html',context)


@login_required
def update_homework(request,pk=None):
    homework=Homework.objects.get(id=pk)
    if homework.is_finished==True:
        homework.is_finished=False
    else:
        homework.is_finished=True
    homework.save()
    return redirect('homework')


@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


def youtube(request):
    if request.method=='POST':
        form =DashboardForm(request.POST)
        text=request.POST['text']
        video=VideosSearch(text,limit=10)
        result_list=[]
        for i in video.result()['result']:
            result_dict={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'viewcount':i['viewCount']['short'],
                'published':i['publishedTime'],
            }
            desc=''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc+=j['text']
            result_dict['description']=desc
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/youtube.html',context)
    else:
        form=DashboardForm()
    context={'form':form}
    return render(request,"dashboard/youtube.html",context)


@login_required
def todo(request):
    if request.method=='POST':
        form =TodoForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST["is_finished"]
                if finished=='on':
                    finished=True
                else:
                    finished=False
            except:
                finished=False
            todos=Todo(
                user=request.user,
                title=request.POST['title'],
                is_finished=finished

            )
            todos.save()
            messages.success(request,f"Todo Added from {request.user.username}!!")
    else:
        form=TodoForm()
    todo=Todo.objects.filter(user=request.user)
    if len(todo)==0:
        todos_done=True
    else:
        todos_done=False
    context={
        'form':form,
        'todos':todo,
        'todos_done':todos_done
    }
    return render(request,"dashboard/todo.html",context)


@login_required
def update_todo(request,pk=None):
    todo=Todo.objects.get(id=pk)
    if todo.is_finished ==True:
        todo.is_finished=False
    else:
        todo.is_finished=True
    todo.save()
    return redirect('todo')


@login_required
def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")

def books(request):
    import requests
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '')
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        try:
            r = requests.get(url)
            r.raise_for_status()
            answer = r.json()

            items = answer.get('items', [])
            result_list = []
            for i in range(min(10, len(items))):  # Limit to available items or 10
                volume_info = items[i].get('volumeInfo', {})
                image_links = volume_info.get('imageLinks', {})
                result_dict = {
                    'title': volume_info.get('title', 'No title available'),
                    'subtitle': volume_info.get('subtitle', 'No subtitle available'),
                    'description': volume_info.get('description', 'No description available'),
                    'count': volume_info.get('pageCount', 'No page count available'),
                    'categories': volume_info.get('categories', ['No categories available']),
                    'rating': volume_info.get('averageRating', 'No rating available'),
                    'thumbnail': image_links.get('thumbnail', 'No image available'),
                    'preview': volume_info.get('previewLink', 'No preview available'),
                }
                result_list.append(result_dict)

            context = {
                'form': form,
                'results': result_list
            }
            return render(request, 'dashboard/books.html', context)
        except requests.exceptions.RequestException as e:
            return render(request, 'dashboard/books.html', {
                'form': form,
                'error': f"An error occurred: {str(e)}"
            })
    else:
        form = DashboardForm()

    context = {'form': form}
    return render(request, "dashboard/books.html", context)


def dictionary(request):
    import requests
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '')
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/" + text
        try:
            r = requests.get(url)
            r.raise_for_status()  # Raise an error for non-200 responses
            answer = r.json()
            
            # Extracting data safely
            phonetics = answer[0].get('phonetics', [{}])[0].get('text', 'No phonetics available')
            audio = answer[0].get('phonetics', [{}])[0].get('audio', 'No audio available')
            definition = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('definition', 'No definition available')
            example = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('example', 'No example available')
            synonyms = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('synonyms', [])
            
            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except requests.exceptions.RequestException as e:
            context = {
                'form': form,
                'input': text,
                'error': f"API request failed: {str(e)}"
            }
        except (IndexError, KeyError):
            context = {
                'form': form,
                'input': text,
                'error': "The word could not be found or the API structure has changed."
            }
    else:
        form = DashboardForm()
        context = {'form': form}

    return render(request, "dashboard/dictionary.html", context)

def wiki(request):
    if request.method=='POST':
        text=request.POST['text']
        form=DashboardForm(request.POST)
        search=wikipedia.page(text)
        context={
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,"dashboard/wiki.html",context)
    else:

        form=DashboardForm()
        context={
            'form':form
        }
    return render(request,"dashboard/wiki.html",context)

def conversion(request):
    if request.method=='POST':
        form=ConversionForm(request.POST)
        if request.POST['measurement']=='length':
            measurement_form=ConversionLengthForm()
            context={
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer=''
                if input and int(input)>=0:
                    if first=='yard' and second=='foot':
                        answer=f'{input} yard={int(input)*3} foot'
                    if first=='foot' and second=='yard':
                        answer=f'{input} foot={int(input)/3} yard'
                context={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }
        
        if request.POST['measurement']=='mass':
            measurement_form=ConversionMassForm()
            context={
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first=request.POST['measure1']
                second=request.POST['measure2']
                input=request.POST['input']
                answer=''
                if input and int(input)>=0:
                    if first=='pound' and second=='kilogram':
                        answer=f'{input} pound={int(input)*0.453592} kilogram'
                    if first=='kilogram' and second=='pound':
                        answer=f'{input} kilogram={int(input)*2.20462} pound'
                context={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }
        

    else:        
        form=ConversionForm()
        context={
            'form':form,
            'input':False
        }
    return render(request,"dashboard/conversion.html",context)

def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f"Account Created for {username}!!")
            return redirect("login")
    else:
        form=UserRegistrationForm()
    context={
        'form':form
    }

    return render(request,"dashboard/register.html",context)


@login_required
def profile(request):
    homeworks=Homework.objects.filter(is_finished=False,user=request.user)
    todos=Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todos)==0:
        todos_done=True
    else:
        todos_done=False
    context={
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todos_done':todos_done
    }
    return render(request,"dashboard/profile.html",context)

