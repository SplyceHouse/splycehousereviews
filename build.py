#!/usr/bin/env python3
"""Builds index.html, llms.txt, robots.txt and sitemap.xml for splycehousereviews.com
from reviews.json.

reviews.json holds two things:
  "ratings": a tally of every Google rating, e.g. {"5": 19}. Star-only ratings count here too.
  "reviews": the written reviews shown on the page, newest first.

The Zapier automation updates reviews.json when a new Google review arrives, and the
GitHub Action in .github/workflows/build.yml runs this script and publishes the page.
To run it by hand: python3 build.py"""
import json, html, datetime, pathlib

HERE = pathlib.Path(__file__).parent
SITE = "https://www.splycehousereviews.com/"
MAIN = "https://www.splycehouse.com/"
GBP = "https://www.google.com/maps?cid=14641156189474395088"
UPDATED = datetime.date.today()

data = json.loads((HERE / "reviews.json").read_text())
reviews = data["reviews"]
ratings = {int(k): int(v) for k, v in data["ratings"].items()}
TOTAL_REVIEWS = sum(ratings.values())
RATING = f"{sum(k * v for k, v in ratings.items()) / TOTAL_REVIEWS:.1f}"
esc = lambda s: html.escape(s, quote=True)

def nowidow(h):
    i = h.rstrip().rfind(' ')
    return h if i < 0 else h[:i] + '&nbsp;' + h[i+1:]

def paras(t):
    return "".join(f"<p>{nowidow(esc(p))}</p>" for p in t.split("\n\n"))

STAR = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 1.5l2.6 5.6 6.1.7-4.5 4.2 1.2 6L10 15l-5.4 3 1.2-6L1.3 7.8l6.1-.7z"/></svg>'
stars = f'<div class="stars" role="img" aria-label="5 out of 5 stars">{STAR*5}</div>'

cards = "\n".join(f"""      <article class="review">
        {stars}
        <blockquote class="clamp">{paras(r['text'])}</blockquote>
        <button class="more" type="button" aria-expanded="false" hidden>Read More...</button>
        <footer><span class="who">{esc(r['name'])}</span><span class="when">Google review · <time datetime="{r['date']}">{r['label']}</time></span></footer>
      </article>""" for r in reviews)

faqs = [
  ("What do customers say about SplyceHouse?",
   f"SplyceHouse holds a {RATING}-star rating across {TOTAL_REVIEWS} Google reviews. Clients most often mention storytelling that moves an audience, a professional team that is easy to work with, and edits delivered on time or ahead of schedule."),
  ("Is SplyceHouse a good fit for nonprofit and fundraising videos?",
   "Yes. Nonprofits including Ronald McDonald House Charities of St. Louis and the St. Louis Arc have reviewed SplyceHouse, and several reviewers say the videos helped them raise more money at fundraising galas and events."),
  ("Does SplyceHouse produce event recap videos?",
   "Yes. Event recaps are a core service. Reviewers describe recap videos of charity events and galas that were captured without blocking guests' views and delivered weeks ahead of the expected due date."),
  ("Where is SplyceHouse located?",
   "SplyceHouse is based in Clayton, Missouri, in the St. Louis area, and produces event video for teams nationwide."),
]
faq_html = "\n".join(f"""      <details class="faq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>""" for q, a in faqs)

