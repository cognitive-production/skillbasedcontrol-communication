import abc
from dataclasses import dataclass
from sbc_statemachine.skilldatahandle import SkillDataHandle
from sbc_statemachine.skilldatatypes import (
    ST_SkillData,
    ST_Parameter,
    ST_SkillState,
)


@dataclass
class AssetSkillsComConnectionInfo:
    """base class for connection info to AssetSkillsCommunication"""


class AssetSkillsCommunication(abc.ABC):
    """abstract class for handling the communication to multiple skills of one asset / machine."""

    def __init__(self, connectionInfo: AssetSkillsComConnectionInfo):
        self.connectionInfo = connectionInfo
        self.skillDataHandles: dict[str, SkillDataHandle] = {}
        self.connected = False

    @abc.abstractmethod
    def connect(self) -> bool:
        """Activate communication / connect.

        Returns:
            bool: returns True if successful
        """
        raise NotImplementedError

    @abc.abstractmethod
    def checkComm(self) -> bool:
        """Check if the communication has been established correctly
        if not, reset self.connected!

        Returns:
            bool: returns True if successful
        """
        raise NotImplementedError

    @abc.abstractmethod
    def disconnect(self) -> bool:
        """Close communication / disconnect

        Returns:
            bool: returns True if successful
        """
        raise NotImplementedError

    @abc.abstractmethod
    def searchfor_Skills(self) -> int:
        """Searches for Skills in assets and fill the skillDataHandles dict

        Returns:
            int: count of found Skills in asset

        """
        raise NotImplementedError

    def read_SkillDatas(self) -> bool:
        """read all skill data by communication interface, update SkillData in self.skillDataHandles

        Returns:
            bool: returns True if successful
        """
        for skill in self.skillDataHandles:
            self.read_stSkillData(skill, useSkillDataDefault=True)
            self.read_stSkillData(skill, useSkillDataDefault=False)
        return True

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
    def read_stSkillState(self, skillName: str) -> ST_SkillState:
        """read stSkillState of specific skill by communication interface

        Args:
            skillName (str): name of skill in self.SkillDatas.

        Returns:
            ST_SkillState: Skillstate as ST_SkillState or None, if not successful
        """
        raise NotImplementedError

    @abc.abstractmethod
    def read_stSkillState_member(self, skillName: str, member: str):
        """read specific member from stSkillState of specific skill by communication interface

        Args:
            skillName (str): name of skill in self.SkillDatas.
            member (str): membername of ST_SkillState

        Returns:
            str, int, ...: Skillstate member value or None, if not successful
        """
        raise NotImplementedError

    @abc.abstractmethod
    def write_SingleSkillCommand(self, skillname: str, skillCommand: str) -> bool:
        """write single stSkillCommand (Start, Reset, ...) of specific skill by communication interface

        Args:
            skillname (str): name of skill in self.SkillDatas.
            SkillCommand (dict): dictionary with single command, like "Start", "Reset", "Offline" (see skilltypes ST_SkillCommand_State and ST_SkillCommand_Mode)

        Returns:
            bool: True if successful
        """
        raise NotImplementedError

    def write_stSkillData(self, skillName: str, useSkillDataDefault=False) -> bool:
        """write stSkillDataCommand or stSkillDataDefault of specific skill by communication interface

        Args:
            skillname (str): name of skill in self.SkillDatas.
            useSkillDataDefault (bool): write stSkillDataDefault or stSkillDataCommand

        Returns:
            bool: True, if successful
        """
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    def get_SkillNames(self) -> list[str]:
        """get strName of each skill from skillDataHandles

        Returns:
            list: of Skill names (strName)
        """
        return self.skillDataHandles.keys()

    def reset_SkillDataCommand(self, skillName: str, useSkillDataDefault=True) -> bool:
        """resets stSkillDataCommand to stSkillDataDefault

        Args:
            skillname (str): name of skill in self.SkillDatas.
            useSkillDataDefault (bool, optional): call read_SkillDataDefault before resetting

        Returns:
            bool: True, if successful
        """
        if useSkillDataDefault:
            ret = self.read_stSkillData(skillName, useSkillDataDefault=True) is not None
        else:
            ret = True
        if ret:
            self.skillDataHandles[skillName].reset_SkillDataCommand()
        return ret

    def get_stSkillData(
        self, skillName: str, useSkillDataDefault=False
    ) -> ST_SkillData:
        """get a reference to the stSkillData structure from skill by index

        Args:
            skillname (str): name of skill in self.SkillDatas.
            useSkillDataDefault (bool, optional): get from default or command struct. Defaults to False.

        Returns:
            ST_SkillData: reference to stSkillData structure
        """
        if useSkillDataDefault:
            return self.skillDataHandles[skillName].stSkillDataDefault
        else:
            return self.skillDataHandles[skillName].stSkillDataCommand

    def set_stSkillData_astParameters(
        self, skillName: str, parameters: list[ST_Parameter], toSkillDataDefault=False
    ) -> bool:
        """checks and set parameter list to stSkillDataDefault or stSkillDataCommand in SkillDatas.

        Args:
            skillname (str): name of skill in self.SkillDatas.
            parameters (list): skill parameters as list of ST_Parameter()
            toSkillDataDefault (bool, optional): use stSkillDataDefault or stSkillDataCommand. Defaults to False.

        Returns:
            bool: True if successful
        """
        for parameter in parameters:
            if not self.skillDataHandles[skillName].set_Parameter(
                setparam=parameter, toSkillDataDefault=toSkillDataDefault
            ):
                return False
        else:
            return True
