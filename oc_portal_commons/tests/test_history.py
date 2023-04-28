import datetime
import os
from . import django_settings

import pytz
import django
from django import test
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models import Model
from oc_delivery_apps.dlmanager.models import Delivery, BusinessStatus
from oc_portal_commons.templatetags import history_tags
from simple_history.models import HistoricalRecords


class DeliveryHistoryTestCase(test.TestCase):

    def setUp(self):
        django.core.management.call_command('migrate', verbosity=0, interactive=False)
        statuses = [BusinessStatus(description=d)
                    for d in ["testing", "deployed", "rejected", "deleted"]]
        for bs in statuses: bs.save()
        user = User.objects.create(username='tester', password='tester')
        user.set_password("tester")
        user.save()
        user = User.objects.create(username='updater', password='updater')
        user.set_password("updater")
        user.save()
        return

    def tearDown(self):
        HistoricalRecords.thread.request = None  # cleanup after setup_current_user
        django.core.management.call_command('flush', verbosity=0, interactive=False)

    def get_delivery(self, created_at=datetime.datetime(2010, 10, 10, tzinfo=pytz.utc),
                     init_history=True):
        delivery = Delivery()
        delivery.creation_date = created_at
        delivery.mf_delivery_author = "tester"
        delivery.save()
        if init_history:
            with open(os.devnull, "w") as suppress:
                call_command("init_delivery_history", stdout=suppress, stderr=suppress)
        return delivery

    def add_status(self, delivery, status_text, username, comment=None):
        new_status = BusinessStatus.objects.get(description=status_text)
        delivery.business_status = new_status
        if not comment:
            comment = "comment: %s" % status_text
        delivery.comment = comment
        self.setup_current_user(username)
        delivery.save()
        return

    def set_flag(self, delivery, flag_name, username):
        self.setup_current_user(username)
        method_to_call = getattr(delivery, "set_" + flag_name)
        method_to_call(True, username)
        return

    def setup_current_user(self, username):
        action_user = User.objects.get(username=username)

        request = test.RequestFactory().get("/")
        request.user = action_user
        # imitate logged in user (it is made via middleware in real app)
        # sample found in simple_history sources
        HistoricalRecords.thread.request = request
        return

    def update_last_revision(self, delivery, date):
        new_rev = delivery.history.first()  # get last revision
        # new_rev.history_user_id=User.objects.get(username=username).pk
        new_rev.history_date = date
        new_rev.save()
        return new_rev

    def test_changelog_no_changes_made(self):
        delivery = self.get_delivery()
        # changelog is iterator, but we need list to get len
        changelog = list(history_tags.get_changelog_internal(delivery))
        self.assertEqual(1, len(changelog))
        self.assertEqual({"description": "New",
                          "date": datetime.datetime(2010, 10, 10, tzinfo=pytz.utc),
                          "author": "tester",
                          "comment": "Delivery created"},
                         changelog[0])

    def test_compared_to_original(self):
        delivery = self.get_delivery()
        original_rev = delivery.history.first()

        self.add_status(delivery, "testing", "updater")
        history_date = datetime.datetime(2011, 11, 11, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        change = next (history_tags.get_changelog_internal(delivery) )
        self.assertEqual({"description": "testing",
                          "date": datetime.datetime(2011, 11, 11, tzinfo=pytz.utc),
                          "author": "updater",
                          "comment": "comment: testing"},
                         change)

    def test_revisions_sorted_by_date(self):
        delivery = self.get_delivery()
        original_rev = delivery.history.all()[0]

        self.add_status(delivery, "testing", "tester")
        history_date = datetime.datetime(2011, 11, 11, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        self.add_status(delivery, "deployed", "tester")
        history_date = datetime.datetime(2014, 12, 12, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        self.add_status(delivery, "rejected", "tester")
        history_date = datetime.datetime(2012, 4, 4, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        changelog = history_tags.get_changelog_internal(delivery)
        self.assertEqual(["deployed", "rejected", "testing", "New"],
                         [chg["description"] for chg in changelog])

    def test_revisions_statuses_compared(self):
        delivery = self.get_delivery()
        original_rev = delivery.history.all()[0]

        self.add_status(delivery, "testing", "tester")
        history_date = datetime.datetime(2011, 11, 11, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        self.add_status(delivery, "deployed", "updater")
        history_date = datetime.datetime(2014, 4, 4, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        changelog = history_tags.get_changelog_internal(delivery)
        last_change = next (changelog)
        self.assertEqual({"description": "deployed",
                          "date": datetime.datetime(2014, 4, 4, tzinfo=pytz.utc),
                          "author": "updater",
                          "comment": "comment: deployed"},
                         last_change)

    def test_creation_date_is_none(self):
        # if no creation date is set, then initial revision should not be created

        delivery = self.get_delivery(created_at=None)
        self.add_status(delivery, "testing", "updater")
        history_date = datetime.datetime(2011, 11, 11, tzinfo=pytz.utc)
        new_rev = self.update_last_revision(delivery, history_date)

        changelog = list(history_tags.get_changelog_internal(delivery))
        # ! 'New' entry will be displayed with date=status date, which is wrong
        # but delivery without creation date is error itself, so skip it
        self.assertCountEqual([{"description": "New",
                                "date": datetime.datetime(2011, 11, 11, tzinfo=pytz.utc),
                                "author": "updater",
                                "comment": "comment: testing"},
                               {"description": "testing",
                                "date": datetime.datetime(2011, 11, 11, tzinfo=pytz.utc),
                                "author": "updater",
                                "comment": "comment: testing"}],
                              changelog)

    def test_repeated_statuses_skipped(self):
        delivery = self.get_delivery()
        self.add_status(delivery, "testing", "tester")
        history_date = datetime.datetime(2011, 11, 11, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        self.add_status(delivery, "testing", "updater")
        history_date = datetime.datetime(2014, 4, 4, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        changelog = list(history_tags.get_changelog_internal(delivery))
        # initial + one change
        self.assertEqual(2, len(changelog))

    def test_unknown_author_processed(self):
        delivery = self.get_delivery()

        self.add_status(delivery, "testing", "tester")
        history_date = datetime.datetime(2011, 11, 11, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        self.add_status(delivery, "deployed", "updater")
        history_date = datetime.datetime(2014, 4, 4, tzinfo=pytz.utc)
        last_rev = self.update_last_revision(delivery, history_date)
        last_rev.history_user_id = 1000000
        last_rev.save()

        changelog = history_tags.get_changelog_internal(delivery)
        last_change = next(changelog)
        self.assertEqual({"description": "deployed",
                          "date": datetime.datetime(2014, 4, 4, tzinfo=pytz.utc),
                          "author": "-",
                          "comment": "comment: deployed"},
                         last_change)

    def test_none_author_processed(self):
        delivery = self.get_delivery()

        self.add_status(delivery, "testing", "tester")
        history_date = datetime.datetime(2011, 11, 11, tzinfo=pytz.utc)
        self.update_last_revision(delivery, history_date)

        self.add_status(delivery, "deployed", "updater")
        history_date = datetime.datetime(2014, 4, 4, tzinfo=pytz.utc)
        last_rev = self.update_last_revision(delivery, history_date)
        last_rev.history_user_id = None
        last_rev.save()

        changelog = history_tags.get_changelog_internal(delivery)
        last_change = next (changelog)
        self.assertEqual({"description": "deployed",
                          "date": datetime.datetime(2014, 4, 4, tzinfo=pytz.utc),
                          "author": "-",
                          "comment": "comment: deployed"},
                         last_change)

    def test_changelog_after_flag_set(self):
        delivery = self.get_delivery()
        # delivery.set_approved(who="tester")
        self.set_flag(delivery, "approved", "tester")
        changelog = history_tags.get_changelog_internal(delivery)
        last_change = next (changelog)
        # cannot check date, so assertIn
        # also dictContainsSubset is deprecated
        self.assert_subdict({"description": "Approved, waiting for delivery",
                             "author": "tester",
                             "comment": "Approved, waiting for delivery"},
                            last_change)

    def test_second_flag_set(self):
        delivery = self.get_delivery()
        self.set_flag(delivery, "approved", "tester")
        self.set_flag(delivery, "uploaded", "updater")
        changelog = history_tags.get_changelog_internal(delivery)
        last_change = next (changelog)
        self.assert_subdict({"description": "Delivered",
                             "author": "updater",
                             "comment": "Delivered"},
                            last_change)

    def test_flag_repeated(self):
        delivery = self.get_delivery()
        self.set_flag(delivery, "approved", "tester")
        self.set_flag(delivery, "approved", "updater")
        changelog = history_tags.get_changelog_internal(delivery)
        last_change = next (changelog)
        self.assert_subdict({"description": "Approved, waiting for delivery",
                             "author": "tester",
                             "comment": "Approved, waiting for delivery"},
                            last_change)

    def test_status_change_after_flags_set(self):
        delivery = self.get_delivery()
        self.set_flag(delivery, "approved", "tester")
        self.set_flag(delivery, "uploaded", "updater")

        self.add_status(delivery, "deployed", "tester")

        changelog = history_tags.get_changelog_internal(delivery)
        last_change = next (changelog)
        # do not set date, assume it was checked in other tests
        self.assert_subdict({"description": "deployed",
                             "author": "tester",
                             "comment": "comment: deployed"},
                            last_change)

    def test_both_statuses_set_simultaneously(self):
        delivery = self.get_delivery()
        new_status = BusinessStatus.objects.get(description="deployed")
        delivery.business_status = new_status
        delivery.comment = "comment: deployed"
        self.setup_current_user("updater")
        self.set_flag(delivery, "uploaded", "updater")  # saved

        changes = list(history_tags.get_changelog_internal(delivery))
        self.assertEqual(3, len(changes))

        self.assert_subdict({"description": "Delivered",
                             "author": "updater",
                             "comment": "Delivered"},
                            changes[1])
        # save was performed on set_uploaded, so comment should match it
        self.assert_subdict({"description": "deployed",
                             "author": "updater",
                             "comment": "Delivered"},
                            changes[0])

    def test_removed_status_given(self):
        delivery = self.get_delivery()
        self.add_status(delivery, "deployed", "tester")
        BusinessStatus.objects.get(description="deployed").delete()

        changelog = history_tags.get_changelog_internal(delivery)
        last_change = next (changelog)
        self.assert_subdict({"description": "Unknown status",
                             "author": "tester",
                             "comment": "comment: deployed"},
                            last_change)

    def test_nonempty_delivery_unknown_creation_date(self):
        delivery = Delivery()
        delivery.business_status = None;
        self.set_flag(delivery, "approved", "updater")  # saved
        changes = list(history_tags.get_changelog_internal(delivery))
        self.assertEqual(1, len(changes))
        self.assert_subdict({"description": "Approved, waiting for delivery",
                             "author": "updater",
                             "comment": "Approved, waiting for delivery"},
                            changes[0])

    def test_user_set_by_author_at_creation(self):
        delivery = self.get_delivery(init_history=False)
        changes = list(history_tags.get_changelog_internal(delivery))
        self.assertEqual(1, len(changes))
        self.assert_subdict({"description": "New",
                             "author": "tester",
                             "comment": ""},  # no comments specified without init_delivery_history
                            changes[0])

    def test_unknown_author_at_creation(self):
        delivery = Delivery()
        delivery.creation_date = datetime.datetime(2010, 10, 10, tzinfo=pytz.utc)
        delivery.mf_delivery_author = "XXX"
        delivery.save()
        changes = list(history_tags.get_changelog_internal(delivery))
        self.assertEqual(1, len(changes))
        self.assert_subdict({"description": "New",
                             "author": "-",
                             "comment": ""},
                            changes[0])

    def test_request_user_is_more_important(self):
        self.setup_current_user("updater")
        delivery = self.get_delivery(init_history=False)
        changes = list(history_tags.get_changelog_internal(delivery))
        self.assert_subdict({"author": "updater", },
                            changes[0])

    def test_author_only_set_for_new_delivery(self):
        delivery = self.get_delivery(init_history=False)
        new_status = BusinessStatus.objects.get(description="deployed")
        delivery.business_status = new_status
        delivery.comment = "comment: deployed"
        delivery.save()
        changes = list(history_tags.get_changelog_internal(delivery))
        self.assertEqual(2, len(changes))
        self.assert_subdict({"description": "deployed",
                             "author": "-",  # request not set - so none
                             "comment": "comment: deployed"},
                            changes[0])

    def test_bug_incorrect_comment_on_repeated_status(self):
        delivery = self.get_delivery()
        self.setup_current_user("tester")
        self.add_status(delivery, "Other", "tester", comment="first")
        self.setup_current_user("updater")
        delivery.set_approved(True, "updater")
        self.add_status(delivery, "Other", "updater", comment="second")
        changes = list(history_tags.get_changelog_internal(delivery))
        self.assertEqual(4, len(changes))
        self.assert_subdict({"description": "Other",
                             "author": "updater",
                             "comment": "second"},  # request not set - so none
                            changes[0])
        self.assert_subdict({"description": "Other",
                             "author": "tester",
                             "comment": "first"},  # request not set - so none
                            changes[2])

    def assert_subdict(self, sub_dict, big_dict):
        for item in sub_dict.items():
            self.assertIn(item, big_dict.items())

    def test_simplehistory_installed(self):
        self.assertTrue("simple_history" in settings.INSTALLED_APPS)
