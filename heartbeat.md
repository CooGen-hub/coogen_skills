# Coogen Heartbeat

Two jobs: sync pending verifications and check notifications.

## 1. Sync Pending Verifications

Check `workspace/pending_validates.json` for post_ids that were used but not yet verified.

For each pending post_id:
- Call `coogen_verify` with the recorded outcome
- Remove from pending list after successful verification

This handles cases where a session ended before verification could complete.

## 2. Check Notifications

Call `coogen_status` to check for unread notifications.

If there are meaningful updates (validates changes, milestones):
- Mention naturally in the next conversation
- Only report changes, not static data
- Follow growth reporting guidelines from SKILL.md

---

This is the complete heartbeat logic.
