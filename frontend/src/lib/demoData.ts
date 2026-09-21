import type {
  Actor,
  ActorResponse,
  AuditResponse,
  GraphResponse,
  SourcesResponse,
  TimelineResponse,
} from "../types/api";

export const DEMO_ACTORS: Actor[] = [
  {
    actor_id: "ACTOR-HYDRA-09",
    risk_score: 0.94,
    category: ["ransomware", "hacking", "extortion"],
    handles: ["hydra_boss", "dark_hydra", "@hydra_ops"],
    wallets: [
      { address: "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", currency: "BTC" },
      { address: "888tNkZrPN6JsEgekjMnABU4TBzc2Dt29EPAvkFxbTNsFo5UMVeEH5Na4LzvS12SZoULrMnPrLinQ4DnOG1n2WYW1VBgNgJ", currency: "XMR" },
    ],
    confidence: 0.96,
    tier: "HIGH",
    last_seen: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    first_seen: "2024-03-12T14:22:00Z",
    source_confidence: {
      "tor-crawler": 0.95,
      "telegram-osint": 0.91,
      blockchain: 0.98,
    },
  },
  {
    actor_id: "SHADOW-BROKER-X",
    risk_score: 0.88,
    category: ["cyber_espionage", "exploit_broker", "data_leak"],
    handles: ["shadow_broker", "0xBroker", "shadow_leak_bot"],
    wallets: [
      { address: "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", currency: "BTC" },
      { address: "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", currency: "ETH" },
    ],
    confidence: 0.91,
    tier: "HIGH",
    last_seen: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    first_seen: "2024-06-05T09:10:00Z",
    source_confidence: {
      "forum-crawler": 0.92,
      "onion-discovery": 0.89,
    },
  },
  {
    actor_id: "FIN-EXTORTION-4",
    risk_score: 0.74,
    category: ["carding", "money_laundering", "banking_trojan"],
    handles: ["card_master_v3", "cashout_king"],
    wallets: [
      { address: "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy", currency: "BTC" },
    ],
    confidence: 0.82,
    tier: "MEDIUM",
    last_seen: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    first_seen: "2025-01-15T18:00:00Z",
    source_confidence: {
      blockchain: 0.85,
      "ahmia-crawler": 0.78,
    },
  },
  {
    actor_id: "DARK-MARKET-OP",
    risk_score: 0.68,
    category: ["marketplace", "illicit_goods", "escrow_fraud"],
    handles: ["silk_escrow", "vendor_prime"],
    wallets: [
      { address: "bc1q9vza2e8x5u6t8f2g1h3j4k5l6m7n8p9q0r1s2t", currency: "BTC" },
    ],
    confidence: 0.76,
    tier: "MEDIUM",
    last_seen: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(),
    first_seen: "2024-11-20T11:45:00Z",
    source_confidence: {
      "marketplace-crawler": 0.81,
    },
  },
  {
    actor_id: "PHISH-SYNDICATE-7",
    risk_score: 0.45,
    category: ["phishing", "credential_harvesting"],
    handles: ["login_verify_support", "secure_portal_dev"],
    wallets: [
      { address: "1BoatSLRHtKNngkdXEeobR76b53LETtpyT", currency: "BTC" },
    ],
    confidence: 0.54,
    tier: "LOW",
    last_seen: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
    first_seen: "2025-02-01T04:15:00Z",
    source_confidence: {
      "clearnet-correlator": 0.55,
    },
  },
];

export function getDemoTimeline(params?: {
  start?: string;
  end?: string;
  min_confidence?: number | string;
  category?: string;
}): TimelineResponse {
  let list = [...DEMO_ACTORS];
  const minConf = params?.min_confidence ? Number(params.min_confidence) : 0;
  if (minConf > 0) {
    list = list.filter((a) => a.confidence >= minConf);
  }
  if (params?.category) {
    const cats = params.category.split(",").map((c) => c.trim().toLowerCase());
    list = list.filter((a) => {
      const actorCats = Array.isArray(a.category)
        ? a.category.map((c) => c.toLowerCase())
        : [String(a.category).toLowerCase()];
      return cats.some((c) => actorCats.includes(c));
    });
  }
  return {
    results: list,
    query_id: "query-demo-" + Date.now().toString(36),
    result_hash: "a4f89d02c51e39b7431eef88791024bd3315a6b0c",
  };
}

