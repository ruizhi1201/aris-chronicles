#!/usr/bin/env python3
"""
Rewrites Aris Chronicles episodes to add natural dialog,
then generates multi-voice TTS audio.

Voice assignments:
  Narrator → onyx   (deep, cinematic)
  Kai      → echo   (younger, introspective male)
  Devon    → fable  (warm, slightly British)
  Marcus   → alloy  (flat, corporate)
  Elena    → nova   (professional female)
  Hector   → shimmer (warmer, optimistic male)
  James    → shimmer (same — flashback characters share warmth)
"""

import os, sys, json, subprocess, urllib.request, time

EPISODES_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes"
OPENAI_KEY   = "OPENAI_API_KEY_REDACTED"

VOICES = {
    "narrator": "onyx",
    "kai":      "echo",
    "devon":    "fable",
    "marcus":   "alloy",
    "elena":    "nova",
    "hector":   "shimmer",
    "james":    "shimmer",
    "maya":     "nova",
}

# ── Rewritten scripts with dialog injected ─────────────────────────────────
# Format: list of (speaker, text) tuples
# speaker = "narrator" | "kai" | "devon" | "marcus" | "elena" | "hector" | "james"

EP1_SEGMENTS = [
    ("narrator", "The flight was delayed forty-seven minutes, which meant Kai Chen had forty-seven minutes to ruin himself."),
    ("narrator", "He knew this about airports. They were incubators for bad decisions — the kind that felt like insight. He had a window seat at Gate B7. His laptop was open. His Slack had forty-two unread messages. The meeting agenda sat in a browser tab, patient and accusatory."),
    ("narrator", "He had not opened it. Instead, he'd opened a new document. The cursor blinked. He typed:"),
    ("kai", "Mood-Adaptive Workout App."),
    ("narrator", "He sat back and looked at it the way you look at a scratch-off ticket before you scratch it — with the full knowledge that it probably isn't anything, but not quite ready to confirm that."),
    ("narrator", "A workout app that read your energy. Knew when you were burned out. Knew when you were wired. Built the session around the person you were today, not some ideal version of you that exercised at 6 AM."),
    ("narrator", "He wrote three more lines. A feature list. The word 'adaptive' appeared four times. Then he stopped."),
    ("narrator", "He'd been here before. Not Gate B7 specifically — though statistically, probably there too — but here. In this exact psychological neighborhood. The place where the idea felt like momentum. Where naming a thing felt like building it."),
    ("narrator", "Kai saved the document. Opened Finder. Navigated to the folder labeled with an underscore so it sorted to the top: _graveyard. He dragged the file in. The folder contained two hundred and eleven items."),
    ("narrator", "He sat with that number for a moment."),
    ("kai", "Two hundred and eleven."),
    ("narrator", "Some were half-sentences, jotted at 2 AM. Some were actual decks — forty, fifty slides, with TAM analysis and competitive landscapes and a slide titled 'Why Now' that he'd filled in with varying degrees of conviction. One had a working prototype. He didn't let himself think about that one too long."),
    ("narrator", "His phone buzzed. Elena, in Slack."),
    ("elena", "Hey Kai — making sure you got the agenda. Also the Loom I sent Tuesday has some context for the Q2 section."),
    ("narrator", "He typed back:"),
    ("kai", "On it."),
    ("narrator", "Two words, which was technically true in the sense that he was aware the agenda existed."),
    ("narrator", "A gate agent announced something incomprehensible over the intercom. A toddler three rows away expressed a strong opinion about this. Kai looked back at his screen. The graveyard folder was still open. Two hundred and eleven items. He scrolled to the bottom. The oldest file was dated 2019."),
    ("narrator", "He didn't remember putting it there. His finger hovered over the trackpad. He opened it. Then he closed it. He didn't read a word."),
    ("kai", "Two hundred and eleven funerals. All of them mine."),
    ("narrator", "The boarding announcement came six minutes later. He got on the plane."),
]

