import assert from 'node:assert/strict';

const SHA256 = /^[0-9a-f]{64}$/i;
const COMMIT_SHA = /^[0-9a-f]{40}$/i;

// Only public Git provenance is released. No environment dump or credentials.
export function buildProvenance(env, exhibitSha256, ruleCount) {
  assert.match(exhibitSha256, SHA256, 'Invalid public exhibit fingerprint');
  assert.ok(Number.isInteger(ruleCount) && ruleCount === 1500, 'Invalid public rule count');

  const isVercel = env.VERCEL === '1';
  const vercelSha = env.VERCEL_GIT_COMMIT_SHA || null;
  const ciSha = env.CI_COMMIT_SHA || null;
  const sha = isVercel ? vercelSha : ciSha;
  if (isVercel && !sha) {
    throw new Error('Missing VERCEL_GIT_COMMIT_SHA: cannot attest deployed source');
  }
  if (sha && !COMMIT_SHA.test(sha)) {
    throw new Error('Invalid git commit SHA in build environment');
  }
  return {
    schema: 'basketlens.release-provenance.v1',
    gitSha: sha ? sha.toLowerCase() : null,
    source: isVercel ? 'vercel-git' : ciSha ? 'gitlab-ci' : 'unverified-local',
    exhibitSha256: exhibitSha256.toLowerCase(),
    ruleCount,
  };
}