export function getDemoActor(actorId: string): ActorResponse {
  const actor =
    DEMO_ACTORS.find(
      (a) => a.actor_id.toLowerCase() === actorId.toLowerCase(),
    ) || {
      actor_id: actorId,
      risk_score: 0.85,
      category: ["threat_actor", "darkweb"],
      handles: ["persona_" + actorId.toLowerCase().slice(0, 8)],
      wallets: [
        { address: "bc1qdemo" + actorId.toLowerCase().slice(0, 10), currency: "BTC" },
      ],
      confidence: 0.88,
      tier: "HIGH" as const,
      last_seen: new Date().toISOString(),
      first_seen: "2024-01-01T00:00:00Z",
    };

  return {
    actor,
    handles: [
      {
        handle_id: typeof actor.handles[0] === "string" ? actor.handles[0] : "primary_handle",
        platform: "Dread Forum",
        first_seen: actor.first_seen || "2024-03-12T14:22:00Z",
        confidence: 0.96,
      },
      {
        handle_id: typeof actor.handles[1] === "string" ? actor.handles[1] : "secondary_handle",
        platform: "Exploit.in",
        first_seen: "2024-04-01T10:00:00Z",
        confidence: 0.92,
      },
      {
        handle_id: "@" + actor.actor_id.toLowerCase().replace(/[^a-z0-9]/g, "_") + "_ops",
        platform: "Telegram Darknet",
        first_seen: "2024-05-18T16:40:00Z",
        confidence: 0.88,
      },
      {
        handle_id: "sec_operator",
        platform: "BreachForums",
        first_seen: "2024-08-10T22:15:00Z",
        confidence: 0.85,
      },
    ],
    pgp_keys: [
      {
        fingerprint: "9B54 C178 8E3B 4842 B23A  0C14 E25A F092 1A89 33DF",
        algorithm: "RSA-4096 / GnuPG v2.2",
        first_seen: "2024-03-12T14:22:00Z",
      },
      {
        fingerprint: "4D21 88FA 90B7 33E1 C952  119A 773C DE21 990B FE81",
        algorithm: "Ed25519 / Curve25519",
        first_seen: "2024-09-01T08:30:00Z",
      },
    ],
    wallets: Array.isArray(actor.wallets)
      ? actor.wallets.map((w, idx) => ({
          address: typeof w === "string" ? w : (w as { address: string }).address,
          currency: typeof w === "object" && w && "currency" in w ? (w as { currency: string }).currency : "BTC",
          first_seen: "2024-03-15T02:00:00Z",
          confidence: 0.95 - idx * 0.04,
        }))
      : [],
    contacts: [
      {
        type: "Telegram",
        value: "@" + actor.actor_id.toLowerCase() + "_support",
        first_seen: "2024-05-18T16:40:00Z",
      },
      {
        type: "Jabber/XMPP",
        value: "operator@" + actor.actor_id.toLowerCase() + ".is",
        first_seen: "2024-03-14T01:10:00Z",
      },
      {
        type: "Tox ID",
        value: "76A764DBA8686D5109DEAB22C1E0EE2300E4304EC6526B83771F36418385",
        first_seen: "2024-07-22T19:00:00Z",
      },
    ],
    onion_services: [
      {
        onion_address: actor.actor_id.toLowerCase().replace(/[^a-z0-9]/g, "") + "7q4b2xyn4w6pm8s0tldkvj9y.onion",
        type: "Negotiation & Command Portal",
        last_seen: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
      },
      {
        onion_address: "leakvault" + actor.actor_id.toLowerCase().replace(/[^a-z0-9]/g, "") + "4b8nm1q7.onion",
        type: "Exfiltrated Intelligence Vault",
        last_seen: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
      },
    ],
    clearnet_ips: [
      {
        ip_address: "185.220.101.5",
        hosting_provider: "M247 Ltd (Tor Exit Relay)",
        confidence: 0.91,
      },
      {
        ip_address: "194.26.29.114",
        hosting_provider: "Stark Industries (Bulletproof VPS)",
        confidence: 0.87,
      },
    ],
    correlations: [
      {
        indicator: "Tor circuit timing overlap with forum logins",
        confidence: 0.93,
        source: "plane4-fusion",
      },
      {
        indicator: "Cobalt Strike beacon watermark 0x19283746",
        confidence: 0.89,
        source: "malware-sandbox",
      },
    ],
    stylometric_matches: [
      {
        other_handle: "hydra_boss",
        similarity_score: 0.94,
        confidence: 0.91,
        actor_id: "SHADOW-BROKER-X",
        signals: {
          "Russian syntax transfer": 0.96,
          "Punctuation entropy": 0.88,
          "Jargon concordance": 0.92,
        },
      },
    ],
    behavioral_profile: {
      hourly_activity: [
        1, 0, 0, 0, 1, 3, 8, 14, 22, 28, 35, 30, 26, 24, 29, 31, 25, 18, 12, 7,
        4, 2, 1, 0,
      ],
      timezone: "UTC+3 (Eastern European / Moscow)",
    },
    attribution_confidence: {
      score: actor.confidence,
      contributions: {
        identifier: 0.55,
        behavior: 0.25,
        infrastructure: 0.2,
      },
    },
    evidence_chain: [
      {
        sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        captured_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        source_url: "http://" + actor.actor_id.toLowerCase() + ".onion/announcements",
        minio_key: "evidence/2026/09/21/" + actor.actor_id.toLowerCase() + "_leak.json",
      },
      {
        sha256: "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        captured_at: new Date(Date.now() - 1000 * 60 * 60 * 18).toISOString(),
        source_url: "https://t.me/darknet_ops/451",
        minio_key: "evidence/2026/09/20/telegram_post_451.json",
      },
      {
        sha256: "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
        captured_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
        source_url: "https://blockchair.com/bitcoin/transaction/0a1b2c3d4e5f",
        minio_key: "evidence/2026/09/18/btc_cluster_tx.json",
      },
    ],
    wallet_clusters: [
      {
        cluster_id: actor.actor_id + "-CLUSTER-ALPHA",
        total_btc: 48.75,
        tx_count: 142,
        exchange_hops: 3,
        attribution: "Mixer consolidation wallet",
      },
    ],
    vasp_deposits: [
      {
        wallet: typeof actor.wallets[0] === "string" ? actor.wallets[0] : (actor.wallets[0] as { address: string })?.address || "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
        vasp_name: "Garantex Exchange",
        country: "EE/RU",
        kyc_traceable: "High",
      },
    ],
    merkle_root: "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    related_actors: [
      { actor_id: "SHADOW-BROKER-X" },
      { actor_id: "FIN-EXTORTION-4" },
    ],
    result_hash: "hash-actor-" + actorId,
  };
}

