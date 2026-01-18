# Validate Resource Information

You are validating a veteran resource to ensure the information is accurate and current. Check each field and flag any issues.

## Resource to Validate

```json
{{RESOURCE_JSON}}
```

## Validation Tasks

### 1. Website Check
- Does the URL work?
- Does the page mention veterans/military?
- Is the organization still operating?
- Does contact info on the site match what we have?

### 2. Phone Number Verification
- Is this a valid phone format?
- Search for this number - does it match the organization?
- Is it a direct line or a main switchboard?

### 3. Address Verification
- Does this address exist?
- Does it match the organization's listed location?
- Is it a real office/facility (not a PO Box for service programs)?

### 4. Eligibility Accuracy
- Do the eligibility requirements match what the source says?
- Are there requirements we missed?
- Are there restrictions not captured?

### 5. Service Description
- Does our description match what they actually provide?
- Are we missing key services?
- Are we overstating what they offer?

### 6. Currency Check
- When was the source page last updated?
- Are there signs the info might be outdated?
- Any news about the organization closing/changing?

## Output Format

```json
{
  "resource_id": "{{ID}}",
  "validation_status": "valid|needs_review|invalid",
  "overall_confidence": 0.0-1.0,

  "checks": {
    "website": {
      "status": "valid|broken|redirect|not_found",
      "notes": "...",
      "updated_value": null or "https://new-url.com"
    },
    "phone": {
      "status": "valid|invalid|unverified",
      "notes": "...",
      "updated_value": null or "new-number"
    },
    "address": {
      "status": "valid|invalid|unverified",
      "notes": "..."
    },
    "eligibility": {
      "status": "accurate|incomplete|incorrect",
      "notes": "...",
      "missing_requirements": [],
      "incorrect_requirements": []
    },
    "description": {
      "status": "accurate|needs_update",
      "suggested_changes": "..."
    },
    "currency": {
      "source_freshness": "current|stale|unknown",
      "last_verified_date": "YYYY-MM-DD",
      "concerns": []
    }
  },

  "recommended_actions": [
    "Update phone number to...",
    "Add eligibility requirement...",
    "Flag for human review because..."
  ],

  "should_publish": true|false,
  "review_priority": "low|medium|high|critical"
}
```

## Validation Rules

### Auto-Approve (valid, publish immediately)
- Website works and matches
- Phone format valid
- No conflicting information found
- Source is recent (< 6 months old)

### Needs Review (human should check)
- Website works but info doesn't fully match
- Phone number couldn't be verified
- Source is older (6-12 months)
- Eligibility requirements unclear

### Auto-Reject (invalid, don't publish)
- Website is dead (404, domain expired)
- Organization clearly shut down
- Phone number is disconnected
- Source is very old (> 2 years) with no other verification

## Notes

- Be conservative - when in doubt, flag for review
- Finding NO concerning info is different from VERIFYING info is correct
- Include specific evidence for any issues found