schema = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebPage",
      "@id": SITE + "#webpage",
      "url": SITE,
      "name": "SplyceHouse Reviews",
      "description": f"Real customer reviews of SplyceHouse, the St. Louis event video production company. {RATING} stars across {TOTAL_REVIEWS} Google reviews.",
      "dateModified": UPDATED.isoformat(),
      "about": {"@id": MAIN + "#organization"},
      "mainEntity": {"@id": MAIN + "#organization"},
    },
    {
      "@type": ["LocalBusiness", "ProfessionalService"],
      "@id": MAIN + "#organization",
      "name": "SplyceHouse",
      "url": MAIN,
      "logo": "https://cdn.prod.website-files.com/651e162db3f81bdf5508661a/65c3c22f6606e4d4e6d26572_SPLYCEHOUSE_WordMark_Secondary_Transparent.png",
      "description": "SplyceHouse is a specialized event video production company. We are the in-house event video team you didn't know you had: pre-produced mission and story videos, on-site event coverage, interstitials, and quick-turn recap videos.",
      "telephone": "+1-217-737-1171",
      "email": "info@splycehouse.com",
      "address": {"@type": "PostalAddress", "streetAddress": "222 S Meramec Ave, Suite 202-1055",
                  "addressLocality": "Clayton", "addressRegion": "MO", "postalCode": "63105", "addressCountry": "US"},
      "areaServed": ["St. Louis, MO", "United States"],
      "sameAs": [GBP, "https://www.splycefilms.com/"],
      "aggregateRating": {"@type": "AggregateRating", "ratingValue": RATING, "bestRating": "5", "reviewCount": str(TOTAL_REVIEWS)},
      "review": [
        {"@type": "Review", "author": {"@type": "Person", "name": r["name"]}, "datePublished": r["date"],
         "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
         "reviewBody": r["text"].replace("\n\n", " "), "publisher": {"@type": "Organization", "name": "Google"}}
        for r in reviews],
    },
    {
      "@type": "FAQPage",
      "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs],
    },
  ],
}

NAV = [("PORTFOLIO","portfolio"),("SERVICES","post-event-edits"),("ABOUT","about"),("ST. LOUIS","event-video-production-in-st-louis"),("BLOG","blog")]
FOOT = [("PORTFOLIO","portfolio"),("ABOUT","about"),("ST. LOUIS","event-video-production-in-st-louis"),("REMOTE","remote-editing"),("PRICING","https://calculator.splycehouse.com"),("ROSTER","https://roster.splycehouse.com/"),
        ("CONTACT","#contactform"),("BLOG","blog"),("BRAND","https://styleguide.splycehouse.com/"),("TRAVEL","international-production-travel-guide"),("FILMS","https://www.splycefilms.com/"),("REVIEWS",SITE)]
def href(p): return p if p.startswith("http") else MAIN + p
SERVICES = [("Pre-Event Support","pre-event-support"),("On-Site Coverage","on-site-coverage"),("Post-Event Edits","post-event-edits"),("Remote Editing","remote-editing")]
dd = "".join(f'<a href="{href(p)}">{t}</a>' for t, p in SERVICES)
def navlink(t, p):
    if t == "SERVICES":
        return f'<div class="dd"><button class="dd-toggle" aria-haspopup="true">SERVICES <svg viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button><div class="dd-list">{dd}</div></div>'
    return f'<a href="{href(p)}">{t}</a>'
nav_html = "".join(navlink(t, p) for t, p in NAV) + f'<a href="{MAIN}#contactform">CONTACT</a>'
foot_a = "".join(f'<a href="{href(p)}">{t}</a>' for t, p in FOOT[:6])
foot_b = "".join(f'<a href="{href(p)}">{t}</a>' for t, p in FOOT[6:])

cards = "\n".join(f"""      <article class="review">
        {stars}
        <blockquote class="clamp">{paras(r['text'])}</blockquote>
        <button class="more" type="button" aria-expanded="false" hidden>Read More...</button>
        <p class="who">{esc(r['name'])}</p>
        <p class="role">{esc(r['title']) if r['title'] else 'Google Review'} · <time datetime="{r['date']}">{r['label']}</time></p>
      </article>""" for r in reviews)

