from oc_delivery_apps.checksums.models import CiTypeGroups, CiTypeIncs, CiTypes
from oc_delivery_apps.checksums.Component import Component


def resolve_search_components(code):
    """ Determines whether single CiType or whole CiTypeGroup was requested 

    :param code: CiType.code or CiTypeGroup.code 
    :returns: list of Component (one for CiType or multiple for CiTypeGroup)
    :raises: SearchError
    """
    try:
        group = CiTypeGroups.objects.get(code=code)
        components = [inclusion.ci_type
                            for inclusion in CiTypeIncs.objects.filter(ci_type_group=group)]
        components = list(map(lambda x: Component(x), components))
    except CiTypeGroups.DoesNotExist:
        try:
            components = [Component(CiTypes.objects.get(code=code)),]
        except (KeyError, CiTypes.DoesNotExist):  # wrong type - nothing can be found
            raise SearchError("Cannot resolve request code to search: " + code)
    return components


class SearchError(Exception):
    pass
