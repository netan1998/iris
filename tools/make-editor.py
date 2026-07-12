#!/usr/bin/env python3
"""בונה את editor.html (עורך התוכן) מתוך index.html.

מריצים אחרי כל שינוי ב-index.html:
    python3 tools/make-editor.py

יוצר שני קבצים זהים:
  - editor.html                (לשימוש מקומי, מוחרג מהאתר החי)
  - edit-iris-x74q9.html       (עותק בכתובת חשאית באתר החי, לגישה בקליק)
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC_NAME = "edit-iris-x74q9.html"

EDITOR_BLOCK = r"""
<style id="iris-editor-css">
#iris-editor-bar {
  position: fixed; top: 0; right: 0; left: 0; z-index: 1000;
  background: #10243E; color: #fff; direction: rtl;
  display: flex; align-items: center; flex-wrap: wrap; gap: 10px;
  padding: 10px 16px; font-family: 'Heebo', Arial, sans-serif; font-size: 15px;
  box-shadow: 0 4px 16px rgba(0,0,0,.35);
}
#iris-editor-bar .ttl { font-weight: 800; font-size: 16px; }
#iris-editor-bar .hint { opacity: .85; font-size: 13px; flex: 1; min-width: 200px; }
#iris-editor-bar button {
  font: inherit; font-weight: 700; cursor: pointer; border: none; border-radius: 10px;
  padding: 8px 14px; min-height: 40px; background: #24466E; color: #fff;
}
#iris-editor-bar button:hover { background: #2F5A8D; }
#iris-editor-bar #ed-save { background: #1E9E5A; font-weight: 800; }
#iris-editor-bar #ed-save:hover { background: #23B968; }
#iris-editor-bar #ed-del.on { background: #D2382C; }
#iris-editor-bar #ed-undo { background: #8A6D1F; display: none; }
body { padding-top: 64px; }
@media (max-width: 760px) { body { padding-top: 160px; } }
#iris-lp .ed-text:hover { outline: 2px dashed #1668C7; outline-offset: 2px; cursor: text; }
#iris-lp .ed-text:focus { outline: 2px solid #1668C7 !important; outline-offset: 2px; background: rgba(22,104,199,.07); }
#iris-lp .ed-img { cursor: pointer; position: relative; }
#iris-lp .ed-img:hover { outline: 3px dashed #1668C7; outline-offset: 3px; }
#iris-lp .ed-img:hover::before {
  content: "📷 בחירת תמונה מהמחשב"; position: absolute; top: 10px; right: 10px; z-index: 5;
  background: #1668C7; color: #fff; padding: 4px 12px; border-radius: 8px;
  font-size: 13px; font-weight: 700;
}
body.ed-del-mode #iris-lp .ed-deletable { cursor: crosshair; }
body.ed-del-mode #iris-lp .ed-deletable:hover {
  outline: 2px solid #D2382C !important; outline-offset: 2px;
  background: rgba(210,56,44,.09);
}
body.ed-del-mode #iris-lp .ed-text:hover { outline: none; cursor: crosshair; }
#iris-editor-toast {
  position: fixed; bottom: 90px; right: 50%; transform: translateX(50%); z-index: 1001;
  background: #10243E; color: #fff; direction: rtl; text-align: center;
  padding: 12px 22px; border-radius: 12px; font-family: 'Heebo', Arial, sans-serif;
  font-weight: 700; box-shadow: 0 8px 24px rgba(0,0,0,.35); display: none; max-width: 90vw;
}
</style>

<div id="iris-editor-bar" dir="rtl">
  <span class="ttl">🖊 מצב עריכה</span>
  <span class="hint">לחיצה על טקסט = עריכה · לחיצה על משבצת תמונה = בחירת תמונה מהמחשב</span>
  <button type="button" id="ed-del">🗑 מחיקת אלמנטים</button>
  <button type="button" id="ed-undo">↩ ביטול מחיקה</button>
  <button type="button" id="ed-add">➕ תמונה לגלריה</button>
  <button type="button" id="ed-reset">↺ איפוס</button>
  <button type="button" id="ed-save">💾 שמירה והורדת הקובץ</button>
</div>
<div id="iris-editor-toast" role="status"></div>

