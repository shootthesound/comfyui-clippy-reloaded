import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const CLASS_NAME = "ClippyRebornImageLoader";

const GREETING =
    "It looks like you're trying to load an image. Would you like help with that?";

const EMPTY_STATES = {
    initial: { icon: "\u{1F4CB}", text: "Copy an image anywhere,<br>then run the workflow." },
    empty: { icon: "\u{1F4CB}", text: "Nothing on the clipboard.<br>Clippy checked twice." },
    bad_data: { icon: "\u{1F928}", text: "That wasn't an image.<br>Clippy doesn't know what it was." },
    file_error: { icon: "\u{1F4C4}", text: "Couldn't open that file.<br>Clippy blames the file." },
};

const CSS = `
.cr-root{display:flex;flex-direction:column;gap:8px;width:100%;height:100%;box-sizing:border-box;padding:4px 2px 2px;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;user-select:none;overflow:hidden;}
.cr-preview{position:relative;flex:1 1 auto;min-height:80px;border-radius:10px;border:1px solid rgba(255,255,255,.08);overflow:hidden;display:flex;align-items:center;justify-content:center;background:linear-gradient(45deg,rgba(255,255,255,.045) 25%,transparent 25%,transparent 75%,rgba(255,255,255,.045) 75%),linear-gradient(45deg,rgba(255,255,255,.045) 25%,transparent 25%,transparent 75%,rgba(255,255,255,.045) 75%),#1a1a1f;background-size:18px 18px;background-position:0 0,9px 9px;}
.cr-img{max-width:calc(100% - 12px);max-height:calc(100% - 12px);object-fit:contain;border-radius:5px;box-shadow:0 5px 16px rgba(0,0,0,.5);opacity:0;transition:opacity .4s ease;}
.cr-img.cr-show{opacity:1;}
.cr-badge{position:absolute;right:8px;bottom:8px;display:none;background:rgba(8,8,10,.75);color:#ecedf1;font-size:11px;font-weight:600;letter-spacing:.4px;padding:3px 9px;border-radius:999px;border:1px solid rgba(255,255,255,.14);backdrop-filter:blur(3px);}
.cr-empty{position:absolute;inset:0;display:flex;flex-direction:column;gap:8px;align-items:center;justify-content:center;text-align:center;color:#8f909c;font-size:12px;line-height:1.55;padding:8px;}
.cr-empty-icon{font-size:26px;opacity:.85;}
.cr-bottom{display:flex;align-items:flex-end;gap:9px;flex:0 0 auto;}
.cr-clippy{flex:0 0 60px;height:88px;}
.cr-clippy-svg{width:100%;height:100%;overflow:visible;filter:drop-shadow(0 3px 6px rgba(0,0,0,.45));}
.cr-bubble{position:relative;flex:1 1 auto;background:#fffcd9;color:#40371c;border:1px solid #d6c97e;border-radius:12px;border-bottom-left-radius:3px;padding:9px 12px 10px;font-size:12.5px;line-height:1.45;min-height:38px;max-height:84px;overflow-y:auto;box-shadow:0 5px 14px rgba(0,0,0,.38);transform-origin:bottom left;scrollbar-width:thin;}
.cr-bubble::before{content:"";position:absolute;left:-6.5px;bottom:10px;width:11px;height:11px;background:#fffcd9;border-left:1px solid #d6c97e;border-bottom:1px solid #d6c97e;transform:rotate(45deg);}
.cr-bubble.cr-pop{animation:cr-pop .38s cubic-bezier(.34,1.56,.64,1);}
@keyframes cr-pop{from{transform:scale(.82);opacity:.3;}to{transform:scale(1);opacity:1;}}
.cr-caret{display:inline-block;width:7px;height:2px;background:#6b5d28;margin-left:2px;vertical-align:baseline;animation:cr-caret .8s steps(2,start) infinite;}
@keyframes cr-caret{50%{opacity:0;}}
.cr-bob{animation:cr-bob 3.8s ease-in-out infinite;}
@keyframes cr-bob{0%,100%{transform:translateY(0);}50%{transform:translateY(-3px);}}
.cr-eyes{transform-origin:50px 29px;animation:cr-blink 4.6s infinite;}
@keyframes cr-blink{0%,93.5%,97.5%,100%{transform:scaleY(1);}95.5%{transform:scaleY(.07);}}
.cr-rig{transform-origin:50px 90px;}
.cr-clippy-svg.cr-talk .cr-rig{animation:cr-talk .16s ease-in-out 5 alternate;}
@keyframes cr-talk{from{transform:rotate(-3deg);}to{transform:rotate(3deg);}}
.cr-brow{transform-box:fill-box;transform-origin:center;transition:transform .35s ease;}
.cr-clippy-svg.cr-mood-empty .cr-brow-l{transform:translate(1.5px,4px) rotate(12deg);}
.cr-clippy-svg.cr-mood-empty .cr-brow-r{transform:translate(-1.5px,4px) rotate(-12deg);}
.cr-clippy-svg.cr-mood-error .cr-brow-l{transform:translateY(-3.5px);}
.cr-clippy-svg.cr-mood-error .cr-brow-r{transform:translate(0,3px) rotate(7deg);}
`;