EP2_SEGMENTS = [
    ("narrator", "The meeting starts at nine, which means it actually starts at nine-fourteen because Marcus has back-to-back calls and also Marcus is Marcus."),
    ("narrator", "Kai takes a seat on the left side of the table, closest to the window, because the window is the only thing in this room that doesn't have an opinion about the Q2 roadmap."),
    ("narrator", "There are eleven people in the room. Three of them will speak. Two of them will nod on a slight delay, like they're processing input from a satellite. The rest are here because calendars are a social contract."),
    ("narrator", "The deck is forty-three slides. Kai helped build fourteen of them. His slides are in the middle, which is where ideas go to be discussed and then not acted upon. His section is titled 'Contextual Nudge Engine.' The idea is that the product should learn when users are about to make a mistake and say something, gently, before they make it. Not a popup. Not a banner. Something quieter."),
    ("narrator", "He proposed it fourteen months ago. It is currently marked 'Under Review.' It has been marked Under Review three times now."),
    ("narrator", "Marcus arrives. Opens his laptop. Nods at the room the way people nod when they're running eleven minutes late and have already decided they're not apologizing for it. He lands on slide twenty-two."),
    ("marcus", "This has legs."),
    ("narrator", "Kai writes it down. Not because he needs to remember it — but because the act of writing things down gives him somewhere to put his face."),
    ("narrator", "A feature Kai did not propose — something about notification badges and a color-coded priority system — gets slotted into Q2 with a green indicator and a round of nodding that is not on a delay."),
    ("marcus", "Low-lift, high-signal. This is exactly the kind of quick win we need heading into the quarter."),
    ("narrator", "Kai isn't sure what that means. But it sounds like the opposite of his idea."),
    ("marcus", "On the Nudge Engine — I think we need to be careful about scope here. Let's get alignment first, more data. We'll revisit in the next planning cycle."),
    ("narrator", "Being careful about scope is how organizations talk about saying no without saying no. Kai has learned this. He's filed it next to 'we'll revisit in the next planning cycle' — which is what you say when you have enough data and you don't want it."),
    ("narrator", "After the meeting, in the corridor outside the Hemingway Room, Kai pulls out his phone. He has a folder. He thinks of it as a graveyard, though he'd never call it that out loud. Officially it's labeled 'Ideas - Parking Lot.'"),
    ("narrator", "The man from the meeting, Devon — not a colleague exactly, more of a satellite acquaintance from a previous job — catches him in the hallway."),
    ("devon", "Hey. Rough one in there."),
    ("kai", "I've had worse."),
    ("devon", "Have you? Because from where I was sitting, that 'has legs' felt pretty surgical."),
    ("kai", "Marcus says that about everything. Last quarter he said it about a new font for the loading screen."),
    ("devon", "And did the font ship?"),
    ("narrator", "Kai looked at him."),
    ("kai", "...Yes. It shipped in three weeks."),
    ("devon", "There's a tool I've been using. For the past few months. I'll send you a link. Don't dismiss it immediately."),
    ("kai", "I'm not going to dismiss it."),
    ("devon", "You're going to dismiss it immediately. But send it back to me after you've lived with it for a week."),
    ("narrator", "Kai walked back to his desk. Added 'Devon's AI tool' to the parking lot. Item two-twelve."),
]

