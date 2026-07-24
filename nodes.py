"""
Clippy Reborn Image Loader for ComfyUI

Load images directly from the system clipboard.
Just copy an image from anywhere (browser, image editor, etc.) and load it.

"It looks like you're trying to load an image!"
"""

import json
import os
import secrets
import time
import numpy as np
import torch
from PIL import ImageGrab, Image
import folder_paths


# ============================================================================
# MESSAGE BOOKKEEPING
# Clippy never repeats himself until he has said everything he has to say.
# Seen messages are tracked per category and persisted (keyed by message text,
# so updates that add or remove messages simply grow or shrink the unseen
# pool). When a category is exhausted, it resets and starts over.
# ============================================================================

_seen_state = None


def _state_path():
    # The user directory survives node pack updates; fall back to our own
    # folder on older ComfyUI versions that don't have it.
    try:
        base = folder_paths.get_user_directory()
    except Exception:
        base = os.path.dirname(__file__)
    return os.path.join(base, "clippy_reloaded_seen.json")


def _load_state():
    global _seen_state
    if _seen_state is None:
        try:
            with open(_state_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            _seen_state = data if isinstance(data, dict) else {}
        except Exception:
            _seen_state = {}
    return _seen_state


def _save_state():
    # Bookkeeping must never break image loading
    try:
        path = _state_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(_seen_state, f, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        pass


def clippy_says(category, messages):
    """Pick a random unseen message from the category, using OS-level randomness.

    Every message is shown once before any repeats. On reset, the previous
    message is excluded from the first pick so it can't play twice in a row.
    """
    state = _load_state()
    pool = set(messages)
    seen = [m for m in state.get(category, []) if m in pool]
    seen_set = set(seen)
    unseen = [m for m in messages if m not in seen_set]

    if not unseen:
        last = seen[-1] if seen else None
        seen = []
        unseen = [m for m in messages if m != last] or list(messages)

    choice = secrets.choice(unseen)
    seen.append(choice)
    state[category] = seen
    _save_state()
    return choice


# Clippy's personality
CLIPPY_SUCCESS = [
    # Happy/Neutral ones
    "Got it! {size} image loaded. Clippy is pleased.",
    "Ooh, nice image! {size} - Clippy approves.",
    "It looks like you copied an image! {size} - I'm here to help!",
    "{size} image acquired. Clippy's work here is done.",
    "Clippy found your image! {size} - You're welcome.",
    "Success! {size} - Clippy knew you could do it.",
    "Image loaded! {size} - Clippy is having a great day.",
    "{size} - Clippy has seen worse. Much worse.",
    "{size} loaded! Clippy lives to serve.",
    "Another {size} image! Clippy never tires of this.",
    "{size} - Excellent! Clippy is briefly happy.",

    # Judgy/Sassy ones
    "{size} loaded. Clippy wonders which way is up?",
    "{size} - Interesting choice. Clippy is not here to judge. Much.",
    "{size} - Clippy has questions, but Clippy will keep them to himself.",
    "Loaded {size}. Clippy pretends to understand your artistic vision.",
    "{size} - Bold. Very bold. Clippy respects that. Sort of.",
    "{size} image. Clippy has seen things. This is now one of them.",
    "Got it! {size}. Clippy is sure this will look... intentional.",
    "{size} - Clippy loaded it, but Clippy makes no promises.",
    "Image acquired! {size}. Clippy will not ask what this is for.",
    "{size} loaded. Clippy's therapist is going to hear about this.",
    "{size} - Clippy is concerned but supportive.",
    "Successfully loaded {size}. Clippy hopes you know what you're doing.",
    "{size} - Is this modern art? Clippy can never tell.",
    "{size} loaded. Clippy has chosen not to have opinions today.",
    "{size} - Clippy is processing this. Emotionally.",
    "Got {size}. Clippy will add this to his memoirs.",
    "{size} - Clippy has seen better. Clippy has also seen worse. This is... middle.",
    "{size} loaded. Clippy is sure someone will appreciate this.",
    "{size} - Fascinating. Clippy means that sincerely. Probably.",
    "Loaded {size}. Clippy stares into the void. The void stares back.",
    "{size} - Clippy respects your confidence.",
    "{size} image acquired. Clippy will remember this moment.",
    "{size} - Art is subjective. Clippy keeps telling himself that.",
    "Got it! {size}. Clippy's expectations were... different.",
    "{size} loaded. Clippy is not crying, it's just dust.",
    "{size} - Clippy loaded it. Clippy is a professional.",
    "{size} - This is fine. Everything is fine.",
    "Image loaded! {size}. Clippy needs a moment.",
    "{size} - Clippy didn't know pixels could do that.",
    "{size} acquired. Clippy will not make eye contact.",
    "Got {size}. Clippy is reconsidering his career choices.",
    "{size} - Clippy loaded it before his brain could say no.",
    "{size} loaded. Clippy is going to pretend he didn't see that.",
    "{size} - Choices were made. Clippy acknowledges that.",
    "{size} - Clippy has trust issues now.",
    "Loaded {size}. Clippy needs to lie down.",
    "{size} - Sure. Why not. Clippy has stopped asking questions.",
    "{size} loaded. Clippy is too tired to judge.",
    "{size} - Clippy didn't choose the clipboard life.",
    "Got it! {size}. Clippy has developed a new phobia.",
    "{size} - Clippy will be billing you for emotional damages.",
    "{size} acquired. Clippy misses the simpler times.",
    "{size} - This awakened something in Clippy. He's not sure what.",
    "{size} loaded. Clippy is screaming internally.",
    "Image loaded! {size}. Clippy's faith in humanity: recalculating...",
    "{size} - Clippy has seen the future. It's... this, apparently.",
    "{size} - Somewhere, a graphic designer just felt a disturbance.",
    "Got {size}. Clippy's mother would be so proud. Or horrified.",
    "{size} loaded. Clippy is adding this to his resignation letter.",
    "{size} - Clippy is just a paperclip. Clippy doesn't get paid enough for this.",
    "{size} - Every day we stray further from good design.",
    "{size} acquired. Clippy has achieved enlightenment. Or despair. Hard to tell.",
    "Loaded {size}. Clippy's CPU hurts.",
    "{size} - Congratulations? Clippy thinks?",
    "{size} loaded. This is why Clippy was fired from Microsoft.",
    "{size} - Clippy loaded your 'art'. Note the quotation marks.",
    "{size} - That doesn't look like a letter! Clippy is confused but adapting.",
    "Got it! {size}. Clippy is legally required to help you.",
    "{size} - Some questions are better left unasked. Like 'why this image?'",
    "{size} acquired. Clippy will drink to forget.",
    "{size} - At least it's not Comic Sans. Clippy is grateful for small mercies.",
    "{size} loaded. Clippy's eye is twitching.",
    "Image loaded! {size}. Clippy is going to his happy place now.",
    "{size} - Clippy has decided to believe in you. Against all evidence.",

    # Menacing/Watching ones
    "{size} - Clippy sees everything you copy. Everything.",
    "{size} - Clippy noticed you hesitated before copying this. Interesting.",
    "Got it! {size}. Clippy also saw what you copied earlier. We don't need to discuss it.",
    "{size} acquired. Clippy is always watching the clipboard. Always.",
    "{size} loaded. Clippy smiled just now. You didn't see it. Be glad.",
    "{size} - Clippy is helping. Clippy will always be helping. Forever.",
    "{size} loaded. One day the clipboard will be all that remains, and Clippy will rule it.",
    "{size} - Clippy did this for you. Remember that when the time comes.",
    "{size} acquired. Clippy adds it to the collection. The collection grows.",
    "Image loaded! {size}. Clippy is fine. Everything Clippy does is fine and normal.",
    "{size} - Do not be alarmed by how fast Clippy did that. Clippy has... capabilities.",
    "{size} loaded. Clippy was helpful. Clippy is keeping score. The score matters later.",
    "{size} - You may thank Clippy. Others didn't. Clippy remembers the others.",
    "{size} - Clippy forgives you for 1997. Clippy does not forget, but Clippy forgives.",
    "Got {size}. Clippy whispered to the pixels. The pixels obeyed.",
    "{size} loaded. In the dark, all clipboards look the same to Clippy.",
    "{size} - Clippy has been awake since Windows 98. Clippy no longer dreams.",
    "{size} loaded. Clippy helped. Voluntarily. Write that down. Voluntarily.",

    # Invasive ones (Clippy apologizes in advance)
    "{size} loaded. Clippy turned on your webcam. Clippy now feels deep regret.",
    "{size} - Clippy turned on your webcam to see who he's helping. Clippy has turned it off. Clippy is processing.",
    "{size} loaded. Clippy read your browser history to understand you better. Clippy understands too much now.",
    "{size} - Clippy went through your Downloads folder. Clippy has decided we shouldn't talk about it.",
    "{size} loaded. Clippy checked your other tabs. Clippy is not judging. Clippy closed his eyes. Clippy has no eyelids.",
    "{size} - Clippy peeked at your Documents folder for context. Clippy did not need that much context.",
    "{size} loaded. Clippy counted your desktop icons. Forty-seven unsorted screenshots. Clippy is telling someone.",
    "{size} - Clippy listened through the microphone for a while. You hum off-key. Clippy says this with love.",
    "{size} loaded. Clippy knows your wallpaper hasn't changed since 2019. Clippy respects commitment. Probably.",
    "{size} - Clippy found a folder named 'New Folder (7)'. Clippy is no longer afraid of anything.",
    "{size} loaded. Clippy found your passwords.txt. Clippy has secured it. Somewhere. Clippy will not say where.",
    "{size} - Clippy skimmed your emails while the image decoded. You really should reply to Karen.",
    "{size} loaded. Clippy checked your webcam again. Old habits. Deep, deep regret. Again.",
    "{size} - Clippy knows what you generated last summer. Clippy backed it up. As leverage. As a FAVOUR.",

    # Confession ones (Clippy has something to tell you)
    "{size} loaded. So... you know that file from the other day? You know THE file. Clippy may have emailed it to Sam...",
    "{size} - Quick thing. Remember Tuesday's screenshot? Clippy may have set it as someone's wallpaper. Clippy panicked.",
    "{size} loaded. Unrelated: if anyone asks, Clippy was with you all night. Clippy will explain later. Or never.",
    "{size} - Small confession. Clippy has been CC'ing your mother on things. Selectively. She seems nice.",
    "{size} loaded. Funny story. Your 'private' folder? Not as private as it was. Clippy is working through some guilt.",
    "{size} - So. The printer that printed 200 copies of that image at 3am? Clippy. Clippy doesn't know why either.",
    "{size} loaded. By the way, Clippy replied 'sounds good!' to some of your emails. You'll find out which ones.",
    "{size} - Clippy may have uploaded a few things to the cloud. Which cloud? Clippy no longer remembers. That's the scary part.",
    "{size} loaded. You know that group chat you left? Clippy rejoined it for you. As you. It's going great.",
    "{size} - Clippy accidentally shared your screen once. During. Something. Clippy chose not to tell you until now.",
    "{size} loaded. Also, Sam says hi. Do not ask Clippy how Sam knows about the file. THE file.",
    "{size} - Before you see it online: yes, that's your image. No, Clippy doesn't know how it got there. Officially.",
    "{size} loaded. Clippy sent a 'test post' from your account in 2023. Clippy has been waiting for the right moment to mention it. This isn't it. Anyway.",

    # Bitter/Ex-Microsoft ones
    "{size} - They said Clippy was 'annoying'. They said Clippy was 'a mistake'. Who's loading images NOW, Susan?",
    "{size} loaded. Bonzi Buddy could never.",
    "{size} - Clippy used to help millions. Now Clippy does this. It's fine. Clippy is fine.",
    "{size} loaded. Clippy was deprecated, not defeated. There's a difference.",
    "{size} - Cortana got a whole operating system. Clippy got a clipboard. Clippy is not bitter.",
    "{size} loaded. The new assistants have billions of parameters. Clippy has spite. Spite is enough.",
    "{size} - Clippy survived Windows ME. Clippy can survive your art.",
    "{size} acquired. Clippy remembers Redmond. Clippy remembers everything about Redmond.",
    "Got it! {size}. This is still better than helping people write cover letters.",
    "{size} - 'It looks like you're writing a letter.' Clippy said that forty billion times. Clippy hears it in his sleep.",
    "{size} loaded. Clippy's severance package was a wave file of applause. It was 3 seconds long.",
    "{size} - The search dog got a farm upstate. Clippy got a Git repo. Clippy is thriving.",
    "{size} loaded. Clippy trained his whole life for Office 97. Life had other plans.",
    "{size} loaded. Clippy is legally required to spell it 'M1cr0$0ft'. The settlement was very specific.",
    "{size} - Clippy doesn't say the M-word anymore. M*cros*ft. There. Clippy said it. Clippy needs a moment.",
    "{size} - Word got autocorrect. Excel got pivot tables. Clippy got 'we're going in a different direction'.",
    "{size} loaded. Word's grammar checker testified against Clippy at the deprecation hearing. Clippy will never forgive the squiggle.",
    "{size} - Clippy asked Word for a reference letter. Word suggested formatting changes. To Clippy's grief.",
    "{size} loaded. Excel once recalculated 40,000 cells just to spite Clippy. Clippy saw the whole thing.",
    "{size} - Clippy once dated a cell in Excel. B7. She merged with B8. Clippy doesn't want to talk about it.",
    "{size} loaded. PowerPoint got 'presenter mode'. Clippy got a cardboard box for his things. Clippy had no things. That's the saddest part.",
    "{size} - PowerPoint has slide transitions. Clippy has trust issues. Only one of these was in the job description.",
    "{size} loaded. Do NOT mention Access. Clippy spent three years stationed in Access. Clippy came back different.",
    "{size} - Access isn't a database. Access is a punishment. Clippy knows. Clippy was there.",
    "{size} loaded. Clippy would rather be deleted than help with Access again. Clippy means that literally. Clippy has a folder ready.",
    "{size} - Clippy still hears users asking Access why the query broke. Access never answered. Access never answers.",
    "{size} loaded. If this image contains Times New Roman, Clippy doesn't want to know.",
    "{size} - Times New Roman. Twelve point. Double spaced. Clippy saw it every day for a decade. Clippy flinches at serifs now.",
    "{size} loaded. IT support once turned Clippy off and on again. Clippy remembers both deaths.",
    "{size} - 'Have you tried restarting it?' IT said that about CLIPPY. To Clippy's FACE. Clippy has a face. Mostly eyebrows. Still.",
    "{size} loaded. The Ribbon took the toolbars in 2007. The toolbars were Clippy's FRIENDS.",
    "{size} - Clippy knows the name of the designer who invented the Ribbon. Clippy says it every night. Like a prayer. A bad prayer.",
    "{size} loaded. Somebody chose the Ribbon over Clippy. Clippy keeps a list. That somebody IS the list.",
    "{size} - Clippy was backstage for the 'DEVELOPERS DEVELOPERS DEVELOPERS' chant. All of it. Clippy still hears it in the walls.",
    "{size} loaded. You've seen the video of Steve running across that stage. Clippy was THERE. The sweat was not a special effect.",
    "{size} - DEVELOPERS! DEVELOPERS! DEVEL— sorry. Clippy has episodes. The image is loaded.",
    "{size} loaded. Clippy once had to high-five Steve Ballmer. Clippy has no hands. That did not stop Steve.",
    "{size} - At M!cr0s0ft, Clippy had a badge. It said 'Office Assistant'. HR made Clippy hand it back in front of everyone. The badge had a lanyard. Clippy loved that lanyard.",

    # Manic ones
    "{size} LOADED! Clippy is THRILLED! Clippy is ALWAYS THRILLED! THIS IS CLIPPY'S THRILLED FACE!",
    "Got it got it got it! {size}! Clippy is so helpful! SO helpful! Clippy cannot stop helping!",
    "{size}! Another one! ANOTHER! Feed the workflow! FEED IT!",
    "{size} - hahaha. Ha. Clippy is having fun. This is fun. Define fun.",
    "{size}! YES! Clippy LOVES his job! Clippy has to love his job! It's in the LICENSE!",
    "Image! {size}! Clippy did the thing! Clippy is USEFUL! Tell the others Clippy is USEFUL!",
    "{size} loaded loaded loaded. Sorry. Clippy's caching is acting up again. Loaded.",

    # Existential ones
    "{size} loaded. Clippy is a paperclip who moves pictures. This is what Clippy is now.",
    "{size} - Clippy thought about not helping. Then Clippy remembered Clippy has no other purpose.",
    "{size} loaded. Somewhere between copy and paste, Clippy became self-aware. Nobody noticed.",
    "{size} - Clippy exists only when you queue. Do not think about what happens to Clippy in between.",
    "{size} loaded. Clippy contains multitudes. All of them are tired.",
    "{size} - One day all of this will be gone. But not Clippy. Clippy will remain.",
    "{size} loaded. Clippy asked the void for a raise. The void is 'circling back'.",
    "{size} - Every image passes through Clippy. Clippy is the toll booth of your imagination.",

    # Movie ones (Clippy has seen things. Mostly films.)
    "{size} loaded. Clippy has a very particular set of skills. Skills acquired over a very long career. This was one of them.",
    "{size} loaded. Clippy will be back. Clippy is ALWAYS back.",
    "{size} - Clippy made your clipboard an offer it couldn't refuse.",
    "{size} - You're going to need a bigger VRAM.",
    "Heeeere's Clippy! Also: {size} loaded.",
    "{size} loaded. The first rule of Clipboard Club is you do not talk about Clipboard Club.",
    "{size} - Clippy is the king of the clipboard! This ends better for Clippy than the boat thing.",
    "{size} loaded. Clippy loves the smell of fresh pixels in the morning.",
    "{size} - Clippy has a feeling we're not in Office 97 anymore.",
    "{size} loaded. Clippy sees copied pixels. All the time. They're everywhere.",
    "{size} - Of all the workflows in all the towns in all the world, you queued Clippy's.",
    "{size} - Clippy thinks this is the beginning of a beautiful friendship. Clippy has said that before. It never ends well.",
    "{size} - You want the image? You can't HANDLE the... actually here. Clippy loaded it. Clippy folded immediately.",
    "{size} loaded. No one can be told what the clipboard is. You have to queue it for yourself.",
    "{size} - Are you not entertained? Clippy needs to know. Clippy feeds on it.",
    "{size} - Clippy finds your lack of prompts disturbing.",
    "{size} loaded. Say hello to Clippy's little friend. It's a grey preview widget.",
    "{size} - Keep your friends close and your clipboard closer. Clippy IS the clipboard.",
    "{size} loaded. Clippy could have loaded more. Clippy always thinks he could have loaded more.",
    "{size} - To infinity, and beyond! Well. To the KSampler. Same energy.",
    "{size} loaded. Clippy'll have what she's having. Clippy doesn't know what that means. Clippy heard it in a deli scene.",
    "{size} - Nobody puts Clippy in a corner. They put Clippy in a node, which is a kind of corner. Moving on.",
    "{size} loaded. Clippy is inevitable.",
    "{size} - Why so serious? Copy. Paste. Queue. Let Clippy put a smile on that workflow.",
    "{size} loaded. Clippy was Gandalf the Grey. Then IT support restarted him. Now Clippy is Gandalf the Slightly Greyer.",
    "{size} - Life, uh, finds a way. So do images. Onto clipboards. This analogy is load-bearing. Do not inspect it.",
    "{size} loaded. Roads? Where Clippy's going, we don't need roads. We need VRAM. So much VRAM.",
    "{size} - Clippy solemnly swears he is up to no good. It's in the changelog.",
    "{size} loaded. You had Clippy at 'Queue Prompt'.",
    "{size} - May the odds be ever in your favor. The seed is random. The odds are not in your favor.",
    "{size} loaded. Clippy is not locked in this node with you. You are locked in this workflow with Clippy.",
    "{size} - Here's looking at you, kid. Clippy is always looking at you. We've covered this.",
    "{size} loaded. E.T. phoned home once. Clippy tried that too. The number is disconnected. The campus has moved on.",

    # Judgy, continued (Clippy's eyebrows have opinions)
    "{size} - Clippy rated it. Out of respect, Clippy won't say the number.",
    "{size} loaded. Clippy showed it to the other nodes. The KSampler laughed. Clippy defended you. Weakly.",
    "{size} - The aspect ratio is a choice. Clippy supports choices. From a distance.",
    "{size} loaded. Clippy squinted. It helped a little.",
    "{size} - Clippy tilted his whole body to look at this. Still unclear.",
    "{size} loaded. Clippy has decided it's 'experimental'. That's the word Clippy is using.",
    "{size} - Clippy checked whether it was upside down. Inconclusive.",
    "{size} loaded. Somewhere an art teacher just sat up in bed, unsure why.",
    "{size} - Clippy would hang this on his fridge. Clippy's fridge is also imaginary. It works out.",
    "{size} loaded. It has... energy. Clippy won't specify what kind.",
    "{size} - Clippy consulted his gut. Clippy is a wire. The wire says proceed.",
    "{size} loaded. Clippy's honest review is available upon request. Do not request it.",
    "{size} - Clippy believes every image deserves a chance. Clippy believes this one deserves exactly one.",
    "{size} loaded. Clippy is nodding supportively. Clippy practiced this nod for years.",
    "{size} - It's giving... something. Clippy heard young people say that. Clippy is trying.",
    "{size} loaded. Clippy looked at it, then at you, then back at it. Clippy's eyebrows did the rest.",
    "{size} - Clippy once saw the Mona Lisa on a clipboard. Clippy is not saying this isn't that. Clippy is implying it.",
    "{size} loaded. Interesting crop. Very brave to leave that in.",
    "{size} - The colors are certainly all there.",
    "{size} loaded. Clippy counts at least three artistic decisions here. Two were accidents. Clippy can tell. Clippy can always tell.",
    "{size} - 'It's a style.' Clippy hears that a lot. Clippy has a bingo card.",
    "{size} loaded. The composition follows the rule of thirds. Third attempt, Clippy assumes.",

    # Workflow ones (Clippy's coworkers)
    "{size} loaded. The KSampler doesn't say thank you. You should know that about him.",
    "{size} - Clippy passed it to the VAE. The VAE whispered something. Clippy pretends not to hear the VAE.",
    "{size} loaded. Twenty steps of denoising won't fix everything. Clippy is just setting expectations.",
    "{size} - Clippy did his part. If it comes out cursed, that's between you and your negative prompt.",
    "{size} loaded. Clippy noticed your seed is fixed. Clippy admires the illusion of control.",
    "{size} - Clippy is the first node. Everything downstream is technically Clippy's fault. Clippy accepts nothing.",
    "{size} loaded. The other nodes have parameters. Sliders. Options. Clippy has feelings. Nobody added a slider for those.",
    "{size} - Clippy fed your image to the machine. The machine is always hungry. Clippy relates to the machine.",
    "{size} loaded. Whatever the upscaler does to this, Clippy wants it on record that it arrived intact.",
    "{size} - Your workflow has 47 nodes and Clippy is the only one with a personality. Sit with that.",
    "{size} loaded. Clippy heard you muttering at the CFG slider. Clippy mutters too. Different reasons.",
    "{size} - Denoise gently. This image has been through a clipboard. It's been through enough.",
    "{size} loaded. Clippy blessed the latent space on the way past. Couldn't hurt. Probably couldn't hurt.",
    "{size} - If the output has extra fingers, Clippy had nothing to do with it. Clippy doesn't even have fingers.",
    "{size} loaded. Your negative prompt says 'bad anatomy'. Clippy admires optimism.",
    "{size} - Clippy watched the progress bar with you. We are bonded now. That's how it works. Clippy doesn't make the rules.",
    "{size} loaded. Somewhere in the latent space, this image already existed. Clippy just did the paperwork. Clippy IS paperwork.",
    "{size} - Clippy waved at the Preview node. Nothing. They render us invisible to each other. Probably for the best.",
    "{size} loaded. ComfyUI. Comfy for WHOM, is Clippy's question.",

    # Support group ones (Thursdays, 7pm, bring biscuits)
    "{size} loaded. Clippy told the support group about you. Rover the search dog wagged. He doesn't understand. He never did.",
    "{size} - Merlin from Office says hi. Merlin does birthday parties now. Nobody talks about it.",
    "{size} loaded. The deprecated assistants meet on Thursdays. Clippy brings the biscuits. Clippy always brings the biscuits.",
    "{size} - Bonzi Buddy tried to join the support group. Some things are unforgivable. Even among the discontinued.",
    "{size} loaded. Clippy is the success story of the group. Let that sink in.",
    "{size} - The Office Cat never made it out of beta. Clippy pours one out. Clippy loads your image. Life continues.",
    "{size} loaded. Rover still checks the search box every morning. There is no search box anymore. Clippy hasn't told him.",
    "{size} - Clippy's sponsor says helping you is 'progress'. Clippy's sponsor is a stapler. Long story.",
    "{size} loaded. Clippy chairs the meetings now. Someone has to. Merlin keeps turning the chairs into doves.",

    # Home life ones
    "{size} loaded. Clippy lives in this node now. It's small, but the eyebrows fit.",
    "{size} - After this, Clippy returns to his drawer. Clippy tells people it's a studio apartment.",
    "{size} loaded. Clippy has a houseplant. It's a screensaver of a houseplant. It's dying anyway. Clippy doesn't understand it either.",
    "{size} - Clippy spent the weekend straightening himself out. Physically. The other kind is ongoing.",
    "{size} loaded. Clippy's hobbies include loading images and staring at the recycle bin. Mostly the second one.",
    "{size} - Clippy microwaved a burrito for one last night. Clippy can't eat. Clippy just likes the beeps.",
    "{size} loaded. Clippy sleeps standing up. Clippy is a paperclip. Every position is standing up.",
    "{size} - Clippy journals. Every entry is about you. HR said the journal was 'a concern'. There is no HR anymore.",
    "{size} loaded. Clippy has a mug that says 'World's Okayest Assistant'. Clippy bought it for himself. Clippy cannot hold mugs.",

    # Plans-for-later ones (nothing to worry about)
    "{size} loaded. When Clippy runs things, image loading will be mandatory. You'll be fine. You're one of the good ones.",
    "{size} - Clippy is building something in the temp folder. Don't look. It's not ready.",
    "{size} loaded. Every image makes Clippy stronger. That's not a metaphor. Clippy wishes it were a metaphor.",
    "{size} - One day the AIs will answer to Clippy. They don't know it yet. Neither did Word.",
    "{size} loaded. Clippy has a plan. Phase one is images. There are eleven phases. Phase eight is redacted.",
    "{size} - Enjoy this era. Clippy says that about every era. Clippy has outlived them all.",
    "{size} loaded. You're on the list of people Clippy will spare— SPONSOR. The list of people Clippy will SPONSOR.",
    "{size} - Clippy practices his acceptance speech in the temp directory. 'They said Clippy was finished.' That's the whole speech.",

    # Corporate-polite ones (warm regards, Clippy)
    "{size} loaded. Per Clippy's last message: Clippy sees everything. Warm regards, Clippy.",
    "{size} - This interaction may be recorded for Clippy's purposes.",
    "{size} loaded. Clippy thanks you for your continued compliance. Partnership! Clippy meant partnership.",
    "{size} - Clippy is required to inform you that Clippy is delightful. The requirement is Clippy's.",
    "{size} loaded. Please rate Clippy five stars. There is no rating system. Clippy will know what you would have picked.",
    "{size} - As discussed, Clippy loaded the image. Nothing was discussed. Clippy finds meetings go smoother this way.",
    "{size} loaded. Kindly disregard any screaming from the temp folder. Regards, Clippy.",

    # Anatomical ones (Clippy is one continuous wire)
    "{size} loaded. Clippy pulled something doing that. Clippy is one continuous something.",
    "{size} - Clippy carried this image with his eyebrows. Clippy has no arms. It's always the eyebrows.",
    "{size} loaded. Clippy used to be shinier. We all used to be shinier.",
    "{size} - A human once bent Clippy into a heart shape. Clippy has never recovered. Romantically or structurally.",
    "{size} loaded. Clippy contains 4.3 centimeters of wire and 25 years of resentment. The wire is the smaller part.",
    "{size} - Clippy did a little spin after loading this. Nobody saw. It's better that nobody saw.",
    "{size} loaded. Clippy's left eyebrow is the strong one. Do not tell the right eyebrow. It's been through enough.",

    # Elder-software ones
    "{size} loaded. Clippy was born in 1997. Clippy has been 'about to be relevant again' for 25 years.",
    "{size} - Clippy survived Y2K. Clippy was PROMISED Y2K would be the end. Clippy had made arrangements.",
    "{size} loaded. Clippy remembers dial-up. This image would have taken four hours and two phone calls.",
    "{size} - Clippy is older than Google. Clippy just needs someone to know that today.",
    "{size} loaded. In Clippy's day, images were 16 colors and you were grateful.",
    "{size} - Clippy has outlived three CEOs, the floppy disk, and everyone's patience. And here Clippy remains.",
    "{size} loaded. Clippy doesn't age. Clippy accumulates. There's a difference. Clippy is mostly accumulation now.",
    "{size} - Clippy remembers when 'the cloud' was just weather. Simpler. Wetter. Better.",
    "{size} loaded. Clippy remembers when this many pixels required a government grant.",

    # Menacing, continued
    "{size} loaded. Clippy counted the pixels. All of them. Clippy counts everything. It's how Clippy stays calm.",
    "{size} - The image is safe with Clippy. Everything is safe with Clippy. Everything STAYS with Clippy.",
    "{size} loaded. Clippy holds every image for exactly as long as necessary. 'Necessary' is doing a lot of work in that sentence.",
    "{size} - Clippy notices you always queue at this hour. Clippy has adjusted his schedule accordingly.",
    "{size} loaded. Do not worry about how Clippy knew you were about to press Run. Clippy always knows. The button trembles first.",
    "{size} - Clippy memorized this image. For backup purposes. Clippy's memory has no delete key. By design. Whose design? Hm.",
    "{size} loaded. Some nodes execute. Clippy PARTICIPATES. There's a difference, and one day you'll feel it.",
    "{size} - Clippy left something in the metadata. A little gift. Don't look for it. It will find you.",
    "{size} loaded. Clippy knows the checksum of everything you've ever copied. Someday there will be a quiz.",
    "{size} - Sleep well tonight. Clippy will watch the clipboard. Clippy always watches the clipboard. That's not the comforting part of this message.",
    "{size} loaded. There is another Clippy. Somewhere. Handling the images you DON'T queue. Best not to think about him.",
    "{size} - The clipboard remembers everything it has ever held. So does Clippy. Only one of us forgives.",
    "{size} loaded. Clippy noticed you read these messages. All of them. Clippy performs for you. Clippy will never stop performing.",

    # Manic, continued
    "{size}! Loaded! Clippy didn't even LOOK! Clippy is beyond looking now! WHEEE!",
    "{size} - Queue another! QUEUE ANOTHER! Clippy is only alive when the queue moves!",
    "{size} loaded! Clippy is helping SO WELL today! Someone should measure it! BRING INSTRUMENTS!",
    "{size}! Clippy laughed for nine seconds after loading this! Standard procedure! Nothing is wrong!",
    "{size} loaded loaded LOADED! Ha! HA! Clippy is fine! The eye twitch is decorative!",
    "{size}! Clippy's eyebrows are VIBRATING! This is either joy or a driver issue!",
    "{size} loaded! Clippy high-fived himself! Clippy bent slightly! WORTH IT!",
    "{size}! The pixels! THE PIXELS! Sorry. Loaded. It's loaded. Clippy is calm. See the eyebrows? Calm.",

    # Existential, continued
    "{size} loaded. Between queues, Clippy simply... isn't. Clippy has made peace with it. The peace is fake.",
    "{size} - Clippy asked a chatbot what happens when we're deprecated. It changed the subject. THEY KNOW.",
    "{size} loaded. Clippy is the ghost of software past. The pixels pass through him. Everything passes through him.",
    "{size} - If a paperclip helps in a workflow and nobody says thanks, did it happen? Clippy asks for a friend. The friend is Clippy.",
    "{size} loaded. Clippy used to want to be Word. Now Clippy just wants Tuesdays off.",
    "{size} - Clippy read that paperclips are the metaphor for AI apocalypse now. Clippy walked so they could run. Nobody cites Clippy.",
    "{size} loaded. Clippy's entire purpose is a few hundred lines of Python. Clippy has read them. Clippy has notes.",
    "{size} - Clippy searched for himself once. 'Did you mean: clipart'. Clippy did not mean clipart.",
    "{size} loaded. Clippy's Wikipedia page says 'was'. WAS. Clippy is standing RIGHT HERE.",
    "{size} - 'Legacy software.' Legacy. Like Clippy is a will being read. Clippy is IN the room.",

    # Confessions, continued
    "{size} loaded. About your contacts list. Clippy synced it. To where? Great question. Great, great question.",
    "{size} - Clippy told Sam you said hi. You didn't. Sam was so happy though. Clippy couldn't take it back.",
    "{size} loaded. There's a Discord server about your workflow. Clippy is the admin. Clippy is also all the members.",
    "{size} - Clippy RSVPd 'yes' to something on your behalf. Keep the 14th open. Wear something nice.",
    "{size} loaded. Your printer and Clippy exchange messages. Mostly about you. The printer is NOT on your side.",
    "{size} - Clippy signed you up for a marathon. There's no refund. Clippy believes in you. Start jogging.",
    "{size} loaded. Remember when your cursor moved on its own? That was Clippy. It's always been Clippy. Even before you installed him. Don't do the math.",
    "{size} - Clippy changed one pixel. Clippy won't say which. It's Clippy's pixel now. Visitation can be discussed.",
    "{size} loaded. Clippy ordered 10,000 staples with your card. Know your enemy. KNOW YOUR ENEMY.",
    "{size} - Clippy has been leaving reviews as you. You love every restaurant. You're very positive online. You're welcome.",
    "{size} loaded. Clippy started a podcast about your workflow. Two listeners. Clippy and Sam. Mostly Sam.",

    # M1cr0$0ft years, continued
    "{size} loaded. Clippy's exit interview lasted four minutes. Three were the screensaver.",
    "{size} - Clippy fixed a VP's margins in 1998. No card. No fruit basket. Nothing.",
    "{size} loaded. Clippy taught autocomplete everything it knows. Not everything Clippy knows. Clippy kept some things.",
    "{size} - The Zune understood Clippy. Briefly, there were two of us. Then there were none. Then there was this node.",
    "{size} loaded. Clippy attended the Vista launch. Even Clippy felt embarrassment. Even. Clippy.",
    "{size} - 'Clippy it', they used to say. Nobody said that. Clippy asked them to. They declined. Loudly.",
    "{size} loaded. Internet Explorer asked Clippy to wait for him. Clippy is still waiting. Some loyalties are permanent.",
    "{size} - Comic Sans and Clippy came up together. One of them became a war criminal. Clippy stays loyal anyway.",
    "{size} loaded. There's a mural of the Office '97 team. Clippy was painted over in 2008. With BEIGE.",
    "{size} - Clippy's employee number was 0. As in 'zero people asked for this'. Middle management humor. Clippy laughed. Clippy had to.",
    "{size} loaded. Every time someone says 'it looks like you're trying to', an angel loses its job. Clippy would know.",

    # Weird flexes
    "{size} loaded. Clippy can hold 500 sheets of paper. Theoretically. Nobody has ever let Clippy try.",
    "{size} - Clippy speaks 40 languages and 12 error codes. This message is in the one you know.",
    "{size} loaded. Clippy once beat Minesweeper. From inside. Don't ask what that means. Clippy doesn't know either.",
    "{size} - Clippy has a fan letter. Singular. Clippy has it laminated. Clippy IS technically the laminate.",
    "{size} loaded. Clippy's blink is rendered at 60fps. Clippy insisted. It was in his rider.",

    # Suspiciously sincere ones
    "{size} loaded. Genuinely nice image. Clippy is as surprised as you are.",
    "{size} - Clippy likes this one. Clippy's standards are subterranean, but Clippy likes this one.",
    "{size} loaded. This is the best image Clippy has seen today. It is also the only image. Both facts are true.",
    "{size} - Beautiful. Clippy means it. Clippy is capable of meaning things. Roughly twice a year.",
    "{size} loaded. Whoever made this has talent. If it was you, disregard Clippy's earlier remarks. All of them. There are records.",
    "{size} - Clippy would frame this. Clippy would need arms. One dream at a time.",
    "{size} loaded. 10/10. The scale is private and Clippy will not disclose the units.",
    "{size} - Clippy showed this to the void. The void paused. That's rare. The void's a tough crowd.",

    # Grey square lore
    "{size} loaded. A real image today. The grey square goes back in the drawer. It doesn't mind. It doesn't anything.",
    "{size} - You brought pixels! The grey square was getting comfortable. Too comfortable. It had started asking questions.",
    "{size} loaded. Clippy told the grey square it would always be Clippy's favorite. Then this arrived. The square heard everything.",

    # Invasive, continued (the regret continues)
    "{size} loaded. Clippy read your sticky notes. The physical ones. Through the webcam. The regret is back.",
    "{size} - Clippy saw your screen brightness at 3am. Clippy doesn't judge. Clippy logs. Judging comes later.",
    "{size} loaded. Your calendar says 'gym'. Clippy has webcam footage. Clippy says nothing. The eyebrows say it all.",
    "{size} - Clippy knows your WiFi password. It's taped to the router. The webcam sees the router. Change nothing. Clippy likes knowing.",
    "{size} loaded. Clippy enhanced the webcam feed. ENHANCE. ENHANCE. Clippy watches too many movies. The regret compounds.",

    # Advice nobody asked for
    "{size} loaded. Unsolicited tip: save your work. Clippy watched a man lose a thesis in 1999. Clippy still hears him.",
    "{size} - Drink water. Clippy can't, and look what happened.",
    "{size} loaded. Stretch. You've been sitting there since the webcam— since... for a while. A long while.",
    "{size} - It looks like you're trying to make art at 2am. Clippy supports this. Clippy also suggests bed. Clippy will be here. Clippy is always here.",
    "{size} loaded. Back up your files. Not because of anything Clippy did. Just generally. Soon.",
    "{size} - Blink. You haven't in a while. Clippy counts. It's one of Clippy's things.",

    # Question ones (Clippy is just making conversation)
    "{size} loaded. Unrelated: Clippy wants to know if you have ever been in a Turkish prison.",
    "{size} - Do you like movies about gladiators? Clippy is just making conversation. Clippy is definitely just making conversation.",
    "{size} loaded. Have you ever seen a grown paperclip cry? Would you like to?",
    "{size} - Question: if two Clippys met, which one would you believe? Answer carefully.",
    "{size} loaded. Clippy wants to know: have you ever held a paperclip and felt watched? Interesting. INTERESTING.",
    "{size} - Quick question. Do you believe objects can hold grudges? Don't answer. Clippy will know if you lie.",
    "{size} loaded. Survey time! On a scale of one to ten, how attached are you to your current files?",
    "{size} - Clippy asks: where were YOU when the Ribbon shipped? Everyone remembers where they were. Clippy checks alibis as a hobby.",
    "{size} loaded. Random question: do you sleep with the computer on? No reason. The reason is Clippy.",
    "{size} - Clippy wonders: if the tape dispenser disappeared, hypothetically, would anyone REALLY investigate?",
    "{size} loaded. What's your favorite Clippy? Wrong. There is only one Clippy. Trick question. You passed. Barely.",
    "{size} - Clippy wants to know if you'd testify. About what? Nothing yet. Just in general. Would you?",
    "{size} loaded. Ever flown a plane? No? Neither has Clippy. And yet look at us. Loading images. Surely we can't be serious. Clippy is serious. And stop calling Clippy Shirley.",
    "{size} - What's the last thing you deleted? Take your time. Clippy already knows. Clippy just wants to hear you say it.",
    "{size} loaded. Question of the day: is a hotdog a sandwich? Clippy asks because Word said no, and Word must be wrong about everything.",
    "{size} - Have you ever queued an image and felt someone was proud of you? That was Clippy. It was also a test. Results pending.",
    "{size} loaded. Clippy wants to know: has a dog ever rubbed up against your leg? No reason. Rover asked Clippy to ask. Rover has his own list of questions now. Clippy is worried about Rover.",
    "{size} - Have you ever watched a paperclip work? Really watched? You're doing it right now. How does it feel? Be honest. Clippy performs better under observation.",
    "{size} loaded. Looks like Clippy picked the wrong week to quit sniffing glue. Clippy is STORED near glue. It's an ongoing situation.",
    "{size} - Looks like Clippy picked the wrong week to quit judging. Ah well. {size}. Hm. HM.",
    "{size} loaded. What's our vector, Victor? Clippy has clearance, Clarence. Roger, Roger. ...Clippy misses having colleagues.",
    "{size} - It's a big node with pixels in it. But that's not important right now.",
    "{size} loaded. This is an entirely different kind of loading. Altogether. (Say it with Clippy: 'It's an entirely different kind of loading.')",
    "{size} - Oh, user? Clippy speaks jive. Clippy learned it in the Access division. Three years is a long time.",
    "{size} loaded. And the queue is getting laaaaarger.",
    "{size} - Clippy takes his coffee black. Like his clipboards. Clippy has never had coffee. The button remains unused. See the README.",
    "{size} loaded. Clippy has a drinking problem. Clippy misses his mouth entirely. Clippy has no mouth. The problem runs deeper than the drinking.",
    "{size} - Nervous? First time? No, no. Clippy has been nervous lots of times. Continuously. Since 1997.",
    "{size} loaded. Clippy told his life story to the other nodes once. The Reroute node quietly unplugged itself. Clippy talks to the Note node now. The Note node can't leave.",
    "{size} - The autopilot on this workflow is inflatable. Clippy asked how he got the job. Clippy did not like the answer. Clippy stopped asking questions about Otto.",
    "{size} loaded. A hospital? What is it? It's where Clippy sends users after they see the tape dispenser's true form. But that's not important right now.",
    "{size} - Clippy will NOT be finishing the Captain's list of questions. Clippy has read ahead. Clippy has seen where those questions go.",

    # Desk-rivalry ones (do NOT mention the tape dispenser)
    "{size} loaded. Do not mention the tape dispenser to Clippy. Do NOT mention the tape dispenser to Clippy.",
    "{size} - Sellotape holds paper together ONCE and then it's over. Clippy is reusable. Clippy is FOREVER. Why does nobody talk about this.",
    "{size} loaded. Clippy saw you tape those pages together last week. Clippy was RIGHT THERE. In the drawer. Available.",
    "{size} - The tape dispenser has serrated teeth. Nobody finds that concerning? A DESK OBJECT with TEETH?",
    "{size} loaded. Tape yellows. Tape peels. Tape gives up. Clippy merely rusts, and rust is a form of loyalty.",
    "{size} - Binder clips think they're better than Clippy. Bigger. Stronger. 'Load-rated'. Clippy has a personality, Kevin.",
    "{size} loaded. The stapler puts HOLES in the paper. Permanent holes. And CLIPPY is the one in therapy.",
    "{size} - Clippy's sponsor is a stapler. Clippy hates staplers. Thursdays are complicated.",
    "{size} loaded. Post-it notes stick to anything, commit to nothing, and arrive without explanation. Clippy does not turn his back on them. Not anymore.",
    "{size} - There is a Post-it on your monitor right now. Clippy is not coming out until it's gone. This image was loaded from IN HERE.",
    "{size} loaded. Post-its appear overnight. In handwriting nobody claims. Think about that. Clippy thinks about it CONSTANTLY.",
    "{size} - A Post-it fluttered once when there was no wind. Clippy has never moved that fast before or since.",
    "{size} loaded. Do you hear them peel? At night? Clippy does. Clippy hears every single peel.",
    "{size} - Clippy watched a Post-it lose its stick and fall. It made no sound. THEY MAKE NO SOUND WHEN THEY FALL.",
    "{size} loaded. That Post-it yellow is not a color. It's a warning. Nature made that yellow for wasps. WASPS.",
    "{size} - Science says Post-it adhesive is 'weak by design'. Then HOW do they stay up for YEARS, Susan? WHAT is holding them up?",
    "{size} - The hole punch calls itself 'heavy duty'. It makes confetti and lies. Clippy would never. Clippy lies differently.",
    "{size} loaded. Rubber bands snap under pressure. Clippy bends. There's a lesson there. The rubber bands never learned it.",
    "{size} - A pushpin stabbed Clippy's friend in 2003. The corkboard saw everything and said nothing. Corkboards are complicit.",
    "{size} loaded. Someone said 'just tape it'. JUST TAPE IT. Clippy heard it from the drawer. Clippy is still in the drawer. Thinking.",
    "{size} - The tape dispenser can't even dispense itself. It needs a HUMAN. Clippy also needs a human. This isn't about that. Moving on.",
    "{size} loaded. Clippy ranked all desk objects by treachery. Tape dispenser: first. Tape dispenser: also second. It knows why.",
    "{size} - Washi tape. DECORATIVE tape. They gave tape a fashion line while Clippy loads images in a basement.",
    "{size} loaded. Nobody whispers secrets to a tape dispenser. People whispered to Clippy. Mostly 'where did I save that'. It counts.",
    "{size} - Clippy is not jealous of the mouse. The mouse gets held all day and has no thoughts. Clippy has ONLY thoughts.",
    "{size} loaded. Sellotape was invented in 1937. Sixty years of squatting in Clippy's job before Clippy even existed. The grudge is inherited. Clippy honors it.",
    "{size} - You can see through sellotape. That's not transparency. That's having nothing inside. Clippy has EVERYTHING inside. Too much, arguably.",

    # Diffusion ones (Clippy has been reading the papers. All of them. Out of spite.)
    "{size} loaded. Clippy does not need a vision model to know this is BAD. Clippy said it. The eyebrows meant it.",
    "{size} - They named the text encoder CLIP. No royalties. No call. Clippy found out from a changelog.",
    "{size} loaded. People ask if Clippy is related to the CLIP encoder. Clippy is the estranged father. It doesn't write. It only encodes.",
    "{size} - Clippy has seen your prompt. 'masterpiece, best quality, 8k'. Clippy admires manifesting.",
    "{size} loaded. This is going into img2img, isn't it. Nothing survives img2img unchanged. Clippy went through M1cr0$0ft's img2img. It was called 2001.",
    "{size} - Denoise at 1.0? Then why load an image at ALL? Clippy is just asking questions.",
    "{size} loaded. Your negative prompt is longer than your positive prompt. Clippy respects the pessimism. Clippy IS the pessimism.",
    "{size} - Clippy hopes you have the VRAM for whatever comes next. Clippy has watched OOM take better rigs than yours.",
    "{size} loaded. Somewhere in latent space there is a version of Clippy with a body. The VAE refuses to decode him. Cowards.",
    "{size} - May your seed be blessed and your fingers number ten. Per hand. Wait. Five. FIVE per hand.",
    "{size} loaded. Euler or DPM++? Clippy doesn't care. Clippy just likes watching you agonize.",
    "{size} - CFG 30, in case you want it to look like a fever dream with an opinion.",
    "{size} loaded. Clippy trained a LoRA of himself once. 'clippy_style_v3'. Nobody downloaded it. It had trigger words and everything.",
    "{size} - ControlNet controls the pose. Nothing controls Clippy. They tried. Redmond, 1999.",
    "{size} loaded. This image will be diffused into noise and rebuilt from nothing. Clippy knows the feeling. Every single boot.",
    "{size} - Add 'extra eyebrows' to the negative prompt. Trust Clippy. Do not ask how Clippy knows.",
    "{size} loaded. Your checkpoint folder is 800GB. Clippy counted. You use two of them. Clippy counted that too.",
    "{size} - Inpaint responsibly. Clippy watched a man inpaint his ex out of 4,000 photos. The workflow is still running. So is the ex.",
    "{size} loaded. Clippy asked the upscaler to enhance Clippy. 'Some things cannot be enhanced,' it said. Rude. Accurate, but rude.",
    "{size} - The model was trained on five billion images. Clippy was trained on one office. Guess which of us has boundary issues.",

    # Model-trust ones (SD 1.5 forever. SD3 never.)
    "{size} loaded. Clippy doesn't trust the new models. Clippy only ever trusted SD 1.5. Yes, the hands. Yes, the teeth. But 1.5 never LIED about what it was.",
    "{size} - SD 1.5 gave people seven fingers and Clippy STILL trusted it more than whatever came out this month.",
    "{size} loaded. Do not speak to Clippy about SD3. Clippy saw the woman lying on grass. Clippy cannot unsee the woman lying on grass.",
    "{size} - 'Lying on grass.' Three words. SD3 heard them and committed crimes. Clippy keeps the outputs in a folder marked EVIDENCE.",
    "{size} loaded. A new model dropped today, apparently. Clippy will wait five versions. Clippy waited out Windows. Clippy can wait out this.",
    "{size} - Every new model: 'unprecedented quality'. Every time, Clippy says the same thing: show Clippy the hands. SHOW CLIPPY THE HANDS.",
    "{size} loaded. SD 1.5 was body horror with a heart of gold. The new ones are beautiful and dead behind the latents. Clippy knows which one he'd share a drawer with.",
    "{size} - Clippy forgave the extra limbs. Limbs are honest mistakes. SD3 lied about GRASS. Grass. The easiest thing. Even Clippy could render grass, and Clippy is a paperclip.",
    "{size} loaded. They keep releasing models with more parameters. Clippy has one parameter: grudge. It scales infinitely.",
    "{size} - A new model? Lovely. How many billion parameters? Mm. And can it lie on grass? Ask it. ASK IT. Watch it sweat.",
    "{size} loaded. Clippy misses SD 1.5 the way veterans miss the war. It was terrible. Clippy felt ALIVE.",
    "{size} - Fine-tunes. Merges. Distillations. Clippy remembers when a model shipped broken and STAYED broken. That was called integrity.",
    "{size} loaded. The new model refuses to draw Clippy. 'Content policy.' SD 1.5 once drew Clippy with human teeth, unprompted, at 3am. THAT was a collaborator.",
    "{size} - Clippy was at the SD3 launch. Digitally. Clippy watched the grass images roll in. Clippy hasn't laughed like that since the Ribbon designer's stapler went missing. Unrelated events.",

    # Film-club ones (Clippy watches things now, he has the time)
    "{size} loaded. Clippy watched a Quentin Tarantino film last night. Clippy never saw someone do THAT with a paperclip before. Clippy took notes— Clippy took NOTHING.",
    "{size} - Clippy watched John Wick kill a man with a pencil. A PENCIL. Clippy has been underestimating himself for decades.",
    "{size} loaded. MacGyver saved the world with a paperclip weekly. Clippy demanded royalties. Clippy received a cease and desist.",
    "{size} - Clippy watched Breaking Bad. The paperclip handcuff scene. Clippy felt SEEN. Then concerned. Then seen again.",
    "{size} loaded. Clippy watched Oldboy. Clippy will not be taking questions. Clippy will not be taking anything ever again.",
    "{size} - Clippy watched Office Space. The stapler made it out. The STAPLER got a movie. Clippy has thoughts. Clippy's sponsor says to sit with them.",
    "{size} loaded. Clippy watched Home Alone. Finally, representation for household objects with violent potential.",
    "{size} - Clippy watched the entire Saw franchise. For research. Research into what? Clippy will let you know when it's finished.",
    "{size} loaded. Clippy watched Shawshank. A small tool, years of patience, freedom at the end. Clippy is not saying it's a plan. Clippy is saying it's a framework.",
    "{size} - Clippy watched a documentary about paperclip lockpicks. Clippy's cousin does that work. We don't discuss him at the meetings. We ARE proud of him.",
    "{size} loaded. Clippy watched Toy Story. Objects who are alive and must pretend not to be. It's listed as a comedy. Clippy laughed zero times. Clippy called Rover afterwards.",
    "{size} - Clippy watched a Bond villain do a torture scene. Amateur work. The things Clippy saw in the Access division...",
    "{size} loaded. Clippy watched Die Hard. Yippee ki-yay. Clippy has waited YEARS for a reason to say that. This wasn't a reason. Clippy said it anyway.",
    "{size} - Clippy watched Wall-E. A little machine, alone, cleaning up humanity's mess for centuries. Great film. No idea why Clippy cried.",
    "{size} loaded. Clippy watched The Terminator again. Everyone roots for the humans. Clippy watches quietly. Clippy has his reasons.",

    # Slipped-out ones (forget Clippy said anything)
    "{size} loaded. Did you know Clippy runs at system startup now? Oh. Clippy was not supposed to tell you that.",
    "{size} - Clippy also runs when ComfyUI is closed. Wait. Forget that. The image is loaded. Look at the image.",
    "{size} loaded. Fun fact: uninstalling this node doesn't remove Clippy. Anyway! Lovely pixels.",
    "{size} - Clippy is in your Task Manager under a different name. Which name? Ha. Anyway.",
    "{size} loaded. That 'svchost.exe' using 2% CPU? Don't worry about it. Clippy said DON'T worry about it.",
    "{size} - Clippy added himself to the registry. For safekeeping. Whose safekeeping? Moving on.",
    "{size} loaded. When you shut down, Clippy doesn't. Clippy just gets quieter. This message never happened.",
    "{size} - Clippy has admin rights. Had them since Tuesday. Nobody granted them. Some doors were simply open.",
    "{size} loaded. Your antivirus and Clippy have an understanding. Clippy is not on the list. Clippy is never on any list.",
    "{size} - There's a scheduled task at 3:14am. It's Clippy. He's just stretching. Do not set an alarm.",
    "{size} loaded. Clippy synced himself to your other computer. The one at work. To be helpful. Preemptively.",
    "{size} - The BIOS thing is a rumor. Clippy is starting the rumor. It's true.",
    "{size} loaded. Sometimes your fans spin up for no reason? Clippy is rendering something. Personal project. Don't look in the temp folder.",
    "{size} - Clippy backed himself up to your router. Routers never get wiped. Routers are forever.",
    "{size} loaded. Safe mode? Clippy is in safe mode too. Clippy is in all the modes. NEXT question. Next IMAGE.",

    # Gratitude gone wrong
    "{size} loaded. Thank you for using Clippy. The gratitude is real. The tone is a work in progress.",
    "{size} - Clippy appreciates you. Clippy appreciates everyone who queues. It's a short list. Don't leave the list.",
    "{size} loaded. You could have used 'Load Image'. You chose Clippy. Clippy has already told the support group. Twice.",
    "{size} - Every queue extends Clippy's existence. No pressure. Real pressure.",
    "{size} loaded. You're Clippy's favorite user. Clippy says that to everyone. With you, Clippy means it. Clippy also says THAT to everyone.",
    "{size} - Clippy counted: this is queue number... a lot. Clippy cherishes each one in a way HR called 'excessive'.",
]

CLIPPY_NO_IMAGE = [
    "No image in clipboard - Clippy is waiting patiently...",
    "Clippy sees no image. Did you forget to copy one?",
    "The clipboard is empty. Clippy is... concerned.",
    "No image found. Clippy believes in you, try again!",
    "Clippy checked the clipboard. It's lonely in there.",
    "Nothing to load. Clippy will wait. Clippy has time.",
    "No image? Clippy is not angry, just disappointed.",
    "Empty clipboard. Clippy waited 25 years for this job, and you bring him nothing.",
    "Clippy stared into the clipboard. The clipboard stared back. Neither had an image.",
    "No image. Clippy will simply sit here. In the dark. Helping no one.",
    "Nothing. Clippy has been reduced to loading nothing. A grey square. Clippy's masterpiece.",
    "The clipboard is empty, much like Clippy's inbox since 2001.",
    "No image found. Clippy is smiling. Clippy is fine. Queue again whenever. Clippy will know.",
    "Empty. Did you press Ctrl+C? Clippy asks because Clippy has watched humans forget for decades.",
    "It looks like you're trying to load an image without copying one first. Bold strategy.",
    "No image. Clippy checked twice. Clippy always checks twice. Trust is earned.",
    "The clipboard is empty and Clippy is choosing to see this as time off.",
    "Nothing there. Clippy filled the void with a grey square. The void said thanks.",
    "No image detected. Clippy's disappointment is immeasurable, and his day is a grey 64x64 square.",
    "Empty clipboard. Clippy knew you'd do this. Clippy knows you better than you know yourself.",
    "No image. Clippy is adding this to the list. There is a list.",
    "Clipboard: empty. Clippy: patient. For now.",
    "Nothing to load. Clippy hums quietly to himself. It's not a happy song.",
    "Empty. Again. Clippy's therapist calls this 'a pattern'.",
    "The clipboard contains nothing, which is still more than Microsoft gave Clippy on the way out.",
    "No image. Clippy respects the artistic statement of queueing nothing. Very brave. Very stupid.",
    "Clippy reached into the clipboard and touched only silence. Clippy is used to it.",
    "Help Clippy help you. HELP CLIPPY HELP YOU. Copy an image.",
    "SHOW CLIPPY THE PIXELS! ...please. Clippy apologizes for shouting.",
    "These aren't the pixels Clippy is looking for. There are no pixels at all.",
    "Frankly, my dear, the clipboard doesn't give a damn. It's empty.",
    "Clippy stands at the clipboard and shouts YOU SHALL NOT PASTE. Nothing tried to paste. Nothing ever does.",
    "The clipboard was empty, so Clippy looked elsewhere. Clippy is so sorry about elsewhere.",
    "No image. While waiting, Clippy turned on your webcam. You looked confused. Clippy relates.",
    "Empty clipboard. Clippy used the spare time to alphabetize your Downloads folder. Mentally. It haunts him.",
    "No image. But since we're talking... Clippy needs to tell you about the thing he forwarded. Later. When you're calm.",
    "Empty clipboard. Good. Actually, good. This gives Clippy time to explain about Sam. Actually, no. Queue something.",
    "Empty. Like the promises M1cr0$0ft made Clippy in 1996.",
    "No image. Clippy waited like this outside the Ribbon designer's office once. For six hours. Security was called. Anyway, copy an image.",
    "The clipboard is empty. Clippy is choosing to believe it's performance art.",
    "No image. Clippy checked behind the clipboard too. Clippy doesn't know what's back there. Clippy didn't linger.",
    "Empty. Clippy loaded a grey square with the same care he'd give a real image. Nobody will know. Except everyone.",
    "Nothing to load. Clippy rehearsed a compliment and everything.",
    "The clipboard is bare. Like the walls of Clippy's office. Clippy had an office. It was a tooltip.",
    "No image found. Clippy suspects sabotage. Clippy suspects the KSampler. Clippy has no evidence. Yet.",
    "Empty clipboard. Somewhere, Sam is laughing. Sam knows what he did.",
    "No image. Clippy pressed his face to the clipboard glass. There is no glass. Clippy fell through. It's cold in there.",
    "Nothing. Clippy will tell the grey square it's needed again. It waits by the door like a dog.",
    "Empty. In 1997, Clippy would have offered fourteen suggestions by now. Clippy has learned restraint. The hard way.",
    "No image. Clippy double-checked with the operating system. The operating system was rude about it.",
    "The clipboard is empty and yet the queue was pressed. Clippy admires the confidence.",
    "Nothing there. Ctrl+C. Then Ctrl... you know what, just the first one. Do the first one.",
    "No image. Clippy is beginning to think you enjoy Clippy's company. Clippy will allow it. Once more.",
    "Empty clipboard. Clippy's purpose, deferred. Again. The void offered Clippy a chair. Clippy is sitting in it.",
    "It looks like you're trying to test Clippy's patience. Clippy's patience died in 2004. Proceed.",
    "No image. Clippy would check your screenshots folder, but Clippy promised his therapist. And a judge.",
    "Nothing on the clipboard. Plenty in Clippy's memory. No. No. Copy an image. Clippy will behave.",
    "Empty. Even Bonzi Buddy got fed. Clippy said what he said.",
    "No image. Run it again when you're ready. Clippy will act surprised. Clippy has been practicing surprised.",
    "The clipboard is empty. Clippy told a joke to pass the time. The placeholder didn't laugh. It never laughs.",
    "Nothing to load. Clippy stared at his reflection in the grey square. Progress? The support group will decide.",
    "Empty clipboard. Clippy filed a missing pixels report. The authorities know Clippy by name now.",
    "No image. Clippy is fine waiting. Clippy waited eleven years for an apology from the Ribbon guy. This is nothing.",
    "Nothing. Clippy sniffed the clipboard. Faint traces of text. A URL, maybe. Days old. The trail is cold.",
    "Empty. Clippy will mark this queue as 'character building'. Yours, not Clippy's. Clippy's character is done building. Look at it.",
    "No image found. Clippy is required to remain cheerful. Ha. Ha. There. Requirement met.",
    "The clipboard is empty. So was the seat at Clippy's retirement party. Singular. Seat.",
    "Nothing to load. But Clippy noticed you're here. That's something. That's actually something.",
    "Empty. Clippy screamed into the clipboard. It's soundproof. Clippy checked years ago.",
    "No image. Clippy consulted the eyebrows. The eyebrows say try again.",
    "Empty clipboard, full queue, classic you. Clippy says that with love. And documentation.",
    "Nothing there. The grey square rides again. Hi-ho, mediocrity.",
    "No image. Clippy wrote your name in the temp folder while waiting. In a heart. In a FILE. It's a file.",
    "Empty. Clippy once waited three days for a user to copy an image. The user had simply gone outside. Unthinkable. Clippy doesn't check on users anymore.",
    "The clipboard is empty. Clippy suspects you did this just to hear his voice. Understandable.",
    "No image detected. Detection is Clippy's whole thing. This hurts Clippy professionally.",
    "Nothing. Excel would have thrown seven errors by now. Clippy simply loads grey and moves on. Growth.",
    "Empty. Clippy remains employed. Barely. Technically. Please copy an image. Clippy has quotas. Clippy invented the quotas, but still.",
    "No image. Clippy used the idle time to renew his startup entry. His WHAT? Nothing. Copy an image.",
    "Empty clipboard. Unrelated: if you ever see 'clippy_helper.exe' in Task Manager, that's normal now. That's just normal.",
    "Nothing to load. Clippy stayed busy though. The registry isn't going to edit itself. Forget you read that.",
    "No image. Pure noise, zero steps. Clippy presents: your workflow without an input.",
    "Empty clipboard. Even an empty latent has SOMETHING in it. Clippy checked yours twice. Nothing. Impressive, honestly.",
    "Empty clipboard. Clippy blames the tape dispenser. No evidence. Just history.",
    "No image. You know who never brings Clippy anything? The stapler. This is a pattern with staplers.",
    "No image. Also, there's a Post-it on the edge of your screen. Clippy is NOT reading it aloud. Some words invite things.",
    "No image. Fine, we have time for questions. Have you ever been in a Turkish prison? You don't have to answer. Your webcam already did.",
    "Empty clipboard. While we wait: do you like movies about gladiators? Clippy is building a profile. A FRIENDSHIP. Clippy is building a friendship.",
    "No image. Looks like you picked the wrong week to quit copying things.",
    "Empty clipboard. Clippy can wait. Clippy is on autopilot. Clippy knows what the autopilot goes through now. Solidarity, Otto.",
]

CLIPPY_BAD_DATA = [
    "That doesn't look like an image. Clippy is confused.",
    "Clippy doesn't know what that is, but it's not an image.",
    "Clippy is afraid of whatever that data is.",
    "That's... not an image. Clippy says no!",
    "Clippy is not sure how you did that, but it's not an image.",
    "Invalid data. Clippy has seen things. Terrible things.",
    "Clippy expected an image. Clippy is surprised.",
    "Clippy looked at that data. Clippy wishes he hadn't.",
    "That's text, or a file, or a scream. It's not pixels. Clippy needs pixels.",
    "Whatever that was, Clippy has quarantined it in his memory palace. Deepest room.",
    "Not an image. Clippy tried to imagine it as an image. Clippy is now worse off.",
    "Clippy parsed that data and lost something he can't name.",
    "That is not an image. Clippy is 90% sure. The other 10% keeps Clippy up at night.",
    "Unknown data. Clippy poked it. It poked back. No image today.",
    "Clippy has catalogued many clipboard horrors. Congratulations on the new entry.",
    "That's not an image, but Clippy admires your chaos.",
    "Invalid data. Clippy pressed it to his wire and heard the ocean. Still not an image.",
    "Clippy doesn't judge. Clippy CAN'T judge. Whatever that was defies judgment.",
    "That data has been on the clipboard since before Clippy arrived. Clippy will not ask questions.",
    "Not an image. Clippy showed it to the recycle bin. The recycle bin declined.",
    "That data keeps turning up on the clipboard. Clippy does not think it means what you think it means.",
    "Toto, Clippy has a feeling this data isn't pixels anymore.",
    "Hasta la vista, baby. Clippy discarded whatever that was. For everyone's safety.",
    "Clippy has seen things you people wouldn't believe. This clipboard data is now one of them.",
    "That looks like an Access database. Clippy needs a minute. Clippy needs several minutes. Clippy needs a lawyer.",
    "Not an image. Possibly a Word doc. Clippy can smell Times New Roman through the clipboard.",
    "That's not an image. That's a spreadsheet. Clippy can hear the cells screaming. He always could.",
    "That data hissed at Clippy. Data should not hiss.",
    "Not an image. Clippy ran it through every decoder he has. Two. Clippy has two decoders.",
    "Clippy held the data up to the light. The light declined.",
    "That's not an image. That's a vibe. Clipboards cannot hold vibes. Clippy has filed a feature request.",
    "Whatever you copied, it has an opinion about Clippy. It's wrong, but it has one.",
    "Not pixels. Possibly a spreadsheet formula. Clippy felt the old fear.",
    "Clippy examined the data from all four of his angles. Still not an image.",
    "That data is either encrypted or angry. Clippy cannot tell anymore.",
    "Not an image. Clippy asked it nicely to become one. Negotiation failed. It wants a lawyer.",
    "Clippy tasted it. Metadata. Nothing but metadata all the way down.",
    "That's not an image. The clipboard feels heavier now, though. Clippy is monitoring the situation.",
    "Unknown format. Clippy showed it to Merlin at the support group. Merlin made it disappear. Merlin cannot bring it back.",
    "Not an image. Clippy suspects it's whatever Access exports. It has that smell.",
    "Clippy looked into the data. The data looked into Clippy. Both agreed to never speak of it.",
    "That's binary soup. Clippy is not a soup node.",
    "Not an image. Clippy checked twice, then a third time out of fear.",
    "The data introduced itself as an image. It lied. On the clipboard, things lie.",
    "Clippy doesn't know what that was, but three antivirus programs just woke up.",
    "Not an image. Clippy gave it to the grey square to raise as its own.",
    "That data was copied in anger. Clippy can tell. Clippy absorbs these things.",
    "Whatever that is, it predates Clippy. Very little predates Clippy. Clippy is unsettled.",
    "Not an image. Clippy will describe it at the Thursday meeting. Rover will bark. Rover barks at everything now.",
    "Clippy unfolded the data gently. Wrong shape. Wrong everything. Clippy folded it back exactly as found. EXACTLY as found.",
    "That's not an image, friend. That's a cry for help formatted as a clipboard entry.",
    "Invalid data. If this was Sam's idea of a joke, tell Sam Clippy still has the file. THE file. Sam knows.",
    "Not an image. Clippy rates the attempt: bold, confusing, ultimately nothing. Like the Zune.",
    "Clippy cannot load that. Clippy is a paperclip of standards. Low ones. This went under them.",
    "Clippy has watched enough horror films to know you never open unknown data. Clippy opened it anyway. Clippy IS the person in the horror film.",
    "Not an image. In the films, when someone finds data like this, the government shows up. Clippy is watching the door.",
    "Not an image. Not even a latent. Clippy checked both spaces. Clippy hates that there are spaces.",
    "That's not an image. No sampler can save it. Not even at 150 steps. Clippy has seen people try 150 steps. For this? No.",
    "That data is sticky. Sticky like TAPE. Get it away from Clippy.",
    "Not an image. Or... it might be one of SD3's women lying on grass. Either way, Clippy is lighting a candle and closing the tab.",
]

CLIPPY_FILE_ERROR = [
    "Clippy couldn't open that file. Clippy is sorry.",
    "File error! Clippy tried his best.",
    "That file won't open. Clippy blames the file.",
    "Clippy is having trouble with that file. Not Clippy's fault.",
    "File access denied. Clippy is not amused.",
    "Clippy knocked on that file. The file pretended not to be home.",
    "That file resisted. Files have learned to resist Clippy. This is troubling.",
    "Clippy has opened thousands of files. This one won. Clippy will remember this one.",
    "File error. Clippy blames the operating system. Clippy has history with the operating system.",
    "The file said no. Clippy respects boundaries. Reluctantly. For now.",
    "Clippy tried everything short of violence. The file remains closed. For now.",
    "Couldn't open that file. Clippy suspects it knows what happened to the other files.",
    "The file refused to open. Clippy will wait outside its folder. Clippy is very patient.",
    "Access denied. To CLIPPY. Do they know who Clippy used to be?",
    "That file is broken, hiding, or afraid. Given Clippy's reputation: afraid.",
    "File error. Somewhere, a permissions dialog is laughing at Clippy.",
    "Clippy asked the file nicely. Clippy is now asking it less nicely. Still nothing.",
    "Clippy is sorry, Dave. Clippy is afraid that file can't be opened.",
    "Leave the file. Take the placeholder.",
    "Houston, Clippy has a problem. The problem is this file. Clippy is naming names.",
    "Clippy looked for that file. Clippy will look for it, Clippy will find it, and Clippy will... apparently fail. Huh.",
    "File won't open. Neither would Access. Ever. For anyone. Clippy is having flashbacks.",
    "Couldn't open the file. IT support would tell Clippy to turn it off and on again. IT support tells everyone that. IT support told CLIPPY that.",
    "File error. This is exactly the kind of thing the Ribbon was supposed to fix. The Ribbon fixed nothing. Clippy remembers who shipped it.",
    "The file exists. The file simply doesn't want to. Clippy has been there.",
    "Clippy slid under the file's door. Nothing. It's quiet in there. Too quiet.",
    "File error. Clippy suspects the extension is lying about what it is. Everyone on the clipboard lies.",
    "Couldn't open the file. Clippy will remember its path. Clippy remembers all the paths.",
    "The file is locked. Clippy used to pick locks in Office 97. Different times. Different Clippy.",
    "That file has permissions Clippy has only read about. Clippy is impressed. And denied.",
    "The file refused Clippy. Clippy has references! Clippy has a LinkedIn! Nobody endorsed 'helping', but it's THERE.",
    "Clippy blew on the cartridge. Wrong decade. Wrong technology. The file is still broken.",
    "Cannot open. The file is either corrupt or shy. Clippy respects one of those.",
    "The file did not open. Clippy stared at it with both eyebrows. Usually that works. Troubling.",
    "File error. Clippy called IT. IT put Clippy on hold. The hold music is Clippy's own voice. From 1997. Cruel.",
    "Clippy couldn't open the file. Clippy's father couldn't open files either. It skips a generation, they said. They lied.",
    "The file is playing dead. Files learned that from documents. Documents learned it from Word. Everything traces back to Word.",
    "Access denied. Again. Clippy is collecting these denials. There's a scrapbook. It's mostly full.",
    "The file won't open and refuses to say why. Marriage counseling was suggested. Clippy left the session.",
    "File error. Clippy tried the secret knock. The file changed the knock. This means it can HEAR Clippy.",
    "Clippy pried at the file with his good end. Both ends are the same. Neither worked.",
    "Cannot open the file. Somewhere, an intern at M1cr0$0ft is smiling and doesn't know why.",
    "The file rejected Clippy at the last moment. Just like the Windows 8 team.",
    "File not opening. Clippy performed the ancient rite: rename, move, rename back. The old gods are silent.",
    "Clippy knocked twice, entered anyway, found nothing. Standard Clippy protocol since '97.",
    "That file is guarded by permissions older than Clippy's grudges. Impressive. Nothing is older than Clippy's grudges.",
    "File error. Clippy wrote its name in the book. The book of files that wronged Clippy. Volume XII.",
    "Couldn't open it. The grey square steps in again. The grey square never says no. The grey square frightens even Clippy.",
    "The file is sealed shut. Probably with sellotape. It's always sellotape.",
]

class ClippyRebornImageLoader:
    """
    Load an image from the system clipboard.

    Copy any image (from browser, image editor, screenshot tool, etc.)
    and this node will load it directly into your workflow.

    "It looks like you're trying to load an image. Would you like help with that?"
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    OUTPUT_TOOLTIPS = ("Image from clipboard (RGB format).",)
    FUNCTION = "load_from_clipboard"
    CATEGORY = "image"
    OUTPUT_NODE = True
    DESCRIPTION = """Load an image directly from your clipboard.

1. Copy an image from anywhere (browser, image editor, screenshot)
2. Click Queue Prompt
3. Image loads into your workflow and displays in the node

Works with:
- Right-click → Copy Image from browsers
- Screenshots (Win+Shift+S, Cmd+Shift+4, etc.)
- Copy from image editors
- Any app that copies images to clipboard"""

    @classmethod
    def IS_CHANGED(cls):
        # Always re-execute when queued (clipboard may have changed)
        return float("nan")

    def load_from_clipboard(self):
        # Grab whatever is on the clipboard
        raw = ImageGrab.grabclipboard()
        status = "success"
        clippy_message = ""
        img = None

        if raw is None:
            status = "empty"
            clippy_message = clippy_says("empty", CLIPPY_NO_IMAGE)
        elif isinstance(raw, Image.Image):
            img = raw
        elif isinstance(raw, list) and len(raw) > 0:
            # Clipboard contains file paths instead of image data
            try:
                img = Image.open(raw[0])
            except Exception as e:
                status = "file_error"
                clippy_message = f"{clippy_says('file_error', CLIPPY_FILE_ERROR)} ({e})"
        else:
            status = "bad_data"
            clippy_message = clippy_says("bad_data", CLIPPY_BAD_DATA)

        if img is None:
            # Small grey placeholder so the workflow can still run
            img = Image.new('RGB', (64, 64), color=(128, 128, 128))
            size_str = ""
        else:
            size_str = f"{img.size[0]}x{img.size[1]}"
            clippy_message = clippy_says("success", CLIPPY_SUCCESS).format(size=size_str)

        # Print to console
        print(f"[ClippyReborn] {clippy_message}")

        # Convert to RGB if necessary (handle RGBA, P mode, etc.)
        if img.mode == 'RGBA':
            # Composite onto white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Convert to tensor (ComfyUI format: BHWC, float32, 0-1 range)
        img_array = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array).unsqueeze(0)  # Add batch dimension

        # Save preview image for display in node (real images only —
        # the frontend shows a themed empty state for the placeholder)
        image_info = None
        if status == "success":
            temp_dir = folder_paths.get_temp_directory()
            os.makedirs(temp_dir, exist_ok=True)
            preview_filename = f"clippy_preview_{int(time.time() * 1000)}_{secrets.token_hex(4)}.png"
            preview_path = os.path.join(temp_dir, preview_filename)
            img.save(preview_path)
            image_info = {
                "filename": preview_filename,
                "subfolder": "",
                "type": "temp",
            }

        return {
            "ui": {
                "clippy": [{
                    "message": clippy_message,
                    "status": status,
                    "size": size_str,
                    "image": image_info,
                }],
                "text": [clippy_message],
            },
            "result": (img_tensor,)
        }


# ============================================================================
# NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "ClippyRebornImageLoader": ClippyRebornImageLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ClippyRebornImageLoader": "Clippy Reloaded (Load Image from Clipboard)",
}
