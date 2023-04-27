from django.shortcuts import render_to_response
from django.template import RequestContext


def http404(request):
    response = render_to_response('dl/404.html', context_instance=RequestContext(request))
    response.status_code = 404
    return response


def http500(request):
    response = render_to_response('dl/500.html', context_instance=RequestContext(request))
    response.status_code = 500
    return response
