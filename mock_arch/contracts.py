import hashlib
import json
from pathlib import Path

CATALOG=json.loads(Path(__file__).with_name('catalog.json').read_text())
BY_ID={entry['id']:entry for entry in CATALOG}
SCENARIOS=('baseline','insufficient-evidence')
NOTICE='MOCK DATA ONLY — not an operational finding, security control, legal document, or attribution.'

def encode(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()

def sha(value):
    return hashlib.sha256(encode(value)).hexdigest()

NODE_TYPES=['Actor','Handle','PGPKey','Wallet','VASP','OnionService','ClearnetIP','SSLCert','Persona','TimeZoneProfile','BehaviorPattern','MalwareSample','Case','Investigation','LegalOrder','HUMINT_Persona','Analyst']
EDGE_TYPES=['HasHandle','UsesPGP','ControlsWallet','DepositsTo','ClustersWith','ResolvesTo','SharesCert','StylometricMatch','SameTimeZone','Trusts','AttributedTo','USES_MALWARE','PARTICIPATED_IN','SUBJECT_OF','AUTHORIZED_BY','REVIEWED_BY','PROVIDED_HUMINT','SHARED_WITH','CLASSIFIED_AS','RETENTION_UNTIL']

def graph_fixture():
    pairs=[(0,1),(1,2),(1,3),(3,4),(3,3),(5,6),(5,7),(1,8),(1,9),(1,1),(8,0),(0,11),(0,13),(0,12),(13,14),(12,16),(15,12),(12,16),(12,14),(12,14)]
    temporal=dict(valid_from='2026-01-01T00:00:00Z',valid_until=None,recorded_at='2026-01-01T00:00:01Z',source_confidence='MOCK',information_confidence=None,classification='MOCK-UNCLASSIFIED')
    nodes=[dict(id='mock:'+t.lower(),type=t,label='Fictional '+t,synthetic=True,**temporal) for t in NODE_TYPES]
    edges=[dict(id='mock-edge:'+str(i),source=nodes[a]['id'],target=nodes[b]['id'],type=t,synthetic=True,**temporal) for i,(t,(a,b)) in enumerate(zip(EDGE_TYPES,pairs))]
    return {'nodes':nodes,'edges':edges}

# Predeclared synthetic outputs, not analytics run on user-supplied text or identifiers.
OUTPUTS={
 'docker-swarm':{'simulated_nodes':12,'simulated_quorum':'healthy','deployment_performed':False},
 'internal-ca':{'certificate_id':'MOCK-CERT-001','certificate_valid_for_tls':False},
 'secrets-manager':{'secret_reference':'mock-vault://fixture/key','hsm_used':False},
 'audit-ledger':{'chain_type':'actual simulator event hash chain','production_ledger':False},
 'data-diode':{'simulated_direction':'ingest-only','hardware_present':False},
 'calico-policies':{'simulated_zones':7,'policy_engine':'fixture','rules_applied':False},
 'pqc-layer':{'ciphertext':'MOCK-NOT-CIPHERTEXT','cryptography_performed':False},
 'key-fragmentation':{'mock_share_ids':['MOCK-SHARE-A','MOCK-SHARE-B','MOCK-SHARE-C'],'secret_split':False},
 'chaos-engineering':{'fault_types':['none','one-shot-service-failure'],'real_infrastructure_affected':False},
 'cost-governance':{'currency':'MOCK-CREDITS','run_cost':78},
 'threat-model-engine':{'fixture_controls':['mock-segmentation','mock-review'],'assessment':'illustrative-only'},
 'sbom-signer':{'artifact':'MOCK-SBOM','signature':'MOCK-NOT-A-SIGNATURE'},
 'tor-proxy-manager':{'circuit_id':'MOCK-CIRCUIT-001','proxy':None,'network_connection':False},
 'crawler-scheduler':{'fixture_jobs':['MOCK-JOB-001'],'priority':5,'dispatch':'fixture-only'},
 'blockchain-nodes':{'transactions':[{'id':'MOCK-TX-001','from':'MOCK-WALLET-A','to':'MOCK-WALLET-B','amount':1}]},
 'clearnet-gateway':{'indicators':[{'ip':'192.0.2.10','domain':'fixture.invalid'}],'lookup_performed':False},
 'evidence-pipeline':{'evidence_id':'MOCK-EVIDENCE-001','content':'Synthetic fixture evidence; no collected content.'},
 'misconfig-analyzer':{'findings':[{'id':'MOCK-FINDING-001','type':'fixture-server-status','verified':False}]},
 'clearnet-correlator':{'matches':[{'service':'MOCK-SERVICE-A','origin':'192.0.2.10'}],'matching_performed':False},
 'blockchain-clusterer':{'clusters':[{'id':'MOCK-CLUSTER-A','wallets':['MOCK-WALLET-A','MOCK-WALLET-B']}],'heuristics_executed':False},
 'privacy-coin-analyzer':{'assessment':'MOCK-INSUFFICIENT','analysis_performed':False},
 'vasp-attributor':{'vasp':'MOCK-EXCHANGE','kyc_traceable':False,'identity_obtained':False},
 'stylometry-engine':{'fixture_pair':['MOCK-HANDLE-A','MOCK-HANDLE-B'],'fixture_similarity':0.92,'model_executed':False},
 'multilingual-nlp':{'fixture_text':'Synthetic example','fixture_language':'en','model_executed':False},
 'behavioral-profiler':{'fixture_profile':'MOCK-PROFILE-A','timezone_inferred':False},
 'cognitive-fingerprint':{'fixture_fingerprint':'MOCK-FINGERPRINT','identification_performed':False},
 'adversarial-defense':{'fixture_verdict':'mock-review','model_executed':False},
 'malware-sandbox':{'sample_id':'MOCK-SAMPLE','verdict':'mock-suspicious','code_executed':False},
 'image-forensics':{'image_id':'MOCK-IMAGE','location_inferred':False},
 'deepfake-detector':{'fixture_verdict':'mock-inconclusive','model_executed':False},
 'evidence-anchor':{'fixture_leaf':sha({'evidence':'MOCK-EVIDENCE-001'}),'external_anchor':False},
 'synthetic-media-analyzer':{'fixture_media_id':'MOCK-MEDIA','analysis_performed':False},
 'language-detector':{'fixture_language':'en','detector_executed':False},
 'transliteration-normalizer':{'fixture_input':'пример','fixture_output':'primer','arbitrary_text_supported':False},
 'yara-generator':{'rule_id':'MOCK-YARA','executable_rule_generated':False},
 'unified-graph':graph_fixture(),
 'entity-resolver':{'fixture_links':[{'from':'MOCK-HANDLE-A','to':'MOCK-ACTOR-A'}],'resolution_performed':False},
 'confidence-scorer':{'fixture_score':0.92,'calibrated':False,'scoring_performed':False},
 'gnn-deanon':{'fixture_link':'MOCK-LINK-A','inference_performed':False},
 'autonomous-agent':{'fixture_plan':['mock-observe','mock-review'],'external_actions':[]},
 'zkp-query-layer':{'proof':'MOCK-NOT-A-ZKP','cryptographic_proof_valid':False},
 'temporal-reasoner':{'fixture_interval':['2026-01-01T00:00:00Z','2026-01-02T00:00:00Z']},
 'source-reliability':{'fixture_source':'MOCK-SOURCE','rating':'MOCK-UNASSESSED'},
 'model-drift-monitor':{'fixture_drift':0.05,'model_loaded':False},
 'explainability-engine':{'rationale':'Links are specified by the bundled mock fixture, not inferred.'},
 'legal-admissibility':{'document':'MOCK EXHIBIT — NOT A LEGAL CERTIFICATE','legally_valid':False},
 'legal-intercept':{'request_id':'MOCK-REQUEST','state':'simulated-only','interception_enabled':False},
 'judicial-oversight':{'view':'mock-read-only-review','judicial_access_granted':False},
 'data-retention':{'fixture_expiry':'2026-02-01T00:00:00Z','would_expire':['MOCK-EVIDENCE-001'],'data_deleted':False},
 'classification-handler':{'classification':'MOCK-UNCLASSIFIED','official_classification':False},
 'court-exhibit-packager':{'package_id':'MOCK-PACKAGE','watermark':'SIMULATION — NOT FOR LEGAL USE'},
 'dpia-engine':{'assessment_id':'MOCK-DPIA','assessment_status':'illustrative-only'},
 'oversight-audit-log':{'view':'mock-audit-events','independent_judicial_system':False},
 'mlat-coordinator':{'request_id':'MOCK-MLAT','sent':False},
 'case-manager':{'case_id':'MOCK-CASE-001','state':'awaiting-review'},
 'pir-tracker':{'requirement_id':'MOCK-PIR-001','state':'fixture-satisfied'},
 'peer-review':{'review_required':True,'approval':'pending-separate-reviewer'},
 'bias-mitigation':{'fixture_flags':['mock-alternative-explanation'],'real_person_profiled':False},
 'analyst-wellness':{'fixture_workload':'mock-normal','people_monitored':False},
 'insider-threat':{'fixture_alert':'MOCK-ALERT','staff_monitored':False},
 'humint-manager':{'persona_id':'MOCK-PERSONA','covert_account_created':False,'contact_performed':False},
 'takedown-coordinator':{'request_id':'MOCK-TAKEDOWN','sent':False,'external_action':False},
 'analyst-api':{'simulation_auth':'actual bearer-role checks','oauth_jwt_mfa':'simulated interface only'},
 'analyst-dashboard':{'route':'/','implementation':'simulation console'},
 'graph-visualization':{'graph_fixture':'17 node types and 20 relationship types','real_attribution':False},
 'report-generator':{'formats':['json','csv','html','graphml'],'watermark':NOTICE},
 'admin-console':{'controls':['run','one-shot-fault','retry'],'real_services_managed':False},
 'inter-agency-gateway':{'recipient':'MOCK-AGENCY','delivery':'simulated','sent':False},
 'field-alerting':{'recipient':'MOCK-FIELD-UNIT','delivery':'simulated','sent':False},
}
for entry in CATALOG:
    if entry['id'] not in OUTPUTS and entry['plane']==2:
        OUTPUTS[entry['id']]={'records':[{'id':'MOCK-'+entry['id'].upper(),'text':'Bundled fictional content.','source':'fixture.invalid'}],'network_connection':False}
assert set(OUTPUTS)==set(BY_ID),'Every listed service must have an explicit fixture output'

def result(service,scenario,run_id,upstream_hash):
    if service not in BY_ID or scenario not in SCENARIOS:
        raise ValueError('Unsupported service or scenario')
    output=json.loads(json.dumps(OUTPUTS[service]))
    if scenario=='insufficient-evidence' and service in ('confidence-scorer','stylometry-engine','entity-resolver','gnn-deanon'):
        output={'fixture_verdict':'MOCK-INSUFFICIENT','links':[],'inference_performed':False}
    payload=dict(service=service,plane=BY_ID[service]['plane'],scenario=scenario,run_id=run_id,
        upstream_hash=upstream_hash,synthetic=True,operational=False,notice=NOTICE,output=output)
    return {**payload,'result_hash':sha(payload)}
