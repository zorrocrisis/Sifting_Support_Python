"""
build_backup_page.py
---------------------
Generates backup_story.html: a single, self-contained, zero-dependency
HTML file (no external fonts, images, or scripts) showing the hardcoded
backup story from config.py.

This is the LAST-RESORT demo fallback -- for when you don't trust the
running Python process at all (frozen, crashed, whatever). Open the
generated file in a separate browser tab (or just double-click it --
it works via a plain file:// URL, no server needed) BEFORE you go on,
so it's already loaded and ready regardless of what happens to
main_demo.py during the demo.

Run this again any time you update config.BACKUP_STORY_* -- it's not
auto-synced, so regenerate the HTML after editing the story text.
"""

import config

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  :root {{
    --bg: #15130F;
    --ember: #E8A33D;
    --cream: #F2EDE4;
    --muted: #9C9484;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0;
    padding: 0;
    background: var(--bg);
    color: var(--cream);
    height: 100%;
  }}
  body {{
    font-family: Cambria, Georgia, "Times New Roman", serif;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 6vh 6vw;
  }}
  .page {{
    max-width: 760px;
    width: 100%;
  }}
  .eyebrow {{
    display: flex;
    align-items: center;
    margin-bottom: 2.2rem;
  }}
  .eyebrow .flame {{
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: var(--ember);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
    margin-right: 14px;
  }}
  .eyebrow .label {{
    font-family: Calibri, Arial, sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--ember);
    text-transform: uppercase;
  }}
  h1 {{
    font-size: 2.1rem;
    line-height: 1.25;
    margin: 0 0 1.6rem 0;
    color: var(--cream);
  }}
  .story p {{
    font-size: 1.15rem;
    line-height: 1.65;
    font-style: italic;
    margin: 0 0 1.2rem 0;
    color: var(--cream);
  }}
  .caption {{
    margin-top: 2.4rem;
    font-family: Calibri, Arial, sans-serif;
    font-size: 0.85rem;
    font-style: italic;
    color: var(--muted);
  }}
</style>
</head>
<body>
  <div class="page">
    <div class="eyebrow">
      <div class="flame">&#128293;</div>
      <div class="label">A story from the colony log</div>
    </div>
    <h1>{title}</h1>
    <div class="story">
      {body_html}
    </div>
    <div class="caption">{caption}</div>
  </div>
</body>
</html>
"""


def build():
    # Each blank-line-separated chunk of BACKUP_STORY_BODY becomes its
    # own <p> -- same paragraph structure as the in-app button and the
    # opening slide, so all three fallback surfaces stay visually
    # consistent once you drop in the real story text.
    paragraphs = [p.strip() for p in config.BACKUP_STORY_BODY.split("\n\n") if p.strip()]
    body_html = "\n      ".join(f"<p>{p}</p>" for p in paragraphs)

    html = HTML_TEMPLATE.format(
        title=config.BACKUP_STORY_TITLE,
        body_html=body_html,
        caption=config.BACKUP_STORY_CAPTION,
    )

    with open("backup_story.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Wrote backup_story.html")


if __name__ == "__main__":
    build()