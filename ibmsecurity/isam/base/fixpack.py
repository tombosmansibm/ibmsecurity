import logging
import os.path
import ibmsecurity.utilities.tools

logger = logging.getLogger(__name__)


def get(isamAppliance, check_mode=False, force=False):
    """
    Retrieve existing fixpacks.
    """
    return isamAppliance.invoke_get("Retrieving fixpacks",
                                    "/fixpacks")


def install(isamAppliance, file, check_mode=False, force=False):
    """
    Install fixpack
    """
    if force is True or _check(isamAppliance, file) is False:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:
            return isamAppliance.invoke_post_files(
                "Install fixpack",
                "/fixpacks",
                [{
                    'file_formfield': 'file',
                    'filename': file,
                    'mimetype': 'application/octet-stream'
                }],
                {})

    return isamAppliance.create_return_object()


def rollback(isamAppliance, file, check_mode=False, force=False):
    """
    Rollback fixpack
    """
    if force is True or _check_rollback(isamAppliance, file) is True:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:
            return isamAppliance.invoke_delete(
                "Rollback fixpack",
                "/fixpacks",
                requires_modules=None,
                requires_version="9.0.3.0")

    return isamAppliance.create_return_object()


def _check_rollback(isamAppliance, fixpack):
    """
    Check if fixpack is already installed
    """
    ret_obj = get(isamAppliance)

    fixpack_name = _extract_fixpack_name(fixpack)

    # Reverse sort the json by 'id'
    json_data_sorted = sorted(ret_obj['data'], key=lambda k: int(k['id']), reverse=True)
    # Eliminate all rollbacks before hitting the first non-rollback fixpack
    del_fixpack = ''  # Delete succeeding fixpack to a rollback, only last fixpack can be rolled back
    for fixpack in json_data_sorted:
        if fixpack['action'] == 'Uninstalled':
            del_fixpack = fixpack['name']
        elif del_fixpack == fixpack['name'] and fixpack['rollback'] == 'Yes':
            del_fixpack = ''
        elif fixpack['name'].lower() == fixpack_name.lower():
            return True
        # The first non-rollback fixpack needs to match the name otherwise skip rollback
        else:
            return False

    return False


def _check(isamAppliance, fixpack):
    """
    Check if fixpack is already installed
    """
    ret_obj = get(isamAppliance)

    fixpack_name = _extract_fixpack_name(fixpack)

    # Reverse sort the json by 'id'
    json_data_sorted = sorted(ret_obj['data'], key=lambda k: int(k['id']), reverse=True)
    # Eliminate all rollbacks
    del_fixpack = ''  # Delete succeeding fixpack to a rollback, only last fixpack can be rolled back
    for fixpack in json_data_sorted:
        if fixpack['action'] == 'Uninstalled':
            del_fixpack = fixpack['name']
        elif del_fixpack == fixpack['name'] and fixpack['rollback'] == 'Yes':
            del_fixpack = ''
        elif fixpack['name'].lower() == fixpack_name.lower():
            return True

    return False


def _extract_fixpack_name(fixpack):
    """
    Extract fixpack name from the given fixpack
    """
    import re

    # Look for the follwing string inside the fixpack file
    # FIXPACK_NAME="9021_IPv6_Routes_fix"
    for s in ibmsecurity.utilities.tools.strings(fixpack):
        match_obj = re.search(r"FIXPACK_NAME=\"(?P<fp_name>\w+)\"", s)
        if match_obj:
            logger.info("Fixpack name extracted from file using strings method: {0}".format(match_obj.group('fp_name')))
            return match_obj.group('fp_name')

    # Unable to extract fixpack name from binary
    # Return fixpack name derived from the filename
    file_name = os.path.basename(fixpack)
    fixpack_name, ext_name = file_name.split('.')

    return fixpack_name


def compare(isamAppliance1, isamAppliance2):
    """
    Compare fixpacks between two appliances
    Sort in reverse order and remove fixpacks that were rolled back before compare
    """
    ret_obj1 = get(isamAppliance1)
    ret_obj2 = get(isamAppliance2)

    json_data1_sorted = sorted(ret_obj1['data'], key=lambda k: int(k['id']), reverse=True)
    del_fixpack = ''  # Delete succeeding fixpack to a rollback, only last fixpack can be rolled back
    for fixpack in json_data1_sorted:
        if fixpack['action'] == 'Uninstalled':
            del_fixpack = fixpack['name']
            del fixpack
        elif del_fixpack == fixpack['name'] and fixpack['rollback'] == 'Yes':
            del_fixpack = ''
            del fixpack
        else:
            del fixpack['date']

    json_data2_sorted = sorted(ret_obj2['data'], key=lambda k: int(k['id']), reverse=True)
    del_fixpack = ''  # Delete succeeding fixpack to a rollback, only last fixpack can be rolled back
    for fixpack in json_data2_sorted:
        if fixpack['action'] == 'Uninstalled':
            del_fixpack = fixpack['name']
            del fixpack
        elif del_fixpack == fixpack['name'] and fixpack['rollback'] == 'Yes':
            del_fixpack = ''
            del fixpack
        else:
            del fixpack['date']

    return ibmsecurity.utilities.tools.json_compare(ret_obj1, ret_obj2, deleted_keys=[])
