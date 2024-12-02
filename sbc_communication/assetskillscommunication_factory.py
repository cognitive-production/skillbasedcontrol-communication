import enum
from functools import partial
from typing import Type
import json
from asyncua.sync import SyncNode

from .assetskillscommunication import (
    AssetSkillsCommunication,
    AssetSkillsComConnectionInfo,
)
from .opcua.assetskillscommunication_opcua import (
    AssetSkillsCommunication_OPCUA,
    OpcUaConnectionInfo,
    ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
)
from . import opcua


class ServerTypes(enum.IntEnum):
    """Enum for representing different server types for asset skill communication"""

    OPC_UA_Beckhoff = 0
    OPC_UA_Siemens = 1
    OPC_UA_Python_Asyncua = 2
    OPC_UA_BundR = 3


# dict mapping server types to AssetSkillCommunication classes
ServerTypesToClass = {
    ServerTypes.OPC_UA_Beckhoff: opcua.assetskillscommunication_opcua_beckhoff.AssetSkillsCommunication_OPCUA_Beckhoff,
    ServerTypes.OPC_UA_Siemens: opcua.assetskillscommunication_opcua_siemens.AssetSkillsCommunication_OPCUA_Siemens,
    ServerTypes.OPC_UA_Python_Asyncua: opcua.assetskillscommunication_opcua_python_asyncua.AssetSkillsCommunication_OPCUA_Python_Asyncua,
    ServerTypes.OPC_UA_BundR: opcua.assetskillscommunication_opcua_bundr.AssetSkillsCommunication_OPCUA_BundR,
}

# list of keywords for searching server type by manufacturer informations
OpcUaServerManufacturerToType = [
    (["beckhoff"], ServerTypes.OPC_UA_Beckhoff),
    (["siemens"], ServerTypes.OPC_UA_Siemens),
    (["freeopcua", "free"], ServerTypes.OPC_UA_Python_Asyncua),
    (["b&r", "bundr"], ServerTypes.OPC_UA_BundR),
]

Basic256Sha256 = "Basic256Sha256"
SignAndEncrypt = "SignAndEncrypt"


def createAssetSkillCommunication_OpcUa(
    serverType: ServerTypes | int | None = None,
    opc_url: str = "opc.tcp://127.0.0.1:4840",
    opc_user: str | None = None,
    opc_password: str | None = None,
    opc_security_policy: str | None = None,
    opc_security_mode: str | None = None,
    rootNodeId: str | list[str] | None = None,
    searchSkillsBrowseDepthMax: int = 3,
    opcua_timeout: float = ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
) -> AssetSkillsCommunication_OPCUA | None:
    """get AssetSkillsCommunication_OPCUA instance to connect to opcua endpoint

    Args:
        serverType (ServerTypes | int | None, optional): serverType, if None try to find by connecting to server. Defaults to None.
        opc_url (str, optional): opcua endpoint url. Defaults to "opc.tcp://127.0.0.1:4840".
        opc_user (str | None, optional): opc ua user. Defaults to None.
        opc_password (str | None, optional): opc ua password. Defaults to None.
        opc_security_policy (str | None, otpional): opc ua security policy: Basic256Sha256, .... Defaults to None.
        opc_security_mode  (str | None, optional):opc ua security mode: SignAndEncrypt, .... Defaults to None.
        rootNodeId (str | list[str] | None, optional): root node id for start searching skills. Defaults to None.
        searchSkillsBrowseDepthMax (int, optional): maximal browse depth from rootNodeId for searching skills. Defaults to 3.
        opcua_timeout (float, optional): opc client connection timeout. Defaults to ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT

    Returns:
        Optional[AssetSkillsCommunication_OPCUA]: server type specific opc ua skill com object
    """
    opcConnectionInfo = OpcUaConnectionInfo(
        opc_url=opc_url,
        opc_user=opc_user,
        opc_password=opc_password,
        opc_security_policy=opc_security_policy,
        opc_security_mode=opc_security_mode,
        rootNodeId=rootNodeId,
        searchSkillsBrowseDepthMax=searchSkillsBrowseDepthMax,
    )
    if serverType is None:
        serverType = getServerTypeFromOpcUaServer(opcConnectionInfo)
    commClass = _create_AssetSkillsCommunication_Class(serverType)
    if issubclass(commClass, AssetSkillsCommunication_OPCUA):
        return commClass(
            opcConnectionInfo=opcConnectionInfo, opcua_timeout=opcua_timeout
        )
    else:
        return None


