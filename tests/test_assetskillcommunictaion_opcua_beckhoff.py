from sbc_communication.assetskillscommunication_factory import (
    createSkillCom_Beckhoff,
)

from basetestclass_test_assetskillcommunictaion_opcua import (
    Test_assetskillscommunication_opcua,
)
from tests._connection_infos_for_tests import connectionInfo_Beckhoff


class Test_assetskillscommunication_opcua_beckhoff(Test_assetskillscommunication_opcua):
    def _instatiateCommObject(cls):
        cls.comm = createSkillCom_Beckhoff(
            opc_url=connectionInfo_Beckhoff.opc_url,
            opc_user=connectionInfo_Beckhoff.opc_user,
            opc_password=connectionInfo_Beckhoff.opc_password,
            rootNodeId=connectionInfo_Beckhoff.rootNodeId,
        )
        cls.testSkillName = "SumSkill"
        cls.sumSkillTest = True