const CLIPPY_SVG = `
<svg class="cr-clippy-svg" viewBox="0 0 100 150" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <linearGradient id="crWire" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#eef3f8"/>
      <stop offset="0.5" stop-color="#a9bccd"/>
      <stop offset="1" stop-color="#6d8299"/>
    </linearGradient>
  </defs>
  <g class="cr-rig">
    <g class="cr-bob">
      <path fill="none" stroke="url(#crWire)" stroke-width="8" stroke-linecap="round"
        d="M 34 62 L 34 118 C 34 140, 66 140, 66 118 L 66 58 C 66 40, 40 40, 40 58 L 40 106 C 40 122, 58 122, 58 106 L 58 66"/>
      <path fill="none" stroke="rgba(255,255,255,0.32)" stroke-width="2.2" stroke-linecap="round"
        d="M 33 61 L 33 117 C 33 138, 65 138, 65 117 L 65 57 C 65 40, 41 40, 41 57 L 41 105 C 41 120, 57 120, 57 105 L 57 65"/>
      <path class="cr-brow cr-brow-l" fill="none" stroke="#cfd8e3" stroke-width="5" stroke-linecap="round" d="M 26 12 Q 37 3 48 11"/>
      <path class="cr-brow cr-brow-r" fill="none" stroke="#cfd8e3" stroke-width="5" stroke-linecap="round" d="M 52 11 Q 63 3 74 12"/>
      <g class="cr-eyes">
        <ellipse cx="38" cy="29" rx="11.5" ry="13.5" fill="#ffffff" stroke="#3c414b" stroke-width="2"/>
        <ellipse cx="62" cy="29" rx="11.5" ry="13.5" fill="#ffffff" stroke="#3c414b" stroke-width="2"/>
        <circle class="cr-pupil" data-cx="38" data-cy="31" cx="38" cy="31" r="4.4" fill="#1c1e22"/>
        <circle class="cr-pupil" data-cx="62" data-cy="31" cx="62" cy="31" r="4.4" fill="#1c1e22"/>
      </g>
    </g>
  </g>
</svg>`;

function injectStyles() {
    if (document.getElementById("clippy-reloaded-style")) return;
    const style = document.createElement("style");
    style.id = "clippy-reloaded-style";
    style.textContent = CSS;
    document.head.appendChild(style);
}

function typewrite(node, msgEl, caretEl, text) {
    if (node._crTypeTimer) clearInterval(node._crTypeTimer);
    if (node._crCaretTimer) clearTimeout(node._crCaretTimer);
    msgEl.textContent = "";
    caretEl.style.display = "inline-block";
    let i = 0;
    node._crTypeTimer = setInterval(() => {
        i++;
        msgEl.textContent = text.slice(0, i);
        if (i >= text.length) {
            clearInterval(node._crTypeTimer);
            node._crTypeTimer = null;
            node._crCaretTimer = setTimeout(() => {
                caretEl.style.display = "none";
            }, 1200);
        }
    }, 16);
}

function replayAnimation(el, cls, duration, timerKey, node) {
    el.classList.remove(cls);
    // Force a reflow so re-adding the class restarts the CSS animation
    void el.getBoundingClientRect();
    el.classList.add(cls);
    if (node[timerKey]) clearTimeout(node[timerKey]);
    node[timerKey] = setTimeout(() => el.classList.remove(cls), duration);
}

function attachEyeTracking(node, svg) {
    const pupils = svg.querySelectorAll(".cr-pupil");
    let raf = null;
    const onMove = (e) => {
        if (raf) return;
        raf = requestAnimationFrame(() => {
            raf = null;
            const r = svg.getBoundingClientRect();
            if (!r.width || !r.height) return;
            pupils.forEach((p) => {
                const cx = r.left + (Number(p.dataset.cx) / 100) * r.width;
                const cy = r.top + (Number(p.dataset.cy) / 150) * r.height;
                const dx = e.clientX - cx;
                const dy = e.clientY - cy;
                const dist = Math.hypot(dx, dy) || 1;
                const m = Math.min(3.2, dist / 24);
                p.setAttribute("transform", `translate(${((dx / dist) * m).toFixed(2)} ${((dy / dist) * m).toFixed(2)})`);
            });
        });
    };
    document.addEventListener("mousemove", onMove);
    node._crDetachEyes = () => {
        document.removeEventListener("mousemove", onMove);
        if (raf) cancelAnimationFrame(raf);
    };
}

