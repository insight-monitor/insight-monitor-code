---
title: Customization Boundaries
type: policy
domain: inference
priority: high
status: review
version: 0.1.0
---

# Customization Boundaries

## What the user CAN customize

### Safe zone (allowed in all modes)
- Role and objectives
- Application classifications
- Work/study schedule
- Sensitivity keywords
- Data retention period
- Signal opt-in/opt-out (within policy limits)

### Restricted zone (personal mode only, with limits)
- Custom free-text instructions appended to prompt
- Custom classification rules for specific domains
- Export frequency and format

## What the user CANNOT customize

### Never modifiable
- System instruction layer (safety, format, constraints)
- Model architecture and inference parameters
- Redaction rules for credentials and PII
- Logging and audit requirements
- Minimum confidence thresholds for flagged inferences

## Boundary enforcement

Custom instructions are filtered by the safety layer before injection. Any instruction attempting to override system constraints is silently ignored and logged as an attempted override for audit.
