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
