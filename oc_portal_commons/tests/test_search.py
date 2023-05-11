from datetime import datetime

from . import django_settings
import pytz
from oc_delivery_apps.checksums.models import CiRegExp, CiTypes, CiTypeGroups, LocTypes, CiTypeIncs
from oc_portal_commons import forms
import django
from django import test
from django.apps import apps
from oc_delivery_apps.dlmanager.models import Delivery
import oc_portal_commons.tests.dictionary as dd


class DeliverySearchTestCase(test.TestCase):

    def tearDown (self):
        django.core.management.call_command('flush', verbosity=0, interactive=False)


    def setUp(self):
        django.core.management.call_command('migrate', verbosity=0, interactive=False)
        self.all_deliveries = []
        dd.fill_dict(apps)
        # 0:
        self.add_delivery()
        # 1:
        self.add_delivery(a="TEST-1", v="0.0.1",
                          comment="weird comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:somedstr:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 2:
        self.add_delivery(a="TEST-2", v="0.0.2",
                          comment="specificcomment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:othdstr:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              "  "
                              ])
        # 3:
        self.add_delivery(a="TEST-3", v="0.0.3",
                          comment="",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 4:
        self.add_delivery(a="TEST-4", d="2022-06-06 12:00:00", da="person", v="0.0.4",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "something.sql",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 5:
        self.add_delivery(a="TEST_US-5", d="2022-06-12 12:00:00", da="person", v="0.0.5",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 6:
        self.add_delivery(a="BEST-6", da="person", v="0.0.6",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 7:
        self.add_delivery(a="BEST-7", da="person", v="0.0.7",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 8:
        self.add_delivery(a="TEST-YY-8", da="person", v="0.0.8",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 9:
        self.add_delivery(a="TEST-YY-9", da="person", v="0.0.9",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 10:
        self.add_delivery(a="TEST-10", da="person", v="0.1.0",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 11:
        self.add_delivery(a="TEST-11", da="person", v="0.1.1",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        return


    def add_delivery (self, 
                      g="com.example.app",
                      a="distribution", 
                      v="0.1.1", 
                      d="2023-01-01 00:00:00", 
                      da="author",
                      fl=["/tmp/tempfile", ], 
                      comment="", 
                      pk=None, 
                      is_approved=False, 
                      is_uploaded=False, 
                      is_failed=False
        ):
        creation_date = datetime.strptime(d, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)

        dlv = Delivery (groupid=g, 
                        artifactid=a, 
                        version=v, 
                        creation_date=creation_date,
                        mf_delivery_author=da, 
                        mf_delivery_files_specified="\n".join(fl), 
                        mf_delivery_comment=comment, 
                        pk=pk, 
                        flag_approved=is_approved, 
                        flag_uploaded=is_uploaded, 
                        flag_failed=is_failed
        )
        dlv.save()
        self.all_deliveries.append(dlv)
        return dlv


    def assert_filtered(self, expected_ids, filter_output):
        expected_deliveries = []
        for _id in expected_ids:
            expected_deliveries.append(self.all_deliveries[_id])
        # filter output may contain additional fields
        filtered_deliveries = Delivery.objects.filter(pk__in=filter_output.values_list("pk", flat=True))
        self.assertCountEqual(expected_deliveries, filtered_deliveries)

    def search_deliveries(self, **kwargs):
        filters = {}
        filter_args = ["project", "component_0", "component_1",
                       "date_range_after", "date_range_before", "created_by",
                       "comment", "is_failed", "is_approved", "is_uploaded"]
        if any([(item in filter_args) for item in kwargs.keys()]):
            filters.update({item: "" for item in filter_args})
            filters["component_0"] = "FILE"  # component_0 is always specified
        filters.update(kwargs)
        default_queryset = Delivery.objects.order_by('-creation_date')
        _filter = forms.DeliveryFormFilter(filters, queryset=default_queryset)
        return _filter.qs.all()

    def search_component_deliveries(self, component_code):
        filtered = self.search_deliveries(component_0=component_code,
                                          component_1="")
        return filtered


class GeneralSearchTestSuite(DeliverySearchTestCase):

    def test_not_fail_on_page_specified(self):
        filtered = self.search_deliveries(page="2")
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ], filtered)


class DeliveryNameSearchTestSuite(DeliverySearchTestCase):

    def test_no_filters_given(self):
        filtered = self.search_deliveries()
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], filtered)

    def test_empty_name_given(self):
        filtered = self.search_deliveries(project="")
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], filtered)

    def test_exact_name(self):
        filtered = self.search_deliveries(project="TEST-2")
        self.assert_filtered([2, ], filtered)

    def test_name_beginning(self):
        filtered = self.search_deliveries(project="TEST-1")
        self.assert_filtered([1, 10, 11 ], filtered)

    def test_part_of_delivery_name_found(self):
        filtered = self.search_deliveries(project="YY")
        self.assert_filtered([8, 9], filtered)

    def test_search_delivery_without_country(self):
        filtered = self.search_deliveries(project="TEST")
        self.assert_filtered([1, 2, 3, 4, 5, 8, 9, 10, 11 ], filtered)

    def test_bug_underscore_in_delivery_name(self):
        filtered = self.search_deliveries(project="US")
        self.assert_filtered([5, ], filtered)

    def test_fullname_search(self):
        Delivery.objects.all().delete()
        self.add_delivery(a="TEST-test", v="v20230101")  # 12
        self.add_delivery(a="TEST-test", v="v20230102")  # 13
        self.add_delivery(a="TEST-test", v="v20230203")  # 14
        filtered = self.search_deliveries(project="TEST-test-v202301")
        self.assert_filtered([12, 13], filtered)

    def test_delivery_version_search(self):
        Delivery.objects.all().delete()
        self.add_delivery(a="TEST-test", v="v20230101")  # 12
        self.add_delivery(a="TEST-test", v="v20230102")  # 13
        self.add_delivery(a="TEST-test", v="v20230203")  # 14
        filtered = self.search_deliveries(project="202301")
        self.assert_filtered([12, 13], filtered)


class DateSearchTestSuite(DeliverySearchTestCase):

    def test_wide_date_range(self):
        filtered = self.search_deliveries(date_range_after="01-01-2010",
                                          date_range_before="01-01-2030")
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ], filtered)


    def test_one_day_range(self):
        self.maxDiff = None   
        filtered = self.search_deliveries(date_range_after="06-06-2022",
                                          date_range_before="06-06-2022")
        self.assert_filtered([4 ], filtered)


    def test_month_range(self):
        self.maxDiff = None
        filtered = self.search_deliveries(date_range_after="01-06-2022",
                                          date_range_before="30-06-2022")
        self.assert_filtered([4, 5], filtered)


    def test_invalid_range(self):
        filtered = self.search_deliveries(date_range_after="01-12-2016",
                                          date_range_before="01-01-2015")
        self.assert_filtered([], filtered)


    def test_date_after_not_set(self):
        filtered = self.search_deliveries(date_range_before="01-12-2022")
        self.assert_filtered([4, 5 ], filtered)


    def test_date_before_not_set(self):
        filtered = self.search_deliveries(date_range_after="01-12-2022")
        self.assert_filtered([0, 1, 2, 3, 6, 7, 8, 9, 10, 11, ], filtered)


    def test_date_invalid_no_dashes(self):
        filtered = self.search_deliveries(date_range_after="01012010",
                                          date_range_before="01012030")
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ], filtered)


    def test_date_invalid_not_digits(self):
        self.maxDiff = None
        filtered = self.search_deliveries(date_range_after="01-JAN-2010",
                                          date_range_before="01-FEB-2030")
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ], filtered)


    def test_type_and_date_specified(self):
        filtered = self.search_deliveries(component_0="SQL",
                                          component_1="",
                                          date_range_after="01-01-2022",
                                          date_range_before="10-11-2022", )
        self.assert_filtered([4, ], filtered)


