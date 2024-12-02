"""
Example for reading skills from asset skills handle
Skill server endpoint with at least one skill required, set information in e01_createAssetSkillsHandle.py
"""

from e01_createAssetSkillsHandle import *

# for creating asset handle see e01_createAssetSkillsHandle.py

# read available skills from server
availableSkills = assetHandle.read_availableSkills()

# print skill count and available skill names
print(f"Available skills: {len(availableSkills)}")

print(f"Skill names = {list(availableSkills.keys())}")


# disconnect on script end!
if __name__ == "__main__":
    assetHandle.disconnect()
