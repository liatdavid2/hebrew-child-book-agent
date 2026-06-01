import json
import zipfile
from html import escape
from pathlib import Path
from typing import Dict, Any


def build_book_site(book: Dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "book.json").write_text(
        json.dumps(book, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    pages_html = []

    pages_html.append(
        f"""
        <article class="page is-active">
          <section class="cover-page">
            <img class="cover-image" src="{escape(book.get('cover_image', ''))}" alt="שער הספר" />
            <div class="cover-overlay">
              <div class="badge">שער</div>
              <h1>{escape(book.get('title', 'ספר ילדים'))}</h1>
              <p class="subtitle">{escape(book.get('subtitle', ''))}</p>
              <div class="cover-text">{escape(book.get('cover_text', ''))}</div>
            </div>
          </section>
        </article>
        """
    )

    for page in book.get("pages", []):
        n = page.get("page_number", "")
        text = page.get("final_text", "")
        image = page.get("image", "")
        pages_html.append(
            f"""
            <article class="page">
              <section class="story-page">
                <div class="image-wrap">
                  <img class="page-image" src="{escape(image)}" alt="איור לעמוד {escape(str(n))}" />
                </div>
                <div class="text-area">
                  <div class="badge">עמוד {escape(str(n))}</div>
                  <p>{escape(text)}</p>
                </div>
              </section>
            </article>
            """
        )

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(book.get('title', 'ספר ילדים'))}</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <main class="app">
    <section class="book-shell">
      <div class="book" id="book">{''.join(pages_html)}</div>
      <nav class="controls" aria-label="דפדוף">
        <button id="nextBtn" type="button">הבא</button>
        <div class="indicator">
          <span id="counter">שער</span>
          <div class="dots" id="dots"></div>
        </div>
        <button id="prevBtn" type="button">הקודם</button>
      </nav>
    </section>
  </main>
  <script src="script.js"></script>
</body>
</html>"""

    css = """*{box-sizing:border-box}
:root{--ratio:1055/1491;--ink:#2d1a3f;--muted:#6d5b7a;--purple:#7b43c6;--pink:#e84f9d;--paper:rgba(255,255,255,.94);--shadow:0 24px 70px rgba(57,28,88,.22)}
html,body{min-height:100%;margin:0}
body{font-family:Arial,'Noto Sans Hebrew',sans-serif;color:var(--ink);background:radial-gradient(circle at 12% 10%,rgba(255,255,255,.95) 0 16rem,transparent 28rem),linear-gradient(135deg,#fae7ff,#d9f7ff 58%,#fff4d8)}
button{font:inherit}.app{min-height:100svh;display:grid;place-items:center;padding:clamp(10px,2.4vw,28px)}.book-shell{width:min(100%,980px);display:grid;gap:clamp(10px,2vw,18px);justify-items:center}
.book{position:relative;width:min(94vw,680px,calc((100svh - 112px)*var(--ratio)));aspect-ratio:var(--ratio);perspective:1800px;filter:drop-shadow(var(--shadow))}
.page{position:absolute;inset:0;overflow:hidden;border-radius:30px;background:var(--paper);border:clamp(5px,1.2vw,10px) solid rgba(255,255,255,.96);box-shadow:inset 0 0 0 1px rgba(123,67,198,.14),0 18px 50px rgba(57,28,88,.17);opacity:0;transform:rotateY(-18deg) scale(.965);transform-origin:right center;pointer-events:none;transition:opacity .38s ease,transform .52s cubic-bezier(.18,.72,.2,1)}
.page.is-active{opacity:1;transform:rotateY(0) scale(1);pointer-events:auto;z-index:2}.page.is-leaving-forward{opacity:0;transform:rotateY(18deg) scale(.965)}.page.is-leaving-back{opacity:0;transform:rotateY(-18deg) scale(.965)}
.cover-page,.story-page{width:100%;height:100%;display:grid;align-content:center;padding:clamp(18px,4vw,30px)}
.cover-page{position:relative;overflow:hidden}.cover-image,.page-image{width:100%;height:100%;object-fit:cover;border-radius:24px;display:block}.cover-overlay{position:absolute;inset:auto 24px 24px 24px;display:grid;gap:12px;padding:18px;background:rgba(255,255,255,.75);backdrop-filter:blur(10px);border-radius:24px;text-align:center}
.badge{justify-self:center;padding:7px 16px;border-radius:999px;background:rgba(123,67,198,.13);color:#55258a;font-weight:900}.cover-overlay h1{margin:0;font-size:clamp(1.8rem,5vw,3.8rem);line-height:1.08}.subtitle{margin:0;color:var(--muted);font-size:clamp(1rem,2.3vw,1.35rem);line-height:1.45}.cover-text{font-size:clamp(1.05rem,2.5vw,1.55rem);line-height:1.55;font-weight:800}
.story-page{grid-template-rows:minmax(0,1.2fr) auto;gap:14px}.image-wrap{display:grid}.text-area{display:grid;gap:12px;padding:18px;border-radius:24px;background:rgba(255,255,255,.82)}.text-area p{margin:0;text-align:center;font-size:clamp(1.1rem,3vw,1.85rem);line-height:1.65;font-weight:750}
.controls{width:min(94vw,680px,calc((100svh - 112px)*var(--ratio)));display:grid;grid-template-columns:minmax(92px,1fr) auto minmax(92px,1fr);gap:12px;align-items:center}.controls button{min-height:48px;border:0;border-radius:999px;padding:11px 18px;background:linear-gradient(135deg,var(--pink),var(--purple));color:white;cursor:pointer;font-weight:900;box-shadow:0 10px 24px rgba(85,37,138,.24)}.controls button:disabled{opacity:.38;cursor:not-allowed;box-shadow:none}.indicator{display:grid;justify-items:center;gap:6px;min-width:86px}#counter{font-size:.88rem;font-weight:900;color:#55258a;background:rgba(255,255,255,.78);padding:4px 10px;border-radius:999px}.dots{display:flex;gap:7px;align-items:center;justify-content:center}.dot{width:8px;height:8px;border:0;border-radius:999px;padding:0;background:rgba(85,37,138,.24)}.dot.is-active{background:var(--purple);transform:scale(1.22)}
@media(max-width:720px){.book,.controls{width:min(96vw,calc((100svh - 96px)*var(--ratio)))}}
@media(max-width:420px){.app{padding:8px}.page{border-radius:22px}.book,.controls{width:min(97vw,calc((100svh - 90px)*var(--ratio)))}.controls button{min-height:44px;padding:9px 12px}.cover-overlay{inset:auto 14px 14px 14px;padding:14px}}
"""

    js = """const pages=Array.from(document.querySelectorAll('.page'));const prevBtn=document.getElementById('prevBtn');const nextBtn=document.getElementById('nextBtn');const counter=document.getElementById('counter');const dotsRoot=document.getElementById('dots');let current=0;
function createDots(){pages.forEach((_,i)=>{const d=document.createElement('button');d.className='dot';d.type='button';d.setAttribute('aria-label',i===0?'שער':`עמוד ${i}`);d.addEventListener('click',()=>showPage(i));dotsRoot.appendChild(d)})}
function update(){prevBtn.disabled=current===0;nextBtn.disabled=current===pages.length-1;counter.textContent=current===0?'שער':`עמוד ${current}`;Array.from(dotsRoot.children).forEach((d,i)=>d.classList.toggle('is-active',i===current))}
function showPage(next){if(next<0||next>=pages.length||next===current)return;const dir=next>current?'forward':'back';const prev=pages[current];const page=pages[next];prev.classList.remove('is-active');prev.classList.add(dir==='forward'?'is-leaving-forward':'is-leaving-back');page.classList.remove('is-leaving-forward','is-leaving-back');page.classList.add('is-active');current=next;update();setTimeout(()=>prev.classList.remove('is-leaving-forward','is-leaving-back'),540)}
function goNext(){showPage(current+1)}function goPrev(){showPage(current-1)}nextBtn.addEventListener('click',goNext);prevBtn.addEventListener('click',goPrev);document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')goNext();if(e.key==='ArrowRight')goPrev()});let sx=null,sy=null;document.addEventListener('touchstart',e=>{sx=e.changedTouches[0].clientX;sy=e.changedTouches[0].clientY},{passive:true});document.addEventListener('touchend',e=>{if(sx===null||sy===null)return;const dx=e.changedTouches[0].clientX-sx;const dy=e.changedTouches[0].clientY-sy;if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)){if(dx<0)goNext();else goPrev()}sx=null;sy=null},{passive:true});createDots();update();"""

    (output_dir / "index.html").write_text(html, encoding="utf-8")
    (output_dir / "style.css").write_text(css, encoding="utf-8")
    (output_dir / "script.js").write_text(js, encoding="utf-8")

    zip_path = output_dir / "storybook_html.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in output_dir.rglob("*"):
            if path.is_file() and path.name != "storybook_html.zip":
                zf.write(path, path.relative_to(output_dir))

    return zip_path
