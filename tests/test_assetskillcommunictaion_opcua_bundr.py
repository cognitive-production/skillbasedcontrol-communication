from sbc_communication.assetskillscommunication_factory import (
    createSkillCom_BundR,
)
from basetestclass_test_assetskillcommunictaion_opcua import (
    Test_assetskillscommunication_opcua,
)
from tests._connection_infos_for_tests import connectionInfo_BundR


class Test_assetskillscommunication_opcua_bundr(Test_assetskillscommunication_opcua):
    def _instatiateCommObject(cls):
        cls.comm = createSkillCom_BundR(
            opc_url=connectionInfo_BundR.opc_url,
            opc_user=connectionInfo_BundR.opc_user,
            opc_password=connectionInfo_BundR.opc_password,
            rootNodeId=connectionInfo_BundR.rootNodeId,
        )
        cls.testSkillName = "AddSkill"
        cls.sumSkillTest = True
