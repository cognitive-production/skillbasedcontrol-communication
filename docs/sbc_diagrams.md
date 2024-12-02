# Communication diagrams for skillbasedcontrolframework
## User / Programmer and communication diagram
Communication between sbc_communication python package and different skillbasedcontrolframework servers via OPC UA.
```plantuml
<style>
actor {
    LineThickness 3
    LineColor black
}
actor\ {
    LineThickness 3
    LineColor black
}
component {
    LineThickness 3
    LineColor black
}
</style>

frame ClientExecution as "Client: Skill execution"{

folder python{
    actor User as "User (Python)"
    component PythonApplication as "Python application"

    package sbc_communication as "sbc_communication" {
        agent AssetSkillsHandle[
            AssetSkillsHandle
            ----
            connect()
            disconnect()
            read_availableSkills()
            executeSkill(skill_name, parameters)
        ]
    }
}
User --> AssetSkillsHandle #line.bold : uses
PythonApplication --> AssetSkillsHandle #line.bold : uses

} 


frame ServerProveder as "Server: Skill provider"{

folder python2 as "python"{
package sbc_framework_server{
    agent SkillServerOPCUA
    agent CustomSkill_python as "Custom Skill(s)"
    SkillServerOPCUA o-- "1..*" CustomSkill_python
}


actor/ Programmer_python as "Programmer (python)"
CustomSkill_python <-- Programmer_python #line.bold : implements
}
sbc_communication <..> SkillServerOPCUA : OPC UA

folder twincat as "Beckhoff TwinCAT 3"{
    agent OPC_UA_Server_twincat as "OPC UA Server (TF6100)"
    folder PLC_twincat as "PLC"{
        agent FB_CustomSkill_twincat as "FB_CustomSkill(s)"
    }
    OPC_UA_Server_twincat <..> "1..*" FB_CustomSkill_twincat
    actor/ Programmer_twincat as "Programmer (Beckhoff)"
    FB_CustomSkill_twincat <-- Programmer_twincat #line.bold : implements
}
sbc_communication <..> OPC_UA_Server_twincat : OPC UA

folder siemensS7 as "Siemens Simatic S7-1500"{
    agent OPC_UA_Server_siemens as "OPC UA Server S7-1500"
    folder PLC_siemens as "PLC S7-1500"{
        agent FB_CustomSkill_siemens as "FB_CustomSkill(s)"
    }
    OPC_UA_Server_siemens <..> "1..*" FB_CustomSkill_siemens : indirect
    actor/ Programmer_siemens as "Programmer (Siemens)"
    FB_CustomSkill_siemens <-- Programmer_siemens #line.bold : implements
}
sbc_communication <..> OPC_UA_Server_siemens : OPC UA

folder BundR as "B&R Automation Runtime"{
    agent OPC_UA_Server_bundr as "OPC UA Server BundR"
    folder PLC_bundr as "PLC BundR"{
        agent FB_CustomSkill_bundr as "FB_CustomSkill(s)"
    }
    OPC_UA_Server_bundr <..> "1..*" FB_CustomSkill_bundr : indirect
    actor/ Programmer_bundr as "Programmer (B&R)"
    FB_CustomSkill_bundr <-- Programmer_bundr #line.bold : implements
}
sbc_communication <..> OPC_UA_Server_bundr : OPC UA


} 
```


## Class and communication diagram with different OPC UA servers
Communication between sbc_communication python package and different skillbasedcontrolframework servers via OPC UA.
```plantuml

frame ClientExecution as "Client: Skill execution"{


folder python{
package asyncua {
    agent Client
    agent Server
}

package sbc_statemachine {
    agent ST_Skill
    agent SkillDataHandle
    agent SkillStateMachine
    ST_Skill <|-- SkillDataHandle
}


package sbc_communication as "sbc_communication" {
    agent AssetSkillsCommunication_OPCUA as "AssetSkillsCommunication_OPCUA\nsubclass server type"
    note right of AssetSkillsCommunication_OPCUA: Subclass depending on\nthe server vendor.
    agent AssetSkillsHandle[
        AssetSkillsHandle
    ]
    agent SkillExecutionHandler
    AssetSkillsHandle o-- AssetSkillsCommunication_OPCUA
    AssetSkillsHandle o-- SkillExecutionHandler
}
SkillDataHandle "1..*" --o AssetSkillsCommunication_OPCUA
Client --o AssetSkillsCommunication_OPCUA
}

} 


frame ServerProveder as "Server: Skill provider"{

folder python2 as "python"{
package sbc_framework_server{
    agent SkillServerOPCUA
    agent BaseSkill
    agent CustomSkill_python as "Custom Skill(s)"
    BaseSkill <|-- CustomSkill_python
    SkillServerOPCUA o-- "1..*" CustomSkill_python
}
SkillStateMachine <|-- BaseSkill
SkillDataHandle --o BaseSkill
Server --o SkillServerOPCUA
}
AssetSkillsCommunication_OPCUA <...> SkillServerOPCUA : OPC UA

folder twincat as "Beckhoff TwinCAT 3"{
    agent OPC_UA_Server_twincat as "OPC UA Server (TF6100)"
    folder PLC_twincat as "PLC"{
        package TC3_SkillbasedControlFramework.library {
            agent FB_Skill_twincat as "FB_Skill"
            agent ST_Skill_twincat as "'ST_Skill'"
            FB_Skill_twincat o-- ST_Skill_twincat
        }
        agent FB_CustomSkill_twincat as "FB_CustomSkill(s)"
        FB_CustomSkill_twincat --|> FB_Skill_twincat
    }
    OPC_UA_Server_twincat <..> "1..*" FB_CustomSkill_twincat
}
AssetSkillsCommunication_OPCUA <...> OPC_UA_Server_twincat : OPC UA

folder siemensS7 as "Siemens Simatic S7-1500"{
    agent OPC_UA_Server_siemens as "OPC UA Server S7-1500"
    folder PLC_siemens as "PLC S7-1500"{
        agent FB_Skill_interface_siemens as "FB_Skill_Interface"
        agent ST_Skill_siemens as "'ST_Skill'"
        agent FB_CustomSkill_siemens as "FB_CustomSkill(s)"
        FB_Skill_interface_siemens o-- ST_Skill_siemens
        FB_CustomSkill_siemens <..> ST_Skill_siemens
    }
    OPC_UA_Server_siemens <..> "1..*" FB_Skill_interface_siemens
}
AssetSkillsCommunication_OPCUA <...> OPC_UA_Server_siemens : OPC UA

folder BundR as "B&R Automation Runtime"{
    agent OPC_UA_Server_bundr as "OPC UA Server BundR"
    folder PLC_bundr as "PLC BundR"{
        agent FB_Skill_interface_bundr as "FB_Skill_Interface"
        agent ST_Skill_bundr as "'ST_Skill'"
        agent FB_CustomSkill_bundr as "FB_CustomSkill(s)"
        FB_Skill_interface_bundr o-- ST_Skill_bundr
        FB_CustomSkill_bundr <..> ST_Skill_bundr
    }
    OPC_UA_Server_bundr <..> "1..*" FB_Skill_interface_bundr
}
AssetSkillsCommunication_OPCUA <...> OPC_UA_Server_bundr : OPC UA


} 
```