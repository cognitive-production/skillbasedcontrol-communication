import unittest
import random
from sbc_communication.assetskillscommunication_factory import (
    createAssetSkillCommunication_OpcUa,
    ServerTypes,
)
from sbc_communication.assetskillshandle import AssetSkillsHandle
from tests._connection_infos_for_tests import connectionInfo_Python


test_add_skillname = "AddSkill"
test_multireturn_skillname = "MultiReturnSkill"
test_noParam_skillname = "NoParamSkill"


class Test_SkillExecutionHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.assetHandle = AssetSkillsHandle(
            assetName="Test",
            assetSkillCommunication=createAssetSkillCommunication_OpcUa(
                serverType=ServerTypes.OPC_UA_Python_Asyncua,
                opc_url=connectionInfo_Python.opc_url,
            ),
        )
        self.assetHandle.connect()
        self.assetHandle.read_availableSkills()

    def tearDown(self) -> None:
        self.assetHandle.disconnect()

    def test_executeSkillWithParameterList(self):
        parameters = self.assetHandle.get_SkillData_byName(
            test_add_skillname
        ).stSkillDataCommand.astParameters
        num1 = round(random.random(), 10)
        num2 = round(random.random(), 10)
        parameters[0].strValue = str(num1)
        parameters[1].strValue = str(num2)
        parameters[2].strValue = ""
        ret = self.assetHandle.executeSkill(test_add_skillname, parameters)
        self.assertIsInstance(ret, str)
        self.assertEqual(num1 + num2, float(ret))

    def test_executeSkillWithParameterKwargs(self):
        num1 = round(random.random(), 10)
        num2 = round(random.random(), 10)
        ret = self.assetHandle.executeSkill(
            test_add_skillname, Operant1=str(num1), Operant2=str(num2)
        )
        self.assertIsInstance(ret, str)
        self.assertEqual(num1 + num2, float(ret))

    def test_executeSkillWithMultipleReutrns(self):
        ret = self.assetHandle.executeSkill(test_multireturn_skillname)
        self.assertIsInstance(ret, tuple)
        ret = self.assetHandle.executeSkill(
            test_multireturn_skillname, return_as_dict=True
        )
        self.assertIsInstance(ret, dict)
        self.assertEqual(len(ret), 3)

    def test_executeSkillWithNoParameters(self):
        ret = self.assetHandle.executeSkill(test_noParam_skillname)
        self.assertIsNone(ret)
