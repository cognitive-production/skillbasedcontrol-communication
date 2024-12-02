import os
import copy
from asyncua.sync import Client, SyncNode, ua, ThreadLoop
from dataclasses import dataclass, fields
from typing import Type
from sbc_statemachine.skilldatahandle import SkillDataHandle
from sbc_statemachine.skilldatatypes import (
    ST_SkillData,
    ST_Parameter,
    ST_SkillCommand,
    ST_SkillState,
)
from ..assetskillscommunication import (
    AssetSkillsCommunication,
    AssetSkillsComConnectionInfo,
)
from ..mapVar import mapVar

ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT = 2.0


@dataclass
class SkillConnectionNodes:
    """dataclass storing opc ua nodes for accessing a skill internal data"""

    nodeId: str = ""
    skillNode: SyncNode = None
    skillStateNode: SyncNode = None
    skillCommandNode: SyncNode = None
    skillDataDefaultNode: SyncNode = None
    skillDataCommandNode: SyncNode = None


@dataclass
class OpcUaConnectionInfo(AssetSkillsComConnectionInfo):
    """dataclass storing the opc ua connection informations"""

    opc_url: str = "opc.tcp://127.0.0.1:4840"
    opc_user: str | None = None  # opc ua username
    opc_password: str | None = None  # opc ua password
    opc_security_policy: str | None = (
        None  # opc ua security policy: Basic256Sha256, ...
    )
    opc_security_mode: str | None = None  # opc ua security mode: SignAndEncrypt, ...
    opc_certificate_filepath: str | None = None  # filepath to opc ua certificate *.der
    opc_private_key_filepath: str | None = None  # filepath to opc ua key *.pem
    rootNodeId: str | None = None  # root node id for start searching skills
    searchSkillsBrowseDepthMax: int = (
        3  # maximal browse depth from rootNodeId for searching skills
    )


@dataclass
class OpcUaSkillTypes:
    """dataclass for storing opc ua server types of different vendors"""

    ST_Parameter: Type | None = None
    ST_SkillData: Type | None = None
    ST_SkillCommand_Mode: Type | None = None
    ST_SkillCommand_State: Type | None = None
    ST_SkillCommand: Type | None = None
    ST_COMMAND_EN_MTP_CC: Type | None = None
    ST_SkillState: Type | None = None


OPC_UA_CERTIFICATE_PATH = os.path.join(os.path.dirname(__file__), "certificates")
OPC_UA_CERTIFICATE_PATH_CERTIFICATE = os.path.join(
    OPC_UA_CERTIFICATE_PATH, "opc_certificate.der"
)
OPC_UA_CERTIFICATE_PATH_PRIVATEKEY = os.path.join(
    OPC_UA_CERTIFICATE_PATH, "opc_private_key.pem"
)