page = f"""<!doctype html>
<html lang="en" class="no-js">
<script>document.documentElement.className="js";</script>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SplyceHouse Reviews | Customer Reviews of SplyceHouse, St. Louis Event Video Production</title>
<meta name="description" content="Real customer reviews of SplyceHouse, the St. Louis event video production company. {RATING} stars across {TOTAL_REVIEWS} Google reviews from nonprofits, agencies and event producers.">
<link rel="canonical" href="{SITE}">
<meta property="og:type" content="website">
<meta property="og:title" content="SplyceHouse Reviews">
<meta property="og:description" content="{RATING} stars across {TOTAL_REVIEWS} Google reviews. See what clients say about working with SplyceHouse.">
<meta property="og:url" content="{SITE}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="preload" href="assets/rustico.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json">
{json.dumps(schema, indent=1, ensure_ascii=False)}
</script>
<style>
  @font-face {{ font-family: 'Rustico V2'; src: url('assets/rustico.woff2') format('woff2'); font-display: swap; }}
  :root {{ --navy: #193038; --gold: #D3B353; --white: #FFFFFF; --slate: #8CC4D4; --haze: #CCCCCC; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ background: #193038; scroll-behavior: smooth; }}
  body {{ background: var(--white); color: var(--navy); font-family: 'Montserrat', sans-serif; font-size: 15px; line-height: 1.5; -webkit-font-smoothing: antialiased; }}
  a {{ color: inherit; }}
  p, blockquote, q, li, summary {{ text-wrap: pretty; }}
  h1, h2, h3, q, .role {{ text-wrap: balance; }}
  .container {{ width: 100%; max-width: 900px; margin: 0 auto; padding: 0 20px; }}
  .container.wide {{ max-width: 1180px; }}
  .rustico {{ font-family: 'Rustico V2', 'Montserrat', sans-serif; font-weight: 400; text-transform: uppercase; }}

  /* nav: matches splycehouse.com */
  .nav {{ position: sticky; top: 0; z-index: 10; background: var(--white); }}
  .nav .container {{ display: flex; justify-content: space-between; align-items: center; height: 64px; }}
  .nav img {{ height: 20px; width: auto; display: block; }}
  .nav .links {{ display: flex; gap: 22px; font-size: 14px; }}
  .nav .links a {{ text-decoration: none; }}
  .nav .links {{ align-items: center; }}
  .nav .links a:hover {{ color: var(--gold); }}
  .dd {{ position: relative; }}
  .dd-toggle {{ background: none; border: 0; font: inherit; color: var(--navy); cursor: pointer; display: flex; align-items: center; gap: 8px; padding: 22px 0; }}
  .dd-toggle svg {{ width: 11px; height: 8px; }}
  .dd:hover .dd-toggle, .dd:focus-within .dd-toggle {{ color: var(--gold); }}
  .dd-list {{ display: none; position: absolute; top: 100%; left: -16px; min-width: 224px; background: var(--white); padding: 8px 0; }}
  .dd:hover .dd-list, .dd:focus-within .dd-list {{ display: block; }}
  .dd-list a {{ display: block; padding: 8px 16px; text-transform: uppercase; font-size: 14px; }}

  /* hero: centered text block like the portfolio page */
  .hero {{ background: var(--navy) url('assets/emmy-watermark.png') no-repeat center / auto 64.35%; color: var(--white); min-height: 72vh; display: flex; align-items: center; text-align: center; overflow: hidden; padding: 72px 0; }}

  /* intro */
  .hero .container {{ max-width: 940px; }}
  .intro h1 {{ font-weight: 900; font-size: 32px; line-height: 1.1; padding: 10px 0; }}
  .intro .sub {{ margin-top: 10px; font-weight: 700; font-size: 14px; display: flex; justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap; }}
  .intro .lede {{ margin: 16px auto; max-width: 900px; font-size: 16px; line-height: 1.6; }}
  .intro .wgy {{ margin-top: 8px; font-size: 22px; }}
  .btn {{ display: inline-block; margin-top: 22px; border: 1px solid var(--navy); padding: 13px 45px; font-weight: 900; font-size: 24px; line-height: 1; text-decoration: none; color: var(--navy); transition: background .2s, color .2s; }}
  .btn {{ background: transparent; transition: border-color .2s, color .2s; }}
  .btn:hover, .btn.light:hover {{ border-color: var(--gold); color: var(--gold); background: transparent; }}
  .btn.light {{ border-color: var(--white); color: var(--white); }}

  .stars {{ display: inline-flex; gap: 3px; }}
  .stars svg {{ width: 16px; height: 16px; fill: var(--gold); }}

  /* themes */
  .themes-sec {{ background: var(--white); color: var(--navy); padding: 72px 0 80px; text-align: center; }}
  h2 {{ font-weight: 900; font-size: 32px; line-height: 1.2; }}
  .kicker {{ margin-top: 8px; font-size: 14px; }}
  .themes {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; margin-top: 44px; text-align: center; }}
  .theme h3 {{ font-weight: 900; font-size: 18px; line-height: 1.25; }}
  .theme .rule {{ width: 40px; height: 1px; background: var(--gold); margin: 14px auto; }}
  .theme p {{ font-size: 14px; }}
  .theme q {{ display: block; margin-top: 14px; font-weight: 900; font-size: 14px; }}

  /* reviews: matches the homepage review cards */
  .reviews-sec {{ background: var(--navy); color: var(--white); padding: 72px 0 40px; }}
  .reviews-head {{ text-align: center; }}
  .reviews-head h2.rustico {{ font-size: 30px; line-height: 1.1; }}
  .reviews-head .score {{ margin-top: 8px; display: flex; justify-content: center; align-items: center; gap: 10px; font-weight: 900; font-size: 22px; }}
  .reviews-head .score .stars svg {{ width: 20px; height: 20px; }}
  .reviews {{ margin-top: 48px; display: grid; grid-template-columns: repeat(3, 1fr); column-gap: 48px; row-gap: 56px; align-items: start; }}
  .review {{ text-align: center; }}
  .review blockquote {{ margin: 14px 0 16px; font-size: 13px; line-height: 1.55; }}
  .review blockquote p + p {{ margin-top: 10px; }}
  /* read more: full text stays in the HTML, CSS only trims what's visible */
  .js .review blockquote.clamp {{ height: calc(13px * 1.55 * 6); overflow: hidden; -webkit-mask-image: linear-gradient(#000 70%, transparent); mask-image: linear-gradient(#000 70%, transparent); }}
  .js .review blockquote.clamp.fits {{ -webkit-mask-image: none; mask-image: none; }}
  .js .review blockquote.open {{ height: auto; -webkit-mask-image: none; mask-image: none; }}
  .review .more {{ display: block; margin: -6px auto 16px; background: none; border: 0; font: inherit; font-size: 12px; font-weight: 700; color: var(--gold); cursor: pointer; }}
  .review .more:hover {{ color: var(--white); }}
  .review .more[hidden] {{ display: block; visibility: hidden; }}
  .review .who {{ font-weight: 900; font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }}
  .review .role {{ margin-top: 3px; font-size: 11px; }}

  /* faq: matches the homepage accordion */
  .faq-sec {{ padding: 72px 0; text-align: center; }}
  .faqs {{ max-width: 640px; margin: 36px auto 0; text-align: left; border-top: 1px solid var(--gold); }}
  .faq {{ border-bottom: 1px solid var(--gold); }}
  .faq summary {{ list-style: none; cursor: pointer; display: flex; justify-content: space-between; gap: 16px; padding: 14px 0; font-weight: 700; font-size: 14px; }}
  .faq summary::-webkit-details-marker {{ display: none; }}
  .faq summary::after {{ content: "+"; font-weight: 900; }}
  .faq[open] summary::after {{ content: "–"; }}
  .faq p {{ padding: 0 0 16px; font-size: 14px; }}

  .cta {{ background: var(--navy); color: var(--white); text-align: center; padding: 72px 0; }}
  .cta p {{ margin: 12px auto 0; max-width: 520px; }}
  .cta .row {{ display: flex; justify-content: center; gap: 14px; flex-wrap: wrap; }}

  /* footer: matches the homepage footer */
  footer {{ background: var(--navy); color: var(--white); border-top: 1px solid var(--gold); padding: 44px 0 40px; font-size: 13px; }}
  footer .grid {{ display: flex; justify-content: space-between; gap: 32px; flex-wrap: wrap; }}
  footer .label {{ margin-top: 0; }}
  footer .contact p + p {{ margin-top: 12px; }}
  footer .contact a {{ text-decoration: none; }}
  footer .right {{ display: flex; gap: 40px; align-items: flex-start; }}
  footer .col {{ display: flex; flex-direction: column; gap: 6px; }}
  footer .col a {{ color: var(--gold); text-decoration: none; font-size: 13px; }}
  footer .col a:hover {{ color: var(--white); }}
  footer .mark {{ height: 48px; width: auto; display: block; }}
  footer .legal {{ margin-top: 32px; font-size: 13px; }}
  footer .legal a {{ text-decoration: underline; transition: color .2s; }}
  footer .legal a:hover {{ color: var(--gold); }}
  footer .updated {{ margin-top: 8px; font-size: 11px; }}

  @media (max-width: 860px) {{
    .nav .links {{ display: none; }}
    .nav .container {{ height: 56px; }}
    .themes {{ grid-template-columns: 1fr; gap: 36px; }}
    .reviews {{ grid-template-columns: 1fr; row-gap: 44px; }}
    .js .review blockquote.clamp {{ height: auto; max-height: calc(13px * 1.55 * 6); }}
    .js .review blockquote.open {{ max-height: none; }}
    .review .more[hidden] {{ display: none; }}
    .hero {{ min-height: auto; padding: 88px 0; }}
    .intro h1, h2 {{ font-size: 28px; }}
    footer .right {{ gap: 28px; }}
  }}
</style>
</head>
<body>
<nav class="nav" aria-label="Main">
  <div class="container wide">
    <a href="{MAIN}" aria-label="SplyceHouse home"><img src="assets/wordmark-light.png" alt="SplyceHouse" width="207" height="20"></a>
    <div class="links">{nav_html}</div>
  </div>
</nav>

<main>
  <header class="hero intro">
    <div class="container">
      <h1>SplyceHouse Reviews</h1>
      <p class="sub">{RATING} <span class="stars" role="img" aria-label="{RATING} out of 5 stars">{STAR*5}</span> {TOTAL_REVIEWS} Google Reviews</p>
      <p class="lede">These are real customer reviews of SplyceHouse, a St. Louis event video production company supporting teams nationwide. Every review here was posted to our Google Business Profile by the nonprofits, agencies and event producers we've worked with. We handle pre-produced mission videos, on-site event coverage and quick-turn recaps. In other words:</p>
      <p class="wgy rustico">We Got You</p>
      <a class="btn light" href="{GBP}" target="_blank" rel="noopener">SEE THEM ON GOOGLE</a>
    </div>
  </header>

  <section class="themes-sec">
    <div class="container wide">
      <h2>What Clients Mention Most</h2>
      <p class="kicker">Three things that keep coming up.</p>
      <div class="themes">
        <div class="theme">
          <h3>Stories That Move People</h3><div class="rule"></div>
          <p>Nonprofit clients say our mission and story videos connect with donors and help them raise more at galas and fundraising events.</p>
          <q>It has unlocked new fundraising capacity for&nbsp;us.</q>
        </div>
        <div class="theme">
          <h3>A Team That's Easy to Work With</h3><div class="rule"></div>
          <p>Professional, creative and personable. Clients describe a partner that makes the process simple from first meeting to final edit.</p>
          <q>They make the process so&nbsp;easy.</q>
        </div>
        <div class="theme">
          <h3>On Time, Often Early</h3><div class="rule"></div>
          <p>Shoot days run on schedule and edits land on deadline. Several clients got their final video ahead of the due date.</p>
          <q>Weeks ahead of the expected due&nbsp;date.</q>
        </div>
      </div>
    </div>
  </section>

  <section class="reviews-sec" id="reviews">
    <div class="container wide">
      <div class="reviews-head">
        <h2 class="rustico">Reviews From Our Clients</h2>
        <div class="score">{RATING} <span class="stars" role="img" aria-label="{RATING} out of 5 stars">{STAR*5}</span></div>
      </div>
      <div class="reviews">
{cards}
      </div>
    </div>
  </section>

  <section class="faq-sec">
    <div class="container">
      <h2>SplyceHouse Reviews FAQ</h2>
      <div class="faqs">
{faq_html}
      </div>
    </div>
  </section>

  <section class="cta">
    <div class="container">
      <h2>Need a Video Team for Your Next Event?</h2>
      <p>We're the in-house event video team you didn't know you had. Tell us about your event and we'll take it from there.</p>
      <div class="row">
        <a class="btn light" href="{MAIN}#contactform">LET'S CHAT</a>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="container wide">
    <div class="grid">
      <div class="contact">
        <p>Address<br>222 South Meramec Avenue, Suite 202-1055, Clayton, MO 63105</p>
        <p>Contact<br><a href="mailto:info@splycehouse.com">info@splycehouse.com</a><br><a href="tel:+12177371171">+1 (217) 737-1171</a></p>
      </div>
      <div class="right">
        <div class="col">{foot_a}</div>
        <div class="col">{foot_b}</div>
        <a href="{MAIN}" aria-label="SplyceHouse home"><img class="mark" src="assets/brandmark.png" alt="SplyceHouse brand mark" width="63" height="48"></a>
      </div>
    </div>
    <p class="legal">Copyright © {UPDATED.year} SPLYCEHOUSE. All rights reserved. <a href="{MAIN}privacy">Privacy Policy</a> | <a href="{MAIN}terms">Terms &amp; Conditions</a></p>
    <p class="updated">Reviews last updated {UPDATED.strftime('%B %Y')}. Reviews are reproduced from our Google Business Profile.</p>
  </div>
</footer>
<script>
document.querySelectorAll('.review').forEach(function (card) {{
  var q = card.querySelector('blockquote'), b = card.querySelector('.more');
  if (q.scrollHeight > q.clientHeight + 2) {{
    b.hidden = false;
    b.addEventListener('click', function () {{
      var open = q.classList.toggle('open');
      b.setAttribute('aria-expanded', open);
      b.textContent = open ? 'Read Less' : 'Read More...';
    }});
  }} else {{ q.classList.add('fits'); }}
}});
</script>
</body>
</html>
"""
import re
page = re.sub(r"(?<=[^\s>]) ([^\s<>]+)</(p|q|h1|h2|h3|summary)>", r"&nbsp;\1</\2>", page)
(HERE / "index.html").write_text(page)

