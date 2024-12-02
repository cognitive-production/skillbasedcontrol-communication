import time
from sbc_statemachine.skilldatatypes import (
    ST_SkillState,
    ST_Parameter,
)
from sbc_statemachine.skillstatemachinetypes import ESkillModes, ESkillStates
from .assetskillscommunication import AssetSkillsCommunication


SKILL_RETURN_PARAMETERS_PATTERN = ["return", "result"]


class SkillExecution_Error(Exception): ...
""" base exception for errors while skill execution"""


class SkillState_Error(SkillExecution_Error):
    """error if skill has wrong state informations, inherits form SkillExecution_Error"""

    def __init__(self, stSkillState: ST_SkillState, msg: str):
        self.stSkillState = stSkillState
        super().__init__(msg)


class WrongSkillMode_Error(SkillState_Error):
    """error if skill is in wrong mode, inherits form SkillState_Error"""


class WrongSkillState_Error(SkillState_Error):
    """error if skill is in wrong state, inherits form SkillState_Error"""


class SkillCommandNotEnabled_Error(SkillState_Error):
    """error if skill command is not enabled, inherits form SkillState_Error"""


class SkillStateCommandTimeout_Error(SkillExecution_Error):
    """error if skill command timeouts, inherits from SkillExecution_Error."""


class WrongSkillParameter(SkillExecution_Error):
    """error if parameter doesnt match to skill parameters SkillExecution_Error."""