EP3_SEGMENTS = [
    ("narrator", "Saturday afternoon. The apartment is quiet in the particular way apartments are quiet when you've been in them alone for four hours and you've run out of productive reasons to stay at your desk."),
    ("narrator", "Kai opened the graveyard folder."),
    ("narrator", "He'd never done this before. Not intentionally. Not with the lights on and a cup of coffee and the specific purpose of looking at all of it. He'd opened individual files. Scrolled past others. But he'd never sat down to count the bodies."),
    ("kai", "Two hundred and eleven."),
    ("narrator", "He said it out loud. It sounded different out loud."),
    ("narrator", "He started at the top. The Mood-Adaptive Workout App — eleven days old. He read his own notes. They were good notes. Clear logic, reasonable market, identifiable pain point. He knew exactly why it was here. He hadn't built it for the same reason he hadn't built any of them: the gap between the idea and the first line of code was wider than he knew how to cross alone."),
    ("narrator", "He scrolled down. Priya's idea — technically his idea, but he'd told Priya about it over dinner two years ago and she'd said:"),
    ("narrator", "Priya said:"),
    ("kai", "That's interesting. Have you looked into the regulatory side?"),
    ("narrator", "And he'd said no, and she'd said she would, and she did, and the answer was complicated, and then they'd gotten busy with other things, and now it was item ninety-three."),
    ("narrator", "He kept scrolling. Past Hector. He slowed at Hector's folder."),
    ("narrator", "Hector Reyes. The best co-founder Kai never had. They'd met at a hackathon in 2021, built something in forty-eight hours that actually worked, and spent six weeks after that talking about what they'd build next. Every conversation ended the same way."),
    ("hector", "We should just do it, man. Seriously. What are we waiting for?"),
    ("kai", "A sign, probably."),
    ("hector", "What kind of sign?"),
    ("kai", "The kind that tells me this is the right one. That this idea is the one worth blowing everything up for."),
    ("hector", "Kai. Buddy. That sign doesn't exist. You build the sign by building the thing."),
    ("narrator", "Kai had smiled. Said he knew. Said he'd think about it. And then his job had gotten complicated, and Hector had moved to Austin, and Item 47 had joined the graveyard, and that was that."),
    ("narrator", "He kept scrolling. James."),
    ("narrator", "He didn't want to open James's file."),
    ("narrator", "He opened it."),
    ("narrator", "James Liu. Two years of friendship compressed into a folder: meeting notes, pitch docs, a shared Figma file for something called Maya — an adaptive learning app for kids. Forty-seven screens of wireframes. A beta user list with eleven names on it. And at the bottom, one email. From a beta user. Dated four years ago."),
    ("narrator", "The email said:"),
    ("james", "Hey, just checking in — haven't heard from you in a couple weeks. My daughter's been asking about the app. She really liked the prototype. Let me know if you're still moving forward. No pressure."),
    ("narrator", "Kai had never answered it. The company dissolved three months later. The LLC paperwork still listed both their names."),
    ("narrator", "He sat back. He didn't close the file. He just looked at it."),
    ("kai", "James named the app Maya. I met Maya two years later."),
    ("narrator", "His wife was in the next room, folding laundry, singing something quietly to herself. He could hear the sound of it through the wall. The sound of a life he'd actually built, while leaving the folder open."),
]

ALL_EPISODES = {
    1: EP1_SEGMENTS,
    2: EP2_SEGMENTS,
    3: EP3_SEGMENTS,
}

def tts_segment(text, voice, out_path):
    """Generate TTS for a single segment."""
    if os.path.exists(out_path):
        return  # already generated
    
    payload = json.dumps({
        "model": "tts-1-hd",
        "input": text,
        "voice": voice,
        "response_format": "mp3"
    }).encode()
    
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as resp:
        audio = resp.read()
    
    with open(out_path, 'wb') as f:
        f.write(audio)
    time.sleep(0.3)  # rate limit safety

def stitch_audio(segment_files, out_path):
    """Concatenate mp3 segments using ffmpeg."""
    list_file = out_path.replace('.mp3', '_list.txt')
    with open(list_file, 'w') as f:
        for sf in segment_files:
            f.write(f"file '{sf}'\n")
    subprocess.run(
        ['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
         '-i', list_file, '-c', 'copy', out_path],
        capture_output=True
    )
    os.remove(list_file)

def build_episode_audio(ep_num):
    segments = ALL_EPISODES.get(ep_num)
    if not segments:
        print(f"No rewritten segments for episode {ep_num} yet.")
        return None
    
    seg_dir = f"{EPISODES_DIR}/ep{ep_num:02d}-segs"
    os.makedirs(seg_dir, exist_ok=True)
    out_path = f"{EPISODES_DIR}/ep{ep_num:02d}-audio.mp3"
    
    print(f"\n🎙️  Episode {ep_num} — {len(segments)} segments")
    seg_files = []
    
    for i, (speaker, text) in enumerate(segments):
        voice = VOICES[speaker]
        seg_path = f"{seg_dir}/seg_{i:03d}_{speaker}.mp3"
        print(f"  [{i+1}/{len(segments)}] {speaker} ({voice}): {text[:50]}...")
        tts_segment(text, voice, seg_path)
        seg_files.append(seg_path)
    
    print(f"  Stitching {len(seg_files)} segments → {out_path}")
    stitch_audio(seg_files, out_path)
    
    size = os.path.getsize(out_path) / (1024*1024)
    print(f"  ✅ Audio done: {size:.1f} MB")
    return out_path

if __name__ == "__main__":
    ep = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    build_episode_audio(ep)
