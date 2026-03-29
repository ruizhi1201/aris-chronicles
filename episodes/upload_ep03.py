#!/usr/bin/env python3
import os
import sys
import json
import requests

PB_KEY = "pb_live_QWGrPJhVWSHvegGSQVw3P4"
VIDEO_FILE = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/ep03-final.mp4"
STATUS_FILE = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes/ep03-status.json"

headers = {"Authorization": f"Bearer {PB_KEY}", "Content-Type": "application/json"}

# Step 1: Get file size
size_bytes = os.path.getsize(VIDEO_FILE)
print(f"File size: {size_bytes} bytes")

# Step 2: Create upload URL
print("Creating upload URL...")
resp = requests.post(
    "https://api.post-bridge.com/v1/media/create-upload-url",
    headers=headers,
    json={
        "mime_type": "video/mp4",
        "size_bytes": size_bytes,
        "name": "ep03-final.mp4"
    }
)
print(f"  Status: {resp.status_code}")
print(f"  Response: {resp.text[:500]}")
if resp.status_code not in (200, 201):
    print("ERROR: Failed to get upload URL")
    sys.exit(1)

data = resp.json()
upload_url = data.get("upload_url") or data.get("url") or data.get("uploadUrl")
media_id = data.get("media_id") or data.get("id") or data.get("mediaId")
print(f"  upload_url: {upload_url[:80] if upload_url else None}")
print(f"  media_id: {media_id}")

# Step 3: Upload file
print("Uploading file...")
with open(VIDEO_FILE, "rb") as f:
    put_resp = requests.put(
        upload_url,
        data=f,
        headers={"Content-Type": "video/mp4"}
    )
print(f"  Upload status: {put_resp.status_code}")
if put_resp.status_code not in (200, 201, 204):
    print(f"  Upload response: {put_resp.text[:200]}")
    print("ERROR: Upload failed")
    sys.exit(1)

# Step 4: Create post
print("Creating scheduled post...")
post_payload = {
    "caption": "Episode 3: 211 Funerals\n\nKai opens the folder. He does this sometimes. Not to feel bad about himself — just to remember he tried.\n\n211 ideas. All of them real. None of them built.\n\n#TheArisChronicles #SciFi #AIStory #SerialFiction",
    "media": [media_id],
    "social_accounts": [52328],
    "scheduled_at": "2026-03-31T12:00:00Z",
    "platform_configurations": {
        "youtube": {"title": "The Aris Chronicles | Ep. 3: 211 Funerals"}
    }
}
post_resp = requests.post(
    "https://api.post-bridge.com/v1/posts",
    headers=headers,
    json=post_payload
)
print(f"  Post status: {post_resp.status_code}")
print(f"  Post response: {post_resp.text[:500]}")

if post_resp.status_code not in (200, 201):
    print("ERROR: Failed to create post")
    # Save partial status
    status = {
        "episode": 3,
        "title": "211 Funerals",
        "media_id": media_id,
        "post_status": "failed",
        "post_response": post_resp.text[:500],
        "error": "Post creation failed"
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)
    sys.exit(1)

post_data = post_resp.json()
post_id = post_data.get("id") or post_data.get("post_id")
print(f"  Post ID: {post_id}")

# Step 6: Save status
status = {
    "episode": 3,
    "title": "211 Funerals",
    "script": "ep03-script.md",
    "audio": "ep03-audio.mp3",
    "video": "ep03-final.mp4",
    "media_id": media_id,
    "post_id": post_id,
    "scheduled_at": "2026-03-31T12:00:00Z",
    "scheduled_et": "2026-03-31 08:00:00 ET",
    "status": "scheduled",
    "post_bridge_response": post_data
}
with open(STATUS_FILE, "w") as f:
    json.dump(status, f, indent=2)

print(f"\nSuccess! Post ID: {post_id}")
print(f"Status saved to {STATUS_FILE}")
