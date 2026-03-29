#!/usr/bin/env python3
"""
Builds multi-voice dialog versions of Episodes 4 and 5 of The Aris Chronicles.

Voice assignments:
  Narrator → onyx    (deep, cinematic)
  Kai      → echo    (younger, introspective male)
  Hector   → shimmer (warm, optimistic — ep4 flashback)
  James    → shimmer (same warmth, slightly melancholy — ep5 memory)

Usage:
  python3 build_ep04_05_dialog.py 4    # Build episode 4
  python3 build_ep04_05_dialog.py 5    # Build episode 5
"""

import os, sys, json, subprocess, urllib.request, time

EPISODES_DIR = "/home/whoami/.openclaw/workspace/aris-chronicles/episodes"
OPENAI_KEY   = os.environ.get("OPENAI_API_KEY", "")

VOICES = {
    "narrator": "onyx",
    "kai":      "echo",
    "hector":   "shimmer",
    "james":    "shimmer",
}

# ── Episode 4: "The Hector Year" ───────────────────────────────────────────
EP4_SEGMENTS = [
    ("narrator", "Kai drives the long way home. Not because he needs to, but because the short way goes past the office, and on Saturdays the office parking lot is empty, and the empty parking lot does something to him that he would rather not name."),
    ("narrator", "He takes Route 9 instead, past the car washes and the mattress stores that never seem to have any customers, past the Dunkin that has been under construction for four months, past the billboard for a personal injury lawyer whose face seems to have faded, leaving behind just the phone number and a vague impression of confidence."),
    ("narrator", "He is narrating to himself. This is something he has started doing in the car. Not out loud, exactly — just a voice in the middle of his head that runs a dry commentary on the proceedings of his own life, as though he is both the subject and the journalist."),
    ("narrator", "Today the subject is Hector."),
    ("narrator", "Hector Marquez, twenty-nine, mechanical engineering degree, minor in computer science, terrific laugh, will make you feel understood — and then will disappear into a job offer in Austin without quite explaining what happened. Former co-founder. Former best thinking partner. Former person who answered his texts."),
    ("narrator", "It was not a bad partnership, in the beginning. That is the part that keeps needling Kai. It was actually good. They had the thing — the energy, the way two people can sit in a coffee shop for four hours and build an entire company in their heads and leave feeling like it is already real."),
    ("narrator", "They named it. They made a deck. They built a prototype that mostly worked. Hector stayed up three nights to fix a memory leak that was not even in his part of the code. Kai brought coffee and bad ideas, and Hector filtered the bad ideas and drank the coffee — and somehow that was enough."),
    ("narrator", "Then Hector got the offer."),
    ("narrator", "Kai is not sure, exactly, when the pivot happened. There was not a meeting where Hector said he was out. There were just longer gaps between messages. There was a conversation about equity that got awkward and then was never followed up on."),
    ("narrator", "There was a time Hector said he would look over the revised pitch deck. And then did not. Kai sent a reminder."),
    ("hector", "Sorry, been slammed."),
    ("narrator", "Kai said no worries. Two more weeks passed."),
    ("narrator", "And then at some point, without any ceremony at all, Hector was just gone."),
    ("narrator", "That was two years ago. Kai still has the Slack workspace. He logs in sometimes, not often. There are four hundred and twelve messages in the general channel, most of them from the six months they were actually working."),
    ("narrator", "Some of them are very good. Some of them are the kind of creative shorthand two people develop when they are really thinking together — references and half-sentences that would mean nothing to anyone else."),
    ("narrator", "He tried to draft a message to Hector on LinkedIn about a month ago. He wrote six versions and sent none of them."),
    ("narrator", "The first version was professional and a little cold, which felt dishonest. The second version was warm and a little needy, which felt worse. The third version asked directly about the equity situation — accurate, but probably wrong as an opening gambit."),
    ("narrator", "The fourth version pretended two years had not passed. The fifth version was actually good — the right length, the right tone — and then he read it one more time and realized it sounded like a pitch. He deleted that one too."),
    ("narrator", "The sixth version was three sentences."),
    ("kai", "Hey. Hope Austin is treating you well. I've been thinking about the old project."),
    ("narrator", "He stared at it for a while and then closed the tab."),
    ("narrator", "The problem, Kai thinks, is not that Hector betrayed him. If it were that simple, he would know what to do with it. He would put it in a box labeled betrayal, carry it for a while, and eventually set it down somewhere."),
    ("narrator", "But Hector did not betray him. Hector got a good job offer at a company with health insurance and a real salary and the kind of stability that is genuinely hard to argue against — especially when the thing you would be sacrificing it for is a prototype that mostly works and a deck and a name."),
    ("narrator", "Life happened around Hector, and the project disappeared into the space that was left. That is all."),
    ("kai", "That almost makes it worse."),
    ("narrator", "Because there is no one to be angry at. There is just the absence — which does not have a face, and so you cannot look it in the eye and tell it what it cost you. You can only drive the long way home and narrate to yourself, in the dry flat voice that has started living in the middle of your head, the story of how you had a co-founder and then you didn't."),
    ("narrator", "He passes a billboard on the right side of the highway. It is tall and backlit, the way billboards are at dusk when the sun is going but the light is not quite gone. The background is dark blue. The text is white and very clean."),
    ("narrator", "Your idea won't build itself."),
    ("narrator", "Below it, in smaller text: Meridian Software. We build for founders."),
    ("narrator", "It is an ad for a software agency. Kai recognizes the genre immediately — the slightly aggressive copy, the appeal to urgency, the targeting of a demographic that has a lot of ideas and not enough engineers."),
    ("narrator", "He puts on his turn signal, pulls onto the shoulder, and sits there for a moment with the engine running. Then he picks up his phone from the passenger seat and takes a photo."),
    ("narrator", "He is not sure why, exactly. He has no immediate plan for it. He will probably look at it later tonight and feel something in the vicinity of embarrassment and also something in the vicinity of recognition — the two feelings arriving together the way they often do."),
    ("narrator", "But he takes it anyway. The billboard, backlit against the darkening sky, the words patient and enormous above the highway. He sets the phone down and pulls back onto the road."),
]