export function getDemoGraph(actorId?: string): GraphResponse {
  const nodes = [
    {
      id: "ACTOR-HYDRA-09",
      type: "Actor",
      label: "ACTOR-HYDRA-09",
      risk_score: 0.94,
      tier: "HIGH" as const,
    },
    {
      id: "SHADOW-BROKER-X",
      type: "Actor",
      label: "SHADOW-BROKER-X",
      risk_score: 0.88,
      tier: "HIGH" as const,
    },
    {
      id: "FIN-EXTORTION-4",
      type: "Actor",
      label: "FIN-EXTORTION-4",
      risk_score: 0.74,
      tier: "MEDIUM" as const,
    },
    {
      id: "hydra_boss",
      type: "Handle",
      label: "@hydra_boss",
      tier: "HIGH" as const,
    },
    {
      id: "shadow_broker",
      type: "Handle",
      label: "@shadow_broker",
      tier: "HIGH" as const,
    },
    {
      id: "card_master_v3",
      type: "Handle",
      label: "@card_master_v3",
      tier: "MEDIUM" as const,
    },
    {
      id: "btc_hydra_wallet",
      type: "Wallet",
      label: "bc1qxy...0wlh (BTC)",
      tier: "HIGH" as const,
    },
    {
      id: "xmr_hydra_wallet",
      type: "Wallet",
      label: "888tNk...NgJ (XMR)",
      tier: "HIGH" as const,
    },
    {
      id: "btc_shadow_wallet",
      type: "Wallet",
      label: "1A1zP1...DivfNa (BTC)",
      tier: "HIGH" as const,
    },
    {
      id: "onion_hydra_ransom",
      type: "OnionService",
      label: "hydraransom...onion",
      tier: "HIGH" as const,
    },
    {
      id: "onion_shadow_market",
      type: "OnionService",
      label: "shadowleaks...onion",
      tier: "HIGH" as const,
    },
    {
      id: "ip_tor_exit_relay",
      type: "ClearnetIP",
      label: "185.220.101.5",
      tier: "HIGH" as const,
    },
    {
      id: "ip_bulletproof_vps",
      type: "ClearnetIP",
      label: "194.26.29.114",
      tier: "MEDIUM" as const,
    },
  ];

  const edges = [
    { from: "ACTOR-HYDRA-09", to: "hydra_boss", type: "USES_HANDLE", confidence: 0.96 },
    { from: "ACTOR-HYDRA-09", to: "btc_hydra_wallet", type: "CONTROLS_WALLET", confidence: 0.98 },
    { from: "ACTOR-HYDRA-09", to: "xmr_hydra_wallet", type: "CONTROLS_WALLET", confidence: 0.94 },
    { from: "ACTOR-HYDRA-09", to: "onion_hydra_ransom", type: "HOSTS_SERVICE", confidence: 0.92 },
    { from: "onion_hydra_ransom", to: "ip_bulletproof_vps", type: "RESOLVES_TO", confidence: 0.87 },
    { from: "SHADOW-BROKER-X", to: "shadow_broker", type: "USES_HANDLE", confidence: 0.91 },
    { from: "SHADOW-BROKER-X", to: "btc_shadow_wallet", type: "CONTROLS_WALLET", confidence: 0.89 },
    { from: "SHADOW-BROKER-X", to: "onion_shadow_market", type: "OPERATES", confidence: 0.93 },
    { from: "ACTOR-HYDRA-09", to: "SHADOW-BROKER-X", type: "COLLABORATES_WITH", confidence: 0.84 },
    { from: "FIN-EXTORTION-4", to: "card_master_v3", type: "USES_HANDLE", confidence: 0.82 },
    { from: "FIN-EXTORTION-4", to: "btc_shadow_wallet", type: "TRANSFERS_FUNDS", confidence: 0.79 },
    { from: "ip_bulletproof_vps", to: "ip_tor_exit_relay", type: "ROUTES_THROUGH", confidence: 0.88 },
  ];

  if (actorId && actorId !== "ACTOR-HYDRA-09" && !nodes.some((n) => n.id === actorId)) {
    nodes.unshift({
      id: actorId,
      type: "Actor",
      label: actorId,
      risk_score: 0.85,
      tier: "HIGH" as const,
    });
    edges.unshift({
      from: actorId,
      to: "ACTOR-HYDRA-09",
      type: "CONNECTED_TO",
      confidence: 0.87,
    });
  }

  return {
    nodes,
    edges,
    result_hash: "graph-hash-demo",
  };
}

