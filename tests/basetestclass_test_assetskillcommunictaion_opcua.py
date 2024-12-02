import os
import time
import unittest
import abc
from typing import Optional
import random

from sbc_statemachine import skilldatatypes

from sbc_communication.opcua.assetskillscommunication_opcua import (
    AssetSkillsCommunication_OPCUA,
)


class Test_assetskillscommunication_opcua(unittest.TestCase):
    @abc.abstractmethod
    def _instatiateCommObject(cls):
        raise unittest.SkipTest(
            f"baseclass for testing _instatiateCommObject is not implemented!"
        )

    @classmethod
    def setUpClass(cls):
        cls.comm: Optional[AssetSkillsCommunication_OPCUA] = None
        cls.testSkillName = ""
        cls.sumSkillTest = False
        cls._instatiateCommObject(cls)

    @classmethod
    def tearDownClass(cls):
        if cls.comm is not None:
            cls.comm.disconnect()

    # one "big" test method for all functions, single methods results in extreme testing times
    def test_skillcommunication_opcua(self):
        self.assertIsNotNone(self.comm)
        self.assertTrue(self.comm.connect())
        self.assertTrue(self.comm.checkComm())

        self.assertGreater(self.comm.searchfor_Skills(), 0)
        self.assertGreater(len(self.comm.skillDataHandles), 0)
        self.assertTrue(self.comm.read_SkillDatas())
        firstSkill = list(self.comm.skillDataHandles.keys())[0]
        self.assertGreater(
            len(self.comm.skillDataHandles[firstSkill].stSkillDataDefault.strName), 0
        )
        self.assertTrue(self.comm.reset_SkillDataCommand(self.testSkillName))
        self.assertTrue(
            isinstance(
                self.comm.read_stSkillState(self.testSkillName),
                skilldatatypes.ST_SkillState,
            )
        )
        self.assertTrue(
            isinstance(
                self.comm.read_stSkillState_member(
                    self.testSkillName, "strActiveState"
                ),
                str,
            )
        )
        self.assertTrue(self.comm.write_SingleSkillCommand(self.testSkillName, "Reset"))
        time.sleep(1.0)
        self.assertTrue(self.comm.reset_SkillDataCommand(self.testSkillName))
        stSkillDataCommand = self.comm.get_stSkillData(self.testSkillName)
        num1 = round(random.random(), 4)
        num2 = round(random.random(), 4)
        stSkillDataCommand.astParameters[0].strValue = str(num1)
        stSkillDataCommand.astParameters[1].strValue = str(num2)
        stSkillDataCommand.astParameters[2].strValue = ""
        self.assertTrue(self.comm.write_stSkillData(self.testSkillName))
        self.assertTrue(self.comm.write_stSkillData_astParameters(self.testSkillName))
        if self.sumSkillTest:
            self.assertTrue(
                self.comm.write_SingleSkillCommand(self.testSkillName, "Start")
            )
            time.sleep(2.0)
            stSkillDataCommandParameters = self.comm.read_stSkillData(
                self.testSkillName, useSkillDataDefault=False
            ).astParameters
            print(f"{stSkillDataCommandParameters=}")
            self.assertGreater(len(stSkillDataCommandParameters[2].strValue), 0)
            self.assertEqual(
                round(float(stSkillDataCommandParameters[2].strValue), 6),
                round(num1 + num2, 6),
            )
            self.assertTrue(
                self.comm.write_SingleSkillCommand(self.testSkillName, "Reset")
            )
        pass
