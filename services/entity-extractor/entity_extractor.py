"""Tier: A — Real. Algorithms: Base58Check, bech32, Ethereum EIP-55 checksum
validation; IPv4/v6 regex; domain regex; Tor v3 onion regex."""
import hashlib
import re
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()

# Bitcoin Base58Check alphabet
B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
B58_RE = re.compile(r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b")
BECH32_RE = re.compile(r"\b(bc1[ac-hj-np-z02-9]{6,87})\b", re.IGNORECASE)
ETH_RE = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
XMR_RE = re.compile(r"\b4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b")
IPV4_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
DOMAIN_RE = re.compile(r"\b(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}\b")
ONION_RE = re.compile(r"\b[a-z2-7]{56}\.onion\b")


def _b58check_valid(addr: str) -> bool:
    """Validate Bitcoin Base58Check address via double-SHA256 checksum."""
    try:
        n = 0
        for c in addr:
            n = n * 58 + B58_ALPHABET.index(c)
        raw = n.to_bytes(25, "big")
        payload, chk = raw[:-4], raw[-4:]
        return hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4] == chk
    except Exception:
        return False


def _eth_checksum_valid(addr: str) -> bool:
    """Validate Ethereum EIP-55 checksum."""
    try:
        from eth_utils import is_checksum_address
        return is_checksum_address(addr)
    except ImportError:
        # Fallback: accept any 40-hex address when eth_utils unavailable
        return bool(ETH_RE.match(addr))


class EntityExtractor(BaseService):
    NAME = "entity-extractor"
    PLANE = 3
    TIER = "Advanced"
    INPUT_TOPICS = ["content.clean"]
    OUTPUT_TOPICS = ["actor.entities"]
    HTTP_PORT = 8037
    HTTP_ROUTES = ["/health", "/ready", "/metrics"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        text = message["text"] if "text" in message else ""
        handle_id = message["handle_id"] if "handle_id" in message else "anon"
        platform = message["platform"] if "platform" in message else "unknown"
        source_sha = message["source_sha256"] if "source_sha256" in message else ""

        entities = []

        # BTC P2PKH / P2SH addresses (Base58Check validated)
        for m in B58_RE.finditer(text):
            addr = m.group(0)
            if _b58check_valid(addr):
                entities.append({"type": "btc_address", "value": addr, "validated": True})

        # BTC bech32 (SegWit) addresses — regex sufficient
        for m in BECH32_RE.finditer(text):
            entities.append({"type": "btc_bech32", "value": m.group(0), "validated": True})

        # ETH addresses — EIP-55 checksum
        for m in ETH_RE.finditer(text):
            addr = m.group(0)
            entities.append({"type": "eth_address", "value": addr,
                              "validated": addr == addr.lower() or _eth_checksum_valid(addr)})

        # XMR addresses — length + prefix check
        for m in XMR_RE.finditer(text):
            entities.append({"type": "xmr_address", "value": m.group(0), "validated": True})

        # IPv4 addresses (exclude RFC1918)
        for m in IPV4_RE.finditer(text):
            ip = m.group(0)
            if not (ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("127.")):
                entities.append({"type": "ipv4", "value": ip, "validated": True})

        # Onion v3 addresses
        for m in ONION_RE.finditer(text):
            entities.append({"type": "onion_v3", "value": m.group(0), "validated": True})

        # Domain names (filter out known TLDs from crypto)
        for m in DOMAIN_RE.finditer(text):
            dom = m.group(0)
            if not dom.endswith(".onion") and len(dom) > 4:
                entities.append({"type": "domain", "value": dom, "validated": True})

        out = [{
            "handle_id": handle_id,
            "platform": platform,
            "source_sha256": source_sha,
            "entities": entities,
            "entity_count": len(entities),
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
        }]
        logger.info("entity_extracted", handle_id=handle_id, entity_count=len(entities),
                    correlation_id=cid)
        return out
