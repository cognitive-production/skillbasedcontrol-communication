import unittest
from sbc_communication.opcua.assetskillscommunication_opcua import (
    OpcUaConnectionInfo,
    AssetSkillsCommunication_OPCUA,
)
from sbc_communication.assetskillscommunication_factory import (
    createAssetSkillCommunication_byConfigDict,
    createAssetSkillCommunication_OpcUa,
    getServerTypeFromOpcUaServer,
    createAssetSkillCommunication_OpcUa_WithUser_Basic256Sha256Security,
    createAssetSkillCommunication_OpcUa_Anonymous_Basic256Sha256Security,
    createAssetSkillCommunication_OpcUa_WithUser_NoSecurity,
    createAssetSkillCommunication_OpcUa_Anonymous_NoSecurity,
    ServerTypes,
)
from tests._connection_infos_for_tests import connectionInfo_Python


class Test_assetskillscommunication_factory(unittest.TestCase):
    Test_Endpoint_Url = connectionInfo_Python.opc_url

    def test_createAssetSkillCommunication_byConfigDict(self):
        configDict = {
            "serverType": ServerTypes.OPC_UA_Python_Asyncua,
            "opc_url": self.Test_Endpoint_Url,
        }
        comm: AssetSkillsCommunication_OPCUA = (
            createAssetSkillCommunication_byConfigDict(configDict)
        )
        self.assertIsInstance(comm, AssetSkillsCommunication_OPCUA)
        self.assertEqual(comm.opcConnectionInfo.opc_url, self.Test_Endpoint_Url)

    def test_createAssetSkillCommunication_OpcUa(self):
        comm = createAssetSkillCommunication_OpcUa(
            ServerTypes.OPC_UA_Python_Asyncua, opc_url=self.Test_Endpoint_Url
        )
        self.assertIsInstance(comm, AssetSkillsCommunication_OPCUA)
        self.assertEqual(comm.opcConnectionInfo.opc_url, self.Test_Endpoint_Url)

    def test_getServerTypeFromOpcUaServer(self):
        serverType = getServerTypeFromOpcUaServer(
            OpcUaConnectionInfo(opc_url=self.Test_Endpoint_Url)
        )
        assert isinstance(serverType, ServerTypes)
        assert serverType == ServerTypes.OPC_UA_Python_Asyncua

    def test_createAssetSkillCommunication_OpcUa_WithUser_Basic256Sha256Security(self):
        comm = createAssetSkillCommunication_OpcUa_WithUser_Basic256Sha256Security(
            ServerTypes.OPC_UA_Python_Asyncua,
            opc_url=self.Test_Endpoint_Url,
            opc_user="User1",
            opc_password="User1",
        )
        self.assertIsInstance(comm, AssetSkillsCommunication_OPCUA)
        self.assertEqual(comm.opcConnectionInfo.opc_url, self.Test_Endpoint_Url)

    def test_createAssetSkillCommunication_OpcUa_Anonymous_Basic256Sha256Security(self):
        comm = createAssetSkillCommunication_OpcUa_Anonymous_Basic256Sha256Security(
            ServerTypes.OPC_UA_Python_Asyncua, opc_url=self.Test_Endpoint_Url
        )
        self.assertIsInstance(comm, AssetSkillsCommunication_OPCUA)
        self.assertEqual(comm.opcConnectionInfo.opc_url, self.Test_Endpoint_Url)

    def test_createAssetSkillCommunication_OpcUa_WithUser_NoSecurity(self):
        comm = createAssetSkillCommunication_OpcUa_WithUser_NoSecurity(
            ServerTypes.OPC_UA_Python_Asyncua,
            opc_url=self.Test_Endpoint_Url,
            opc_user="User1",
            opc_password="User1",
        )
        self.assertIsInstance(comm, AssetSkillsCommunication_OPCUA)
        self.assertEqual(comm.opcConnectionInfo.opc_url, self.Test_Endpoint_Url)

    def test_createAssetSkillCommunication_OpcUa_Anonymous_NoSecurity(self):
        comm = createAssetSkillCommunication_OpcUa_Anonymous_NoSecurity(
            ServerTypes.OPC_UA_Python_Asyncua,
            opc_url=self.Test_Endpoint_Url,
        )
        self.assertIsInstance(comm, AssetSkillsCommunication_OPCUA)
        self.assertEqual(comm.opcConnectionInfo.opc_url, self.Test_Endpoint_Url)
