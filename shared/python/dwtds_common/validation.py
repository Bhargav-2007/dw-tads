"""Pydantic v2 models for every Kafka message schema in DW-TADS."""

from typing import Literal
from pydantic import BaseModel, Field


class ScanRaw(BaseModel):
    onion_address: str
    finding_type: str
    match_text: str
    http_status: int
    headers: dict[str, str] = {}
    favicon_sha256: str | None = None
    ssl_serial: str | None = None
    etag: str | None = None
    captured_at: str
    correlation_id: str


class ContentClean(BaseModel):
    handle_id: str
    platform: str
    text: str
    posted_at: str
    source_sha256: str
    correlation_id: str


class PersonaLink(BaseModel):
    handle_a: str
    handle_b: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    signals: dict[str, float]
    correlation_id: str


class WalletAttribution(BaseModel):
    wallet_address: str
    cluster_id: str | None = None
    cluster_size: int | None = None
    vasp_name: str | None = None
    kyc_traceable: bool | None = None
    currency: str
    heuristic: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    correlation_id: str


class InfraIndicator(BaseModel):
    onion_address: str
    finding_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    matched_clearnet_domain: str | None = None
    matched_clearnet_ip: str | None = None
    match_type: str | None = None
    detected_at: str
    correlation_id: str


class BehaviorProfile(BaseModel):
    handle_id: str
    post_count: int
    estimated_timezone_offset: int
    hour_histogram: list[int]
    mean_word_count: float
    std_word_count: float
    frequency_variance: float
    anomaly_score: float
    is_anomaly: bool
    computed_at: str


class CategorySignal(BaseModel):
    handle_id: str
    platform: str
    source_sha256: str
    category_scores: dict[str, float]
    top_category: str
    top_score: float
    confidence: float
    detected_at: str
    correlation_id: str


class ActorEntities(BaseModel):
    handle_id: str
    platform: str
    source_sha256: str
    entities: list[dict]
    extracted_at: str
    correlation_id: str


class ChainTx(BaseModel):
    tx_hash: str
    currency: Literal["BTC", "ETH", "XMR"]
    from_address: str
    to_address: str
    amount: float
    timestamp: str
    block_height: int | None = None
    correlation_id: str


class ThreatIoc(BaseModel):
    ioc: str
    ioc_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str
    first_seen: str | None = None
    tags: list[str] = []
    correlation_id: str


class OnionDiscoveryMsg(BaseModel):
    onion_address: str
    title: str | None = None
    keyword: str | None = None
    source_url: str | None = None
    discovered_at: str
    correlation_id: str


SCHEMAS: dict[str, type[BaseModel]] = {
    "scan.raw": ScanRaw,
    "content.clean": ContentClean,
    "persona.links": PersonaLink,
    "wallet.attribution": WalletAttribution,
    "infra.indicators": InfraIndicator,
    "behavior.profile": BehaviorProfile,
    "category.signals": CategorySignal,
    "actor.entities": ActorEntities,
    "chain.tx": ChainTx,
    "threat.iocs": ThreatIoc,
    "onion.discovery": OnionDiscoveryMsg,
}


def validate(topic: str, payload: dict) -> dict:
    """Validate payload against the schema for the given Kafka topic.
    Returns validated dict or raises ValidationError."""
    cls = SCHEMAS.get(topic)
    if not cls:
        return payload
    return cls(**payload).model_dump()
