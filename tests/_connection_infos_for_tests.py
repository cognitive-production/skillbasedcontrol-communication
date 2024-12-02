from sbc_communication.assetConnectionInfo import OpcUaConnectionInfo, ServerTypes

connectionInfo_Python = OpcUaConnectionInfo(
    opc_url="opc.tcp://localhost:4841", rootNodeId=["i=85"]
)

connectionInfo_Beckhoff = OpcUaConnectionInfo(
    opc_url="opc.tcp://", # TODO: for running tests, enter endpoint and credentials here
    opc_user="",
    opc_password="",
    rootNodeId=[""],
)

connectionInfo_BundR = OpcUaConnectionInfo(
    opc_url="opc.tcp://",# TODO: for running tests, enter endpoint and credentials here
    opc_user="",
    opc_password="",
    rootNodeId="",
)

connectionInfo_Siemens = OpcUaConnectionInfo(
    opc_url="opc.tcp://", # TODO: for running tests, enter endpoint and credentials here
    opc_user="",
    opc_password="",
    rootNodeId="",
)
