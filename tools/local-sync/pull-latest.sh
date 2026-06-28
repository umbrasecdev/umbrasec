#!/usr/bin/env bash
# Keep a local UMBRASEC checkout in step with the github-actions[bot] KEV
# commits that land on origin/master twice a day. Safe to run from cron:
#  - only fast-forwards (never creates merge commits, never clobbers local work)
#  - only touches the tree when HEAD is on master
#  - if the working tree has diverged or is dirty in a conflicting way,
#    --ff-only refuses and the script exits non-zero without changing anything
#
# Install (hourly, quiet unless something changed):
#   crontab -l 2>/dev/null | { cat; echo '17 * * * * /home/atrax/Documents/projects/github/umbrasec/tools/local-sync/pull-latest.sh >> /home/atrax/Documents/projects/github/umbrasec/tools/local-sync/sync.log 2>&1'; } | crontab -

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO"

ts() { date '+%Y-%m-%dT%H:%M:%S%z'; }

branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$branch" != "master" ]; then
  # Refresh the remote ref so it's ready, but don't touch a feature branch.
  git fetch --quiet origin master || true
  echo "$(ts) on '$branch', not master - fetched only, no merge."
  exit 0
fi

before="$(git rev-parse HEAD)"
git fetch --quiet origin master

if git merge --ff-only --quiet origin/master 2>/dev/null; then
  after="$(git rev-parse HEAD)"
  if [ "$before" != "$after" ]; then
    echo "$(ts) fast-forwarded master ${before:0:7} -> ${after:0:7}"
  fi
  # silent when already up to date, to keep the cron log quiet
else
  echo "$(ts) WARNING: ff-only merge refused (local master diverged or dirty); left untouched."
  exit 1
fi
