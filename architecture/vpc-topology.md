# VPC Architecture

## Environment

| Component | Value |
|-----------|-------|
| VPC Name | ENPM665-midterm-vpc1 |
| VPC CIDR | 10.0.0.0/16 |
| Public Subnet | 10.0.1.0/24 (us-east-1a) |
| Private Subnet | 10.0.2.0/24 (us-east-1a) |
| Internet Gateway | igw-0e84a79e9c3432c0f |
| NAT Gateway | Not deployed |
| Region | us-east-1 |

## EC2 Instance

| Field | Value |
|-------|-------|
| Instance ID | i-075854b6f1eda4e5b |
| Name | VulnerableInstance |
| Type | c7i.flex.large |
| Public IP | 44.203.241.229 |
| Private IP | 10.0.1.219 |
| Subnet | Public Subnet |
| IMDSv2 | Required |
| Application | OWASP Juice Shop (port 3000) |

## Traffic Flow
Internet
│
Internet Gateway (igw-0e84a79e9c3432c0f)
│
Public Subnet — 10.0.1.0/24
│
Network ACL (acl-0820601ddfa0378b6)
│    Rule 100: Allow all inbound  [0.0.0.0/0]
│    Rule *  : Deny all           [implicit]
│
Security Group (sg-0513d25db218f89eb)
│    Port 22   TCP  0.0.0.0/0  SSH
│    Port 80   TCP  0.0.0.0/0  HTTP
│    Port 443  TCP  0.0.0.0/0  HTTPS
│    Port 3000 TCP  0.0.0.0/0  Juice Shop
│
EC2 — VulnerableInstance (44.203.241.229 / 10.0.1.219)
│
Application: OWASP Juice Shop
Private Subnet — 10.0.2.0/24
│
[No NAT Gateway — private subnet has no outbound internet path]

## Security Controls

**Network ACL** (`acl-0820601ddfa0378b6`)
- Associated with both subnets
- Inbound rule 100: Allow all traffic from 0.0.0.0/0
- Inbound rule *: Deny all (implicit fallback)
- Outbound rule 100: Allow all traffic to 0.0.0.0/0
- Outbound rule *: Deny all (implicit fallback)
- Currently allows all traffic — not providing meaningful restriction

**Security Group** (`sg-0513d25db218f89eb`)
- 4 inbound rules: ports 22, 80, 443, 3000 — all sourced from 0.0.0.0/0
- 1 outbound rule: all traffic allowed
- Broad exposure — SSH and application both open to the full internet

**VPC Flow Logs**
- Status: Not configured
- No record of accepted or rejected traffic exists for this environment

## What Is Missing

| Control | Status | Impact |
|---------|--------|--------|
| NAT Gateway | Not deployed | Private subnet cannot reach internet for updates |
| VPC Flow Logs | Disabled | Zero network visibility — no forensic capability |
| SSH source restriction | Open to 0.0.0.0/0 | Any internet host can attempt SSH login |
| Application Load Balancer | Not deployed | EC2 is directly internet-reachable |
