"""Plane 7 services package (8 services)."""
from .deepfake_detector import DeepfakeDetector
from .image_forensics import ImageForensics
from .malware_sandbox import MalwareSandbox
from .synthetic_media_analyzer import SyntheticMediaAnalyzer
from .analyst_dashboard import AnalystDashboard
from .admin_console import AdminConsole
from .classification_handler import ClassificationHandler
from .zkp_query_layer import ZkpQueryLayer

SERVICES = [
    DeepfakeDetector, ImageForensics, MalwareSandbox, SyntheticMediaAnalyzer,
    AnalystDashboard, AdminConsole, ClassificationHandler, ZkpQueryLayer,
]