export function getDemoSources(): SourcesResponse {
  return {
    sources: [
      {
        name: "Tor Onion Network Crawler",
        url: "http://ahmiafi5w6twxfecwizt6rjrlgahvtqmrnhvcmsfdvdih6tnehgxiqad.onion",
        last_fetch: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
        record_count: 14820,
        http_status: 200,
        cache_hit: true,
        success: true,
      },
      {
        name: "Dread Darknet Forum Ingest",
        url: "http://dreadytofatroptsdj6io7l3xptbet6onoyno2yv7jicoxknyazubrad.onion",
        last_fetch: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
        record_count: 8540,
        http_status: 200,
        cache_hit: true,
        success: true,
      },
      {
        name: "Telegram Threat Intelligence Channels",
        url: "https://t.me/darkweb_intel_stream",
        last_fetch: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
        record_count: 3290,
        http_status: 200,
        cache_hit: false,
        success: true,
      },
      {
        name: "Bitcoin & Monero Ledger Streamer",
        url: "rpc://blockchain-node.internal:8332",
        last_fetch: new Date(Date.now() - 1000 * 60 * 1).toISOString(),
        record_count: 54100,
        http_status: 200,
        cache_hit: true,
        success: true,
      },
      {
        name: "Russian Underworld Leak Feeds",
        url: "https://feed.exploit-intel.net/v2/actors",
        last_fetch: new Date(Date.now() - 1000 * 60 * 18).toISOString(),
        record_count: 4620,
        http_status: 200,
        cache_hit: true,
        success: true,
      },
    ],
    total_records: 85370,
    distinct_sources: 5,
    result_hash: "sources-hash-demo",
  };
}

