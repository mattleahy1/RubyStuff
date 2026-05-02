#!/usr/bin/env bash
# Installs a daily cron job that runs the job search agent at 7 AM local time.
# Safe to re-run — will not add duplicate entries.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="$SCRIPT_DIR/run_job_search.sh"
CRON_LINE="0 7 * * * $RUNNER >> $SCRIPT_DIR/logs/cron.log 2>&1"
MARKER="# job-search-agent"

if ! crontab -l 2>/dev/null | grep -qF "$RUNNER"; then
  (crontab -l 2>/dev/null; echo "$CRON_LINE  $MARKER") | crontab -
  echo "Cron job installed: runs daily at 7 AM"
  echo "Entry: $CRON_LINE"
else
  echo "Cron job already installed (no changes made)"
fi

echo ""
echo "Current crontab entries for job-search-agent:"
crontab -l 2>/dev/null | grep -F "$MARKER" || echo "  (none found)"
echo ""
echo "To remove:  crontab -l | grep -vF '$MARKER' | crontab -"
echo "To run now: $RUNNER"
