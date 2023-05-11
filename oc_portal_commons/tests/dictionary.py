import os
import sys

from django.core.wsgi import get_wsgi_application;
sys.path.append( os.path.dirname(os.path.dirname(os.path.abspath(__file__))) )
application = get_wsgi_application()

from oc_delivery_apps.checksums import models

def check_create_app_CI_TYPE_GROUPS( apps, h_rec ):
    """
    Check ci_type_group record exist, create new one if not
    :param h_rec: dictionary with a record
    """
    CiTypeGroups = apps.get_model( "checksums", "CiTypeGroups" )

    if ( CiTypeGroups.objects.filter( code = h_rec[ "code" ] ).count() == 0 ):
        obj_ct = CiTypeGroups( code = h_rec[ "code" ], name = h_rec[ "name" ] )

        if "rn_gav" in h_rec:
            obj_ct.rn_gav = h_rec[ "rn_gav" ]

        obj_ct.save()

def check_create_app_CI_TYPES(apps, h_rec ):
    """
    Check that record with a specified code exist
    Create such a record if not
    @ ARGS:
    @    h_rec - dictionary with a record
    @ RETURNS: Nothing
    """
    CiTypes=apps.get_model("checksums", "CiTypes")
    if ( CiTypes.objects.filter( code = h_rec[ "code" ] ).last() is None ):
        CiTypes( code = h_rec[ "code" ], name = h_rec[ "name" ], is_standard = h_rec[ "is_standard" ] ).save()

    return

def check_create_app_CS_TYPES(apps, h_rec ):
    """
    Check that record with a specified code exist
    Create such a record if not
    @ ARGS:
    @    h_rec - dictionary with a record
    @ RETURNS: Nothing
    """
    CsTypes=apps.get_model("checksums", "CsTypes")
    if ( CsTypes.objects.filter( code = h_rec[ "code" ] ).last() is None ):
        CsTypes( code = h_rec[ "code" ], name = h_rec [ "name" ] ).save()
    return

def check_create_app_LOC_TYPES(apps, h_rec ):
    """
    Check that record with a specified code exist
    Create such a record if not
    @ ARGS:
    @    h_rec - dictionary with a record
    @ RETURNS: Nothing
    """
    LocTypes=apps.get_model("checksums", "LocTypes")
    if ( LocTypes.objects.filter( code = h_rec[ "code" ] ).last() is None ):
        LocTypes( code = h_rec[ "code" ], name = h_rec[ "name" ] ).save()
    return

def check_create_app_CI_REGEXP(apps, h_rec ):
    """
    Check that record with a specified code exist
    Create such a record if not
    @ ARGS:
    @    h_rec - dictionary with a record
    @ RETURNS: Nothing
    """
    LocTypes, CiTypes, CiRegExp = (apps.get_model("checksums", name)
                                       for name in ["LocTypes", "CiTypes", "CiRegExp"])
    obj_loc_type = LocTypes.objects.filter( code = h_rec[ "loc_type" ] ).last()
    obj_ci_type = CiTypes.objects.filter( code = h_rec[ "ci_type" ] ).last()

    if ( obj_loc_type is None ):
        raise Exception( "Check location type '" + h_rec[ "loc_type" ] + "'" )

    if ( obj_ci_type is None ):
        raise Exception( "Check ci_type '" + h_rec[ "ci_type" ] + "'" )

    if( CiRegExp.objects.filter( loc_type = obj_loc_type, ci_type = obj_ci_type, regexp = h_rec[ "regexp" ]  ).last() is None ):
        CiRegExp( loc_type = obj_loc_type, ci_type = obj_ci_type, regexp = h_rec[ "regexp" ] ).save()
    return

def include_app_ci_types( apps, str_group_code, ls_types ):
    """
    check ci_type and group inclusion
    :param str_group_code: group code of ci_type_group
    :param ls_types: list of stringsi with ci_type codes
    """
    CiTypes, CiTypeGroups, CiTypeIncs = ( apps.get_model( "checksums", name ) for name in [ "CiTypes", "CiTypeGroups", "CiTypeIncs" ] )
    obj_gr = CiTypeGroups.objects.filter( code = str_group_code ).last()

    for str_type_code in ls_types:
        obj_type = CiTypes.objects.filter( code = str_type_code ).last()

        if ( CiTypeIncs.objects.filter( ci_type_group = obj_gr, ci_type = obj_type ).last() is not None ):
            continue

        CiTypeIncs( ci_type_group = obj_gr, ci_type = obj_type ).save()

def fill_dict( o_apps = None, o_sched = None ):
    check_create_CI_TYPES = lambda *args: check_create_app_CI_TYPES(o_apps, *args)
    check_create_CI_TYPE_GROUPS = lambda *args: check_create_app_CI_TYPE_GROUPS( o_apps, *args )
    include_ci_types = lambda *args: include_app_ci_types( o_apps, *args )

    check_create_CI_TYPES( { "code":"FILE", "name":"Any regular file", "is_standard":"N" } )
    check_create_CI_TYPES( { "code":"SQL", "name":"Any sql file", "is_standard":"N" } )
    check_create_CI_TYPES( { "code":"SOMEDSTR", "name":"Some distribution", "is_standard":"Y" } )
    check_create_CI_TYPES( { "code":"OTHDSTR", "name":"Some other distribution", "is_standard":"Y" } )

    # groups:
    check_create_CI_TYPE_GROUPS( { "code":"FILE", "name" : "General Files" } )
    include_ci_types( "FILE", [ "FILE" ] )

    # CS_TYPES 
    check_create_CS_TYPES=lambda *args: check_create_app_CS_TYPES(o_apps, *args)
    check_create_CS_TYPES( { "code":"MD5", "name":"MD5 digest algoritm" } )
    

    # LOC_TYPES
    check_create_LOC_TYPES=lambda *args: check_create_app_LOC_TYPES(o_apps, *args)
    check_create_LOC_TYPES( { "code":"SMB", "name":"Samba share" } )
    check_create_LOC_TYPES( { "code":"NXS", "name":"Nexus (Maven) GAV storage" } )
    check_create_LOC_TYPES( { "code":"FTP", "name":"FTP server" } )
    check_create_LOC_TYPES( { "code":"SVN", "name":"SubVersion revision" } )
    check_create_LOC_TYPES( { "code":"CRM", "name":"CRM BLOB" } )
    check_create_LOC_TYPES( { "code":"ARCH", "name":"Inside Archive" } )
    check_create_LOC_TYPES( { "code":"OTH", "name":"Anything - for test purposes only" } )
    check_create_LOC_TYPES( { "code":"LOC", "name":"Local file system" } )

    # CI_REGEXP
    check_create_CI_REGEXP=lambda *args: check_create_app_CI_REGEXP(o_apps, *args)
    check_create_CI_REGEXP( { "loc_type":"NXS", "ci_type":"FILE", "regexp": ".+:zip$" } )
    check_create_CI_REGEXP( { "loc_type":"NXS", "ci_type":"SQL", "regexp": ".+sql" } )
    check_create_CI_REGEXP( { "loc_type":"NXS", "ci_type":"SOMEDSTR", "regexp": ".+somedstr.+" } )
    check_create_CI_REGEXP( { "loc_type":"NXS", "ci_type":"OTHDSTR", "regexp": ".+othdstr.+" } )
    return

def main():
    fill_dict( None, None )
    return

if ( __name__ == '__main__' ):
    main()
