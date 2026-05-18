// MFA enrollment — disabled in v1 (SHIELD_AUTH_REQUIRE_MFA=false). Master Spec §4.5.
// The page renders null so existing links don't 404; v1.x activates without
// touching consumers.

export default function MfaEnrollPage() {
  return null;
}
