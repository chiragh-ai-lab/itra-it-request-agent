# Cedar Policies for IT Request Agent

This directory contains Cedar policy definitions that provide deterministic guardrails for agent actions.

## Policy Files

- `cedar-schema.json` - Defines the entity types (Principal, Action, Resource) and their attributes
- `cedar-policies.cedar` - Contains the actual policy rules

## Policies

### 1. No Provisioning Without Manager Approval
Prevents the agent from provisioning resources (cloud infrastructure, accounts, etc.) without explicit manager approval.

```cedar
forbid (
  principal,
  action == Action::"provision_resource",
  resource
) unless {
  resource.has_manager_approval == true
};
```

### 2. Force Escalation for Critical Requests
Prevents auto-resolution of severity 1 (critical) requests. These must be escalated to human operators.

```cedar
forbid (
  principal,
  action == Action::"auto_resolve",
  resource
) when {
  resource.severity == 1
};
```

### 3. Rate Limit Agent Actions
Limits the agent to a maximum of 5 actions per request to prevent runaway automation.

```cedar
forbid (
  principal,
  action == Action::"agent_action",
  resource
) when {
  resource.action_count >= 5
};
```

### 4. Restrict Payroll Access
Restricts access to payroll-related requests to the security team only.

```cedar
forbid (
  principal,
  action == Action::"access_payroll",
  resource
) unless {
  principal.role == "security"
};
```

## Integration

These policies are checked in `itra_agent_action.py` before executing any agent action. The Lambda function:

1. Loads the request context from DynamoDB
2. Constructs a Cedar authorization request
3. Evaluates the policies
4. Blocks the action if any policy forbids it
5. Logs policy blocks for observability

## Testing

Test scenarios are in `tests/fixtures/policy-test-cases.json`. Each test case includes:
- Request context
- Action to test
- Expected result (allow/deny)
- Policy that should trigger (if denied)

## Future Enhancements

- Integrate AWS Verified Permissions service for centralized policy management
- Add time-based policies (e.g., no auto-provisioning outside business hours)
- Add budget-based policies (e.g., block provisioning if monthly spend exceeds threshold)
- Add compliance policies (e.g., require multi-factor auth for sensitive actions)