# ── Episode 5: "The James Wound" ──────────────────────────────────────────
EP5_SEGMENTS = [
    ("narrator", "The cursor blinks. Kai has been staring at it for eleven minutes."),
    ("narrator", "The document is called untitled.md. He'll rename it when he's done, if he finishes, which he probably won't. That's what he tells himself every time he opens it and closes it without writing a word. He's opened it six times this week."),
    ("narrator", "Tonight is different. Tonight he leaves his hands on the keyboard and forces himself to stay."),
    ("kai", "His name was James."),
    ("narrator", "He stops. Deletes it. Types it again."),
    ("kai", "His name was James, and he was the best co-founder I never kept."),
    ("narrator", "Kai stares at that sentence for a long time. Then he keeps going."),
    ("narrator", "They met at a Midwest accelerator cohort in the spring, two years before Kai moved to the city, back when he still believed that the right room could change everything. James was the kind of person who made rooms feel smaller — not because he dominated them, but because he filled them completely."),
    ("narrator", "He had a way of listening that made you feel like the most interesting problem in the world. Kai noticed it immediately. He hated it a little. Then he wanted it."),
    ("narrator", "They spent four nights in a row talking through an idea Kai had been sitting on for eighteen months — a career navigation tool. Not a job board. Not a resume helper. Something that could model a person's actual trajectory and surface the paths that matched who they were becoming, not just who they'd been. Kai called it Pathline."),
    ("narrator", "James made it real. James was the one who found the first beta users. James was the one who wired the payment processor at two in the morning because neither of them could sleep. James was the one who wrote the emails, gave the demos, talked to the investors who almost said yes."),
    ("narrator", "Kai built the engine. James built the world around it. For eighteen months, it did."),
    ("narrator", "Kai pauses. His hands lift off the keyboard. He goes to the kitchen and stands by the window for three minutes without doing anything. Then he comes back."),
    ("narrator", "The pivot argument started on a Tuesday. Kai doesn't remember which Tuesday, exactly — but he remembers the light. Late afternoon, the office still humid from a broken AC unit, both of them exhausted in a way that had stopped feeling temporary."),
    ("narrator", "James had been talking to users. Not just their two paying beta customers, but people adjacent to the problem — people who almost fit the product but didn't quite. He'd found a pattern. The tool worked better as a recruiting surface than a personal growth tool. The demand signal was cleaner. The willingness to pay was higher."),
    ("james", "We should go where the water flows."),
    ("narrator", "Kai didn't."),
    ("narrator", "It wasn't stubbornness. He's told himself that a hundred times since. It was something more like grief, preemptive and irrational — the sense that pivoting meant admitting the original thing wasn't real, that the eighteen months weren't what he thought they were. James saw a business opportunity. Kai saw an obituary."),
    ("narrator", "The argument lasted three weeks. Not continuous — they'd go quiet for a few days, work in parallel, pretend it was resolved. Then one of them would say something and it would start again."),
    ("narrator", "On the twenty-second day, James sent a calendar invite."),
    ("james", "Dissolution Meeting."),
    ("narrator", "Kai accepted without responding. A lawyer handled the rest. The LLC was unwound with the kind of institutional efficiency that made Kai feel like none of it had meant anything. James moved to San Francisco six weeks later. They haven't spoken since."),
    ("narrator", "Pathline died on a Wednesday in November. The servers ran until February, when the hosting bill came due and Kai let it lapse."),
    ("narrator", "In April, six months after the shutdown, one of the two paying beta users emailed to ask when the product was coming back. She'd been recommending it to people. She thought it was just a hiatus. She said she'd pay more if that was the issue."),
    ("narrator", "Kai read the email on the train. He read it again that night. He started a draft reply four separate times. He never sent one."),
    ("narrator", "He still thinks about that sometimes — not as guilt, exactly, but as a kind of static. The person who wanted the thing he built. The product that worked for someone. The email he couldn't answer because answering it would have required explaining something he still doesn't have words for."),
    ("narrator", "He's tried to describe the James year to people since. Investors who ask about past projects. Founders who ask about early failures. He gives them the clean version: co-founder conflict, irreconcilable vision differences, amicable dissolution. It lands fine. Nobody pushes."),
    ("narrator", "The cursor blinks."),
    ("narrator", "Kai looks at what he's written. He doesn't edit it. He doesn't read it back. He types one more line at the bottom."),
    ("kai", "I need a co-founder who can't quit. I don't think that person exists."),
    ("narrator", "He saves the file. He renames it james.md. He moves it into the folder he keeps for things that are finished and dead. Pathline lives there. Three other projects live there. Now James does too."),
    ("narrator", "He closes the laptop. The room is very quiet."),
]

