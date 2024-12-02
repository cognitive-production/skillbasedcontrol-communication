from typing import Type
import logging

from sbc_statemachine.skilldatahandle import SkillDataHandle
from .assetskillscommunication import AssetSkillsCommunication
from .skillexecutionhandler import SkillExecutionHandler


# implement logging


class AssetSkillsHandle:
    """generate handle for accessing and executing single assets skills"""

    def __init__(
        self,
        assetName: str,
        assetSkillCommunication: AssetSkillsCommunication,
        skillExecutionHandlerClass: Type[SkillExecutionHandler] | None = None,
        logger: logging.Logger | None = None,
    ):
        """generate handle for accessing and executing single assets skills

        Args:
            assetName (str): unique asset name
            assetSkillCommunication (AssetSkillsCommunication): object for skill communication
            logger (Optional[logging.Logger], optional): object for logging. Defaults to None.
        """
        self.assetName = assetName
        self.skillCom = assetSkillCommunication
        self.logger: logging.Logger | None = logger
        if skillExecutionHandlerClass:
            self.skillExecHandler = skillExecutionHandlerClass(skillcom=self.skillCom)
        else:
            self.skillExecHandler = SkillExecutionHandler(self.skillCom)
        self.executeSkill = self.skillExecHandler.executeSkill
        self.resetSkill = self.skillExecHandler.resetSkill

    def connect(self) -> bool:
        """runs connect method of self.assetSkillsCommunication

        Returns:
            bool: True, if successful
        """
        return self.skillCom.connect()

    def disconnect(self) -> bool:
        """runs connect method of self.assetSkillsCommunication

        Returns:
            bool: True, if successful
        """
        return self.skillCom.disconnect()

    def read_availableSkills(self) -> dict[str, SkillDataHandle]:
        """searches available Skills and return names in self.assetSkillsCommunication

        Returns:
            list: list of Skill names or None, if not successful
        """
        if not self.skillCom.connected:
            if not self.skillCom.connect():
                return []
        self.skillCom.searchfor_Skills()
        self.skillCom.read_SkillDatas()
        return self.skillCom.skillDataHandles

    def get_SkillData_byName(self, skillName: str) -> SkillDataHandle:
        """get skillData by skill name

        Args:
            skillName (str): skill name

        Returns:
            SkillData: SkillData or None
        """
        return self.skillCom.skillDataHandles[skillName]

    def read_stSkillData(
        self, skillName: str, readSkillDataDefault=True, readSkillDataCommand=False
    ) -> SkillDataHandle:
        """read skill data structures in skilldata.

        Args:
            skillName (str): skill name
            readSkillDataDefault (bool, optional): read stSkillDataDefault. Defaults to True.
            readSkillDataCommand (bool, optional): read stSkillDataCommand. Defaults to False.

        Returns:
            SkillData: SkillData with newly read skilldata structures or None
        """
        if readSkillDataDefault:
            self.skillCom.read_stSkillData(skillName, useSkillDataDefault=True)
        if readSkillDataCommand:
            self.skillCom.read_stSkillData(skillName, useSkillDataDefault=False)
        return self.get_SkillData_byName(skillName)
