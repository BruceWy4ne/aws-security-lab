# Security Assessment Report

**Target:** EC2 Instance (OWASP Juice Shop Host)  
**Application:** OWASP Juice Shop (Node.js, Port 3000)  
**Environment:** Custom AWS VPC with public and private subnets

---

## Scope

This assessment evaluated the network security posture of an AWS environment hosting OWASP Juice Shop.

The review focused on:

- Network exposure
- Security Group configuration
- Network ACL configuration
- Subnet segmentation
- Reachability from the Internet
- Monitoring and visibility controls

Application-layer testing was not performed.

---

## Methodology

| Step | Tool | Purpose |
|--------|--------|--------|
| Port Discovery | Nmap | Identify exposed services |
| Path Validation | AWS Reachability Analyzer | Verify routable paths |
| Security Review | AWS Console | Evaluate Security Groups and NACLs |
| Architecture Review | AWS Console | Assess subnet segmentation and routing |
| Monitoring Review | AWS Console | Verify logging and visibility controls |

---

## Findings

### CRIT-01 — SSH Accessible from the Internet

**Severity:** Critical

**Evidence:**

- `screenshots/05-security-group-inbound.png`
- `screenshots/09-nmap-scan.png`

The Security Group permits inbound SSH (TCP/22) from `0.0.0.0/0`.

Nmap validation confirmed that SSH is externally reachable and responding.

Allowing unrestricted SSH access exposes the host to:

- Credential brute-force attacks
- Password spraying
- Exploitation of future SSH vulnerabilities
- Unauthorized access attempts from any Internet host

#### Recommendations

- Restrict SSH access to trusted IP ranges
- Use a bastion host
- Replace SSH with AWS Systems Manager Session Manager where possible

---

### CRIT-02 — Application Directly Exposed to the Internet

**Severity:** Critical

**Evidence:**

- `screenshots/03-ec2-instance.png`
- `screenshots/04-ec2-networking.png`
- `screenshots/11-reachability-analyzer.png`
- `screenshots/12-juiceshop-running.png`

The application is deployed on an EC2 instance located within a public subnet and assigned a public IPv4 address.

Reachability Analyzer confirmed that a complete network path exists from the Internet Gateway to the instance.

As a result, any application vulnerability would be directly reachable from the Internet without additional filtering layers.

#### Recommendations

- Deploy an Application Load Balancer (ALB)
- Move the EC2 instance into a private subnet
- Restrict direct access to application ports
- Allow inbound traffic only through the ALB

---

### HIGH-01 — VPC Flow Logs Disabled

**Severity:** High

**Evidence:**

- `screenshots/10-flow-logs-disabled.png`

No VPC Flow Logs were configured.

Without Flow Logs, there is limited visibility into:

- Port scans
- Rejected traffic
- Unexpected outbound connections
- Incident response investigations

#### Recommendations

- Enable VPC Flow Logs
- Forward logs to CloudWatch or S3
- Retain logs for at least 90 days
- Automate analysis using `flowlog_parser.py`

---

### HIGH-02 — Overly Permissive Security Group Rules

**Severity:** High

**Evidence:**

- `screenshots/05-security-group-inbound.png`

Multiple services are exposed to the entire Internet using `0.0.0.0/0`, including:

- SSH (22)
- HTTP (80)
- HTTPS (443)
- Application Port (3000)

While public web traffic may require exposure on ports 80 and 443, administrative and backend services should be restricted.

#### Recommendations

- Restrict SSH to trusted IP ranges
- Restrict application ports to internal Security Groups
- Use an ALB for external access
- Follow least-privilege principles

---

### MED-01 — Network ACL Provides Minimal Security Value

**Severity:** Medium

**Evidence:**

- `screenshots/06-nacl-inbound.png`
- `screenshots/07-nacl-outbound.png`

The default Network ACL allows all inbound and outbound traffic.

As configured, the ACL functions primarily as a pass-through mechanism and does not provide meaningful subnet-level filtering.

This reduces the effectiveness of defense-in-depth controls.

#### Recommendations

- Create dedicated NACLs per subnet
- Restrict inbound traffic to required ports only
- Restrict outbound traffic where appropriate
- Implement explicit deny rules where necessary

---

### LOW-01 — Private Subnet Lacks Outbound Internet Connectivity

**Severity:** Low

**Evidence:**

- `screenshots/08-nat-gateway-missing.png`
- `screenshots/02-vpc-resource-map.png`

No NAT Gateway was deployed for the private subnet.

While this is not a direct security vulnerability, it limits the ability of private resources to:

- Download operating system updates
- Retrieve application dependencies
- Access AWS services requiring outbound Internet connectivity

#### Recommendations

- Deploy a NAT Gateway for production environments
- Route private subnet outbound traffic through the NAT Gateway
- Maintain inbound isolation while enabling controlled outbound access

---

## Reachability Analysis

AWS Reachability Analyzer confirmed a valid path between the Internet Gateway and the EC2 instance.

The successful path traversed:

Internet Gateway → Network ACL → Security Group → EC2 Instance

**Status:** Reachable

This confirms that external traffic can reach the instance when permitted by Security Group rules.

**Evidence:**

- `screenshots/11-reachability-analyzer.png`

---

## Summary

| ID | Severity | Finding |
|------|------|------|
| CRIT-01 | Critical | SSH accessible from the Internet |
| CRIT-02 | Critical | Application directly exposed to the Internet |
| HIGH-01 | High | VPC Flow Logs disabled |
| HIGH-02 | High | Overly permissive Security Group rules |
| MED-01 | Medium | Network ACL provides minimal security value |
| LOW-01 | Low | Private subnet lacks outbound Internet connectivity |

---

## Recommended Remediation Order

1. Restrict SSH access
2. Enable VPC Flow Logs
3. Move application instances to private subnets
4. Introduce an Application Load Balancer
5. Harden Security Group rules
6. Implement custom Network ACLs
7. Deploy a NAT Gateway if private workloads require outbound connectivity

---

## Lessons Learned

A few things stood out during this assessment that I didn't fully appreciate before doing it hands-on.

The Reachability Analyzer was more useful than I expected — instead of mentally tracing rules, it walks the actual path component by component and shows exactly where traffic is allowed or blocked. That's a much faster way to validate exposure than reading Security Group rules in isolation.

The missing Flow Logs were also a reminder that detection gaps are easy to overlook when building an environment. The VPC looked functional from a routing perspective, but there was zero record of any traffic hitting it. In a real incident you'd have nothing to work with.

The NACL situation was interesting — it's the default configuration and it passes all traffic, which means a lot of AWS environments are running with NACLs that provide no actual filtering. They're easy to forget because Security Groups handle most of the work, but that's exactly the wrong reason to leave them unconfigured.
