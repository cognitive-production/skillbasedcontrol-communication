from dataclasses import fields
from asyncua.sync import ua
from sbc_statemachine.skilldatatypes import ST_SkillData, ST_Parameter
from .assetskillscommunication_opcua import (
    AssetSkillsCommunication_OPCUA,
    OpcUaConnectionInfo,
    ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
)
from ..mapVar import mapVar


# TODO: implement and test
class AssetSkillsCommunication_OPCUA_BundR(AssetSkillsCommunication_OPCUA):
    """OPC UA communication class working for B&R OPC UA Servers
    Inherits form (abstract) AssetSkillsCommunication_OPCUA"""

    def __init__(
        self,
        opcConnectionInfo: OpcUaConnectionInfo,
        opcua_timeout: float = ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
    ):
        super().__init__(opcConnectionInfo, opcua_timeout)
        self.opcUaNameSpaceIndex = 6
        self.plc_parameter_list_count = 0

    def loadSkillDataTypes(self) -> bool:
        """loads skill datatypes from opcua server e.g. ST_Parameter*, ...

        Returns:
            bool: True, if all neccessary skill types found
        """
        # no working with skills in python without them...
        uaDataTypes = self.opcClient.load_type_definitions()[1]
        # get Skill datatypes
        skillTypeFields = fields(self.opcUaSkillTypes)
        for dataType in uaDataTypes:
            for skillType in skillTypeFields:
                if skillType.name in dataType:
                    setattr(self.opcUaSkillTypes, skillType.name, uaDataTypes[dataType])
        for skillType in skillTypeFields:
            if getattr(self.opcUaSkillTypes, skillType.name) is None:
                raise TypeError(f"Cant find {skillType.name} type in OPC Ua Server!")
        else:
            return True

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
        # B&R specific:
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
        # B&R specific:
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
        # B&R specific:
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
