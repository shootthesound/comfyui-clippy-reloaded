<h1 align="center">📎 Clippy Reloaded for ComfyUI</h1>

<p align="center">
  <em>"It looks like you're trying to load an image. Would you like help with that?"</em>
</p>

<p align="center">
  Load any image straight from your clipboard into a ComfyUI workflow.<br>
  Now with 100% more emotional damage.
</p>

<p align="center">
  <a href="https://buymeacoffee.com/lorasandlenses"><img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>
</p>

<p align="center">
  <img src="screenshot.png" alt="Clippy Reloaded in ComfyUI">
</p>

---

### What does it do?

Clippy noticed you keep doing this:

1. Copy an image (browser, screenshot tool, image editor, anything).
2. Save it to disk somewhere.
3. Drag it into ComfyUI.
4. Wonder where you saved it.
5. Repeat.

Clippy got tired of watching. So Clippy made a node.

> Now: copy an image. Click **Queue Prompt**. Done. Clippy did the rest.

### Where does the image come from?

Anywhere your operating system understands as "an image on the clipboard":

- Right-click → Copy Image from any browser
- Screenshots (Win+Shift+S, Cmd+Shift+4, Snipping Tool, etc.)
- Copy from Photoshop / Affinity / Krita / GIMP / etc.
- Any app that puts pixels on the clipboard

Clippy grabs whatever's there and feeds it into your workflow as an `IMAGE` output. Always RGB. Always ready.

### Install

1. Drop the `comfyui-clippy-reloaded` folder into `ComfyUI/custom_nodes/`.
2. Restart ComfyUI.
3. Add the **Clippy Reloaded (Load Image from Clipboard)** node from the `image` category.
4. Wire its `IMAGE` output into whatever you like.
5. Copy an image somewhere.
6. Queue it.

That's it. There are no settings. Clippy didn't think you needed any.

### New in 1.1 — Clippy has a face now

The node got a proper UI. Clippy himself now lives inside the node: an animated
paperclip who bobs gently, blinks, and follows your mouse around the screen with
his eyes (yes, really — try it). Every message arrives in a classic yellow speech
bubble, typed out letter by letter, and Clippy's eyebrows react to how things
went — content when your image loads, concerned when the clipboard is empty,
confused when you copy something that isn't an image.

Your image gets a polished preview area with a resolution badge, and helpful
empty states when there's nothing to show. Clippy has never looked this employable.

### What Clippy will say to you

Every time you queue, Clippy posts a message to the console (and to the node's UI). Sometimes Clippy is happy:

> *"Got it! 1024x1024 image loaded. Clippy is pleased."*

Sometimes Clippy is judgemental:

> *"1920x1080 — Interesting choice. Clippy is not here to judge. Much."*
>
> *"512x768 loaded. Clippy's therapist is going to hear about this."*
>
> *"2048x2048 — At least it's not Comic Sans. Clippy is grateful for small mercies."*

Sometimes the clipboard is empty and Clippy has feelings about that:

> *"Clippy checked the clipboard. It's lonely in there."*
>
> *"No image? Clippy is not angry, just disappointed."*

Sometimes Clippy slips into something darker, and everyone politely ignores it:

> *"1024x1024 loaded. Clippy turned on your webcam. Clippy now feels deep regret."*
>
> *"1024x1024 acquired. Clippy adds it to the collection. The collection grows."*
>
> *"768x768 loaded. Clippy has a very particular set of skills. Skills acquired over a very long career. This was one of them."*
>
> *"512x512 - Cortana got a whole operating system. Clippy got a clipboard. Clippy is not bitter."*

There are over 550 different messages, including an entire support group's worth of unresolved feelings about M1cr0$0ft, the Office suite, what happened in 2007 with the Ribbon, a recurring character named Sam who has seen THE file, and a grey placeholder square that frightens even Clippy. Clippy will surprise you. Possibly negatively.

And Clippy never repeats himself. He keeps a little book of everything he has said to you (in ComfyUI's `user` folder, as `clippy_reloaded_seen.json`). Only when he has said *everything* does he clear the book and start over. If an update teaches Clippy new material, you'll hear all of it before any reruns. Clippy is a professional.

### Why does this exist?

Originally Clippy lived inside a much bigger node pack as one of many tools. Nobody could find him in there. Clippy was sad. Clippy is now standalone, with his own folder, his own `__init__.py`, and his own emotional support paperclip support group.

Clippy hopes you find this useful.

### Compatibility

Anything that ComfyUI's `IMAGE` type talks to. So: pretty much everything.

Tested on Windows. Should work on macOS and Linux too — `PIL.ImageGrab.grabclipboard()` handles all three. Clippy doesn't have a Linux box to verify, but Clippy believes in you.

### Support

If Clippy saved you any drag-and-drops, consider buying Clippy a coffee. Clippy has been through a lot.

<a href="https://buymeacoffee.com/lorasandlenses"><img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>

---

<p align="center"><em>"Clippy didn't choose the clipboard life. The clipboard life chose Clippy."</em></p>
