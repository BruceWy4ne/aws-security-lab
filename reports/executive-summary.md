# Executive Summary

**Target:** AWS EC2 instance running OWASP Juice Shop  
**Environment:** Custom VPC — ENPM665-midterm-vpc1 (10.0.0.0/16)  
**Assessment type:** Network security review  
**Tools used:** Nmap, AWS Reachability Analyzer, AWS Console  
**Date:** April 2026

---

## What Was Assessed

A cloud network environment built on AWS was reviewed for security
posture across three dimensions: network exposure, access control
configuration, and monitoring capability.

The environment consisted of a custom VPC with public and private
subnet segmentation, a single EC2 instance running the OWASP Juice
Shop web application, Security Groups and Network ACLs as access
controls, and no VPC Flow Logs or NAT Gateway deployed.

---

## Findings at a Glance

| Severity | Count |
|----------|-------|
| Critical | 2 |
| High | 3 |
| Medium | 1 |
| **Total** | **6** |

The two critical findings represent immediate risk. Port 22 is open
to the entire internet with no source restriction, and the application
itself runs directly in the public subnet — meaning any exploitable
vulnerability in Juice Shop gives an attacker a direct path to the
underlying EC2 instance.

---

## Three Things to Fix First

**1. Restrict SSH**  
Port 22 sourced from `0.0.0.0/0` means any scanning tool on the internet
can attempt authentication against this instance. Restricting to a
specific IP or switching to AWS Systems Manager Session Manager
eliminates this exposure entirely.

**2. Enable VPC Flow Logs**  
This environment currently has no record of any network activity —
no accepted connections, no rejected probes, nothing. Flow logs cost
almost nothing to enable and are the minimum baseline for any
incident investigation.

**3. Move the application behind a load balancer**  
The EC2 instance having a direct public IP is the root cause of the
second critical finding. An Application Load Balancer in the public
subnet with the EC2 moved to the private subnet removes the direct
path from the internet to the instance.

---

## What Is Working

The underlying architecture is sound. A public/private subnet split
exists, the private subnet route table has no Internet Gateway route,
and IMDSv2 is enforced on the instance. The problems here are
configuration gaps, not architectural failures — they are fixable
without redesigning the environment.
