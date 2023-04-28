#! /usr/bin/python
""" Filelist search widgets and forms """

import django_filters
from oc_delivery_apps.checksums.models import CiTypeGroups, CiTypeIncs
from django import forms
from django.db.models import F, Value, CharField
from django.db.models import Q
from django.db.models.functions import Concat
from oc_delivery_apps.dlmanager import models
from oc_delivery_apps.checksums.Component import Component
from itertools import chain
from oc_portal_commons.search import resolve_search_components, SearchError


class ComponentWidget(forms.MultiWidget):
    """ Form widget for both component type and verson/path """

    def __init__(self, *args, **kwargs):
        searchable_components = _get_search_components(Component.get_all_components(),
                                                       CiTypeGroups.objects.all())
        dropdown_list = _order_search_components(searchable_components)
        widgets = [forms.Select(choices=dropdown_list,
                                attrs={"class": "component_type"}),
                   forms.TextInput(attrs={"class": "file_or_version"})]
        super(ComponentWidget, self).__init__(*args, widgets=widgets,
                                              **kwargs)

    def decompress(self, value):
        # space-separated value is expected
        if value:
            return value.split(' ', 1)
        else:
            return ["", ""]

    def value_from_datadict(self, data, files, name):
        component_type = data.get('component_0', "FILE")
        file_or_version = data.get('component_1', "")
        # "file" type without path means no filter set
        if component_type == "FILE" and not file_or_version:
            return ""
        ret = " ".join([component_type, file_or_version])
        return ret

    def format_output(self, rendered_widgets):
        return ' '.join(rendered_widgets)


def _order_search_components(choices):
    # case-insensitive sorting by readable component name except 'File' entry always first
    ordered = sorted(choices, key=lambda choice: choice[1].lower())
    file_entry = next((choice for choice in ordered if choice[0] == "FILE"), None)
    if file_entry:
        ordered.remove(file_entry)
        ordered.insert(0, file_entry)
    return ordered


def _get_search_components(components, groups):
    """ Builds searchable components list from groups and components which doesn't belong to group """
    groups_data = [(group.code, group.name) for group in groups]
    # part of components are included in groups, so they shouldn't be displayed 
    grouped_codes = [inclusion.ci_type.code for inclusion in
                     CiTypeIncs.objects.filter(ci_type_group__in=groups)]
    is_component_displayed = lambda comp: ((comp.short_name == 'FILE' or
                                            (isinstance(comp.stubs, list)
                                             and len(comp.stubs) > 0))
                                           and comp.short_name not in grouped_codes)
    components_data = [(obj_item.short_name, obj_item.full_name)
                       for obj_item in filter(is_component_displayed, components)]
    all_data = components_data + groups_data
    return all_data


class DeliveryFormFilter(django_filters.FilterSet):
    """ Form to search by delivery parameters """

    project = django_filters.CharFilter(method="process_delivery_name")
    created_by = django_filters.CharFilter(field_name="mf_delivery_author", lookup_expr="icontains")
    comment = django_filters.CharFilter(field_name="mf_delivery_comment", lookup_expr="icontains")
    component = django_filters.CharFilter(
        field_name="mf_delivery_files_specified",
        lookup_expr='icontains',
        widget=ComponentWidget,  # no instantiation because we need to dynamically load dropdown list
        method="process_component_info",
        strip=False)
    date_range = django_filters.DateFromToRangeFilter(field_name="creation_date")
    # default format uses slashes as delimiters
    # if format is "invalid" then nothing is returned
    # custom filter method is not called at all
    date_range.field.fields[0].input_formats = ["%d-%m-%Y"]
    date_range.field.fields[1].input_formats = ["%d-%m-%Y"]
    is_failed = django_filters.BooleanFilter(field_name='flag_failed')
    is_approved = django_filters.BooleanFilter(field_name='flag_approved')
    is_uploaded = django_filters.BooleanFilter(field_name='flag_uploaded')

    def process_delivery_name(self, queryset, name, value):
        """ Annotates delivery with standard delivery name (without packaging) """
        if not value:
            return queryset
        fullname_annotation = Concat(F("artifactid"), Value("-"), F("version"),
                                     output_field=CharField())
        # we should avoid conflict with Delivery.delivery_name property
        enhanced_qs = queryset.annotate(annotated_delivery_name=fullname_annotation)
        found_deliveries = enhanced_qs.filter(annotated_delivery_name__icontains=value)
        return found_deliveries

    def process_component_info(self, queryset, name, value):
        component_type, file_or_version = value.split(' ', 1)

        if component_type == "FILE":  # plain filename specified - find it in delivery lists
            if not file_or_version or len(file_or_version) == 0:  # skip any filtering
                return queryset
            return queryset.filter(mf_delivery_files_specified__icontains=file_or_version)
        else:  # look for artifactid:version using Component functionality
            version = file_or_version
            try:
                components = resolve_search_components(component_type)
                templates = list(chain(*[component.get_templates(version)
                                         for component in components]))
                combined_regex = '|'.join(templates)
                return queryset.filter(Q(mf_delivery_files_specified__iregex=combined_regex))
            except SearchError:
                return queryset.none()

    class Meta:
        model = models.Delivery
        fields = []
