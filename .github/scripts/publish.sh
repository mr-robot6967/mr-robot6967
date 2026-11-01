#!/usr/bin/env bash
# Publish a generated directory to the single-commit `output` branch, so daily bot commits stay out of main's history.
# Several workflows share the branch; the lease makes a lost race fail the push, and the loop retries on the new tip.
set -euo pipefail

dir=$1
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

for attempt in 1 2 3 4 5 6; do
  work=$(mktemp -d)

  if git ls-remote --exit-code --heads origin output >/dev/null 2>&1; then
    git fetch -q origin +refs/heads/output:refs/remotes/origin/output
    tip=$(git rev-parse origin/output)
    git worktree add -q --detach "$work" "$tip"
  else
    tip=""
    git worktree add -q --detach "$work"
    git -C "$work" checkout -q --orphan publish
    git -C "$work" rm -rfq .
  fi

  rm -rf "${work:?}/$dir"
  mkdir -p "$work/$dir"
  cp -R "$dir"/. "$work/$dir"/

  git -C "$work" add -A
  if git -C "$work" diff --cached --quiet; then
    git worktree remove --force "$work"
    exit 0
  fi
  if [ -n "$tip" ]; then
    git -C "$work" commit -q --amend -m "Generated images"
  else
    git -C "$work" commit -q -m "Generated images"
  fi

  if git -C "$work" push -q --force-with-lease="refs/heads/output:$tip" origin HEAD:output; then
    git worktree remove --force "$work"
    exit 0
  fi
  git worktree remove --force "$work"
  sleep $((RANDOM % 4 + 1))
done
echo "could not publish $dir after several attempts" >&2
exit 1
