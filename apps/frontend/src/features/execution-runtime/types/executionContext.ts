export interface AuthorizationContext {
  principal: string;
  role: 'ADMINISTRATOR' | 'OPERATOR' | 'GUEST';
  workspace: string;
  device: string;
  capability: string;
  scope: string;
  risk: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  policy: 'ALLOW' | 'ALLOW_WITH_APPROVAL' | 'DENY';
}
