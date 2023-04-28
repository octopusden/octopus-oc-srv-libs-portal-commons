from . import django_settings
from django import test
from oc_delivery_apps.dlmanager.models import Delivery
from oc_portal_commons.templatetags import custom_tags
from copy import deepcopy

class MockMessage(object):
    def __init__(self, extra_tags=None):
        self.extra_tags = extra_tags

class CustomTagsTestCase(test.TestCase):

    def test_reset_cache_suffix(self):
        self.assertTrue(custom_tags.cache_reset_suffix().startswith("STATICS_VERSION="))

    def test_get_delivery_messages(self):
        delivery = Delivery()
        delivery.flag_uploaded = True
        delivery.save()
        self.assertIsNotNone(delivery.id)
        all_msgs = [MockMessage("delivery_%d" % delivery.id)]
        self.assertEqual(deepcopy(all_msgs).pop().extra_tags, custom_tags.get_delivery_messages(delivery, all_msgs).pop().extra_tags)

    def test_get_general_messages(self):
        delivery = Delivery()
        delivery.flag_uploaded = False
        delivery.save()
        all_msgs = [MockMessage("delivery_%d" % (delivery.id + 1)), MockMessage("pupking")]
        self.assertEqual(custom_tags.get_general_messages(all_msgs).pop().extra_tags, MockMessage("pupking").extra_tags)
        
