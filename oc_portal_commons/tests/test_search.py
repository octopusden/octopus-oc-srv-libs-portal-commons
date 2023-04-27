from datetime import datetime

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
        self.add_delivery(a="TEST-1", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 2:
        self.add_delivery(a="TEST-2", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 3:
        self.add_delivery(a="TEST-3", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 4:
        self.add_delivery(a="TEST-4", d="2022-06-06 12:00:00", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 5:
        self.add_delivery(a="TEST_US-5", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 6:
        self.add_delivery(a="BEST-6", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 7:
        self.add_delivery(a="BEST-7", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 8:
        self.add_delivery(a="TEST-YY-8", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 9:
        self.add_delivery(a="TEST-YY-9", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 10:
        self.add_delivery(a="TEST-10", da="person",
                          comment="test comment",
                          fl=["/tmp/work/data",
                              "some file with spaces",
                              "com.example.app:distribution:2.2.2:zip",
                              "com.example.app.branches-int.apps:distribution:2.6.684-22:war",
                              "com.example.app:distribution:1.0.93:war",
                              ])
        # 11:
        self.add_delivery(a="TEST-11", da="person",
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
        for id in expected_ids:
            expected_deliveries.append(self.all_deliveries[id])
        # filter output may contain additional fields
        filtered_deliveries = Delivery.objects.filter(pk__in=filter_output.values_list("pk", flat=True))
        self.assertCountEqual(expected_deliveries, filtered_deliveries)

    def search_deliveries(self, **kwargs):
        filters = {}
        filter_args = ["project", "component_0", "component_1",
                       "date_range_0", "date_range_1", "created_by",
                       "comment", "is_failed", "is_approved", "is_uploaded"]
        if any([(item in filter_args) for item in kwargs.keys()]):
            filters.update({item: "" for item in filter_args})
            filters["component_0"] = "FILE"  # component_0 is always specified
        filters.update(kwargs)
        default_queryset = Delivery.objects.order_by('-creation_date')
        filter = forms.DeliveryFormFilter(filters, queryset=default_queryset)
        return filter.qs.all()

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

    def _est_delivery_version_search(self):
        Delivery.objects.all().delete()
        self.add_delivery(a="TEST-test", v="v20230101")  # 12
        self.add_delivery(a="TEST-test", v="v20230102")  # 13
        self.add_delivery(a="TEST-test", v="v20230203")  # 14
        filtered = self.search_deliveries(project="202301")
        self.assert_filtered([12, 13], filtered)


class DateSearchTestSuite(DeliverySearchTestCase):

    def test_wide_date_range(self):
        filtered = self.search_deliveries(date_range_0="01-01-2010",
                                          date_range_1="01-01-zxzx")
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ], filtered)

    def test_one_day_range(self):
        self.maxDiff = None
        filtered = self.search_deliveries(date_range_0="01-01-2010",
                                          date_range_1="01-01-2010")
        print ("count is [%s]" % len (filtered) )
        for d in filtered:
            print (d.creation_date)
        self.assert_filtered([4 ], filtered)

    def _est_month_range(self):
        filtered = self.search_deliveries(date_range_0="01-12-2016",
                                          date_range_1="01-01-2017")
        self.assert_filtered([0, 1, 2], filtered)

    def _est_invalid_range(self):
        filtered = self.search_deliveries(date_range_0="01-12-2016",
                                          date_range_1="01-01-2015")
        self.assert_filtered([], filtered)

    def _est_date_from_not_set(self):
        filtered = self.search_deliveries(date_range_1="05-12-2016")
        self.assert_filtered([0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, ], filtered)

    def _est_date_to_not_set(self):
        filtered = self.search_deliveries(date_range_0="05-12-2016")
        self.assert_filtered([0, 1, 2], filtered)

    def _est_date_invalid_no_dashes(self):
        filtered = self.search_deliveries(date_range_0="01012010",
                                          date_range_1="01012030")
        self.assert_filtered([], filtered)

    def _est_date_invalid_not_digits(self):
        filtered = self.search_deliveries(date_range_0="01-JAN-2010",
                                          date_range_1="01-FEB-2030")
        self.assert_filtered([], filtered)

    def _est_type_and_date_specified(self):
        filtered = self.search_deliveries(component_0="CPBDSTR",
                                          component_1="",
                                          date_range_0="01-10-2016",
                                          date_range_1="15-10-2016", )
        self.assert_filtered([3, ], filtered)


class AuthorSearchTestSuite(DeliverySearchTestCase):

    def _est_created_by_beginning(self):
        filtered = self.search_deliveries(created_by="aut")
        self.assert_filtered([0, 2, 3, 4, 5], filtered)

    def _est_created_by_full(self):
        filtered = self.search_deliveries(created_by="author")
        self.assert_filtered([0, 2, 4, 5], filtered)

    def _est_partial_created_by(self):
        filtered = self.search_deliveries(created_by="utho")
        self.assert_filtered([0, 2, 4, 5], filtered)


class CommentSearchTestSuite(DeliverySearchTestCase):

    def _est_search_by_comment(self):
        filtered = self.search_deliveries(comment="comment")
        self.assert_filtered([1, 2, 3, 4, ], filtered)

    def _est_search_by_comment_with_space(self):
        filtered = self.search_deliveries(comment="test comment")
        self.assert_filtered([1, 4, ], filtered)

    def _est_search_by_empty_comment(self):
        filtered = self.search_deliveries(comment="")
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ], filtered)


class ContentSearchTestSuite(DeliverySearchTestCase):

    def _est_svn_file_found(self):
        filtered = self.search_deliveries(component_0="FILE",
                                          component_1="cards/wrap.txt")
        self.assert_filtered([0, 2], filtered)

    def _est_svn_file_beginning_found(self):
        filtered = self.search_deliveries(component_0="FILE",
                                          component_1="cards")
        self.assert_filtered([0, 1, 2], filtered)

    def _est_spaces_are_processed(self):
        filtered = self.search_deliveries(component_0="FILE",
                                          component_1="some file")
        self.assert_filtered([1, ], filtered)

    def _est_only_spaces_given(self):
        filtered = self.search_deliveries(component_0="FILE",
                                          component_1="  ")
        self.assert_filtered([2, ], filtered)


class ComponentSearchTestSuite(DeliverySearchTestCase):

    def _est_all_ts_found(self):
        self.assert_filtered([3, 4], self.search_component_deliveries("TSDSTR"))

    def _est_all_ns_found(self):
        self.assert_filtered([2, 4], self.search_component_deliveries("NSDSTRCLIENT"))

    def _est_all_smsb_found(self):
        self.assert_filtered([1, 3, 5], self.search_component_deliveries("SMSBDSTR"))

    def _est_all_ws_found(self):
        self.assert_filtered([4, 5, 6], self.search_component_deliveries("WSDSTRCLIENT"))

    def _est_all_mwb_found(self):
        self.assert_filtered([3], self.search_component_deliveries("MWBDSTRCLIENT"))

    def _est_all_schedulers_found(self):
        self.assert_filtered([4, ], self.search_component_deliveries("SCHDSTR"))

    def _est_all_appservers_found(self):
        self.assert_filtered([5, ], self.search_component_deliveries("APPSRVDSTR"))

    def _est_all_w4g_found(self):
        self.assert_filtered([1, 2, ], self.search_component_deliveries("W4GDSTR"))

    def _est_all_cp_found(self):
        filtered = self.search_deliveries(component_0="CPBDSTR",
                                          component_1="")
        self.assert_filtered([3, 5, ], filtered)
        self.assert_filtered([3, 5], self.search_component_deliveries("CPBDSTR"))

    def _est_all_mpi_found(self):
        self.assert_filtered([5, ], self.search_component_deliveries("MPIDSTR"))

    def _est_all_acs_found(self):
        self.assert_filtered([1, ], self.search_component_deliveries("ACSDSTR"))

    def _est_all_egw_found(self):
        # if egwapp belongs to egw, then include 4
        self.assert_filtered([3, ], self.search_component_deliveries("EGWDSTR"))

    def _est_all_egwapp_found(self):
        self.assert_filtered([4, ], self.search_component_deliveries("EGWAPPDSTR"))

    def _est_all_as_found(self):
        self.assert_filtered([5, ], self.search_component_deliveries("ACCSRVDSTR"))

    def _est_type_and_version_beginning(self):
        filtered = self.search_deliveries(component_0="SMSBDSTR",
                                          component_1="2.8.52", )
        self.assert_filtered([1, 5], filtered)

    def _est_missing_component_processed(self):
        self.assert_filtered([], self.search_component_deliveries("WRONG"))

    def _est_all_redis_found(self):
        self.assert_filtered([8, 11, ], self.search_component_deliveries("REDISDSTR"))

    def _est_all_demob_found(self):
        self.assert_filtered([7, ], self.search_component_deliveries("DEMOBDSTR"))

    def _est_all_epin_found(self):
        self.assert_filtered([7, ], self.search_component_deliveries("EPINDSTR"))

    def _est_all_epinapp_found(self):
        self.assert_filtered([9, 10, ], self.search_component_deliveries("EPINAPPDSTR"))

    def _est_all_pind_found(self):
        self.assert_filtered([5, ], self.search_component_deliveries("PINDDSTR"))

    def _est_all_pindapp_found(self):
        self.assert_filtered([7, ], self.search_component_deliveries("PINDAPPDSTR"))

    def _est_all_paysrv_found(self):
        self.assert_filtered([11, ], self.search_component_deliveries("PAYSRVDSTR"))


class GroupSearchTestSuite(DeliverySearchTestCase):

    # no initial setup is needed
    def setUp(self):
        self.all_deliveries = []
        CiTypes(code="FILE", name="FILE").save()
        self.at_nexus, _ = LocTypes.objects.get_or_create(code="NXS", name="NXS")

    # missing group is the same as missing component - tested above
    # def _est_missing_group_skipped(self):

    def _est_empty_group_processed(self):
        CiTypeGroups(code="TEST", name="TEST").save()
        self.assert_filtered([], self.search_component_deliveries("TEST"))

    def _est_group_without_regexps_processed(self):
        citype1, _ = CiTypes.objects.get_or_create(code="test1", name="test1")
        group, _ = CiTypeGroups.objects.get_or_create(code="TEST", name="TEST")
        CiTypeIncs(ci_type_group=group, ci_type=citype1).save()

        self.assert_filtered([], self.search_component_deliveries("TEST"))

    def _est_group_components_found(self):
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

    def _est_group_code_prevails_component(self):
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

    def _est_delivery_is_approved_search(self):
        Delivery.objects.all().delete()
        self.add_delivery(is_approved=True, v="v20010101")  # 12
        self.add_delivery(v="v20011111")  # 13
        self.add_delivery(is_approved=True, v="v20020202")  # 14
        filtered = self.search_deliveries(is_approved=True)
        self.assert_filtered([12, 14], filtered)

    def _est_delivery_is_not_approved_search(self):
        self.add_delivery(is_approved=True, v="v20010101")  # 12
        self.add_delivery(v="v20011111")  # 13
        self.add_delivery(is_approved=True, v="v20020202")  # 14
        filtered = self.search_deliveries(is_approved=False)
        self.assert_filtered([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13], filtered)

    def _est_delivery_is_uploaded_search(self):
        self.add_delivery(is_approved=True, is_uploaded=True, v="v20010101")  # 12
        self.add_delivery(v="v20011111")  # 13
        self.add_delivery(is_approved=True, v="v20020202")  # 14
        filtered = self.search_deliveries(is_uploaded=True)
        print(filtered)
        self.assert_filtered([12], filtered)

    def _est_delivery_is_failed_search(self):
        self.add_delivery(is_approved=True, is_uploaded=True, v="v20010101")  # 12
        self.add_delivery(is_approved=True, is_uploaded=True, is_failed=True, v="v20011111")  # 13
        self.add_delivery(is_approved=True, v="v20020202")  # 14
        filtered = self.search_deliveries(is_failed=True)
        print(filtered)
        self.assert_filtered([13], filtered)
    


# is_approved=False, 
#                      is_uploaded=False, 
#                      is_failed=False
