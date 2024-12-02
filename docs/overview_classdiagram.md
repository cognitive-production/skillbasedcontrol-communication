# Class overview for sbc_communication package
```plantuml
package sbc_communication{
class AssetSkillsHandle {
    "handle all skills of one asset; one communiation endpoint"
    skillCom : AssetSkillsCommunication
    read_availableSkills()
    }

class SkillExecutionHandler {
    "handle the execution of skills"
    executeSkill()
}
AssetSkillsHandle o-- SkillExecutionHandler
abstract AssetSkillsCommunication {
    "abstract class for communicating 
    to asset skills via connection interface"
    skillDataHandles : dict[strSkillName, SkillDataHandle]
}
AssetSkillsHandle o-- AssetSkillsCommunication
class AssetSkillsCommunication_OPCUA {
    "communicating 
    to asset skills via opc ua"
}
AssetSkillsCommunication <|-- AssetSkillsCommunication_OPCUA
class ASC_OPCUA_Beckhoff{
    "communicating to 
    Beckhoff PLC skills via opc ua"
}
AssetSkillsCommunication_OPCUA <|-- ASC_OPCUA_Beckhoff
class ASC_OPCUA_Siemens{
    "communicating to 
    Siemens PLC skills via opc ua"
}
AssetSkillsCommunication_OPCUA <|-- ASC_OPCUA_Siemens
class ASC_OPCUA_Python_Asyncua{
    "communicating to Python 
    skillframework skills via opc ua"
}
AssetSkillsCommunication_OPCUA <|-- ASC_OPCUA_Python_Asyncua
class ASC_OPCUA_BundR{
    "communicating to 
    B&R PLC skills via opc ua"
}
AssetSkillsCommunication_OPCUA <|-- ASC_OPCUA_BundR
}
package sbc_statemachine {
class SkillDataHandle{
    handling skill related data, see sbc_statemachine package.\n'Seperate code from data!
}
}
AssetSkillsCommunication o-- SkillDataHandle
class asyncua.sync.Client{} 
class asyncua.sync.SyncNode{} 
AssetSkillsCommunication_OPCUA o-- asyncua.sync.Client
AssetSkillsCommunication_OPCUA o-- asyncua.sync.SyncNode
```