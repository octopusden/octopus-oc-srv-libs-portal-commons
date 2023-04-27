""" Library module for listing artifacts groups """

import operator

from oc_cdtapi import NexusAPI
from oc_delivery_apps.checksums.models import LocTypes, CiTypes, CiRegExp, Locations, CiTypeGroups, CiTypeIncs
from django.db.models import Q
from packaging import version
from functools import reduce


def get_citype_artifacts(citype_code):
    """ Retrieves list of citype's artifacts

    :param citype_code: code of CiType
    :returns: QuerySet of Locations of given CiType
    """
    citype = CiTypes.objects.get(code=citype_code)
    listing = Locations.objects.filter(_get_citype_query(citype))
    return listing


def get_cigroup_artifacts(cigroup_code):
    """ Retrieves list of cigroup's artifacts

    :param citype_code: code of CiTypeGroup
    :returns: QuerySet of Locations of CiTypes belonging to given CiTypeGroup
    """
    cigroup = CiTypeGroups.objects.get(code=cigroup_code)
    group_citypes = CiTypeIncs.objects.filter(ci_type_group=cigroup).values_list("ci_type", flat=True)
    artifacts_query = _combine_querysets(map(_get_citype_query, group_citypes))
    return Locations.objects.filter(artifacts_query)


def append_release_notes_and_documentation(artifacts, citype, release_notes=True, documentation=True):
    """
    Append release_notes for artifacts if possible
    :param artifacts: list/QuerySet of Locations representing artifacts
    :param citype: CI_TYPE of the artifact
    :param release_notes: release notes should be appended
    :param documentation: documentation should be appended
    :return: completed by release notes list of artifacts
    """
    possible_rn_artifacts = '[^\.]+\.[^\.]+\.cdt\.ext\.release_notes:{}:[^:]+?:(txt|htm)'
    possible_doc_artifacts = '[^\.]+\.[^\.]+\.cdt\.ext\.documentation:{}-(russian|english):[^:]+?:zip'
    loctype = LocTypes.objects.get(code="NXS")
    try:
        citype_incs = CiTypeIncs.objects.get(ci_type__code=citype)
    except CiTypeIncs.DoesNotExist:
        return artifacts

    rn_artifact_id = citype_incs.ci_type_group.rn_artifactid or citype_incs.ci_type.rn_artifactid
    doc_artifact_id = citype_incs.ci_type_group.doc_artifactid or citype_incs.ci_type.doc_artifactid

    def get_rn_location(gav_regex):
        return Locations.objects.filter(loc_type=loctype, path__regex=gav_regex)

    def get_doc_location(gav_regex):
        return Locations.objects.filter(loc_type=loctype, path__regex=gav_regex)

    rn_gav_regex = possible_rn_artifacts.format(rn_artifact_id)
    doc_gav_regex = possible_doc_artifacts.format(doc_artifact_id)

    rn_locations = get_rn_location(rn_gav_regex)
    doc_locations = get_doc_location(doc_gav_regex)
    result = artifacts
    if release_notes and rn_locations.exists():
        result = result | rn_locations
    if documentation and doc_locations.exists():
        result = result | doc_locations

    return result


def order_artifacts(artifacts):
    """ Sorts artifacts by groupid, artifactid and classifier existence first, then by version (descending), then by classifier 

    :param artifacts: list/QuerySet of Locations representing artifacts
    :returns: sorted **list** of same Locations
    """

    # perform those sorts in opposite order
    parse_gav = lambda location: NexusAPI.parse_gav(location.path)
    sorted_by_classifier = sorted(artifacts, key=lambda item: parse_gav(item).get("c", ""))
    name_key = lambda gav: (gav["g"], gav["a"], len(gav))
    sorted_by_name = sorted(sorted_by_classifier, key=lambda location: name_key(parse_gav(location)))
    extract_version = lambda location: version.parse(parse_gav(location)["v"])
    sorted_by_version = sorted(sorted_by_name, reverse=True, key=extract_version)
    return sorted_by_version


def _get_artifacts_regexp_query(regexp):
    full_regex = regexp.regexp.replace("_VERSION_", "[^:]*")
    matching_path_query = Q(path__regex=full_regex)
    return matching_path_query


def _get_citype_query(citype):
    loctype = LocTypes.objects.get(code="NXS")
    citype_query = Q(loc_type=loctype, file__ci_type=citype)
    return citype_query


def _combine_querysets(querysets):
    """ Merges querysets by OR clauses """
    return reduce(operator.or_, querysets, Q(pk=None))
