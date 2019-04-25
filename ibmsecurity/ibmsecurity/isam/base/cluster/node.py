import logging
import ibmsecurity.utilities.tools
from ibmsecurity.appliance.ibmappliance import IBMError

logger = logging.getLogger(__name__)


def get_all(isamAppliance, check_mode=False, force=False):
    """
    List the current nodes in the cluster
    """
    return isamAppliance.invoke_get("List the current nodes in the cluster",
                                    "/isam/cluster/nodes/v1")


def get_id(isamAppliance, check_mode=False, force=False):
    """
    Retrieve the cluster identifier
    """
    return isamAppliance.invoke_get("Retrieve the cluster identifier",
                                    "/isam/cluster/id/v2")


def get_default_id(isamAppliance, check_mode=False, force=False):
    """
    Retrieve the default cluster identifier of the instance
    """
    return isamAppliance.invoke_get("Retrieve the cluster identifier",
                                    "/isam/cluster/id/default/v2")


def get_state(isamAppliance, cluster_id, check_mode=False, force=False):
    """
    Get the state of the given cluster ID to check whether it is valid.
    """
    if not cluster_id:
        return isamAppliance.create_return_object()
    return isamAppliance.invoke_get("Get the state of the given cluster ID",
                                    "/isam/cluster/id/address/{0}/state/v2".format(cluster_id))


def get_master(isamAppliance, check_mode=False, force=False):
    """
    Check if the node is the primary master
    """
    return isamAppliance.invoke_get("Check if the node is the primary master",
                                    "/isam/cluster/ismaster/v2")


def add_v2(isamAppliance, signature_file, cluster_id=None, restricted=False,
           check_mode=False, force=False):
    """
    Add a node to the cluster v2, accepting IP or hostname as cluster ID.
    If the cluster ID is not given, it falls back to the legacy behavior,
    to use the default address as the cluster ID.
    :param isamAppliance: The ISAM appliance to be added to the cluster.
    :param signature_file: The signature file to be used to join the cluster.
    :param cluster_id: The cluster ID to be used by the target node.
                        Could be a hostname or an IP address.
    :param restricted: Whether it is a restricted node.
    :return: True if succeeded.
    """

    if check_mode is True:
        return isamAppliance.create_return_object(changed=True)
    else:
        return isamAppliance.invoke_post_files(
            "Add a node to the cluster v2",
            "/isam/cluster/nodes/v2",
            [
                {
                    'file_formfield': 'signature_file',
                    'filename': signature_file,
                    'mimetype': 'application/octet-stream'
                }
            ],
            {'restricted': restricted,
             'signature_file': open(signature_file, 'rb'),
             'address': cluster_id,
             }, json_response=False)

    return isamAppliance.create_return_object()


def add(isamAppliance, signature_file, restricted=False, check_mode=False, force=False):
    """
    Add a node to the cluster
    """
    id = None
    if force is False:
        try:
            ret_obj = get_id(isamAppliance)
            id = ret_obj['data']['value']
        except IBMError:
            ret_obj = get_default_id(isamAppliance)
            id = ret_obj['data']['address']

    if force is True or _check(isamAppliance, id) is False:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:
            return isamAppliance.invoke_post_files(
                "Add a node to the cluster",
                "/isam/cluster/nodes/v1",
                [
                    {
                        'file_formfield': 'signature_file',
                        'filename': signature_file,
                        'mimetype': 'application/octet-stream'
                    }
                ],
                {'restricted': restricted}, json_response=False)

    return isamAppliance.create_return_object()


def _check(isamAppliance, id):
    ret_obj = get_all(isamAppliance)

    for node in ret_obj['data']:
        if node['address'] == id:
            return True

    return False


def delete(isamAppliance, id, check_mode=False, force=False):
    """
    Remove a node from the cluster
    """
    if force is True or _check(isamAppliance, id) is True:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:
            return isamAppliance.invoke_delete(
                "Remove a node from the cluster",
                "/isam/cluster/nodes/{0}/v1".format(id))

    return isamAppliance.create_return_object()


def compare(isamAppliance1, isamAppliance2):
    """
    Compare cluster nodes between two appliances
    """
    ret_obj1 = get_all(isamAppliance1)
    ret_obj2 = get_all(isamAppliance2)

    return ibmsecurity.utilities.tools.json_compare(ret_obj1, ret_obj2, deleted_keys=[])