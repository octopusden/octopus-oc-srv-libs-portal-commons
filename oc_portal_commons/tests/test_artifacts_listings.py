from collections import namedtuple

from . import django_settings
from oc_delivery_apps.checksums.models import CiTypes, LocTypes, Files, Locations, CiRegExp, CiTypeGroups, CiTypeIncs
import django
from django import test

from oc_portal_commons.artifacts_listings import get_citype_artifacts, order_artifacts, get_cigroup_artifacts

MockLocation = namedtuple("MockLocation", ["path", ])


class ArtifactsOrderingTestSuite(django.test.TransactionTestCase):

    def setUp (self):
        django.core.management.call_command('migrate', verbosity=0, interactive=False)


    def tearDown (self):
        django.core.management.call_command('flush', verbosity=0, interactive=False)


    def test_empty_list_processed(self):
        self.assertEqual([], order_artifacts([]))

    def test_artifacts_sorted(self):
        gavs = ["g:a:1:zip:c2", "g:a:1:zip:c1", "g:a:1:zip",
                "g:a:2:zip", "g:b:1:zip", "h:a:1:zip", ]
        sorted_artifacts = order_artifacts([MockLocation(gav) for gav in gavs])
        self.assertEqual(["g:a:2:zip", "g:a:1:zip", "g:a:1:zip:c1",
                          "g:a:1:zip:c2", "g:b:1:zip", "h:a:1:zip", ],
                         [artifact.path for artifact in sorted_artifacts])


class CitypeRegexpsListingTestSuite(django.test.TransactionTestCase):

    def setUp(self):
        django.core.management.call_command('migrate', verbosity=0, interactive=False)
        self.citype = _create_artifact_citype("TEST_TYPE", ["g:.+", ])
        _create_artifact("g:a:v1", self.citype)
        _create_artifact("g2:a:v2", self.citype)
        citype2 = _create_artifact_citype("TEST_TYPE2", ["g:.+", ])
        _create_artifact("g:a:v3", citype2)

    def test_existing_citype_code_required(self):
        self.citype.delete()
        with self.assertRaises(CiTypes.DoesNotExist):
            get_citype_artifacts("TEST_TYPE")

    def tearDown(self):
        django.core.management.call_command('flush', verbosity=0, interactive=False)


class CigroupListingTestSuite(test.TestCase):

    def setUp(self):
        django.core.management.call_command('migrate', verbosity=10, interactive=False)
        self.citype = _create_artifact_citype("TEST_TYPE", ["g:.+", ])
        _create_artifact("g:a:v1", self.citype)
        _create_artifact("g2:a:v2", self.citype)
        citype2 = _create_artifact_citype("TEST_TYPE2", ["g:.+", ])
        _create_artifact("g:a:v3", citype2)

        self.cigroup, _ = CiTypeGroups.objects.get_or_create(code="TEST_GROUP", name="TEST_GROUP")
        CiTypeIncs(ci_type_group=self.cigroup, ci_type=self.citype).save()
        CiTypeIncs(ci_type_group=self.cigroup, ci_type=citype2).save()

    def test_existing_cigroup_required(self):
        self.cigroup.delete()
        with self.assertRaises(CiTypeGroups.DoesNotExist):
            get_cigroup_artifacts("TEST_GROUP")

    def test_empty_cigroup_processed(self):
        CiTypeIncs.objects.filter(ci_type_group=self.cigroup).delete()
        listing = get_cigroup_artifacts("TEST_GROUP")
        self.assertCountEqual([], listing)


    def tearDown(self):
        django.core.management.call_command('flush', verbosity=0, interactive=False)


def _create_artifact_citype(code, regexps):
    loctype, _ = LocTypes.objects.get_or_create(code="NXS", name="NXS")
    citype, _ = CiTypes.objects.get_or_create(code=code, name=code,
                                              is_standard="Y", is_deliverable=True)
    for regexp in regexps:
        CiRegExp(ci_type=citype, regexp=regexp, loc_type=loctype).save()
    return citype


def _create_artifact(path, citype):
    loctype, _ = LocTypes.objects.get_or_create(code="NXS", name="NXS")
    cifile, _ = Files.objects.get_or_create(ci_type=citype)
    location, _ = Locations.objects.get_or_create(file=cifile, loc_type=loctype, path=path)
