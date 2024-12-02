from asyncua.sync import ua, SyncNode
from sbc_statemachine.skilldatatypes import ST_SkillData, ST_Parameter
from .assetskillscommunication_opcua import (
    AssetSkillsCommunication_OPCUA,
    SkillConnectionNodes,
    OpcUaConnectionInfo,
    ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
)
from ..mapVar import mapVar


class AssetSkillsCommunication_OPCUA_Siemens(AssetSkillsCommunication_OPCUA):
    """OPC UA communication class working for Siemens S7 OPC-UA Server (Simatic S7-1500 OPC UA)
    Inherits form (abstract) AssetSkillsCommunication_OPCUA"""

    def __init__(
        self,
        opcConnectionInfo: OpcUaConnectionInfo,
        opcua_timeout: float = ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
        opcua_session_timeout=30.0,
    ):
        super().__init__(opcConnectionInfo, opcua_timeout)
        # Siemens specific:
        # keep length of plc array in struct, read from server
        self.opcClient.session_timeout = int(opcua_session_timeout * 1000)
        self.plc_parameter_list_count = 0

    def _browseNodes_recursive(
        self,
        node: SyncNode,
        searchname: str,
        searchtype: str,
        browsedepth=0,
        browsedepthmax=3,
    ) -> list[SkillConnectionNodes]:
        """browses opc ua node and childs for specific nodeID and NodType
        TODO: look for better suitable functions in asyncua

        Args:
            node (Node): root node to search of
            searchname (str): snippet of NodeId to search for
            searchtype (str): snippet of NodeType to search for
            browsedepth (int): actual browse depth
            browsedepthmax (int): maximal browse depth

        Returns:
            list: list of skillConnectionNodes
        """
        # Siemens specific:
        # extra quotes "" for searchname, only onces...
        if not searchname.startswith('"') and not searchname.endswith('"'):
            searchname = f'"{searchname}"'
        return super()._browseNodes_recursive(
            node, searchname, searchtype, browsedepth, browsedepthmax
        )

    def read_stSkillData(
        self, skillName: str, useSkillDataDefault=True
    ) -> ST_SkillData:
        """read stSkillDataDefault or stSkillDataCommand of specific skill by communication interface, update SkillData in self.SkillDataHandles

        Args:
            skillName (str): name of skill in self.SkillDataHandles.
            useSkillDataDefault (bool): read stSkillDataDefault or stSkillDataCommand

        Returns:
            ST_SkillData: stSkillDataDefault or stSkillDataCommand as ST_SkillData or None, if not successful
        """
        if useSkillDataDefault:
            setSkillData = self.skillDataHandles[skillName].stSkillDataDefault
            sourceSkillDataNode = self.skillConnectionNodes[
                skillName
            ].skillDataDefaultNode
        else:
            setSkillData = self.skillDataHandles[skillName].stSkillDataCommand
            sourceSkillDataNode = self.skillConnectionNodes[
                skillName
            ].skillDataCommandNode
        skillData = sourceSkillDataNode.read_value()
        # Siemens specific:
        # keep length of array in struct, read from server
        self.plc_parameter_list_count = len(skillData.astParameters)
        setSkillData.astParameters = [
            ST_Parameter() for i in range(skillData.iParameterCount)
        ]
        mapVar(skillData, setSkillData, maxListLength=skillData.iParameterCount)
        return setSkillData

    def write_stSkillData(self, skillName: str, useSkillDataDefault=False) -> bool:
        """write stSkillDataCommand or stSkillDataDefault of specific skill by communication interface

        Args:
            skillname (str): name of skill in self.SkillDatas.
            useSkillDataDefault (bool): write stSkillDataDefault or stSkillDataCommand

        Returns:
            bool: True, if successful
        """

        if useSkillDataDefault:
            skillDataNode = self.skillConnectionNodes[skillName].skillDataDefaultNode
            sourceSkillData = self.skillDataHandles[skillName].stSkillDataDefault
        else:
            skillDataNode = self.skillConnectionNodes[skillName].skillDataCommandNode
            sourceSkillData = self.skillDataHandles[skillName].stSkillDataCommand
        targetSkillData = self.opcUaSkillTypes.ST_SkillData()
        # Siemens specific:
        # length of array in struct, written to server, must be exact!
        # beckhoff server accepts smaller arrays in structs
        targetSkillData.astParameters = [
            self.opcUaSkillTypes.ST_Parameter()
            for i in range(self.plc_parameter_list_count)
        ]
        mapVar(
            sourceSkillData,
            targetSkillData,
            maxListLength=sourceSkillData.iParameterCount,
        )

        skillDataNode.write_value(ua.DataValue(targetSkillData))
        return True

    def write_stSkillData_astParameters(
        self, skillname: str, useSkillDataDefault=False
    ) -> bool:
        """write astParameters of stSkillDataCommand or stSkillDataDefault of specific skill by communication interface

        Args:
            skillname (str): name of skill in self.SkillDatas.
            useSkillDataDefault (bool): read stSkillDataDefault or stSkillDataCommand

        Returns:
            bool: True, if successful
        """
        if useSkillDataDefault:
            skillDataParameterNode = self.skillConnectionNodes[
                skillname
            ].skillDataDefaultNode.get_child(
                f"{self.opcUaNameSpaceIndex}:astParameters"
            )
            sourceSkillData = self.skillDataHandles[skillname].stSkillDataDefault
        else:
            skillDataParameterNode = self.skillConnectionNodes[
                skillname
            ].skillDataCommandNode.get_child(
                f"{self.opcUaNameSpaceIndex}:astParameters"
            )
            sourceSkillData = self.skillDataHandles[skillname].stSkillDataCommand

        # if no parameters then return
        if sourceSkillData.iParameterCount <= 0:
            return True
        sourceSkillDataParameters = sourceSkillData.astParameters
        # Siemens specific:
        # length of array in struct, written to server, must be exact!
        # beckhoff server accepts smaller arrays in structs
        targetskillDataParameter = [
            self.opcUaSkillTypes.ST_Parameter()
            for i in range(self.plc_parameter_list_count)
        ]
        mapVar(
            sourceSkillDataParameters,
            targetskillDataParameter,
            maxListLength=sourceSkillData.iParameterCount,
        )
        skillDataParameterNode.write_value(ua.DataValue(targetskillDataParameter))
        return True

    def get_SkillConnectionNodes(
        self, skillNode: SyncNode, nodeId: str
    ) -> SkillConnectionNodes:
        """get nodes to skill internal structures: ST_SkillState, ST_SkillCommand, ST_SkillDataDefault, ST_SkillDataCommand.

        Args:
            skillNode (Node): node to skill

        Returns:
            SkillConnectionNodes: object containing connection nodes.
        """
        # Siemens specific:
        # skill structs are nested in "Inputs" / "Outputs" nodes
        # create correct skill node id, then get SkillConnectionNodes directly by NodeId
        # Disadvantage: less secure than get_child, more "hard coded"
        if skillNode.nodeid.Identifier.endswith(".Outputs"):
            nodeid = f'ns=3;s={skillNode.nodeid.Identifier.replace(".Outputs", "")}'
            skillNode = self.opcClient.get_node(nodeid)
        if skillNode.nodeid.Identifier.endswith(".Inputs"):
            nodeid = f'ns=3;s={skillNode.nodeid.Identifier.replace(".Inputs", "")}'
            skillNode = self.opcClient.get_node(nodeid)
        return SkillConnectionNodes(
            nodeId=nodeId,
            skillNode=skillNode,
            skillStateNode=self.opcClient.get_node(nodeid + '."stSkillState"'),
            skillCommandNode=self.opcClient.get_node(nodeid + '."stSkillCommand"'),
            skillDataDefaultNode=self.opcClient.get_node(
                nodeid + '."stSkillDataDefault"'
            ),
            skillDataCommandNode=self.opcClient.get_node(
                nodeid + '."stSkillDataCommand"'
            ),
        )
