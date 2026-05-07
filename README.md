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

There are over 80 different messages. Clippy will surprise you. Possibly negatively.

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