# "abstract" class for connecting to Skills provided by OPC-UA Server
# works for Beckhoff OPC-UA Server (TF6100)
class AssetSkillsCommunication_OPCUA(AssetSkillsCommunication):
    """abstract class for handling the opc ua communication to multiple skills of one asset / machine.
    Inherits form (abstract) AssetSkillsCommunication"""

    def __init__(
        self,
        opcConnectionInfo: OpcUaConnectionInfo,
        opcua_timeout: float = ASSET_SKILL_COMMUNICATION_OPC_TIMEOUT_DEFAULT,
    ):
        # init super class: AssetSkillsCommunication
        super().__init__(opcConnectionInfo)

        # set opc connection values
        self.opcConnectionInfo = opcConnectionInfo

        # init list for OPC connection nodes
        self.skillConnectionNodes: dict[str, SkillConnectionNodes] = {}
        self.opcUaSkillTypes = OpcUaSkillTypes()

        # create asyncio EventLoop for handling async opc Ua Client
        # self.asyncEventLoop = asyncio.new_event_loop()

        # init OPC UA client
        self.__initOpcUaClientConnection(opcua_timeout)

        # marker for opc ua browse namespaceIndex
        self.opcUaNameSpaceIndex = 4

        # communication try count and reconnect time
        self.maxtrycount: int = 10
        self.reconnectTime: float = 1.0

    def __initOpcUaClientConnection(self, opcua_timeout):
        """init opcClient (asyncua.Client). Security is not set yet, because it establishes conenction to endpoint.

        Raises:
            ValueError: providing wrong / not enough security informations in OpcUaConnectionInfo
        """
        # crate own ThreadLoop for Sync Client and set to daemon (fix for blocking end of script)
        tloop = ThreadLoop()
        tloop.setDaemon(True)
        tloop.start()
        # create opc ua Client object with server url and timeouts
        self.opcClient = Client(
            self.opcConnectionInfo.opc_url, timeout=opcua_timeout, tloop=tloop
        )
        self.opcClient.close_tloop = True

        # set conenction user and password
        if self.opcConnectionInfo.opc_user is not None:
            self.opcClient.set_user(self.opcConnectionInfo.opc_user)

        if self.opcConnectionInfo.opc_password is not None:
            self.opcClient.set_password(self.opcConnectionInfo.opc_password)

        # set security configurations, create security string and checkSum for later use
        securiy_check_sum = 0
        self.opc_security_string = ""
        # set security mode and policy
        if self.opcConnectionInfo.opc_security_policy is not None:
            self.opc_security_string += self.opcConnectionInfo.opc_security_policy + ","
            securiy_check_sum += 1
        if self.opcConnectionInfo.opc_security_mode is not None:
            self.opc_security_string += self.opcConnectionInfo.opc_security_mode + ","
            securiy_check_sum += 1
        # if security mode and policy set, then check certificate and key file
        if securiy_check_sum > 0:
            if self.opcConnectionInfo.opc_certificate_filepath is None:
                self.opc_security_string += OPC_UA_CERTIFICATE_PATH_CERTIFICATE + ","
            else:
                self.opc_security_string += (
                    self.opcConnectionInfo.opc_certificate_filepath + ","
                )
            securiy_check_sum += 1
            if self.opcConnectionInfo.opc_private_key_filepath is None:
                self.opc_security_string += OPC_UA_CERTIFICATE_PATH_PRIVATEKEY
            else:
                self.opc_security_string += (
                    self.opcConnectionInfo.opc_private_key_filepath
                )
            securiy_check_sum += 1

        # securiy_check_sum == 0 => no security
        # securiy_check_sum == 4 => set security
        # other: raise exception
        if securiy_check_sum == 0 or securiy_check_sum == 4:
            return
        else:
            raise ValueError(
                f"When providing opc server security, at least opc_policy and opc_mode must be set!"
            )

    def connect(self) -> bool:
        """Activate communication.

        Returns:
            bool: returns True if successful
        """
        # only connect if not already connected
        if not self.connected:
            self.opcClient.set_security_string(self.opc_security_string)
            self.opcClient.connect()
            # load data type definitions on connection
            self.connected = self.loadSkillDataTypes()
            self.connected = self.checkComm()
        return self.connected

    def loadSkillDataTypes(self) -> bool:
        """loads skill datatypes from opcua server e.g. ST_Parameter*, ...

        Returns:
            bool: True, if all neccessary skill types found
        """
        # no working with skills in python without them...
        uaDataTypes = self.opcClient.load_data_type_definitions(overwrite_existing=True)
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

    def getOpcUaTypebyName(self, typeName: str) -> Type | None:
        """get OPC UA datatype from ua module, created by "load_data_type_definitions" call

        Args:
            typeName (str): name of opc ua type to search for, case sensitive!

        Returns:
            cls: opc ua type class
        """
        #
        for name in ua.extension_object_typeids.keys():
            if typeName in name:
                return copy.deepcopy(
                    ua.extension_objects_by_typeid[ua.extension_object_typeids[name]]
                )
        else:
            return None

    def checkComm(self) -> bool:
        """Check if the communication has been established correctly

        Returns:
            bool: returns True if successful
        """
        if self.connected:
            try:
                serverstatusnode = self.opcClient.get_node(
                    f"i={ua.object_ids.ObjectIds().Server_ServerStatus_State}"
                )
                status = serverstatusnode.read_value()
                return status == 0
            except Exception as e:
                try:
                    self.disconnect()
                except:
                    ...
                self.connected = False
                return False
        else:
            return False

    def disconnect(self) -> bool:
        """Close communication

        Returns:
            bool: returns True if successful
        """
        if self.connected:
            self.opcClient.disconnect()
            self.connected = False
        return True

    def _browseNodes_recursive(
        self,
        node: SyncNode,
        searchname: str,
        searchtype: str,
        browsedepth=0,
        browsedepthmax=3,
    ) -> list[SkillConnectionNodes]:
        """browses opc ua node and childs for specific nodeID and NodType
        TODO: look for better suitable functions in asyncua

        Args:
            node (Node): root node to search of
            searchname (str): snippet of NodeId to search for
            searchtype (str): snippet of NodeType to search for
            browsedepth (int): actual browse depth
            browsedepthmax (int): maximal browse depth

        Returns:
            list: list of skillConnectionNodes
        """
        #
        skillConnectionNodesList = []
        if browsedepth > browsedepthmax:
            return skillConnectionNodesList
        for childId in node.get_children():
            ch = self.opcClient.get_node(childId.nodeid)
            chclass = ch.read_node_class()
            if chclass == ua.NodeClass.Object:
                skillConnectionNodesList.extend(
                    self._browseNodes_recursive(
                        ch,
                        searchname,
                        searchtype,
                        browsedepth=browsedepth + 1,
                        browsedepthmax=browsedepthmax,
                    )
                )
            elif chclass == ua.NodeClass.Variable:
                if str(ch.nodeid.Identifier).endswith(f".{searchname}"):
                    dt = ch.read_data_type()
                    dt_sym = self.opcClient.get_node(dt)
                    dt_sym_val = dt_sym.read_display_name().to_string()
                    if searchtype.lower() in dt_sym_val.lower():
                        nodeid = ch.nodeid.to_string()
                        skillConnectionNodesList.append(
                            self.get_SkillConnectionNodes(node, nodeid)
                        )
                        break
        return skillConnectionNodesList

    def searchfor_Skills(self) -> int:
        """Searches for Skills in assets and fill the SkillDatas list

        Returns:
            int: count of found Skills in asset

        """
        searchname = "stSkillDataDefault"
        searchtype = "ST_SkillData"
        # check root node configuration for skill search
        # can be None/empty, single NodeId or list of NodeIds
        if self.opcConnectionInfo.rootNodeId is None:
            SearchNodeList = [self.opcClient.get_root_node()]
        elif isinstance(self.opcConnectionInfo.rootNodeId, list):
            SearchNodeList = []
            for NodeId in self.opcConnectionInfo.rootNodeId:
                if isinstance(NodeId, str):
                    SearchNodeList.append(self.opcClient.get_node(NodeId))
                else:
                    return -1
        elif isinstance(self.opcConnectionInfo.rootNodeId, str):
            SearchNodeList = [
                self.opcClient.get_node(self.opcConnectionInfo.rootNodeId)
            ]
        else:
            return -1
        # init skillConnectionNodesList
        self.skillDataHandles = {}
        skillConnectionNodesList: list[SkillConnectionNodes] = []
        # get skillConnectionNodesList from root nodes
        for SearchNode in SearchNodeList:
            skillConnectionNodesList.extend(
                self._browseNodes_recursive(
                    SearchNode,
                    searchname,
                    searchtype,
                    browsedepthmax=self.opcConnectionInfo.searchSkillsBrowseDepthMax,
                )
            )

        # self.SkillDatas = [SkillDataHandle()] * 0
        for skillConnectionNodes in skillConnectionNodesList:
            # read skillname
            stSkillDataDefault = skillConnectionNodes.skillDataDefaultNode.read_value()
            # handle stSkillDataDefault.strName is empty ("")
            if len(stSkillDataDefault.strName) == 0:
                skillName = "Unnamed"
            else:
                skillName = stSkillDataDefault.strName
            # handle duplicate skillname in dict
            duplicateCounter = 1
            newSkillName = skillName
            while newSkillName in self.skillDataHandles:
                newSkillName = skillName + "_duplicate" + str(duplicateCounter)
                duplicateCounter += 1
            # create Skill Data Handle for new skill
            self.skillDataHandles[newSkillName] = SkillDataHandle(
                connectionID=skillConnectionNodes.nodeId
            )
            self.skillConnectionNodes[newSkillName] = skillConnectionNodes
        return len(self.skillDataHandles.keys())

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
        setSkillData.astParameters = [
            ST_Parameter() for i in range(skillData.iParameterCount)
        ]
        mapVar(skillData, setSkillData, maxListLength=skillData.iParameterCount)
        return setSkillData

    def read_stSkillState(self, skillName: str) -> ST_SkillState:
        """read stSkillState of specific skill by communication interface

        Args:
            skillName (str): name of skill in self.SkillDatas.

        Returns:
            ST_SkillState: Skillstate as ST_SkillState or None, if not successful
        """
        skillStateNodeValue = self.skillConnectionNodes[
            skillName
        ].skillStateNode.read_value()
        mapVar(skillStateNodeValue, self.skillDataHandles[skillName].stSkillState)
        return self.skillDataHandles[skillName].stSkillState

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

        skillStateMemberNode = self.skillConnectionNodes[
            skillName
        ].skillStateNode.get_child(f"{self.opcUaNameSpaceIndex}:{member}")
        skillStateMemberNodeValue = skillStateMemberNode.read_value()
        setattr(
            self.skillDataHandles[skillName].stSkillState,
            member,
            skillStateMemberNodeValue,
        )
        return skillStateMemberNodeValue

    def write_SingleSkillCommand(self, skillname: str, skillCommand: str) -> bool:
        """write single stSkillCommand (Start, Reset, ...) of specific skill by communication interface

        Args:
            skillname (str): name of skill in self.SkillDatas.
            SkillCommand (dict): dictionary with single command, like "Start", "Reset", "Offline" (see skilltypes ST_SkillCommand_State and ST_SkillCommand_Mode)

        Returns:
            bool: True if successful
        """

        if (
            isinstance(skillCommand, str)
            and skillCommand in ST_SkillCommand().stCommand_State.__dict__
        ):
            skillCommandStateMemberNode = self.skillConnectionNodes[
                skillname
            ].skillCommandNode.get_child(
                f"{self.opcUaNameSpaceIndex}:stCommand_State.{self.opcUaNameSpaceIndex}:{skillCommand}"
            )

            skillCommandStateMemberNode.write_value(
                ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
            )
            return True
        elif (
            isinstance(skillCommand, str)
            and skillCommand in ST_SkillCommand().stCommand_Mode.__dict__
        ):
            skillCommandModeMemberNode = self.skillConnectionNodes[
                skillname
            ].skillCommandNode.get_child(
                f"{self.opcUaNameSpaceIndex}:stCommand_Mode.{self.opcUaNameSpaceIndex}:{skillCommand}"
            )
            skillCommandModeMemberNode.write_value(
                ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
            )
            return True
        else:
            return False

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
        # if  parameters exists
        if sourceSkillData.iParameterCount > 0:
            targetSkillData.astParameters = [
                self.opcUaSkillTypes.ST_Parameter()
                for i in range(sourceSkillData.iParameterCount)
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
        targetskillDataParameter = [
            self.opcUaSkillTypes.ST_Parameter()
            for i in range(sourceSkillData.iParameterCount)
        ]
        mapVar(
            sourceSkillDataParameters,
            targetskillDataParameter,
            maxListLength=sourceSkillData.iParameterCount,
        )
        skillDataParameterNode.write_value(ua.DataValue(targetskillDataParameter))
        return True

    def get_SkillConnectionNodes(
        self, skillNode: SyncNode, nodeId: str
    ) -> SkillConnectionNodes:
        """get nodes to skill internal structures: ST_SkillState, ST_SkillCommand, ST_SkillDataDefault, ST_SkillDataCommand.

        Args:
            skillNode (Node): node to skill

        Returns:
            SkillConnectionNodes: object containing connection nodes.
        """
        return SkillConnectionNodes(
            nodeId=nodeId,
            skillNode=skillNode,
            skillStateNode=skillNode.get_child(
                f"{self.opcUaNameSpaceIndex}:stSkillState"
            ),
            skillCommandNode=skillNode.get_child(
                f"{self.opcUaNameSpaceIndex}:stSkillCommand"
            ),
            skillDataDefaultNode=skillNode.get_child(
                f"{self.opcUaNameSpaceIndex}:stSkillDataDefault"
            ),
            skillDataCommandNode=skillNode.get_child(
                f"{self.opcUaNameSpaceIndex}:stSkillDataCommand"
            ),
        )

    # def runAsync(self, method) -> Any | None:
    #     while self.asyncEventLoop.is_running():
    #         time.sleep(0.001)
    #     return self.asyncEventLoop.run_until_complete(method)

    # def runAsyncWithReconnect(
    #     self,
    #     method,
    #     margs: tuple = [],
    #     mkwargs: dict = {},
    #     maxtrycount: int = None,
    #     reconnectTime: float = None,
    # ) -> Any | None:
    #     while self.asyncRunning:  # self.asyncEventLoop.is_running():
    #         time.sleep(0.001)
    #     self.asyncRunning = True
    #     while True:
    #         try:
    #             ret = self.asyncEventLoop.run_until_complete(method(*margs, **mkwargs))
    #             self.asyncRunning = False
    #             return ret
    #         except (
    #             ConnectionError,
    #             TimeoutError,
    #             asyncio.exceptions.TimeoutError,
    #         ) as e:
    #             # TODO: remove
    #             print(
    #                 f"Timeout / Connection Error while calling method {method.__name__}: {e}"
    #             )
    #             self.asyncEventLoop.run_until_complete(
    #                 self.reconnectRoutine(maxtrycount, reconnectTime)
    #             )

    # async def reconnectRoutine(
    #     self, maxtrycount: int = None, reconnectTime: float = None
    # ) -> None:
    #     if maxtrycount is None:
    #         maxtrycount = self.maxtrycount
    #     if reconnectTime is None:
    #         reconnectTime = self.reconnectTime
    #     count = 1
    #     while count <= maxtrycount:
    #         self.connected = False
    #         await self.opcClient.disconnect()
    #         await asyncio.sleep(reconnectTime)
    #         try:
    #             print(
    #                 f"AssetSkillsCommunication_OPCUA: try reconnect {count}/{maxtrycount}"
    #             )
    #             await self.opcClient.connect()
    #             self.connected = True
    #             return
    #         except (
    #             ConnectionError,
    #             TimeoutError,
    #             asyncio.exceptions.TimeoutError,
    #         ) as e:
    #             count += 1
    #     # no ceonnection established
    #     raise ConnectionError(
    #         f"AssetSkillsCommunication_OPCUA: Cant reconnect after {maxtrycount} tries."
    #     )