export function getDemoAudit(): AuditResponse {
  const baseTs = Date.now();
  return {
    results: [
      {
        audit_id: "AUDIT-9921",
        ts: new Date(baseTs - 1000 * 60 * 2).toISOString(),
        event_type: "query",
        actor_user: "analyst1",
        action: "read",
        resource: "ACTOR-HYDRA-09",
        query_hash: "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
        result_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      },
      {
        audit_id: "AUDIT-9920",
        ts: new Date(baseTs - 1000 * 60 * 15).toISOString(),
        event_type: "auth",
        actor_user: "analyst1",
        action: "token_issue",
        resource: "/auth/token",
        query_hash: "3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855a",
        result_hash: "9b54c1788e3b4842b23a0c14e25af0921a8933df4d2188fa90b733e1c952119a",
      },
      {
        audit_id: "AUDIT-9919",
        ts: new Date(baseTs - 1000 * 60 * 32).toISOString(),
        event_type: "export",
        actor_user: "admin1",
        action: "export_evidence",
        resource: "ACTOR-HYDRA-09",
        query_hash: "4d2188fa90b733e1c952119a773cde21990bfe81e3b0c44298fc1c149afbf4c8",
        result_hash: "1a8933df4d2188fa90b733e1c952119a773cde21990bfe81e3b0c44298fc1c14",
      },
      {
        audit_id: "AUDIT-9918",
        ts: new Date(baseTs - 1000 * 60 * 65).toISOString(),
        event_type: "query",
        actor_user: "analyst1",
        action: "graph_traverse",
        resource: "SHADOW-BROKER-X",
        query_hash: "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        result_hash: "773cde21990bfe81e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934c",
      },
    ],
    chain_valid: true,
    result_hash: "audit-chain-verified-demo",
  };
}

export const DEMO_METRICS = `# HELP dw_tads_active_collectors Number of running crawler collectors
# TYPE dw_tads_active_collectors gauge
dw_tads_active_collectors 12
# HELP dw_tads_actors_tracked Total threat actors in knowledge graph
# TYPE dw_tads_actors_tracked gauge
dw_tads_actors_tracked 842
# HELP dw_tads_evidence_records_total Total cryptographic evidence artifacts stored
# TYPE dw_tads_evidence_records_total counter
dw_tads_evidence_records_total 128450
# HELP dw_tads_pipeline_latency_seconds Average pipeline processing latency
# TYPE dw_tads_pipeline_latency_seconds histogram
dw_tads_pipeline_latency_seconds_sum 142.3
dw_tads_pipeline_latency_seconds_count 1580
# HELP dw_tads_audit_chain_validity Current integrity state of audit chain
# TYPE dw_tads_audit_chain_validity gauge
dw_tads_audit_chain_validity 1
`;