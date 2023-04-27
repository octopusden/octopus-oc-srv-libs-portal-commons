import ldap
import os
from django_auth_ldap.config import LDAPSearch, NestedActiveDirectoryGroupType

# Baseline configuration.
AUTH_LDAP_SERVER_URI = os.getenv("AD_URL")

AUTH_LDAP_BIND_DN = os.getenv("AD_USER")
AUTH_LDAP_BIND_PASSWORD = os.getenv("AD_PASSWORD")

AUTH_LDAP_USER_SEARCH = LDAPSearch(os.getenv("AD_USER_SEARCH_BASE_DN"),
                                   ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(os.getenv("AD_GROUP_SEARCH_BASE_DN"),
                                    ldap.SCOPE_SUBTREE, "(objectClass=group)"
                                    )
AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()

# Simple group restrictions
AUTH_LDAP_REQUIRE_GROUP = os.getenv("AD_REQUIRE_GROUP")

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

AUTH_LDAP_PROFILE_ATTR_MAP = {
    "telephone_number": "telephoneNumber"
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": os.getenv("AD_REQUIRE_GROUP"),
    "is_staff": os.getenv("AD_STAFF_GROUP"),
    "is_superuser": os.getenv("AD_ADMIN_DN")
}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
# AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_MIRROR_GROUPS = True