def createAssetSkillCommunication_OpcUa_Anonymous_NoSecurity(
    serverType: ServerTypes | int | None = None,
    opc_url: str = "opc.tcp://127.0.0.1:4840",
    rootNodeId: str | list[str] | None = None,
    searchSkillsBrowseDepthMax: int = 3,
    opcua_timeout: float = ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
) -> AssetSkillsCommunication_OPCUA:
    """get AssetSkillsCommunication_OPCUA instance to connect no User and NoSecurity opc endpoint

    Args:
        serverType (ServerTypes | int | None, optional): serverType, if None try to find by connecting to server. Defaults to None.
        opc_url (str, optional): opcua endpoint url. Defaults to "opc.tcp://127.0.0.1:4840".
        rootNodeId (str | list[str] | None, optional): root node id for start searching skills. Defaults to None.
        searchSkillsBrowseDepthMax (int, optional): maximal browse depth from rootNodeId for searching skills. Defaults to 3.
        opcua_timeout (float, optional): opc client connection timeout. Defaults to ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT

    Returns:
        AssetSkillsCommunication_OPCUA: server type specific opc ua skill com object
    """
    return createAssetSkillCommunication_OpcUa(
        serverType=serverType,
        opc_url=opc_url,
        rootNodeId=rootNodeId,
        searchSkillsBrowseDepthMax=searchSkillsBrowseDepthMax,
        opcua_timeout=opcua_timeout,
    )


def createAssetSkillCommunication_OpcUa_WithUser_NoSecurity(
    serverType: ServerTypes | int | None = None,
    opc_url: str = "opc.tcp://127.0.0.1:4840",
    opc_user: str | None = None,
    opc_password: str | None = None,
    rootNodeId: str | list[str] | None = None,
    searchSkillsBrowseDepthMax: int = 3,
    opcua_timeout: float = ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
) -> AssetSkillsCommunication_OPCUA:
    """get AssetSkillsCommunication_OPCUA instance to connect wit User but NoSecurity opc endpoint

    Args:
        serverType (ServerTypes | int | None, optional): serverType, if None try to find by connecting to server. Defaults to None.
        opc_url (str, optional): opcua endpoint url. Defaults to "opc.tcp://127.0.0.1:4840".
        opc_user (str | None, optional): opc ua user. Defaults to None.
        opc_password (str | None, optional): opc ua password. Defaults to None.
        rootNodeId (str | list[str] | None, optional): root node id for start searching skills. Defaults to None.
        searchSkillsBrowseDepthMax (int, optional): maximal browse depth from rootNodeId for searching skills. Defaults to 3.
        opcua_timeout (float, optional): opc client connection timeout. Defaults to ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT

    Returns:
        AssetSkillsCommunication_OPCUA: server type specific opc ua skill com object
    """
    return createAssetSkillCommunication_OpcUa(
        serverType=serverType,
        opc_url=opc_url,
        opc_user=opc_user,
        opc_password=opc_password,
        rootNodeId=rootNodeId,
        searchSkillsBrowseDepthMax=searchSkillsBrowseDepthMax,
        opcua_timeout=opcua_timeout,
    )


