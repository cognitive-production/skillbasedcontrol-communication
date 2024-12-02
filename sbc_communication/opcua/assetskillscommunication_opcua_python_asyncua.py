from asyncua.sync import ua
from sbc_statemachine.skilldatatypes import ST_SkillCommand
from .assetskillscommunication_opcua import (
    AssetSkillsCommunication_OPCUA,
    OpcUaConnectionInfo,
    ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
)


class AssetSkillsCommunication_OPCUA_Python_Asyncua(AssetSkillsCommunication_OPCUA):
    """OPC UA communication class working for Python asyncua server (v1.1.*)
    Inherits form (abstract) AssetSkillsCommunication_OPCUA"""

    # Problem with opc ua types ST_SkillCommand, ST_SkillState: default bool values are True!
    # must be set to False after instatiating specific ua datatype
    # couldnt find solution on python opc ua server side, cant find code location for setting default value of bool
    # editing ua datatype after load_data_type_definitions doesnt work,
    # cause constructor (default_factory of dataclass fields) ist hard coded inside ua (code string generated)

    def __init__(
        self,
        opcConnectionInfo: OpcUaConnectionInfo,
        opcua_timeout: float = ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
    ):
        super().__init__(opcConnectionInfo, opcua_timeout)
        self.opcUaNameSpaceIndex = 0

    def read_stSkillState_member(self, skillName: str, member: str):
        """read specific member from stSkillState of specific skill by communication interface

        Args:
            skillName (str): name of skill in self.SkillDatas.
            member (str): membername of ST_SkillState

        Returns:
            str, int, ...: Skillstate member value or None, if not successful
        """
        if not hasattr(self.skillDataHandles[skillName].stSkillState, member):
            return None

        skillStateNodeValue = self.skillConnectionNodes[
            skillName
        ].skillStateNode.read_value()

        return getattr(skillStateNodeValue, member)

    def write_SingleSkillCommand(self, skillname: str, skillCommand: str) -> bool:
        """write single stSkillCommand (Start, Reset, ...) of specific skill by communication interface

        Args:
            skillname (str): name of skill in self.SkillDatas.
            SkillCommand (dict): dictionary with single command, like "Start", "Reset", "Offline" (see skilltypes ST_SkillCommand_State and ST_SkillCommand_Mode)

        Returns:
            bool: True if successful
        """
        stSkillCommand = self.opcUaSkillTypes.ST_SkillCommand()
        self.reset_ST_DataType_object_bools(stSkillCommand)
        if (
            isinstance(skillCommand, str)
            and skillCommand in ST_SkillCommand().stCommand_State.__dict__
        ):
            setattr(stSkillCommand.stCommand_State, skillCommand, True)
        elif (
            isinstance(skillCommand, str)
            and skillCommand in ST_SkillCommand().stCommand_Mode.__dict__
        ):
            setattr(stSkillCommand.stCommand_Mode, skillCommand, True)
        else:
            return False
        self.skillConnectionNodes[skillname].skillCommandNode.write_value(
            ua.DataValue(stSkillCommand)
        )
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
        # must write complete ST_SkillData on python opc ua server
        return self.write_stSkillData(skillname, useSkillDataDefault)

    def reset_ST_DataType_object_bools(self, obj: object):
        """resets bool values in obj to False, recursive calling inside.

        Args:
            obj (object): object with bools inside

        Returns:
            _type_: object (reference)
        """
        _dict = obj.__dict__
        for k in _dict.keys():
            if isinstance(_dict[k], bool):
                _dict[k] = False
            elif isinstance(_dict[k], object):
                self.reset_ST_DataType_object_bools(_dict[k])
        return object
