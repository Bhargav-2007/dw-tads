# Full application: free-hosting readiness

Status: NOT DEPLOYED. User requires the full application with real data, not a sample-data demo. No cloud account or server has been supplied. Do not publish the frontend alone as a working deployment.

## Candidate hosting route (checked 21 September 2026)

Oracle Cloud Always Free Ampere A1 currently provides an aggregate 2 OCPUs / 12 GB memory allowance for Always Free tenancies (1,500 OCPU-hours and 9,000 GB-hours per month), with up to 200 GB combined boot/block storage. Resources must be Always Free-eligible and in the home region. Availability is not guaranteed and idle resources can be reclaimed. A small installation may fit; this repository has not been load-tested against those limits. All container images must be checked for ARM64 support before choosing an A1 instance.

Official limits: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
Account signup: https://www.oracle.com/cloud/free/

The user must create their own account and complete the provider's identity, terms and payment-verification steps. Do not send account passwords, payment details, private keys or MFA secrets through chat. Do not upgrade to paid services or exceed free allocations without explicit authorization. No resources have been created and no costs have been incurred by this deployment task.

Render free hosting is unsuitable for preserving this full stack as-is: free web services cannot attach persistent disks, and free Render Postgres expires after 30 days. https://render.com/docs/free

## Backend work required before deployment

1. Expose a real HTTP analyst service implementing the frontend contract: /auth/token, /query/timeline, /query/actor/{id}, /query/graph, /query/sources, /query/audit, /export, /health, /ready, /metrics.
2. The existing plane7 service is a message handler with simulated responses, not a conforming HTTP authentication backend. Its advertised route list is not evidence that the runner serves these routes. The existing plane6 authentication handler contains Argon2/JWT/TOTP logic, but is not exposed as the required HTTP application.
3. Preserve real-data semantics. `intel/app.py` models technical intelligence records rather than the frontend's attributed actors. Do not relabel vulnerability records as threat actors or fabricate confidence, actor associations, source success or audit verification.
4. Provision new administrator credentials and an authenticator enrollment. `infra/postgres/init.sql` contains known demonstration users and MFA secrets; these must not become online production credentials. The current frontend cannot authenticate until a running service and account are provisioned.
5. Use persistent PostgreSQL, Neo4j, Kafka and MinIO volumes; verify ingestion actually produces the queried entities. Reconcile the existing online and airgap Compose service/network definitions before treating them as a deployment manifest.
6. Keep database and broker ports private. Expose only the HTTPS application ingress. Use generated secrets, backend role enforcement, login rate limiting, validated JWT expiry, and TOTP replay prevention.
7. Verify restart persistence, query ownership for exports, audit-chain validity and backup restoration with actual services. A successful frontend build and API fixture tests are not substitutes.

## Account handoff

After the user creates the cloud account, establish an approved connection to a free-eligible VM in that account. Confirm the selected compute, storage, architecture and resource limits before provisioning. Use provider-managed authentication or a local SSH agent/key file, not credentials pasted into chat.

Deployment is complete only after the hosted URL serves the frontend, a newly provisioned real account signs in, and real backend queries and exports pass verification. At present, both the hosting account and backend integration are outstanding.