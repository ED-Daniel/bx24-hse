"""
!5@28AK 4;O @01>BK A Bitrix24 8 8=B53@0F859


>4C;8:
- bitrix24_client: ;85=B 4;O @01>BK A Bitrix24 REST API
- integration_service: !5@28A 8=B53@0F88 >?@>A>2 A Bitrix24
"""

from .bitrix24_client import Bitrix24Client, bitrix24_client
from .integration_service import BitrixIntegrationService, integration_service

__all__ = [
    "bitrix24_client",
    "Bitrix24Client",
    "integration_service",
    "BitrixIntegrationService",
]
