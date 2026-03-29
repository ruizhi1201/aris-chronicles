#!/usr/bin/env python3
"""
Re-schedule ep03 with correct params:
- Date: 2026-03-29T11:00:00Z (7 AM ET)
- Accounts: YouTube 52328 + TikTok 51230
- TikTok is_aigc: true
- Correct YouTube title
"""
import json
import requests

PB_KEY = "pb_live_QWGrPJhVWSHvegGSQVw3P4"
STATUS_FILE = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/ep03-status.json"

headers = {
    "Authorization": f"Bearer {PB_KEY}",
    "Content-Type": "application/json"
}

# Existing media_id from previous upload — reuse it
EXISTING_MEDIA_ID = "263cc4ea-3a3d-4abc-86b6-e50dd6194f22"
OLD_POST_ID = "c7693b24-01e1-470e-b2ad-8cd89d4d4820"

# Step 1: Delete old post
print(f"Deleting old post {OLD_POST_ID}...")
del_resp = requests.delete(
    f"https://api.post-bridge.com/v1/posts/{OLD_POST_ID}",
    headers=headers
)
print(f"  Delete status: {del_resp.status_code}")
print(f"  Delete response: {del_resp.text[:300]}")

# Step 2: Create new post with correct params
print("\nCreating new scheduled post...")
caption = (
    "Kai Chen has 211 product ideas sitting in a folder he calls the graveyard. "
    "Today, for the first time in months, he opens it.\n\n"
    "#TheArisChronicles #SerialFiction #AIStory #Entrepreneurship"
)

post_payload = {
    "caption": caption,
    "media": [EXISTING_MEDIA_ID],
    "social_accounts": [52328, 51230],
    "scheduled_at": "2026-03-29T11:00:00Z",
    "platform_configurations": {
        "youtube": {
            "title": "Aris Chronicles Ep. 3 — 211 Funerals"
        },
        "tiktok": {
            "is_aigc": True
        }
    }
}

post_resp = requests.post(
    "https://api.post-bridge.com/v1/posts",
    headers=headers,
    json=post_payload
)
print(f"  Post status: {post_resp.status_code}")
print(f"  Post response: {post_resp.text[:1000]}")

if post_resp.status_code not in (200, 201):
    print("ERROR: Failed to create post")
    exit(1)

post_data = post_resp.json()
post_id = post_data.get("id") or post_data.get("post_id")
print(f"\nNew Post ID: {post_id}")

# Step 3: Save updated status
status = {
    "episode": 3,
    "title": "211 Funerals",
    "script": "EP003-211-funerals.md",
    "audio": "ep03-audio.mp3",
    "video": "ep03-final.mp4",
    "media_id": EXISTING_MEDIA_ID,
    "post_id": post_id,
    "scheduled_at": "2026-03-29T11:00:00Z",
    "scheduled_et": "2026-03-29 07:00:00 ET",
    "status": "scheduled",
    "social_accounts": [52328, 51230],
    "platforms": ["youtube (The Aris Chronicles)", "tiktok (dayryz.social)"],
    "youtube_title": "Aris Chronicles Ep. 3 — 211 Funerals",
    "caption": caption,
    "post_bridge_response": post_data
}

with open(STATUS_FILE, "w") as f:
    json.dump(status, f, indent=2)

print(f"\nStatus saved to {STATUS_FILE}")
print(f"Scheduled for: 2026-03-29T11:00:00Z (7:00 AM ET)")