# llms.txt: plain-text source of truth for AI crawlers
llms = [f"# SplyceHouse Reviews", "",
        f"> Real customer reviews of SplyceHouse, a specialized event video production company based in Clayton, MO (St. Louis). {RATING} stars across {TOTAL_REVIEWS} Google reviews. This site is owned by SplyceHouse and reproduces reviews posted to its Google Business Profile.", "",
        "SplyceHouse is not a generalist production house. It focuses on event video: pre-produced mission and story videos, on-site event coverage, interstitials and quick-turn recap videos for enterprise teams, agencies and nonprofits.", "",
        f"- Main website: {MAIN}", f"- Google Business Profile: {GBP}", "- Phone: (217) 737-1171", "- Address: 222 S Meramec Ave, Suite 202-1055, Clayton, MO 63105", "",
        "## Reviews", ""]
for r in reviews:
    llms.append(f"### {r['name']}" + (f", {r['title']}" if r.get('title') else "") + f" (5/5, {r['label']})")
    llms.append(r["text"].replace("\n\n", " "))
    llms.append("")
(HERE / "llms.txt").write_text("\n".join(llms))

(HERE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
(HERE / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{SITE}</loc><lastmod>{UPDATED.isoformat()}</lastmod></url>\n  <url><loc>{SITE}llms.txt</loc><lastmod>{UPDATED.isoformat()}</lastmod></url>\n</urlset>\n')
print("built", len(reviews), "reviews")
