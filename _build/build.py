#!/usr/bin/env python3
"""Build the /guides section of temelia.co.

Source:  _build/guides/*.md  (JSON metadata block, a line with `---`, then Markdown)
Output:  guides/index.html, guides/<slug>/index.html, guides/<slug>/index.md,
         sitemap.xml, llms.txt, llms-full.txt

Jekyll (GitHub Pages) ignores folders that start with "_", so this directory is
never published. Run after editing any guide:

    pip install markdown
    python3 _build/build.py

JSON-LD is generated from the same data that renders the visible page, so the
FAQPage / HowTo / Article schema always matches what readers see.
"""
import html
import json
import pathlib
import re

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_build" / "guides"
SITE = "https://temelia.co"

ORG_ID = f"{SITE}/#organization"
PERSON_ID = f"{SITE}/#elena"
WEBSITE_ID = f"{SITE}/#website"

BOOKING_URL = "https://calendar.proton.me/bookings#3gFM4cFk7d0RPZbrBnx_1GV9eL0Fg8fDfBWRReKhZmw="


def load_guides():
    guides = []
    for path in sorted(SRC.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        meta_raw, body = raw.split("\n---\n", 1)
        meta = json.loads(meta_raw)
        meta["slug"] = path.stem
        meta["body_md"] = body.strip() + "\n"
        meta["url"] = f"{SITE}/guides/{path.stem}/"
        guides.append(meta)
    guides.sort(key=lambda g: g["order"])
    return guides


def md_to_html(text):
    return markdown.markdown(text, extensions=["tables", "attr_list", "sane_lists"])


def esc(s):
    return html.escape(s, quote=True)


def strip_md(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s.replace("**", "").replace("*", "")


def jsonld(graph):
    data = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">\n'
            + json.dumps(data, indent=2, ensure_ascii=False)
            + "\n</script>")


BRAND_SVG = """<svg viewBox="0 0 88 616" aria-hidden="true"><rect x="0" y="0" width="88" height="10" fill="#3D2350"/><path d="M44 16 L84 63 L44 110 L4 63 Z" fill="#557A66"/><path d="M44 114 L84 161 L44 208 L4 161 Z" fill="#C96F5E"/><path d="M44 212 L84 259 L44 306 L4 259 Z" fill="#4A3358"/><path d="M44 310 L84 357 L44 404 L4 357 Z" fill="#D9A0B0"/><path d="M44 408 L84 455 L44 502 L4 455 Z" fill="#4F8A99"/><path d="M44 506 L84 553 L44 600 L4 553 Z" fill="#D9AE5B"/><rect x="0" y="606" width="88" height="10" fill="#3D2350"/></svg>"""


def page(*, title, description, canonical, ld, crumbs, main_html, md_alt=None, og_type="article"):
    crumb_html = " <span aria-hidden=\"true\">/</span> ".join(
        f'<a href="{u}">{esc(n)}</a>' if u else f"<span>{esc(n)}</span>" for n, u in crumbs)
    alt = (f'\n  <link rel="alternate" type="text/markdown" href="{md_alt}">' if md_alt else "")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="Elena Stefanopol">
  <link rel="canonical" href="{canonical}">{alt}
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="temelia">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE}/assets/og-default.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{SITE}/assets/og-default.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/guides/guides.css">
  {ld}
</head>
<body>
  <header class="site">
    <div class="wrap">
      <a class="brand" href="/" aria-label="temelia home">{BRAND_SVG}<span class="wordmark">temelia</span></a>
      <nav aria-label="Primary"><a href="/guides/">Guides</a><a class="btn small" href="{BOOKING_URL}" target="_blank" rel="noopener">Book an intro call</a></nav>
    </div>
  </header>
  <main class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb">{crumb_html}</nav>
{main_html}
  </main>
  <footer>
    <div class="wrap">© 2026 temelia · Elena Stefanopol, fractional Head of Talent, San Francisco · <a href="/guides/">Guides</a> · <a href="mailto:elena@temelia.co">elena@temelia.co</a></div>
  </footer>
