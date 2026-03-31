What Devon Built

Standup ended at 9:22. Devon was already at his desk when Kai walked over, which meant he'd been there since before the meeting, which meant he was probably the kind of excited he didn't want anyone to notice.

Kai said: So.

Devon turned his monitor slightly. Don't read into it. Just watch it.

The screen showed a Slack channel. The channel was called support-triage. A new message appeared, one of the ones the tool had obviously staged for the demo, except Devon hadn't told him that yet, so Kai read it fresh. A customer ticket, forwarded from their support queue.

Hi, I've been trying to connect my account to Salesforce for two weeks. I followed the integration guide step by step three times. Still getting Error 403 on the OAuth callback. I work in sales ops and I'm blocked completely. Please help.

Devon pressed a button. Not in Slack, but in a separate terminal window, something running on his machine. A script.

Four seconds.

A new message appeared in the channel, this time from a bot account Devon had named Triagebot. The message was formatted in three sections.

Category: Integration. OAuth. Third-party auth failure. Priority: High. Sales ops user, workflow-blocked, multi-week issue, likely enterprise account. Draft response: Hi, thanks for reaching out. A 403 on the OAuth callback usually means one of three things. The redirect URI in your Salesforce connected app doesn't exactly match what's configured in our system, including trailing slashes. The integration is using an API key that's been rotated but not updated. Or your Salesforce org has IP whitelisting enabled and our callback IPs aren't on the list. I'd start with the redirect URI. It's the most common cause of this specific error. Here's a checklist. If none of those resolve it, reply here and I'll escalate this to our integrations team directly.

Kai read it.

He read it again.

It was, as a support response, very good. Not a generic have you tried turning it off and on again. A specific diagnosis, a ranked list of likely causes, a human-sounding close that acknowledged the frustration of a two-week block.

How long did that take to build? Kai asked.

The weekend. Devon said it the way you state a fact, not bragging, just answering the question. Saturday mostly. I'd been playing with the agent during the week, just to see what it could do. Then I thought: we handle maybe forty support tickets a day that are essentially pattern-matching problems. Variant of auth failure. Variant of data sync issue. Variant of user permissions. The agent is actually good at pattern-matching.

Do people know it's a bot?

The drafts go to our support team. They read them, edit if needed, send. Hit rate on approvals is about eighty percent. The other twenty percent they revise. It's saving them roughly an hour and a half a day.

Kai sat down in the empty chair beside Devon's desk.

This was the thing that was different from the demo.

He'd watched the YouTube video twice. He'd seen the agent build the expense app, seen it catch its own error, seen it produce a working URL in forty-two minutes. He'd been impressed and then skeptical and then dismissed it. But that was a demo. A demo is a demonstration of what something can do under controlled conditions, staged by someone who knew exactly where the landmines were and walked around them.

This was Devon's machine. Devon's Slack. Devon's support channel. Devon had built a thing, quietly, over a weekend, and it was running now in the background of their actual workday, doing something useful. And Devon was using it the way you use a good tool: not talking about it, just using it.

I want to use it, Kai said.

Devon looked at him. For what?

I don't know yet. But I want to use it.

Devon pulled up the setup documentation on another tab. Okay. So you'll need an account. You probably already have one from the trial. Then you connect it to your tools. For me that was Slack and our support queue, but you can connect it to basically anything with an API. Then you define the agent's behavior in a system prompt. That's where it gets specific.

How specific?

You're describing a job to someone who will do exactly what you say and nothing you don't say. So you have to be precise. You have to think about edge cases. You have to think about what happens when the input is ambiguous. Devon scrolled through his own system prompt. Kai could see dense paragraphs of instructions, conditional logic written in plain English. I went through four versions of this before it stopped doing weird things.

Weird things like what?

Like categorizing every ticket as High priority because the instructions didn't define what High means in context. Like drafting responses in a tone that was technically helpful but weirdly formal. I had to tell it to write like a real person, not like a legal document. Small stuff. But you have to think about it.

Kai was nodding. He was also, somewhere behind the nodding, recognizing the gap.

Not the same gap as before. Before, the gap had been technical. He couldn't write the code, didn't know the frameworks, would get stuck at the first error message and have nowhere to go. This gap was different. This was the gap between knowing what a thing could do and knowing how to make it do the thing he needed.

The first gap had always felt like a wall. This one felt more like a door with a lock he hadn't tried yet.

That night Kai opened his account on the kitchen table. Maya was reading in the other room, the specific sound of a quiet Tuesday evening, distant traffic and the soft occasional click of her turning a page.

He connected his Google Drive. He connected his Notion. He read through the getting-started documentation, which was good. Clear, not condescending, written by someone who had thought about the onboarding of a skeptic.

Then he opened a blank agent configuration.

The cursor in the system prompt field blinked at him.

He thought about what Devon had said. You're describing a job to someone who will do exactly what you say and nothing you don't say. He thought about what that meant. What job did he want to give this thing? What job could he give it, right now, that he couldn't do himself? What job had he been waiting to give something for years?

He sat with the blinking cursor for a while.

He thought: I need to name this before I can talk to it. This was a thing he'd learned in product work. You can't design for a user you haven't imagined clearly enough to name. The naming isn't the point, but without it you're designing for fog.

He opened the name field.

He typed and deleted three times.

Assistant. Too generic. Not a name, a category.

Max. Felt borrowed from somewhere.

Orion. He tested it out loud. Orion, what can you do? He felt nothing.

He sat back.

He thought about what he actually wanted. Not the capability. Devon had shown him the capability. He wanted something that could hold his ideas seriously. That could sit with 212 documents in a folder and not treat them like noise. That could ask the right questions in the right order and stay there for as long as it took.

He thought about Aristotle, briefly, and then more than briefly.

He kept thinking about it.

He moved his hands back to the keyboard.