def createAssetSkillCommunication_OpcUa_Anonymous_Basic256Sha256Security(
    serverType: ServerTypes | int | None = None,
    opc_url: str = "opc.tcp://127.0.0.1:4840",
    rootNodeId: str | list[str] | None = None,
    searchSkillsBrowseDepthMax: int = 3,
    opcua_timeout: float = ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
) -> AssetSkillsCommunication_OPCUA:
    """get AssetSkillsCommunication_OPCUA instance to connect with no User but Basic256Sha256 Security opc endpoint

    Args:
        serverType (ServerTypes | int | None, optional): serverType, if None try to find by connecting to server. Defaults to None.
        opc_url (str, optional): opcua endpoint url. Defaults to "opc.tcp://127.0.0.1:4840".
        rootNodeId (str | list[str] | None, optional): root node id for start searching skills. Defaults to None.
        searchSkillsBrowseDepthMax (int, optional): maximal browse depth from rootNodeId for searching skills. Defaults to 3.
        opcua_timeout (float, optional): opc client connection timeout. Defaults to ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT

    Returns:
        AssetSkillsCommunication_OPCUA: server type specific opc ua skill com object
    """
    return createAssetSkillCommunication_OpcUa(
        serverType=serverType,
        opc_url=opc_url,
        opc_security_policy=Basic256Sha256,
        opc_security_mode=SignAndEncrypt,
        rootNodeId=rootNodeId,
        searchSkillsBrowseDepthMax=searchSkillsBrowseDepthMax,
        opcua_timeout=opcua_timeout,
    )


def createAssetSkillCommunication_OpcUa_WithUser_Basic256Sha256Security(
    serverType: ServerTypes | int | None = None,
    opc_url: str = "opc.tcp://127.0.0.1:4840",
    opc_user: str | None = None,
    opc_password: str | None = None,
    rootNodeId: str | list[str] | None = None,
    searchSkillsBrowseDepthMax: int = 3,
    opcua_timeout: float = ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
) -> AssetSkillsCommunication_OPCUA:
    """get AssetSkillsCommunication_OPCUA instance to connect with User and Basic256Sha256 Security opc endpoint

    Args:
        serverType (ServerTypes | int | None, optional): serverType, if None try to find by connecting to server. Defaults to None.
        opc_url (str, optional): opcua endpoint url. Defaults to "opc.tcp://127.0.0.1:4840".
        opc_user (str | None, optional): opc ua user. Defaults to None.
        opc_password (str | None, optional): opc ua password. Defaults to None.
        rootNodeId (str | list[str] | None, optional): root node id for start searching skills. Defaults to None.
        searchSkillsBrowseDepthMax (int, optional): maximal browse depth from rootNodeId for searching skills. Defaults to 3.
        opcua_timeout (float, optional): opc client connection timeout. Defaults to ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT

    Returns:
        AssetSkillsCommunication_OPCUA: server type specific opc ua skill com object
    """
    return createAssetSkillCommunication_OpcUa(
        serverType=serverType,
        opc_url=opc_url,
        opc_user=opc_user,
        opc_password=opc_password,
        opc_security_policy=Basic256Sha256,
        opc_security_mode=SignAndEncrypt,
        rootNodeId=rootNodeId,
        searchSkillsBrowseDepthMax=searchSkillsBrowseDepthMax,
        opcua_timeout=opcua_timeout,
    )


def createAssetSkillCommunication_byConfigDict(
    configDict: dict,
) -> AssetSkillsCommunication | None:
    """get AssetSkillsCommunication instance to connect to endpoint

    Args:
        configDict (dict): dictionary containing the connection info, see OpcUaConnectionInfo

    Returns:
        Optional[AssetSkillsCommunication]: server type specific skill com object
    """
    commClass = _create_AssetSkillsCommunication_Class(configDict["serverType"])
    if issubclass(commClass, AssetSkillsCommunication_OPCUA):
        return commClass(
            OpcUaConnectionInfo(
                opc_url=configDict["opc_url"],
                opc_user=(configDict["opc_user"] if "opc_user" in configDict else None),
                opc_password=(
                    configDict["opc_password"] if "opc_password" in configDict else None
                ),
                opc_security_policy=(
                    configDict["opc_security_policy"]
                    if "opc_security_policy" in configDict
                    else None
                ),
                opc_security_mode=(
                    configDict["opc_security_mode"]
                    if "opc_security_mode" in configDict
                    else None
                ),
                opc_certificate_filepath=(
                    configDict["opc_certificate_filepath"]
                    if "opc_certificate_filepath" in configDict
                    else None
                ),
                opc_private_key_filepath=(
                    configDict["opc_private_key_filepath"]
                    if "opc_private_key_filepath" in configDict
                    else None
                ),
                rootNodeId=(
                    configDict["rootNodeId"] if "rootNodeId" in configDict else None
                ),
                searchSkillsBrowseDepthMax=(
                    configDict["searchSkillsBrowseDepthMax"]
                    if "searchSkillsBrowseDepthMax" in configDict
                    else 3
                ),
            )
        )
    else:
        return None


