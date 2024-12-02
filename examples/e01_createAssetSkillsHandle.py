"""
Example for creating asset skills handle
No skill server endpoint required, just the information
"""

from sbc_communication.assetskillshandle import AssetSkillsHandle
from sbc_communication.assetskillscommunication_factory import (
    createSkillCom_Python_Asyncua,
    createSkillCom_Beckhoff,
    createSkillCom_Siemens,
    createSkillCom_BundR,
)

# with Asset skill communication factory:
# create skill communication object by server type and connection infos
# use helper functions in factory specific to your serverType and opc security:
#    createSkillCom_Beckhoff
#    createSkillCom_Siemens
#    createSkillCom_BundR
#    createAssetSkillCommunication_OpcUa_Anonymous_NoSecurity
#    ...
skillComm = createSkillCom_Python_Asyncua(
    opc_url="opc.tcp://127.0.0.1:4841",
    rootNodeId=["i=85"],
    searchSkillsBrowseDepthMax=2,
)

# create asset skills handle, inject the skill communication object
assetHandle = AssetSkillsHandle(
    assetName="LocalPythonAsset", assetSkillCommunication=skillComm
)
