from django import template

""" Common template tags used on both portals """

from pkg_resources import get_distribution

register = template.Library()

@register.simple_tag
def cache_reset_suffix():
    """ Appends suffix to static file requests to force browsers to update cache. Suffix includes package version so with every release browsers receive new statics """
    statics_suffix = get_distribution("oc_portal_commons").version
    suffix = "STATICS_VERSION=%s" % statics_suffix
    return suffix


@register.filter
def get_delivery_messages(delivery, all_messages):
    """ Filters messages related to specific delivery based on message tags """
    is_for_delivery = lambda msg: ("delivery_%d" % delivery.id) in (msg.extra_tags or "")
    return list (filter(is_for_delivery, all_messages) )


@register.filter
def get_general_messages(all_messages):
    """ Filters messages not related to specific delivery """
    not_for_delivery = lambda msg: "delivery_" not in (msg.extra_tags or "")
    return list (filter(not_for_delivery, all_messages) )
