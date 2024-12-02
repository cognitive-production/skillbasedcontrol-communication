import dataclasses
from .opcua.assetskillscommunication_opcua import OpcUaConnectionInfo
from .assetskillscommunication_factory import ServerTypes


@dataclasses.dataclass
class AssetOpcUaConnectionInfo:
    """dataclass for storing opc ua connection info for one asset.
    Used by other packages, which import this package.

    """

    assetName: str
    serverType: ServerTypes
    connectionInfo: OpcUaConnectionInfo

    def asdict(self) -> dict:
        return dataclasses.asdict(self)

    @staticmethod
    def fromdict(dictionary: dict) -> "AssetOpcUaConnectionInfo":
        assetInfo = AssetOpcUaConnectionInfo(**dictionary)
        assetInfo.connectionInfo = OpcUaConnectionInfo(**assetInfo.connectionInfo)
        return assetInfo