class AuthorSearchTestSuite(DeliverySearchTestCase):

    def test_created_by_beginning(self):
        filtered = self.search_deliveries(created_by="aut")
        self.assert_filtered([0, 1, 2, 3], filtered)

    def test_created_by_full(self):
        filtered = self.search_deliveries(created_by="author")
        self.assert_filtered([0, 1, 2, 3], filtered)

    def test_partial_created_by(self):
        filtered = self.search_deliveries(created_by="utho")
        self.assert_filtered([0, 1, 2, 3], filtered)


class CommentSearchTestSuite(DeliverySearchTestCase):

    def test_search_by_comment(self):
        self.maxDiff = None
        filtered = self.search_deliveries(comment="specificcomment")
        self.assert_filtered([2], filtered)

    def test_search_by_comment_with_space(self):
        self.maxDiff = None
        filtered = self.search_deliveries(comment="weird comment")
        self.assert_filtered([1], filtered)

    def test_search_by_empty_comment(self):
        self.maxDiff = None
        filtered = self.search_deliveries(comment="")
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], filtered)


class ContentSearchTestSuite(DeliverySearchTestCase):

    def test_svn_file_found(self):
        filtered = self.search_deliveries(component_0="SQL",
                                          component_1="something.sql")
        self.assert_filtered([4], filtered)

    def test_svn_file_beginning_found(self):
        filtered = self.search_deliveries(component_0="SQL",
                                          component_1="some")
        self.assert_filtered([4], filtered)

    def test_spaces_are_processed(self):
        filtered = self.search_deliveries(component_0="FILE",
                                          component_1="some file")
        self.assert_filtered([1, 2, 3, 5, 6, 7, 8, 9, 10, 11], filtered)

    def test_only_spaces_given(self):
        filtered = self.search_deliveries(component_0="FILE",
                                          component_1="  ")
        self.assert_filtered([2, ], filtered)


