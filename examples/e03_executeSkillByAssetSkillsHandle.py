"""
Example for executing one skill from asset skills handle
Skill server endpoint with "AddSkill" skill required, set information in e01_createAssetSkillsHandle.py
"""

from random import random
from e02_readSkillsByAssetSkillsHandle import *

# for creating asset handle see e01_createAssetSkillsHandle.py
# for reading skills see e02_readSkillsByAssetSkillsHandle

# name of skill to execute
skillName = "AddSkill"

# read actual skilldata (SkillData) as reference
# not needed, if assetHandle.read_availableSkills is called before
skilldata = assetHandle.read_stSkillData(skillName)

# reset skillDataCommand to be equal to skillDataDefault
# not needed if all skill parameters will be set on execution
skilldata.reset_SkillDataCommand()

# create some random numbers for skill parameters
num1 = round(random(), 4)
num2 = round(random(), 4)

# execute skill
# skill parameters can be set by keyword arguments
# will return all parameters with result / return pattern
result = assetHandle.skillExecHandler.executeSkill(
    skillName, Operant1=str(num1), Operant2=str(num2)
)

# print result
print(f"Result of {skillName} call is: {result}")
print(f"calculated check result: {num1} + {num2} = {num1+num2}")
assert num1 + num2 == float(result)


# disconnect on script end!
if __name__ == "__main__":
    assetHandle.disconnect()
