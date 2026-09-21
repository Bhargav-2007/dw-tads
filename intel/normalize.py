"""Normalize only public vulnerability, malware, and technique records."""
from datetime import datetime, timezone


def timestamp(value):
    date=datetime.fromisoformat(value.replace('Z','+00:00'))
    if date.tzinfo is None:
        date=date.replace(tzinfo=timezone.utc)
    return date.astimezone(timezone.utc).isoformat()


def parse(source, doc):
    records=[]
    edges=[]
    if source=='cisa-kev':
        items=doc['vulnerabilities']
        if not isinstance(items,list) or not items:
            raise ValueError('Empty or invalid KEV catalog')
        for item in items:
            cve=item['cveID']
            if not cve.startswith('CVE-'):
                raise ValueError('Invalid CVE identifier')
            records.append(dict(id='cisa-kev:'+cve,source=source,external_id=cve,kind='vulnerability',
                title=item['vulnerabilityName'],description=item['shortDescription'],published_at=timestamp(item['dateAdded']),
                source_url='https://www.cisa.gov/known-exploited-vulnerabilities-catalog',
                data={k:item.get(k) for k in ['vendorProject','product','requiredAction','dueDate','knownRansomwareCampaignUse','cwes','notes']}))
    elif source=='mitre-attack':
        if doc.get('type')!='bundle':
            raise ValueError('Expected STIX bundle')
        for item in doc['objects']:
            if item.get('type') not in ('malware','attack-pattern') or item.get('revoked') or item.get('x_mitre_deprecated'):
                continue
            ref=next((r for r in item.get('external_references',[]) if r.get('source_name')=='mitre-attack'),{})
            records.append(dict(id='mitre-attack:'+item['id'],source=source,external_id=ref.get('external_id',item['id']),
                kind='malware' if item['type']=='malware' else 'technique',title=item['name'],description=item.get('description',''),
                published_at=timestamp(item['modified']),source_url=ref.get('url','https://attack.mitre.org/'),
                data={'platforms':item.get('x_mitre_platforms',[]),'created':item.get('created'),'modified':item['modified']}))
        identifiers={r['id']:r['kind'] for r in records}
        for item in doc['objects']:
            a='mitre-attack:'+item.get('source_ref','')
            b='mitre-attack:'+item.get('target_ref','')
            if (item.get('type')=='relationship' and item.get('relationship_type')=='uses'
                and not item.get('revoked') and not item.get('x_mitre_deprecated')
                and identifiers.get(a)=='malware' and identifiers.get(b)=='technique'):
                edges.append({'source_id':a,'target_id':b,'type':'uses'})
        if not records:
            raise ValueError('No supported technical objects in ATT&CK bundle')
    else:
        raise ValueError('Unsupported source')
    if len({r['id'] for r in records}) != len(records):
        raise ValueError('Duplicate source record identifiers')
    return records,edges