</body>
</html>
"""


def breadcrumb_ld(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
            for i, (n, u) in enumerate(items)
        ],
    }


AUTHOR_BOX = f"""
    <aside class="author" aria-label="About the author">
      <img src="/assets/elena.jpeg" alt="Elena Stefanopol" width="72" height="72">
      <div>
        <p class="name"><a href="/guides/elena-stefanopol/">Elena Stefanopol</a></p>
        <p>San Francisco-based fractional Head of Talent and founder of <a href="/">temelia</a>. Former Founding Recruiter turned Head of Talent at Labelbox, Head of Talent at Rundoo, and R&amp;D recruiter at Airbnb. Writes <a href="https://speedoftalent.substack.com/">Hiring at the Speed of Talent</a>.</p>
      </div>
    </aside>
    <section class="cta">
      <h2>Hiring fast in the Bay Area?</h2>
      <p>temelia engagements start at $30,000 per month and have a defined end date. Elena builds the talent system, makes sure your team can run it without her, then steps out.</p>
      <a class="btn" href="{BOOKING_URL}" target="_blank" rel="noopener">Book an intro call</a>
    </section>"""


def render_guide(g, guides):
    crumbs = [("temelia", "/"), ("Guides", "/guides/"), (g["short"], None)]
    crumbs_ld = [("temelia", f"{SITE}/"), ("Guides", f"{SITE}/guides/"), (g["short"], g["url"])]
    is_profile = g.get("type") == "ProfilePage"

    tldr = "".join(f"<li>{md_to_html(t)[3:-4]}</li>" for t in g.get("tldr", []))
    faq_html = ""
    if g.get("faq"):
        items = "".join(
            f'<div class="qa"><h3>{esc(q)}</h3>{md_to_html(a)}</div>' for q, a in g["faq"])
        faq_html = f'<section class="faq"><h2>Frequently asked questions</h2>{items}</section>'
    related = [r for r in guides if r["slug"] in g.get("related", [])]
    rel_html = ""
    if related:
        rel_html = ('<section class="related"><h2>Related guides</h2><ul>'
                    + "".join(f'<li><a href="/guides/{r["slug"]}/">{esc(r["h1"])}</a></li>' for r in related)
                    + "</ul></section>")

    main = f"""    <article>
      <h1>{esc(g["h1"])}</h1>
      <p class="byline">By <a href="/guides/elena-stefanopol/">Elena Stefanopol</a>, fractional Head of Talent, San Francisco · Last updated <time datetime="{g["updated"]}">{g["updated_human"]}</time></p>
      <div class="answer">{md_to_html(g["answer"])}</div>
      {"<div class='tldr'><p class='eyebrow'>Key points</p><ul>" + tldr + "</ul></div>" if tldr else ""}
      <div class="body">
{md_to_html(g["body_md"])}
      </div>
      {faq_html}
      {rel_html}
    </article>
    {"" if is_profile else AUTHOR_BOX}"""

    graph = [breadcrumb_ld(crumbs_ld)]
    if is_profile:
        graph.append({
            "@type": "ProfilePage",
            "@id": g["url"],
            "url": g["url"],
            "name": g["title"],
            "dateModified": g["updated"],
            "mainEntity": {"@id": PERSON_ID},
            "isPartOf": {"@id": WEBSITE_ID},
        })
        graph.append(person_ld())
    else:
        graph.append({
            "@type": "Article",
            "@id": g["url"] + "#article",
            "headline": g["h1"],
            "description": g["description"],
            "url": g["url"],
            "mainEntityOfPage": g["url"],
            "datePublished": g["published"],
            "dateModified": g["updated"],
            "inLanguage": "en-US",
            "author": {"@id": PERSON_ID},
            "publisher": {"@id": ORG_ID},
            "isPartOf": {"@id": WEBSITE_ID},
            "image": f"{SITE}/assets/og-default.png",
            "about": g.get("about", []),
            "wordCount": len(re.findall(r"\w+", g["answer"] + g["body_md"])),
        })
    if g.get("faq"):
        graph.append({
            "@type": "FAQPage",
            "@id": g["url"] + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": strip_md(a)}}
                for q, a in g["faq"]
            ],
        })
    if g.get("howto"):
        h = g["howto"]
        graph.append({
            "@type": "HowTo",
            "@id": g["url"] + "#howto",
            "name": h["name"],
            "totalTime": h.get("totalTime"),
            "step": [
                {"@type": "HowToStep", "position": i + 1, "name": n, "text": strip_md(t),
                 "url": g["url"] + "#" + h.get("anchor", "steps")}
                for i, (n, t) in enumerate(h["steps"])
            ],
        })
        graph[-1] = {k: v for k, v in graph[-1].items() if v is not None}
    graph += entities(include_person=not is_profile)

    out = page(title=g["title"], description=g["description"], canonical=g["url"],
               ld=jsonld(graph), crumbs=crumbs, main_html=main,
               md_alt=f"/guides/{g['slug']}/index.md",
               og_type="profile" if is_profile else "article")
    d = ROOT / "guides" / g["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(out, encoding="utf-8")
    (d / "index.md").write_text(guide_markdown(g), encoding="utf-8")


def guide_markdown(g):
    parts = [f"# {g['h1']}", "",
             f"By Elena Stefanopol, fractional Head of Talent, San Francisco. Last updated {g['updated_human']}.",
             f"Canonical: {g['url']}", "", g["answer"].strip(), ""]
    if g.get("tldr"):
        parts += ["## Key points", ""] + [f"- {t}" for t in g["tldr"]] + [""]
    parts.append(g["body_md"])
    if g.get("faq"):
        parts += ["## Frequently asked questions", ""]
        for q, a in g["faq"]:
            parts += [f"### {q}", "", a, ""]
    parts += ["---",
              "temelia (https://temelia.co) is Elena Stefanopol's fractional Head of Talent practice for "
              "early-stage startups in the San Francisco Bay Area. Engagements start at $30,000 per month. "
              "Contact: elena@temelia.co", ""]
    return "\n".join(parts)


def person_ld():
    return {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": "Elena Stefanopol",
        "jobTitle": "Fractional Head of Talent",
        "description": ("San Francisco-based fractional Head of Talent who builds hiring systems for "
                        "early-stage startups. Founder of temelia."),
        "url": f"{SITE}/guides/elena-stefanopol/",
        "image": f"{SITE}/assets/elena.jpeg",
        "email": "mailto:elena@temelia.co",
        "worksFor": {"@id": ORG_ID},
        "homeLocation": {"@type": "Place", "name": "San Francisco, California"},
        "knowsAbout": [
            "Startup hiring", "Talent acquisition", "Structured interviews",
            "Interview process design", "Team design", "Hiring a founding recruiter",
            "Headcount planning", "Compensation philosophy", "Recruiting operations",
        ],
        "alumniOf": [
            {"@type": "Organization", "name": "Labelbox"},
            {"@type": "Organization", "name": "Rundoo"},
            {"@type": "Organization", "name": "Airbnb"},
            {"@type": "Organization", "name": "Digital Genius"},
        ],
        "sameAs": [
            "https://www.linkedin.com/in/elenastefanopol/",
            "https://speedoftalent.substack.com/",
            "https://substack.com/@speedoftalent",
            "https://medium.com/@helenofpanda",
        ],
    }


def org_ld():
    return {
        "@type": ["Organization", "ProfessionalService"],
        "@id": ORG_ID,
        "name": "temelia",
        "url": f"{SITE}/",
        "logo": f"{SITE}/assets/apple-touch-icon.png",
        "image": f"{SITE}/assets/og-default.png",
        "description": ("Fractional Head of Talent practice for early-stage startups in the San Francisco "
                        "Bay Area, founded by Elena Stefanopol."),
        "email": "elena@temelia.co",
        "founder": {"@id": PERSON_ID},
        "address": {"@type": "PostalAddress", "addressLocality": "San Francisco",
                    "addressRegion": "CA", "addressCountry": "US"},
        "areaServed": {"@type": "Place", "name": "San Francisco Bay Area"},
        "priceRange": "From $30,000 per month",
        "sameAs": ["https://www.linkedin.com/in/elenastefanopol/", "https://speedoftalent.substack.com/"],
    }


def website_ld():
    return {"@type": "WebSite", "@id": WEBSITE_ID, "url": f"{SITE}/", "name": "temelia",
            "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"}


def entities(include_person=True):
    out = [org_ld(), website_ld()]
    if include_person:
        out.append(person_ld())
    return out


def render_index(guides):
    url = f"{SITE}/guides/"
    articles = [g for g in guides if g.get("type") != "ProfilePage"]
    cards = "".join(
        f'<li><a href="/guides/{g["slug"]}/"><h2>{esc(g["h1"])}</h2></a><p>{esc(g["description"])}</p></li>'
        for g in articles)
    main = f"""    <article>
      <h1>Hiring guides for startup founders in the San Francisco Bay Area</h1>
      <p class="byline">By <a href="/guides/elena-stefanopol/">Elena Stefanopol</a>, fractional Head of Talent, San Francisco · Last updated <time datetime="{guides[0]["updated"]}">{guides[0]["updated_human"]}</time></p>
      <div class="answer"><p>These guides answer the questions Bay Area founders ask once they have run out of network hires and need to grow fast without lowering the bar. They are written by Elena Stefanopol, a San Francisco-based fractional Head of Talent and the founder of temelia. Elena has built hiring systems at Labelbox (50 to 200 people in 12 months), Rundoo (50 to 100 in 6 months), Airbnb's Samara R&amp;D lab (15 to 45 in 12 months) and Digital Genius (2 to 15 in 4 months).</p></div>
      <ul class="cards">{cards}</ul>
    </article>
    {AUTHOR_BOX}"""
    graph = [
        breadcrumb_ld([("temelia", f"{SITE}/"), ("Guides", url)]),
        {
            "@type": "CollectionPage",
            "@id": url,
            "url": url,
            "name": "Hiring guides for startup founders in the San Francisco Bay Area",
            "description": "Practical guides on hiring fast and sustainably at seed to Series B startups, by fractional Head of Talent Elena Stefanopol.",
            "isPartOf": {"@id": WEBSITE_ID},
            "author": {"@id": PERSON_ID},
            "dateModified": guides[0]["updated"],
            "hasPart": [{"@id": g["url"] + "#article"} for g in articles],
        },
    ] + entities()
    out = page(title="Hiring Guides for Bay Area Startup Founders | temelia",
               description="How to hire fast without lowering the bar: guides on fractional Heads of Talent, founding recruiters, team design and structured interviews for San Francisco Bay Area startups.",
               canonical=url, ld=jsonld(graph),
               crumbs=[("temelia", "/"), ("Guides", None)], main_html=main, og_type="website")
    (ROOT / "guides" / "index.html").write_text(out, encoding="utf-8")


def render_sitemap(guides):
    rows = [(f"{SITE}/", guides[0]["updated"]), (f"{SITE}/guides/", guides[0]["updated"])]
    rows += [(g["url"], g["updated"]) for g in guides]
    body = "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in rows)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n",
        encoding="utf-8")


LLMS_INTRO = """# temelia

