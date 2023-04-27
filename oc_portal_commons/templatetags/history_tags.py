""" Template tags used to display delivery history """

from django import template
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter
def get_changelog_external(delivery):
    return get_changelog(delivery, False)


@register.filter
def get_changelog_internal(delivery):
    return get_changelog(delivery, True)


def get_changelog(delivery, consider_tech_statuses):
    """ Computes changes between history entries

    :param delivery: delivery to analyze
    :param consider_tech_statuses: whether to account technical status changes too
    :returns: list of dictionaries with 'date', 'comment', 'author' and 'description' keys sorted by descending date
    """
    revisions = delivery.history.order_by("history_date")
    changelog = []
    last_status = None
    for revision in revisions:
        try:
            next_status = revision
            _check_business_status(next_status)
        except HistoryError:
            revision_info = get_revision_info(revision)
            revision_info["description"] = "Unknown status"
            changelog.append(revision_info)
            continue
        status_diffs = compare_with_previous(next_status, last_status, consider_tech_statuses)
        if status_diffs:
            revision_info = get_revision_info(revision)
            changelog.extend([dict(revision_info.items()
                                   | {"description": diff}.items())
                              for diff in status_diffs])
            last_status = next_status
    return reversed(changelog)


def get_revision_info(revision):
    """ Extracts comment information from revision """
    info = {"date": revision.history_date, "comment": revision.comment}
    try:
        info["author"] = User.objects.get(pk=revision.history_user_id).username
    except ObjectDoesNotExist:
        info["author"] = "-"
    return info


@register.filter
def get_flags_description(delivery):
    return delivery.get_flags_description()


def compare_with_previous(self_rev, other, consider_tech_status=True):
    # other may be none if first history entry is analyzed
    diffs = []
    # first check technical status change if needed
    if consider_tech_status and (not other or _get_flags(self_rev) != _get_flags(other)):
        # we can neither call get_flags_description on history entry directly
        # nor just do somethink like revision.delivery - there is no such attrubute
        matching_delivery = self_rev.history_object
        diffs.append(matching_delivery.get_flags_description())
    # then compare business statuses and comments (which only matter if tech status wasn't changed)
    if (not other or self_rev.business_status != other.business_status
            or (not diffs and self_rev.comment != other.comment)):
        if self_rev.business_status:
            diffs.append(self_rev.business_status.description)
    return diffs


def _get_flags(revision):
    return (revision.flag_approved, revision.flag_uploaded, revision.flag_failed)


def _check_business_status(revision):
    try:
        _ = revision.business_status  # access to field will cause Django to look up in db
    except ObjectDoesNotExist:
        raise HistoryError("Business status for revision %s was removed" % revision)


class HistoryError(Exception):
    pass