<script id="iris-editor-js">
(function () {
  'use strict';
  var root = document.getElementById('iris-lp');
  if (!root) return;

  if (window.__rvStop) window.__rvStop();

  var robots = document.createElement('meta');
  robots.name = 'robots';
  robots.content = 'noindex, nofollow';
  robots.id = 'iris-editor-robots';
  document.head.appendChild(robots);

  /* ── טקסט עריך ── */
  var SEL = 'h1,h2,h3,h4,p,li,summary,small,label,blockquote,span,b,strong,em,a,button';
  root.querySelectorAll('main, footer').forEach(function (scope) {
    scope.querySelectorAll(SEL).forEach(function (el) {
      if (el.closest('.ed-text') && el.closest('.ed-text') !== el) return;
      if (el.closest('.rv-nav')) return;
      if (el.matches('input, select, textarea, .rv-nav')) return;
      if (el.querySelector('input, select, textarea, img')) return;
      if (!el.textContent.trim()) return;
      el.classList.add('ed-text');
      el.setAttribute('contenteditable', 'true');
      el.setAttribute('spellcheck', 'false');
    });
  });

  /* ── במצב עריכה אין ניווט ואין שליחת טפסים ── */
  document.querySelectorAll('#iris-lp details').forEach(function (d) { d.open = true; });
  document.addEventListener('click', function (e) {
    if (e.target.closest('#iris-editor-bar')) return;
    var a = e.target.closest('a');
    if (a && !a.hasAttribute('download')) e.preventDefault();
    if (e.target.closest('button[type="submit"]')) e.preventDefault();
    if (e.target.closest('summary')) e.preventDefault();
  }, true);

  /* ── מצב מחיקת אלמנטים ── */
  var DEL_SEL = '.spots, .eyebrow, .hero-small, .form-small, .recap span, .stat, .urgency, ' +
    '.gallery .tile, .rv-card, .offer-item, .step, .faq-list details, .sec-sub, ' +
    '.about-photo, .gallery, h2, h3, p, li';
  var delMode = false;
  var undoStack = [];
  var delBtn = document.getElementById('ed-del');
  var undoBtn = document.getElementById('ed-undo');

  function setDelMode(on) {
    delMode = on;
    document.body.classList.toggle('ed-del-mode', on);
    delBtn.classList.toggle('on', on);
    delBtn.textContent = on ? '✔ סיום מחיקה' : '🗑 מחיקת אלמנטים';
    root.querySelectorAll(DEL_SEL).forEach(function (el) {
      if (el.closest('#iris-editor-bar')) return;
      el.classList.toggle('ed-deletable', on);
    });
    if (on) toast('מצב מחיקה 🗑 לחצו על אלמנט כדי להסיר אותו מהדף');
  }
  delBtn.addEventListener('click', function () { setDelMode(!delMode); });

  document.addEventListener('click', function (e) {
    if (!delMode) return;
    if (e.target.closest('#iris-editor-bar')) return;
    var el = e.target.closest('.ed-deletable');
    if (!el) return;
    e.preventDefault();
    e.stopPropagation();
    undoStack.push({ el: el, parent: el.parentNode, next: el.nextSibling });
    el.remove();
    undoBtn.style.display = '';
    toast('האלמנט נמחק · ↩ ביטול מחיקה מחזיר אותו');
  }, true);

  undoBtn.addEventListener('click', function () {
    var last = undoStack.pop();
    if (!last) return;
    var anchor = (last.next && last.next.parentNode === last.parent) ? last.next : null;
    last.parent.insertBefore(last.el, anchor);
    if (!undoStack.length) undoBtn.style.display = 'none';
    toast('האלמנט שוחזר ✔');
  });

  /* ── תמונות ── */
  var fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = 'image/*';
  fileInput.id = 'iris-editor-file';
  fileInput.style.display = 'none';
  document.body.appendChild(fileInput);
  var currentTarget = null;

  function bindImg(el) {
    el.classList.add('ed-img');
    el.addEventListener('click', function (e) {
      if (delMode) return;
      e.preventDefault();
      e.stopPropagation();
      currentTarget = el;
      fileInput.click();
    });
  }
  root.querySelectorAll('.gallery .tile, .about-photo').forEach(bindImg);

  fileInput.addEventListener('change', function () {
    var file = fileInput.files && fileInput.files[0];
    fileInput.value = '';
    if (!file || !currentTarget) return;
    var target = currentTarget;
    var reader = new FileReader();
    reader.onload = function () {
      var img = new Image();
      img.onload = function () {
        var MAX = 1400;
        var scale = Math.min(1, MAX / Math.max(img.width, img.height));
        var canvas = document.createElement('canvas');
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
        canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
        var out = document.createElement('img');
        out.src = canvas.toDataURL('image/jpeg', 0.82);
        out.alt = 'תמונה מהסטודיו';
        target.innerHTML = '';
        target.appendChild(out);
        target.classList.add('has-img');
        toast('התמונה נכנסה 🙂 אפשר ללחוץ עליה שוב כדי להחליף');
      };
      img.src = reader.result;
    };
    reader.readAsDataURL(file);
  });

  function addTile() {
    var gallery = root.querySelector('.gallery');
    if (!gallery) return;
    var t = document.createElement('div');
    t.className = 'tile';
    t.innerHTML = '<span aria-hidden="true">📷</span>מקום לתמונה';
    gallery.appendChild(t);
    bindImg(t);
    if (delMode) t.classList.add('ed-deletable');
    t.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  /* ── שמירה: שכפול הדף, ניקוי שכבת העורך, הורדת index.html ── */
  function buildCleanHtml() {
    var clone = document.documentElement.cloneNode(true);
    ['#iris-editor-bar', '#iris-editor-css', '#iris-editor-js', '#iris-editor-file',
     '#iris-editor-toast', '#iris-editor-robots']
      .forEach(function (sel) {
        var el = clone.querySelector(sel);
        if (el) el.remove();
      });
    clone.querySelectorAll('[contenteditable]').forEach(function (el) {
      el.removeAttribute('contenteditable');
      el.removeAttribute('spellcheck');
    });
    clone.querySelectorAll('.ed-text, .ed-img, .ed-deletable').forEach(function (el) {
      el.classList.remove('ed-text');
      el.classList.remove('ed-img');
      el.classList.remove('ed-deletable');
      if (!el.getAttribute('class')) el.removeAttribute('class');
    });
    var body = clone.querySelector('body');
    if (body) {
      body.classList.remove('ed-del-mode');
      if (!body.getAttribute('class')) body.removeAttribute('class');
    }
    clone.querySelectorAll('details').forEach(function (d) { d.removeAttribute('open'); });
    clone.querySelectorAll('.reveal').forEach(function (el) { el.classList.remove('in'); });
    clone.querySelectorAll('form.sent').forEach(function (f) { f.classList.remove('sent'); });
    clone.querySelectorAll('.rv-card').forEach(function (c) {
      c.classList.remove('is-center', 'is-right', 'is-left');
    });
    var stage = clone.querySelector('#rv-stage');
    if (stage) stage.removeAttribute('style');
    var r = clone.querySelector('#iris-lp');
    if (r) {
      r.removeAttribute('class');
      r.setAttribute('data-fs', '0');
    }
    var abtn = clone.querySelector('#a11y-btn');
    if (abtn) abtn.classList.remove('active');
    var apanel = clone.querySelector('#a11y-panel');
    if (apanel) apanel.classList.remove('open');
    clone.querySelectorAll('.a11y-panel [aria-pressed="true"]').forEach(function (b) {
      b.setAttribute('aria-pressed', 'false');
    });
    return '<!DOCTYPE html>\n' + clone.outerHTML;
  }

  function save() {
    var html = buildCleanHtml();
    var blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'index.html';
    document.body.appendChild(a);
    a.click();
    a.remove();
    toast('הקובץ ירד למחשב 🎉 שלחו לי אותו או העבירו לתיקיית הפרויקט');
  }

  var toastEl = document.getElementById('iris-editor-toast');
  var toastTimer = null;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.style.display = 'block';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.style.display = 'none'; }, 4500);
  }

  document.getElementById('ed-save').addEventListener('click', save);
  document.getElementById('ed-add').addEventListener('click', addTile);
  document.getElementById('ed-reset').addEventListener('click', function () {
    if (confirm('לאפס את כל השינויים שלא נשמרו?')) location.reload();
  });

  window.__irisEditor = {
    buildCleanHtml: buildCleanHtml, save: save, addTile: addTile, setDelMode: setDelMode
  };
})();
</script>
</body>"""


def main():
    src = (ROOT / "index.html").read_text()
    out = src.replace("</body>", EDITOR_BLOCK, 1)
    assert out != src, "no </body> found in index.html"
    (ROOT / "editor.html").write_text(out)
    (ROOT / PUBLIC_NAME).write_text(out)
    print(f"written: editor.html + {PUBLIC_NAME} ({len(out)//1024} KB)")


if __name__ == "__main__":
    main()