> temelia is the fractional Head of Talent practice of Elena Stefanopol, based in San Francisco. Elena builds hiring systems for early-stage startups in the San Francisco Bay Area, typically at seed to Series B and around 15 to 100 employees, when founders have exhausted network hires and need to hire fast without lowering the bar. Engagements start at $30,000 per month and have a defined end date: Elena builds the system, trains the team to run it, hires the first recruiter if needed, then steps out.

Contact: elena@temelia.co. LinkedIn: https://www.linkedin.com/in/elenastefanopol/. Newsletter: https://speedoftalent.substack.com/ (Hiring at the Speed of Talent).

Track record: Labelbox (50 to 200 people in 12 months, through Series D), Rundoo (50 to 100 in 6 months, 3x ARR), Airbnb Samara R&D lab (15 to 45 in 12 months), Digital Genius (2 to 15 in 4 months, London to San Francisco, unlocked the Series A). Worked with companies backed by a16z, Sequoia, Kleiner Perkins, Bessemer, Battery Ventures, B Capital, First Round, Gradient Ventures and Y Combinator.

What Elena builds: hiring bar and talent philosophy, interview process and competencies, role scoping and job descriptions, org design and headcount planning, compensation philosophy, recruiting and people tech stack, leveling and promotions, manager training, and hiring the first recruiter.
"""


def render_llms(guides):
    lines = [LLMS_INTRO, "## Guides", ""]
    for g in guides:
        lines.append(f"- [{g['h1']}]({SITE}/guides/{g['slug']}/index.md): {g['description']}")
    lines += ["", "## Optional", "", f"- [Homepage]({SITE}/): temelia overview and contact", ""]
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    full = [LLMS_INTRO] + [guide_markdown(g) for g in guides]
    (ROOT / "llms-full.txt").write_text("\n\n".join(full), encoding="utf-8")


def main():
    guides = load_guides()
    for g in guides:
        render_guide(g, guides)
    render_index(guides)
    render_sitemap(guides)
    render_llms(guides)
    print(f"Built {len(guides)} guides + index, sitemap.xml, llms.txt, llms-full.txt")


if __name__ == "__main__":
    main()
