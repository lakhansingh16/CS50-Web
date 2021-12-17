from django.shortcuts import render,redirect
from random import randint
from . import util
from markdown2 import Markdown

#function to view index page
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

#function to open an entry
def showentry(request,entry):
    
    if util.get_entry(entry) == None:
        return render(request,"encyclopedia/error.html",{
            "error":"Entry does not exist",
            "Alternative":"Either create the entry,or search for an entry that exists.",
            "title":"File not found"
        })
    else:
        markdowner =Markdown()
        content = markdowner.convert(util.get_entry(entry.strip()))
        return render(request,"encyclopedia/entry.html",{
            "entry": content,
            "title":entry
        })


#function to search an entry from the existing entries
def search(request):
    title = request.GET.get('q').strip()
    if title in util.list_entries():
        return redirect("entry", entry=title)
    else:
        entries1 = []
        for entry in util.list_entries():
            if title.lower() in entry.lower():
                entries1.append(entry)

        return render(request,"encyclopedia/search.html",{
            "entry_list": entries1
        })


#function to add new entries
def add(request):
    if request.method == "GET":
        return render(request, "encyclopedia/add.html")
    else:
        title = request.POST.get('Pagetitle')
        content = request.POST.get('content')
        if title not in util.list_entries():
            util.save_entry(title,content)
            return redirect("entry", entry=title)
        else:
            return render(request,"encyclopedia/error.html",{
            "error":"Entry already exists",
            "Alternative":"Either change title, or create a different entry.",
            "title":"File already exists"
            })

#function to edit existing entry
def edit(request,title):
    content = util.get_entry(title.strip())
    if content == None:
        return render(request, "encyclopedia/error.html", {"error":"Entry does not exist",
            "Alternative":"Either create the entry,or search for an entry that exists.",
            "title":"File not found"
        })

    if request.method == "GET":
        return render(request,"encyclopedia/edit.html",{'title':title,
        'content':util.get_entry(title.strip())
        })
    else:
        content = request.POST.get("content")
        util.save_entry(title,content)
        return redirect("entry", title)


#function to view a random page
def random_page(request):
    entries = util.list_entries()
    end=len(entries)-1
    randomint = randint(0,end)
    return redirect("entry",entry=entries[randomint])