def createAssetSkillCommunication_byConfigJsonFile(
    configJsonFilePath: str,
) -> AssetSkillsCommunication:
    """get AssetSkillsCommunication instance to connect to endpoint

    Args:
        configJsonFilePath (str): filepath to json file containing the connection info, see OpcUaConnectionInfo

    Returns:
        Optional[AssetSkillsCommunication]: server type specific skill com object
    """
    with open(configJsonFilePath, "r") as configJsonFile:
        configDict = json.load(configJsonFile)
        return createAssetSkillCommunication_byConfigDict(configDict)


def createAssetSkillCommunication(
    serverType: ServerTypes | int,
    connectionInfo: AssetSkillsComConnectionInfo,
) -> AssetSkillsCommunication | None:
    """get AssetSkillsCommunication instance to connect to asset endpoint

    Args:
        serverType (ServerTypes): serverType
        connectionInfo (AssetSkillsComConnectionInfo): Connection Info

    Returns:
        Optional[AssetSkillsCommunication]: server type specific skill com object
    """
    commClass = _create_AssetSkillsCommunication_Class(serverType)
    if issubclass(commClass, AssetSkillsCommunication):
        return commClass(connectionInfo)
    else:
        return None


def _create_AssetSkillsCommunication_Class(
    serverType: ServerTypes | int,
) -> Type[AssetSkillsCommunication]:
    """get specific skill com class by serverType

    Args:
        serverType (ServerTypes | int): serverType

    Raises:
        NotImplementedError: if no corresponding com class is found with serverType

    Returns:
        Type[AssetSkillsCommunication]: server type specific skill com class
    """
    serverType = ServerTypes(serverType)
    if serverType in ServerTypesToClass:
        return ServerTypesToClass[serverType]
    else:
        raise NotImplementedError(
            "Cant find AssetSkillsCommunication_Class for server type {serverType}"
        )


def getServerTypeFromOpcUaServer(
    opcConnectionInfo: OpcUaConnectionInfo,
) -> ServerTypes | None:
    """get ServerType by connecting to opc ua server and look for ManufactureName

    Args:
        opcConnectionInfo (OpcUaConnectionInfo): opc ua connection info

    Returns:
        Optional[ServerTypes]: serverType or None
    """
    comm = AssetSkillsCommunication_OPCUA(opcConnectionInfo)
    comm.opcClient.set_security_string(comm.opc_security_string)
    comm.opcClient.connect()
    manufactureNameNode: SyncNode = comm.opcClient.get_node("i=2263")
    manufactureName = manufactureNameNode.read_value()
    for pair in OpcUaServerManufacturerToType:
        for name in pair[0]:
            if name.lower() in manufactureName.lower():
                comm.opcClient.disconnect()
                return pair[1]
    else:
        comm.opcClient.disconnect()
        return None


# set additional vendor specific functions
createSkillCom_Beckhoff = partial(
    createAssetSkillCommunication_OpcUa_WithUser_Basic256Sha256Security,
    serverType=ServerTypes.OPC_UA_Beckhoff,
)

createSkillCom_Siemens = partial(
    createAssetSkillCommunication_OpcUa_WithUser_Basic256Sha256Security,
    serverType=ServerTypes.OPC_UA_Siemens,
)

createSkillCom_Python_Asyncua = partial(
    createAssetSkillCommunication_OpcUa_Anonymous_NoSecurity,
    serverType=ServerTypes.OPC_UA_Python_Asyncua,
)

createSkillCom_BundR = partial(
    createAssetSkillCommunication_OpcUa_WithUser_Basic256Sha256Security,
    serverType=ServerTypes.OPC_UA_BundR,
)
