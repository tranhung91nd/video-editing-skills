#!/bin/bash
# Create a job folder with the Remotion template.  Usage: bash new_job.sh <job-dir>
set -e
JOB="$1"; [ -n "$JOB" ] || { echo "usage: new_job.sh <job-dir>"; exit 1; }
SK="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$JOB"/{voice/takes,music,source/raw,work,out,remotion/src,remotion/public/v}
cp "$SK/assets/remotion/src/index.tsx" "$JOB/remotion/src/"
cp "$SK/assets/remotion/tsconfig.json" "$SK/assets/remotion/package.json" "$SK/assets/remotion/package-lock.json" "$JOB/remotion/"
[ -f "$JOB/remotion/public/logo.png" ] || cp "$SK/assets/remotion/public/logo.png" "$JOB/remotion/public/"
[ -e "$JOB/remotion/node_modules" ] || ln -s "$HOME/.tour-ad-video/remotion/node_modules" "$JOB/remotion/node_modules"
echo "Job: $JOB"
