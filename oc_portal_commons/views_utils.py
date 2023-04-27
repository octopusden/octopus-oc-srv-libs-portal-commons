from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import generic
from django.utils.safestring import mark_safe
from dlmanager.models import Delivery, JiraProjects, JiraInstances


from portal_commons.forms import DeliveryFormFilter

import re


def redirect_to_next(request):
    """ Redirects to 'next' parameter in GET/POST or index page if it's missing """
    return redirect(request.GET.get("next", request.POST.get("next", "dlmanager:index")))


def get_context_for_filter(request, initial_queryset):
    """ Builds part of context required to filter deliveries """
    delivery_filter = DeliveryFormFilter(request.GET, queryset=initial_queryset)
    context = {"filter": delivery_filter,
               "deliveries": delivery_filter.qs.all()}
    return context


class DetailsByGavView(generic.View):
    """ Redirects request by delivery gav to delivery details page """

    def get(self, request, **kwargs):
        try:
            g, a, v = [kwargs[key] for key in ['g', 'a', 'v']]
        except KeyError:
            return HttpResponseBadRequest("No GAV specified")
        try:
            delivery = Delivery.objects.get(groupid=g, artifactid=a, version=v)
        except ObjectDoesNotExist:
            raise Http404("Delivery not found")
        return HttpResponseRedirect("/dl/delivery_details/%d" % delivery.pk)


def find_jira_tickets(comment, ext=False):
    """
    Searching for JIRA's ticket ids in the provided commentary and transforming them into URLs

    :param comment: mf_delivery_comment property of Delivery model's object
    :param ext: is True if you call this method from ext_portal
    :returns: formatted commentary with JIRA tickets' urls
    """
    subbed_comment = re.sub(r'[^A-Z0-9-]', " ", comment)
    regex = re.compile(r"([A-Z]{1,10}-[0-9][0-9]{0,9})")
    ticket_number_regex = re.compile(r"[^\d ]+")
    for word in list(set(subbed_comment.split())):
        if regex.search(word):
            project = get_jira_projects(word)
            if project and not ticket_number_regex.search(word.split("-")[-1]):
                instance = get_jira_instance(project.instance_id_id)
                link_template = '<a href={0}/{1} target="_blank">{1}</a>'
                if not ext and instance.int_url_prefix:
                    comment = mark_safe(comment.replace(word, link_template.format(instance.int_url_prefix, word)))
                elif ext and instance.ext_url_prefix:
                    comment = mark_safe(comment.replace(word, link_template.format(instance.ext_url_prefix, word)))
    return comment


def get_jira_projects(ticket_id):
    """ Utility method to check if such project exists in JIRA

    :param ticket_id: JIRA ticket id obtained from the commentary
    :returns: A JIRA's project object
    """
    try:
        project = JiraProjects.objects.filter(code=ticket_id.split("-")[-2]).order_by("-instance_id__priority").first()
        return project
    except JiraProjects.DoesNotExist:
        pass


def get_jira_instance(instance_id):
    """ Utility method to retrieve jira instance information by its id

    :param instance_id: jiraprojects_instance_id_id value
    :returns: A JIRA's instance object
    """
    return JiraInstances.objects.get(id=instance_id)
