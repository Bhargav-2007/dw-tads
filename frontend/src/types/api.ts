export type Tier = "HIGH" | "MEDIUM" | "LOW" | "INSUFFICIENT";
export type RecordData = Record<string, unknown>;
export interface Actor {
  actor_id: string;
  risk_score: number;
  category: string | string[];
  handles: (string | RecordData)[];
  wallets: (string | RecordData)[];
  confidence: number;
  tier: Tier;
  last_seen: string;
  first_seen?: string;
  source_confidence?: Record<string, number>;
}
export interface TimelineResponse {
  results: Actor[];
  result_hash: string;
  query_id: string;
}
export interface GraphNode {
  id: string;
  type: string;
  label: string;
  risk_score?: number;
  tier?: Tier;
  cluster_size?: number;
}
export interface GraphEdge {
  from: string;
  to: string;
  type: string;
  confidence: number;
}
export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  result_hash: string;
}
export interface Source {
  name: string;
  url: string;
  last_fetch: string;
  record_count: number;
  http_status: number;
  cache_hit: boolean | string;
  success: boolean;
  error?: string;
}
export interface SourcesResponse {
  sources: Source[];
  total_records: number;
  distinct_sources: number;
  result_hash: string;
}
export interface AuditEntry {
  audit_id: string;
  ts: string;
  event_type: string;
  actor_user: string;
  action: string;
  resource: string;
  query_hash?: string;
  result_hash?: string;
  metadata?: RecordData;
}
export interface AuditResponse {
  results: AuditEntry[];
  chain_valid: boolean;
  broken_at?: string;
  result_hash: string;
}
export interface ActorResponse {
  actor: Actor;
  handles: RecordData[];
  pgp_keys: RecordData[];
  wallets: RecordData[];
  contacts: RecordData[];
  onion_services: RecordData[];
  clearnet_ips: RecordData[];
  stylometric_matches: RecordData[];
  behavioral_profile: RecordData;
  attribution_confidence: number | RecordData;
  evidence_chain: RecordData[];
  result_hash: string;
  merkle_root?: string;
  correlations?: RecordData[];
  wallet_clusters?: RecordData[];
  vasp_deposits?: RecordData[];
  related_actors?: RecordData[];
}
export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}
export interface ApiError {
  error: string;
  correlation_id?: string;
}
