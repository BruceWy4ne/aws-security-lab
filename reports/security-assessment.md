# Security Assessment Report

**Target:** EC2 instance `i-075854b6f1eda4e5b` — VulnerableInstance  
**Public IP:** 44.203.241.229  
**Application:** OWASP Juice Shop (Node.js, port 3000)  
**VPC:** ENPM665-midterm-vpc1 (10.0.0.0/16)  
**Region:** us-east-1

---

## Scope

Network-layer security review of a single AWS VPC environment.
Assessment covers inbound/outbound exposure, access control
configuration, network monitoring capability, and subnet segmentation.
No application-layer testing was performed.

---

## Methodology

| Step | Tool | What It Answered |
|------|------|-----------------|
| Port scan | Nmap `-sV -p 22,80,443,3000` | Which ports are open and what is running |
| Path validation | AWS Reachability Analyzer | Does a routable path exist from IGW to EC2 |
| Access control review | AWS Console | What the Security Group and NACL rules actually permit |
| Segmentation review | AWS Console | How subnets, route tables, and NAT are configured |
| Monitoring check | AWS Console | Whether VPC Flow Logs are enabled |

---

## Findings

---

### CRIT-01 — SSH Open to the Internet

**Severity:** Critical  
**Evidence:** `screenshots/05-security-group-inbound.png`, `screenshots/09-nmap-scan.png`

The Security Group (`sg-0513d25db218f89eb`) has an inbound rule allowing
TCP port 22 from `0.0.0.0/0`. Nmap confirmed this port is open and
identified the service as OpenSSH 8.7.

Any host on the internet can initiate an SSH connection attempt against
this instance. There is no rate limiting, no source restriction, and no
second factor enforced at the network layer.

**Remediation options:**
- Restrict port 22 to a specific IP (`your-ip/32`) in the Security Group
- Deploy a bastion host and allow SSH only from the bastion's Security Group ID
- Remove port 22 entirely and use AWS Systems Manager Session Manager —
  this eliminates the open port completely

---

### CRIT-02 — Application Running Directly in Public Subnet

**Severity:** Critical  
**Evidence:** `screenshots/03-ec2-instance.png`, `screenshots/04-ec2-networking.png`, `screenshots/13-juiceshop-running.png`

The EC2 instance sits in the public subnet (`subnet-0dc7413162c9ba630`)
with a direct public IP (`44.193.79.248`). The Juice Shop application is
accessible from any browser at `http://44.193.79.248:3000` with no
intermediate control between the internet and the application process.

Reachability Analyzer confirmed the path: Internet Gateway →
Network ACL (Rule 100, allow) → Security Group (port 3000 allow) →
EC2 instance. The path succeeds with no blocking component.

Any vulnerability in the application — authentication bypass, RCE,
file path traversal — gives an attacker direct access to the host.

**Remediation:**  
Deploy an Application Load Balancer in the public subnet. Move the
EC2 instance to the private subnet. The ALB becomes the only
internet-facing component; the EC2 gets no public IP.

---

### HIGH-01 — VPC Flow Logs Disabled

**Severity:** High  
**Evidence:** `screenshots/10-flow-logs-disabled.png`

The Flow logs tab for `vpc-095f7a5bcc4f4b8bd` shows "No flow logs found."
No traffic records exist for this environment — not accepted connections,
not rejected probes, not port scans.

Without flow logs there is no way to answer basic incident response
questions: Was this instance scanned? Did it make unexpected outbound
connections? Which source IPs have been connecting to port 3000?

**Remediation:**  
Enable VPC Flow Logs at the VPC level. Send to CloudWatch Logs for
real-time querying or to an S3 bucket for cost-efficient storage.
Set a 90-day retention minimum. The `flowlog_parser.py` script in
this repository can parse the resulting log files and summarize
rejected connections by source and port.

---

### HIGH-02 — No NAT Gateway Deployed

**Severity:** High  
**Evidence:** `screenshots/08-nat-gateway-missing.png`, `screenshots/02-vpc-resource-map.png`

The NAT Gateways console shows "No NAT gateways found." The private
subnet route table has no route to the internet at all — only a local
VPC route.

This means the private subnet EC2 instances have two bad options:
either they have no internet access at all (blocking OS updates, package
installs, AWS API calls), or they are moved to the public subnet to get
internet access, which defeats the purpose of the segmented design.

**Remediation:**  
Deploy a NAT Gateway in the public subnet. Update the private subnet
route table to send `0.0.0.0/0` traffic to the NAT Gateway. The private
instances get outbound internet access without any inbound exposure.

---

### HIGH-03 — Flat Security Group Rules

**Severity:** High  
**Evidence:** `screenshots/05-security-group-inbound.png`

All four inbound rules in the Security Group use `0.0.0.0/0` as the
source: ports 22, 80, 443, and 3000 are open to the entire internet.
This is appropriate only for ports 80 and 443 on a public web server —
not for SSH and not for a direct application port.

There is no segmentation between what external users should reach
(port 80/443 via a load balancer) and what should be internal-only
(port 22, port 3000).

**Remediation:**  
- Port 22: restrict to specific IP or Security Group ID (bastion)
- Port 3000: restrict to ALB Security Group ID only — no direct access
- Port 80/443: these can remain open once an ALB is in front

---

### MED-01 — Network ACL Provides No Restriction

**Severity:** Medium  
**Evidence:** `screenshots/06-nacl-inbound.png`, `screenshots/07-nacl-outbound.png`

The NACL `acl-0820601ddfa0378b6` is the default NACL for the VPC and
is associated with both subnets. Its only rule (100) allows all traffic
from `0.0.0.0/0` in both directions. It functions as a pass-through
with no filtering value.

NACLs are the subnet-level complement to Security Groups. In a properly
hardened environment they provide a second independent layer of control.
Here they add no protection at all.

**Remediation:**  
Create subnet-specific NACLs. For the public subnet: allow 80, 443
inbound from `0.0.0.0/0`; allow ephemeral ports (1024–65535) for
return traffic. For the private subnet: allow traffic only from the
public subnet CIDR. Deny everything else explicitly.

---

## Reachability Analyzer Results

AWS Reachability Analyzer confirmed a valid network path from Internet
Gateway `igw-0e84a79e9c3432c0f` to EC2 instance `i-075854b6f1eda4e5b`
on TCP port 22. The path traversed: Internet Gateway → NACL rule 100
(allow) → Security Group port 22 rule (allow) → EC2.

Status: **Reachable**. No blocking component exists in the path.

See `screenshots/11-reachability-analyzer.png`.

---

## Summary

| ID | Severity | Finding | Evidence |
|----|----------|---------|----------|
| CRIT-01 | Critical | SSH open to 0.0.0.0/0 | `05`, `09` |
| CRIT-02 | Critical | Application in public subnet, direct internet path | `03`, `04`, `13` |
| HIGH-01 | High | VPC Flow Logs disabled | `10` |
| HIGH-02 | High | No NAT Gateway | `08`, `02` |
| HIGH-03 | High | All SG rules sourced to 0.0.0.0/0 | `05` |
| MED-01 | Medium | NACL allows all traffic, no subnet-level filtering | `06`, `07` |

---

## Recommendations Priority Order

1. Enable VPC Flow Logs — takes 2 minutes, zero cost impact, immediate visibility
2. Restrict port 22 to your IP — one rule change, eliminates brute-force exposure
3. Deploy ALB + move EC2 to private subnet — resolves CRIT-02 and HIGH-03 simultaneously
4. Deploy NAT Gateway — unblocks private subnet outbound access
5. Create custom NACLs per subnet — adds independent defense layer
