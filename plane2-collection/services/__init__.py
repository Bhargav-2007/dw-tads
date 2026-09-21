"""Plane 2 services package (14 services)."""
from .onion_crawler import OnionCrawler
from .forum_crawler import ForumCrawler
from .marketplace_crawler import MarketplaceCrawler
from .onion_discovery import OnionDiscovery
from .ahmia_crawler import AhmiaCrawler
from .onionscan_runner import OnionscanRunner
from .forum_loader import ForumLoader
from .threat_feed_loader import ThreatFeedLoader
from .blockchain_loader import BlockchainLoader
from .i2p_collector import I2pCollector
from .zeronet_collector import ZeronetCollector
from .telegram_osint import TelegramOsint
from .clearnet_enrichment_gateway import ClearnetEnrichmentGateway
from .raw_storage import RawStorage

# Alias for backwards compat
ZeroNetCollector = ZeronetCollector

SERVICES = [
    OnionCrawler, ForumCrawler, MarketplaceCrawler, OnionDiscovery,
    AhmiaCrawler, OnionscanRunner, ForumLoader, ThreatFeedLoader,
    BlockchainLoader, I2pCollector, ZeronetCollector, TelegramOsint,
    ClearnetEnrichmentGateway, RawStorage,
]