class ComponentSearchTestSuite(DeliverySearchTestCase):

    def test_all_sql_found(self):
        self.assert_filtered([4], self.search_component_deliveries("SQL"))

    def test_all_somedstr_found(self):
        self.maxDiff = None
        self.assert_filtered([1], self.search_component_deliveries("SOMEDSTR"))

    def test_all_othdstr_found(self):
        self.maxDiff = None
        self.assert_filtered([2], self.search_component_deliveries("OTHDSTR"))

    def test_missing_component_processed(self):
        self.assert_filtered([], self.search_component_deliveries("WRONG"))


class GroupSearchTestSuite(DeliverySearchTestCase):

    # no initial setup is needed
    def setUp(self):
        self.all_deliveries = []
        CiTypes(code="FILE", name="FILE").save()
        self.at_nexus, _ = LocTypes.objects.get_or_create(code="NXS", name="NXS")


    def test_empty_group_processed(self):
        CiTypeGroups(code="TEST", name="TEST").save()
        self.assert_filtered([], self.search_component_deliveries("TEST"))

    def test_group_without_regexps_processed(self):
        citype1, _ = CiTypes.objects.get_or_create(code="test1", name="test1")
        group, _ = CiTypeGroups.objects.get_or_create(code="TEST", name="TEST")
        CiTypeIncs(ci_type_group=group, ci_type=citype1).save()

        self.assert_filtered([], self.search_component_deliveries("TEST"))

    def test_group_components_found(self):
        citype1, _ = CiTypes.objects.get_or_create(code="test1", name="test1")
        citype2, _ = CiTypes.objects.get_or_create(code="test2", name="test2")
        citype3, _ = CiTypes.objects.get_or_create(code="test3", name="test3")
        CiRegExp(loc_type=self.at_nexus, ci_type=citype1, regexp="^a.+$").save()
        CiRegExp(loc_type=self.at_nexus, ci_type=citype2, regexp="^b.+$").save()
        CiRegExp(loc_type=self.at_nexus, ci_type=citype3, regexp="^c.+$").save()
        group, _ = CiTypeGroups.objects.get_or_create(code="TEST", name="TEST")
        CiTypeIncs(ci_type_group=group, ci_type=citype1).save()
        CiTypeIncs(ci_type_group=group, ci_type=citype2).save()
        self.add_delivery(a="0", fl=["a.b.c"], pk=0)
        self.add_delivery(a="1", fl=["b.b.c"], pk=1)
        self.add_delivery(a="2", fl=["c.b.c"], pk=2)
        self.assert_filtered([0, 1], self.search_component_deliveries("TEST"))

    def test_group_code_prevails_component(self):
        citype1, _ = CiTypes.objects.get_or_create(code="test1", name="test1")
        CiRegExp(loc_type=self.at_nexus, ci_type=citype1, regexp="^a.+$").save()
        group, _ = CiTypeGroups.objects.get_or_create(code="TEST", name="TEST")
        CiTypeIncs(ci_type_group=group, ci_type=citype1).save()

        citype2, _ = CiTypes.objects.get_or_create(code="TEST", name="TEST")
        CiRegExp(loc_type=self.at_nexus, ci_type=citype2, regexp="^b.+$").save()

        self.add_delivery(a="0", fl=["a.b.c"], pk=0)
        self.add_delivery(a="1", fl=["b.b.c"], pk=1)

        self.assert_filtered([0], self.search_component_deliveries("TEST"))

class StatusSearchTestSuite(DeliverySearchTestCase):

    def test_delivery_is_approved_search(self):
        Delivery.objects.all().delete()
        self.add_delivery(is_approved=True, v="v20010101")  # 12
        self.add_delivery(v="v20011111")  # 13
        self.add_delivery(is_approved=True, v="v20020202")  # 14
        filtered = self.search_deliveries(is_approved=True)
        self.assert_filtered([12, 14], filtered)

    def test_delivery_is_not_approved_search(self):
        self.add_delivery(is_approved=True, v="v20010101")  # 12
        self.add_delivery(v="v20011111")  # 13
        self.add_delivery(is_approved=True, v="v20020202")  # 14
        filtered = self.search_deliveries(is_approved=False)
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13], filtered)

    def test_delivery_is_uploaded_search(self):
        self.add_delivery(is_approved=True, is_uploaded=True, v="v20010101")  # 12
        self.add_delivery(v="v20011111")  # 13
        self.add_delivery(is_approved=True, v="v20020202")  # 14
        filtered = self.search_deliveries(is_uploaded=True)
        print(filtered)
        self.assert_filtered([12], filtered)

    def test_delivery_is_failed_search(self):
        self.add_delivery(is_approved=True, is_uploaded=True, v="v20010101")  # 12
        self.add_delivery(is_approved=True, is_uploaded=True, is_failed=True, v="v20011111")  # 13
        self.add_delivery(is_approved=True, v="v20020202")  # 14
        filtered = self.search_deliveries(is_failed=True)
        print(filtered)
        self.assert_filtered([13], filtered)
    