class SkillExecutionHandler:
    """handles the execution of specific skill in assetskilsshandle"""

    def __init__(
        self,
        skillcom: AssetSkillsCommunication,
        assetSkillsCycleTime: float = 0.1,
        skillExecutionTimeout: float = 0.0,
        skillResettingTimeout: float = 0.0,
    ) -> None:
        """generate SkillExecutionHandler object

        Args:
            skillcom (AssetSkillsCommunication): conencted skill communicaiton object
            assetSkillsCycleTime (float, optional): cycle time of asset skills in seconds. Defaults to 0.1.
            skillExecutionTimeout (float, optional): skill execution timeout value in seconds. Defaults to 0.0.
            skillResettingTimeout (float, optional): skill resetting timeout value in seconds. Defaults to 0.0.
        """
        self.skillcom = skillcom
        self.assetSkillsCycleTime = assetSkillsCycleTime
        self.skillResettingTimeout = skillResettingTimeout
        self.skillExecutionTimeout = skillExecutionTimeout

    def executeSkill(
        self,
        skillName: str,
        parameters: list[ST_Parameter] | None = None,
        stSkillState: ST_SkillState | None = None,
        return_as_dict: bool = False,
        **kwargs,
    ) -> None | str | tuple[str, ...] | dict[str, str]:
        """execute single skill, specified by skillName.
        0. read skill state and check for automatic external mode
        1. reset skill
        2. set and write skill parameters from parameters or **kwargs
        3. write start command
        4. wait for execution completed
        5. read return parameters and return

        Args:
            skillName (str): name of skill to execute
            parameters (list[ST_Parameter] | None, optional): list of typed skill parameters. Defaults to None.
            stSkillState (ST_SkillState | None, optional): skill state structure if already read. Defaults to None.
            return_as_dict (bool, optional): return "result" parameters as dict, not as str or tuple. Defaults to False.
            **kwargs(any, optional): skill parameters as keyword arguments: <parameterName> = <parameterValue>

        Returns:
            None | str | tuple[str, ...] | dict[str, str]: return/result parameters if available
        """
        if not stSkillState:
            stSkillState = self.skillcom.read_stSkillState(skillName)

        # 0: check Automatic_Extern mode
        self._checkAutoamticExternalMode(skillName, stSkillState)

        # 1: reset skill
        self.resetSkill(skillName, stSkillState)

        # check Start command enabled
        if not stSkillState.stCommandEnabled.StartEnabled:
            raise SkillCommandNotEnabled_Error(
                f"Start command is not enabled in skill {skillName}!"
            )

        # 2: set and write skill parameters
        self._2writeSkillParameters(skillName, parameters, **kwargs)

        # 3: write start command
        self.skillcom.write_SingleSkillCommand(skillName, "Start")

        # 4: wait for Completed or other held, Stopped, ABorted...
        self._4waitForSkillExecution(skillName, stSkillState)

        # 5: get sill return / result parameters
        return self._5getSkillReturnParameters(skillName, return_as_dict)

    def resetSkill(
        self, skillName: str, stSkillState: ST_SkillState | None = None
    ) -> None:
        """resets skill, if skill is in completed, stopped or aborted state.

        Args:
            skillName (str): name of skill to reset
            stSkillState (ST_SkillState | None, optional): skill state if already read. Defaults to None.
        """
        # get actual SkillState
        if not stSkillState:
            stSkillState = self.skillcom.read_stSkillState(skillName)

        # check Automatic_Extern mode
        self._checkAutoamticExternalMode(skillName, stSkillState)

        # check already resetted, idle state
        if stSkillState.eActiveState == ESkillStates.Idle.value:
            return

        # check Completed, Stopped or Aborted state
        if not (
            stSkillState.eActiveState == ESkillStates.Completed.value
            or stSkillState.eActiveState == ESkillStates.Stopped.value
            or stSkillState.eActiveState == ESkillStates.Aborted.value
        ):
            raise WrongSkillState_Error(
                stSkillState,
                f"Skill {skillName} is not in Completed, Stopped or Aborted and therefore cant be resetted! Skill is in {stSkillState.strActiveState} state.",
            )
        # check Reset command enabled
        if not stSkillState.stCommandEnabled.ResetEnabled:
            raise SkillCommandNotEnabled_Error(
                stSkillState, f"Reset command is not enabled in skill {skillName}!"
            )
        # write reset command
        self.skillcom.write_SingleSkillCommand(skillName, "Reset")
        # wait for idle
        self._wait_for_skillStates(
            skillName, [ESkillStates.Idle], stSkillState, self.skillResettingTimeout
        )

    def _checkAutoamticExternalMode(
        self, skillName: str, stSkillState: ST_SkillState | None = None
    ):
        # get actual SkillState
        if not stSkillState:
            stSkillState = self.skillcom.read_stSkillState(skillName)
        # check Automatic_Extern mode
        if not stSkillState.eActiveMode == ESkillModes.Automatic_External.value:
            raise WrongSkillMode_Error(
                stSkillState,
                f"Skill {skillName} is not in Automatic_External mode, is {stSkillState.strActiveMode}",
            )

    def _wait_for_skillStates(
        self,
        skillName: str,
        skillStates: list[ESkillStates],
        stSkillState: ST_SkillState | None = None,
        timeout: float = 0.0,
    ) -> None:
        if not stSkillState:
            stSkillState: ST_SkillState = self.skillcom.read_stSkillState(skillName)
        skillStatesValues = [skillState.value for skillState in skillStates]
        resetStartTime = time.perf_counter()
        checkState = stSkillState.eActiveState in skillStatesValues
        while not checkState:
            time.sleep(self.assetSkillsCycleTime)
            stSkillState: ST_SkillState = self.skillcom.read_stSkillState(skillName)
            checkState = stSkillState.eActiveState in skillStatesValues
            if timeout > 0 and time.perf_counter() - resetStartTime > timeout:
                raise SkillStateCommandTimeout_Error(
                    f"Timout while waiting for {skillStates} state in skill {skillName}, after {timeout} seconds skill is in {stSkillState.eActiveState} state"
                )

    def _2writeSkillParameters(
        self, skillName: str, parameters: list[ST_Parameter] | None = None, **kwargs
    ):
        if parameters:
            if not self.skillcom.set_stSkillData_astParameters(
                skillName, parameters=parameters
            ):
                raise WrongSkillParameter(
                    f"Cant set parameters to skill {skillName}: {parameters=}"
                )
        # iterate kwargs parameters
        for key, value in kwargs.items():
            param = self.skillcom.skillDataHandles[skillName].get_Parameter_byName(
                parameterName=key, fromSkillDataDefault=False
            )
            if param is not None:
                param.strValue = str(value)
        if not self.skillcom.write_stSkillData_astParameters(skillName):
            raise WrongSkillParameter(
                f"Cant write parameters to skill {skillName}: {parameters=}"
            )

    def _4waitForSkillExecution(self, skillName: str, stSkillState: ST_SkillState):
        self._wait_for_skillStates(
            skillName,
            [
                ESkillStates.Completed,
                ESkillStates.Aborted,
                ESkillStates.Stopped,
                ESkillStates.Held,
            ],
            stSkillState,
            self.skillExecutionTimeout,
        )
        # check held, stopped, aborted, completed
        match stSkillState.eActiveState:
            case ESkillStates.Aborted.value:
                raise WrongSkillState_Error(
                    stSkillState,
                    f"Skill {skillName} switched to Aborted state after Start command",
                )
            case ESkillStates.Stopped.value:
                raise WrongSkillState_Error(
                    stSkillState,
                    f"Skill {skillName} switched to Stopped state after Start command",
                )
            case ESkillStates.Held.value:
                # Skill Error -> Hold
                # TODO: Holding handling, wait for skill to be unholded after skill error
                raise WrongSkillState_Error(
                    stSkillState,
                    f"Skill {skillName} switched to Holding state after Start command",
                )
            case ESkillStates.Completed.value:
                # execution finished
                return

    def _5getSkillReturnParameters(
        self,
        skillName: str,
        return_as_dict: bool = False,
    ) -> None | str | tuple[str, ...] | dict[str, str]:
        # first look for SKILL_RETURN_PARAMETERS_PATTERN in default parameters
        return_parameter_exists = False
        for param in self.skillcom.skillDataHandles[
            skillName
        ].stSkillDataDefault.astParameters:
            for pattern in SKILL_RETURN_PARAMETERS_PATTERN:
                if pattern in param.strName.lower():
                    return_parameter_exists = True
                    break
            if return_parameter_exists:
                break
        # no parameters found -> return None
        if not return_parameter_exists:
            return None
        # parameters found
        return_parameters = {}
        # read parameters
        stSkillData = self.skillcom.read_stSkillData(
            skillName=skillName, useSkillDataDefault=False
        )
        for param in stSkillData.astParameters:
            for pattern in SKILL_RETURN_PARAMETERS_PATTERN:
                if pattern in param.strName.lower():
                    return_parameters[param.strName] = param.strValue
        # return None, str, tuple, dict based on return parameter count and return_as_dict
        return_parameter_count = len(return_parameters)
        if return_parameter_count == 0:
            # no return parameter -> return None
            return None
        elif return_as_dict:
            # at least one return parameter and return_as_dict -> return dict
            return return_parameters
        elif return_parameter_count == 1:
            # one return parameter and not return_as_dict -> return strValue
            return list(return_parameters.values())[0]
        else:
            # at least one return parameter and not return_as_dict -> return tuple
            return tuple(return_parameters.values())
