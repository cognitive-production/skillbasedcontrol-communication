from sbc_communication.assetskillscommunication_factory import (
    createSkillCom_Python_Asyncua,
)

from basetestclass_test_assetskillcommunictaion_opcua import (
    Test_assetskillscommunication_opcua,
)
from tests._connection_infos_for_tests import connectionInfo_Python


class Test_assetskillscommunication_opcua_python_asyncua(
    Test_assetskillscommunication_opcua
):
    def _instatiateCommObject(cls):
        cls.comm = createSkillCom_Python_Asyncua(
            opc_url=connectionInfo_Python.opc_url,
            rootNodeId=connectionInfo_Python.rootNodeId,
        )
        cls.testSkillName = "AddSkill"
        cls.sumSkillTest = True