function buildUI(node) {
    injectStyles();

    const root = document.createElement("div");
    root.className = "cr-root";
    root.innerHTML = `
        <div class="cr-preview">
            <img class="cr-img" style="display:none" draggable="false">
            <div class="cr-badge"></div>
            <div class="cr-empty">
                <div class="cr-empty-icon">${EMPTY_STATES.initial.icon}</div>
                <div class="cr-empty-text">${EMPTY_STATES.initial.text}</div>
            </div>
        </div>
        <div class="cr-bottom">
            <div class="cr-clippy">${CLIPPY_SVG}</div>
            <div class="cr-bubble"><span class="cr-msg"></span><span class="cr-caret"></span></div>
        </div>`;

    const el = {
        img: root.querySelector(".cr-img"),
        badge: root.querySelector(".cr-badge"),
        empty: root.querySelector(".cr-empty"),
        emptyIcon: root.querySelector(".cr-empty-icon"),
        emptyText: root.querySelector(".cr-empty-text"),
        svg: root.querySelector(".cr-clippy-svg"),
        bubble: root.querySelector(".cr-bubble"),
        msg: root.querySelector(".cr-msg"),
        caret: root.querySelector(".cr-caret"),
    };

    node.addDOMWidget("clippy_ui", "div", root, { serialize: false });
    attachEyeTracking(node, el.svg);

    node._crUpdate = (payload) => {
        const status = payload.status || "success";
        const message = payload.message || "";

        // Mood (eyebrows)
        el.svg.classList.remove("cr-mood-empty", "cr-mood-error");
        if (status === "empty") el.svg.classList.add("cr-mood-empty");
        else if (status !== "success") el.svg.classList.add("cr-mood-error");

        // Speech
        replayAnimation(el.bubble, "cr-pop", 450, "_crPopTimer", node);
        replayAnimation(el.svg, "cr-talk", 900, "_crTalkTimer", node);
        typewrite(node, el.msg, el.caret, message);

        // Preview
        const image = payload.image;
        if (status === "success" && image && image.filename) {
            const url = api.apiURL(
                `/view?filename=${encodeURIComponent(image.filename)}` +
                `&type=${encodeURIComponent(image.type || "temp")}` +
                `&subfolder=${encodeURIComponent(image.subfolder || "")}` +
                `&t=${Date.now()}`
            );
            el.img.classList.remove("cr-show");
            el.img.onload = () => el.img.classList.add("cr-show");
            el.img.style.display = "block";
            el.img.src = url;
            el.empty.style.display = "none";
            el.badge.textContent = payload.size || "";
            el.badge.style.display = payload.size ? "block" : "none";
        } else {
            el.img.classList.remove("cr-show");
            el.img.style.display = "none";
            el.badge.style.display = "none";
            const state = EMPTY_STATES[status] || EMPTY_STATES.initial;
            el.emptyIcon.textContent = state.icon;
            el.emptyText.innerHTML = state.text;
            el.empty.style.display = "flex";
        }
    };

    // Greet on creation (small delay so the node has settled on canvas)
    setTimeout(() => typewrite(node, el.msg, el.caret, GREETING), 400);
}

app.registerExtension({
    name: "ClippyReloaded.UI",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== CLASS_NAME) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);
            buildUI(this);
            this.setSize([330, 440]);
        };

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);
            const payload = message?.clippy?.[0];
            if (payload) {
                this._crUpdate?.(payload);
            } else if (message?.text?.[0]) {
                // Fallback for older backend payloads
                this._crUpdate?.({ message: message.text[0], status: "success" });
            }
        };

        const onRemoved = nodeType.prototype.onRemoved;
        nodeType.prototype.onRemoved = function () {
            this._crDetachEyes?.();
            if (this._crTypeTimer) clearInterval(this._crTypeTimer);
            if (this._crCaretTimer) clearTimeout(this._crCaretTimer);
            if (this._crPopTimer) clearTimeout(this._crPopTimer);
            if (this._crTalkTimer) clearTimeout(this._crTalkTimer);
            onRemoved?.apply(this, arguments);
        };
    },
});
