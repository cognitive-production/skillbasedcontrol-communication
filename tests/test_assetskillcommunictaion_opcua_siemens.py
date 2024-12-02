from sbc_communication.assetskillscommunication_factory import (
    createSkillCom_Siemens,
)
from basetestclass_test_assetskillcommunictaion_opcua import (
    Test_assetskillscommunication_opcua,
)
from tests._connection_infos_for_tests import connectionInfo_Siemens


class Test_assetskillscommunication_opcua_siemens(Test_assetskillscommunication_opcua):
    def _instatiateCommObject(cls):
        cls.comm = createSkillCom_Siemens(
            opc_url=connectionInfo_Siemens.opc_url,
            opc_user=connectionInfo_Siemens.opc_user,
            opc_password=connectionInfo_Siemens.opc_password,
            rootNodeId=connectionInfo_Siemens.rootNodeId,
        )
        cls.testSkillName = "AddSkill"
        cls.sumSkillTest = True
