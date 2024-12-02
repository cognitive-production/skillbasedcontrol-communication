import unittest
import random
from sbc_communication.assetskillscommunication_factory import (
    createAssetSkillCommunication_OpcUa,
    ServerTypes,
)
from sbc_communication.assetskillshandle import AssetSkillsHandle
from sbc_communication.assetskillscommunication import AssetSkillsCommunication

from tests._connection_infos_for_tests import connectionInfo_Python

test_skillname = "AddSkill"


class Test_AssetSkillsHandle(unittest.TestCase):
    def setUp(self):
        self.handle = AssetSkillsHandle(
            assetName="Test",
            assetSkillCommunication=createAssetSkillCommunication_OpcUa(
                serverType=ServerTypes.OPC_UA_Python_Asyncua,
                opc_url=connectionInfo_Python.opc_url,
            ),
        )

    def tearDown(self) -> None:
        self.handle.disconnect()

    def test_create_handle(self):
        self.assertIsNotNone(self.handle)
        self.assertEqual(self.handle.assetName, "Test")
        self.assertIsInstance(self.handle.skillCom, AssetSkillsCommunication)

    def test_connect_disconnect(self):
        self.handle.connect()
        self.assertTrue(self.handle.skillCom.connected)
        self.handle.disconnect()
        self.assertFalse(self.handle.skillCom.connected)

    def test_read_availableSkills(self):
        skilldatahandles = self.handle.read_availableSkills()
        self.assertGreater(len(skilldatahandles), 0)

    def test_get_SkillData_byName(self):
        self.handle.read_availableSkills()
        skilldatahandle = self.handle.get_SkillData_byName(test_skillname)
        self.assertEqual(skilldatahandle.stSkillDataDefault.strName, test_skillname)

    def test_read_stSkillData(self):
        self.handle.read_availableSkills()
        skilldatahandle = self.handle.read_stSkillData(test_skillname)
        self.assertEqual(skilldatahandle.stSkillDataDefault.strName, test_skillname)
