import logging

logger = logging.getLogger(__name__)


# *** WORK IN PROGRESS - module not done yet


def get_all(isamAppliance, admin_id, admin_pwd, admin_domain='Default', **kwargs):
    """
    Retrieve a list of POPs
    """
    ret_obj = isamAppliance.invoke_post("Retrieve a list of POPs",
                                        "/isam/pdadmin/poplistext/v1",
                                        ignore_error=True,
                                        data={
                                            "admin_id": admin_id,
                                            "admin_pwd": admin_pwd,
                                            # "pop_name": pop_name,
                                            # "pop_attribute_name": pop_attribute_name,
                                            # "pop_attribute_value": pop_attribute_value,
                                            "admin_domain": admin_domain
                                        })
    ret_obj['changed'] = False
    if ret_obj['rc'] == 404:
        logger.info(f"No POPs found")
        return isamAppliance.create_return_object()
    return ret_obj


def get(isamAppliance, admin_id, admin_pwd, pop_name, admin_domain='Default', **kwargs):
    """
    Retrieve a specific POP
    """
    ret_obj = isamAppliance.invoke_post("Retrieve a specific POP",
                                        "/isam/pdadmin/popshowext/v1",
                                        ignore_error=True,
                                        data={
                                            "admin_id": admin_id,
                                            "admin_pwd": admin_pwd,
                                            "pop_name": pop_name,
                                            "admin_domain": admin_domain
                                        })
    ret_obj['changed'] = False
    if ret_obj['rc'] == 404:
        logger.info(f"No POP {pop_name} found in {admin_domain}")
        return isamAppliance.create_return_object()
    return ret_obj


def get_pop_list(isamAppliance, admin_id, admin_pwd, **kwargs):
    """
    Retrieve a list of protected objects
    :param str admin_id: policy administrator, typically sec_master
    :param str admin_pwd:
    :param str admin_domain: the webseal domain, defaults to 'Default' if not supplied
    :param str object: optional
    :param str pop_name: the name of the pop, optional
    :param str pop_attribute_name: optional
    :param str pop_attribute_value: optional
    :param bool check_mode: not used
    :param bool force: not used
    :return: the returned data
    :rtype: object
    """
    input_args = {
        "admin_id": admin_id,
        "admin_pwd": admin_pwd
    }
    for k, v in kwargs.items():
        if k == 'check_mode':
            continue
        if k == 'force':
            continue
        input_args[k] = v

    ret_obj = isamAppliance.invoke_post("Retrieve a list of protected objects",
                                        "/isam/pdadmin/popfindext/v1",
                                        ignore_error=True,
                                        data=input_args)
    if ret_obj['rc'] == 404:
        logger.info(f"No pops found for your arguments {input_args}")
        return isamAppliance.create_return_object()
    ret_obj['changed'] = False
    return ret_obj


def compare(isamAppliance1, isamAppliance2, isamUser, admin_domain='Default', **kwargs):
    """
    Compare URL Mapping between two appliances
    TODO: THIS IS NOT READY
    """
    ret_obj1 = get_all(isamAppliance1, isamUser=isamUser, admin_domain=admin_domain)
    ret_obj2 = get_all(isamAppliance2, isamUser=isamUser, admin_domain=admin_domain)

    for obj in ret_obj1['data']:
        del obj['version']
        ret_obj = get(isamAppliance1, pop_name=obj['id'], isamUser=isamUser, admin_domain=admin_domain)
        obj['script'] = ret_obj['data']['contents']
    for obj in ret_obj2['data']:
        del obj['version']
        ret_obj = get(isamAppliance2, pop_name=obj['id'], isamUser=isamUser, admin_domain=admin_domain)
        obj['script'] = ret_obj['data']['contents']

    import ibmsecurity.utilities.tools
    return ibmsecurity.utilities.tools.json_compare(ret_obj1, ret_obj2, deleted_keys=['version'])