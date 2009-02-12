from django.http import HttpResponse, Http404

from pydelicious import DeliciousAPI


# Bookmarklet parameters
# URL - 
# Highlighted text -
# Course
# Username
# Continget - Deffo/Poss
# Week

# Return OK


def cook_select_resource (request, key):
    """Take the submitted resource and tag it in delicious using the users prerferences ready for the Baking step"""
    # This is in the framework template return HttpResponse(render_to_string(request, template_name, data),
    # Process request["url"]
    # res_url = request.REQUEST["resource_url"]
    res_url = request.REQUEST.get("resource_url")
    # res_txt = request.REQUEST["resource_text"]
    res_txt = request.REQUEST.get("resource_text")

    if res_txt is None:
      res_txt = "Untitled resource";

    if res_url is None:
      print "No URL given"
    else:
      # a = pydelicious.apiNew('ibbomashup', '**************')
      a = DeliciousAPI('ibbomashup', '**************')

      a.tags_get()
      print "Select the resource "+res_url+" notes text is "+res_txt
      a.posts_add(res_url, res_txt, tags="test", extended="text");
      # a.posts_add("http://my.com/", "title", extended="description", tags="my tags")

    return HttpResponse("fred.html")