ALL_EPISODES = {
    4: EP4_SEGMENTS,
    5: EP5_SEGMENTS,
}


def tts_segment(text, voice, out_path):
    """Generate TTS for a single segment. Skips if file already exists."""
    if os.path.exists(out_path):
        print(f"    (cached) {os.path.basename(out_path)}")
        return

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
    time.sleep(0.3)  # rate-limit safety


def stitch_audio(segment_files, out_path):
    """Concatenate mp3 segments using ffmpeg concat demuxer."""
    list_file = out_path.replace('.mp3', '_list.txt')
    with open(list_file, 'w') as f:
        for sf in segment_files:
            f.write(f"file '{sf}'\n")
    result = subprocess.run(
        ['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
         '-i', list_file, '-c', 'copy', out_path],
        capture_output=True
    )
    os.remove(list_file)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg stitch failed: {result.stderr.decode()[-300:]}")


def get_audio_duration(path):
    out = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', path],
        capture_output=True, text=True
    )
    return float(out.stdout.strip())


def build_episode_audio(ep_num):
    segments = ALL_EPISODES.get(ep_num)
    if not segments:
        print(f"No segments defined for episode {ep_num}.")
        return None

    seg_dir = f"{EPISODES_DIR}/ep{ep_num:02d}-segs"
    os.makedirs(seg_dir, exist_ok=True)
    out_path = f"{EPISODES_DIR}/ep{ep_num:02d}-audio.mp3"

    print(f"\n🎙️  Episode {ep_num} — {len(segments)} segments")
    seg_files = []

    for i, (speaker, text) in enumerate(segments):
        voice = VOICES[speaker]
        seg_path = f"{seg_dir}/seg_{i:03d}_{speaker}.mp3"
        print(f"  [{i+1:02d}/{len(segments)}] {speaker} ({voice}): {text[:60]}...")
        tts_segment(text, voice, seg_path)
        seg_files.append(seg_path)

    print(f"\n  Stitching {len(seg_files)} segments → {out_path}")
    stitch_audio(seg_files, out_path)

    duration = get_audio_duration(out_path)
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"  ✅ Audio done: {size_mb:.1f} MB, {duration:.1f}s")
    return out_path, duration


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 build_ep04_05_dialog.py <episode_number>")
        print("  e.g.: python3 build_ep04_05_dialog.py 4")
        sys.exit(1)

    ep_num = int(sys.argv[1])
    if ep_num not in ALL_EPISODES:
        print(f"Episode {ep_num} not in this script. Available: {list(ALL_EPISODES.keys())}")
        sys.exit(1)

    result = build_episode_audio(ep_num)
    if result:
        audio_path, duration = result
        print(f"\n🎬 Audio ready: {audio_path} ({duration:.1f}s)")
        print(f"   Now run: python3 build_episode.py {ep_num}")


if __name__ == "__main__":
    main()
