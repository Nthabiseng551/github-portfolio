from django.shortcuts import render

from . import util
import markdown2
from markdown2 import Markdown

# markdown2.markdown(content)
def md_html(title):
    content = util.get_entry(title)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):

     if util.get_entry(title) == None:
        return render(request, "encyclopedia/error.html", {
            "message:" "The requested page not found"
        })

     return render(request,"encyclopedia/entry.html", {
         "title": title,
         "content": markdown2.markdown(util.get_entry(title))
    })

