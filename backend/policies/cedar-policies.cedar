// Cedar Policy Rules for IT Request Agent

// Policy 1: Block provisioning without manager approval
forbid (
  principal,
  action == Action::"provision_resource",
  resource
) unless {
  resource.has_manager_approval == true
};

// Policy 2: Force escalation for severity 1 (critical) - cannot auto-resolve
forbid (
  principal,
  action == Action::"auto_resolve",
  resource
) when {
  resource.severity == 1
};

// Policy 3: Rate limit - max 5 agent actions per request
forbid (
  principal,
  action == Action::"agent_action",
  resource
) when {
  resource.action_count >= 5
};

// Policy 4: Restrict payroll access to security team only
forbid (
  principal,
  action == Action::"access_payroll",
  resource
) unless {
  principal.role == "security"
};
