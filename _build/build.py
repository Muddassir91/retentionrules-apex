#!/usr/bin/env python3
"""Builds retentionrules.com as plain HTML. Run: python3 _build/build.py

Edit copy in this file, run it, and every page plus the shared header and
footer update together. It also runs the Flesch-Kincaid copy gate per page.
"""
import html as htmllib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://retentionrules.com"
FLOWS = "https://flows.retentionrules.com/"
LETTERS = "https://letters.retentionrules.com/"
BOOK = "https://calendar.app.google/LEcHPfT7csau1WCQ7"
BOOK_COACH = "https://calendar.app.google/AQSuMFqLSSZbnqQTA"
FK_TOOL = ROOT.parent / "Content-Master/tools/fk_grade.py"


def btn(label, href):
    attrs = ' target="_blank" rel="noopener"' if "calendar.app.google" in href else ""
    return f'<a class="btn" href="{href}"{attrs}>{label}</a>'


def ps(*lines):
    return "".join(f"<p>{x}</p>" for x in lines)


def sec(body, cls=""):
    return f'<section class="sec {cls}"><div class="wrap">{body}</div></section>'


def mid(body, cls=""):
    return f'<section class="sec {cls}"><div class="mid prose">{body}</div></section>'


def head(label, h2, sub=""):
    s = f"<p>{sub}</p>" if sub else ""
    return f'<div class="head"><span class="label">{label}</span><h2>{h2}</h2>{s}</div>'


def hero(pill, h1, sub, cta="", trust=()):
    t = '<div class="trustline">' + "".join(f"<span>{x}</span>" for x in trust) + "</div>" if trust else ""
    return (f'<section class="hero"><div class="wrap"><p class="pill">{pill}</p><h1>{h1}</h1>'
            f'<p class="sub">{sub}</p>{cta}{t}</div></section>')


LOGOS = [("img", "passion-mark.png", "Passion.io"), ("img", "moonlamp-wordmark.png", "The Original Moon Lamp"),
         ("text", "", "Oshun"), ("text", "", "Psychic Sharma"),
         ("img", "javaburn-logo.png", "Java Burn"), ("img", "allfemme-black.png", "Allfemme")]


def logos():
    out = ""
    for kind, f, n in LOGOS:
        if f == "passion-mark.png":
            out += f'<span class="lg pass"><img src="/images/logos/{f}" alt="" loading="lazy">{n}</span>'
        elif kind == "img":
            cls = "lg multi" if "moonlamp" in f else "lg"
            out += f'<span class="{cls}"><img src="/images/logos/{f}" alt="{n}" loading="lazy"></span>'
        else:
            out += f'<span class="lg word">{n}</span>'
    return f'<div class="logos nocheck">{out}</div>'


def logostrip():
    return f'<section class="logostrip"><div class="wrap"><span class="label">Brands I have worked with</span>{logos()}</div></section>'


def stats(*items):
    return '<div class="stats">' + "".join(f'<div class="stat"><b>{a}</b><span>{b}</span></div>' for a, b in items) + "</div>"


def shot(img, alt, cap=""):
    c = f"<figcaption>{cap}</figcaption>" if cap else ""
    return f'<figure class="shot"><div class="frame"><img src="/images/proof/{img}" alt="{alt}" loading="lazy"></div>{c}</figure>'


def wall(*items, one=False):
    cls = "wall one" if one else "wall"
    return f'<div class="{cls}">' + "".join(shot(i, a) for i, a in items) + "</div>"


def wide(item):
    return f'<div class="wide">{shot(*item)}</div>'


def cards(*items, cols=""):
    out = "".join(
        f'<div class="card">{f"<span class=tag>{t}</span>" if t else ""}<h3>{h}</h3><p>{p}</p></div>'
        for t, h, p in items)
    return f'<div class="cards {cols}">{out}</div>'


def compare(old_title, old, new_title, new):
    li = lambda xs: "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    return (f'<div class="compare"><div class="col"><h3>{old_title}</h3>{li(old)}</div>'
            f'<div class="col good"><h3>{new_title}</h3>{li(new)}</div></div>')


def bars(title, rows, note=""):
    top = max(v for _, v, _ in rows)
    out = "".join(
        f'<div class="bar">{a}<i style="width:{max(round(v / top * 100), 26)}%">{t}</i></div>' for a, v, t in rows)
    n = f"<small>{note}</small>" if note else ""
    return f'<div class="chart"><h3>{title}</h3>{out}{n}</div>'


def timeline(*items):
    return '<div class="line">' + "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in items) + "</div>"


def faq(*items):
    out = ""
    for i, (q, a) in enumerate(items):
        out += f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>'
    return f'<div class="faq mid">{out}</div>'


def door(who, prob, go, href):
    return f'<a class="door" href="{href}"><span class="who">{who}</span><span class="prob">{prob}</span><span class="go">{go}</span></a>'


def doors():
    return '<div class="doors">' + door(
        "I run a SaaS", "Losing more than 5% of your customers to churn each month?", "Fix my churn", "/saas/"
    ) + door(
        "I run an ecommerce brand", "Email brings in less than 20% of your revenue?", "Grow my email revenue", FLOWS
    ) + door(
        "I'm a coach or expert", "Want more money from the subscribers you already have?", "Make money from my list", "/coaches/"
    ) + "</div>"


def case(href, pic, num, title, text, more="See the proof"):
    if pic.startswith("word:"):
        p = f'<div class="pic logo"><span class="lg word">{pic[5:]}</span></div>'
    elif pic.startswith("logo:"):
        p = f'<div class="pic logo multi"><img src="/images/logos/{pic[5:]}" alt="" loading="lazy"></div>'
    else:
        p = f'<div class="pic"><img src="/images/proof/{pic}" alt="" loading="lazy"></div>'
    inner = f'{p}<div class="txt"><b>{num}</b><h3>{title}</h3><p>{text}</p>'
    if href:
        return f'<a class="case" href="{href}">{inner}<span class="more">{more}</span></div></a>'
    return f'<div class="case">{inner}</div></div>'


def close(h2, text, button, fine=""):
    f = f'<p class="fine nocheck">{fine}</p>' if fine else ""
    return f'<section class="close"><div class="wrap"><h2>{h2}</h2><p>{text}</p>{button}{f}</div></section>'


NAV = [("SaaS", "/saas/"), ("Ecommerce", FLOWS), ("Coaches", "/coaches/"),
       ("Case Studies", "/case-studies/"), ("About", "/about/"), ("Newsletter", LETTERS)]


def header(path, book):
    links = "".join(
        f'<a href="{h}"{" aria-current=page" if h == path else ""}>{t}</a>' for t, h in NAV)
    button = btn("Book a call", book) if book else ""
    return f'''<header class="site-head"><div class="wrap head-row">
<a class="brand" href="/"><img src="/images/rr-mark.png" alt="" width="44" height="44">Retention Rules</a>
<nav class="nav" aria-label="Main">{links}{button}</nav>
<details class="menu"><summary>Menu</summary><div class="menu-links">{links}{button}</div></details>
</div></header>'''


FOOT_WORK = [("SaaS", "/saas/"), ("Ecommerce", FLOWS), ("Coaches", "/coaches/"), ("Case Studies", "/case-studies/")]
FOOT_COMPANY = [("About", "/about/"), ("Newsletter", LETTERS)]


def foot_col(title, items):
    links = "".join(f'<a href="{h}">{t}</a>' for t, h in items)
    return f'<div class="foot-col"><h2>{title}</h2>{links}</div>'


# Results disclaimer follows the standard earnings disclaimer pattern: results are
# real but not typical, what they depend on, no promise, past is not future.
FOOTER = f'''<footer class="site-foot"><div class="wrap">
<div class="foot-top">
<div class="foot-brand"><a class="brand" href="/"><img src="/images/rr-mark.png" alt="" width="44" height="44">Retention Rules</a>
<p>Most growth comes from the customers you already have.</p></div>
{foot_col("Work", FOOT_WORK)}
{foot_col("Company", FOOT_COMPANY)}
</div>
<div class="foot-legal">
<p><strong>Results disclaimer.</strong> The results on this site come from real client work. They are not typical. They are not a promise of what you will make. Your results will differ. They depend on your list, your offer, your market and your timing. Some of that is out of our hands. What worked in the past may not work for you. Any range we state is a goal, not a promise. A guarantee only counts if an offer states it in writing, on that offer's terms.</p>
<p>Retention Rules is a business of Abdurrub LLC.</p>
<p>&copy; 2026 Abdurrub LLC. All rights reserved.</p>
</div>
</div></footer>'''


def page(path, title, desc, body, book=None):
    url = SITE + path
    full_title = "Retention Rules" if path == "/" else f"{title} | Retention Rules"
    schema = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization",'
              f'"name":"Retention Rules","url":"{SITE}/","logo":"{SITE}/images/rr-logo.png",'
              '"founder":{"@type":"Person","name":"Muddassir Abdur Rub"}}</script>') if path == "/" else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="Retention Rules">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/images/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Retention Rules logo">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{full_title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/images/og.png">
<link rel="icon" type="image/png" href="/images/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site.css">
{schema}
</head>
<body>
{header(path, book)}
<main>
{body}
</main>
{FOOTER}
</body>
</html>
'''


def redirect(target, title, desc=""):
    desc = desc or "Retention Rules helps businesses at $250K to $1M a year earn more from the leads and customers they already paid for."
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<meta property="og:site_name" content="Retention Rules">
<meta property="og:type" content="website">
<meta property="og:url" content="{target}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/images/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/images/og.png">
<script>location.replace("{target}" + location.hash);</script>
</head>
<body><p><a href="{target}">Continue to {title}</a></p></body>
</html>
'''


OLLY_ALT = "Slack message from Olly at Passion.io listing total email revenue of $2,442,707, Black Fridays of $615,355, mini promos of $643,381, nurture emails of $68,564 and webinar follow ups of $1,115,407."
T_MATT = ("linkedin-matthias-passion-io.png", "LinkedIn recommendation from Matthias Bellmann, founder of Passion.io.")
T_KIT = ("upwork-convertkit.png", "Five star Upwork review: Hire him. One of the most intelligent and strategic humans I have ever worked with.")
T_STRAT = ("upwork-saas-email-strategy.png", "Five star Upwork review for SaaS email strategy.")
T_COPY = ("upwork-saas-email-copywriter.png", "Five star Upwork review for a SaaS email copywriter job.")
T_BRAIN = ("upwork-fb-ads-brainhive.png", "Five star Upwork review: So much thought went into this project.")
T_AYMAN = ("upwork-ayman.png", "Verified Upwork testimonial: an 80% response rate on a cold email campaign.")

# ---------------------------------------------------------------- HOME
# Reader: cold, unaware. Lead: proclamation. One action: pick your business.
HOME = hero(
    "For businesses doing $250K to $1M a year",
    "Most growth comes from <em>the customers you already have.</em>",
    "You paid to get your leads and customers. Retention Rules finds the money leaking from them, then fixes it.",
    btn("Find my leak", "#choose"),
    ("100% Job Success on Upwork", "Klaviyo deliverability certified", "Founded by an ex doctor"),
) + (
    '<section class="trust"><div class="wrap"><h2><em>$4M+</em> in tracked revenue.</h2>' + logos() + "</div></section>"
) + f'<section class="sec" id="choose"><div class="wrap">' + head(
    "Start here", "Which one <em>sounds like you?</em>", "Pick your business. The page you land on shows the fix."
) + doors() + "</div></section>" + sec(
    '<div class="split"><div><span class="label">The proof</span><h2>Do not take my word for it. <em>Read the Slack message.</em></h2>'
    + ps("Olly at Passion.io sent me these numbers from his team.",
         "$2.4M+ in email revenue. Revenue per lead doubled. A record Black Friday.",
         "The biggest numbers on this site have a screen like this one behind them.")
    + "</div>" + shot("olly-kpis.jpg", OLLY_ALT, "The start of the message. See all of it in the case study.") + "</div>", "panel"
) + sec(
    head("The problem", "Buying more ads is <em>the costly fix.</em>", "Sales dip, so the business buys more traffic. The leak stays open.")
    + cards(
        ("", "Leads go cold", "You paid for each lead. Most hear from you a few times, then never again."),
        ("", "Customers buy once", "They buy, then drift off. Nobody gives them a reason to come back."),
        ("", "Emails all sound the same", "Same claim. Same discount. So your list stops reading."),
    )
) + sec(
    head("The method", "A doctor's rule, <em>used on your marketing.</em>", "Doctors find out what is wrong before they treat it. Each job here runs the same way.")
    + cards(
        ("Step 1", "Read the chart", "Sales calls. Support tickets. Replies. Revenue by email. Your customers tell you what is wrong."),
        ("Step 2", "Find the leak", "Each leak gets a name and a place. The biggest one goes first."),
        ("Step 3", "Fix it", "The emails get written and launched in your voice. Then the numbers get checked."),
    ), "panel"
) + sec(
    head("Case studies", "Real work. <em>Real screens.</em>", "Three results. Each one shows the proof.")
    + '<div class="cases">' + case(
        "/case-studies/saas/", "olly-kpis.jpg", "$13 to $27", "Revenue per lead at Passion.io", "Same traffic. Each lead became worth twice as much."
    ) + case(
        "/case-studies/coaches/", "bf-day3.png", "$615,355", "Three Black Fridays", "Promo emails to a list of coaches, from 2023 to 2025."
    ) + case(
        "/case-studies/ecommerce/", "word:Psychic Sharma", "10% to 34%", "Open rate at Psychic Sharma", "Same list. Same offers. New writing."
    ) + '</div><div class="action"><a href="/case-studies/">See all case studies</a></div>'
) + sec(
    head("What clients say", "People notice when <em>the emails get sharper.</em>")
    + wall(T_MATT, T_KIT, T_BRAIN, T_STRAT, T_COPY) + wide(T_AYMAN), "panel"
) + sec(
    '<div class="founder"><img src="/images/muddassir.png" alt="Muddassir Abdur Rub" width="120" height="120"><div><h2>Why a doctor runs this.</h2>'
    + ps("In 2018, I graduated from medical school. Doctors read the chart before they treat you.",
         "Marketing does the opposite. So I brought the doctor's rule with me.",
         'At Passion.io, I read the sales calls and the support tickets first. Revenue per lead went from $13 to $27.')
    + '<strong>Muddassir Abdur Rub</strong><span class="muted">Founder. <a href="/about/">Read the full story</a></span></div></div>'
) + (
    '<section class="close"><div class="wrap"><h2>Which one <em>is you?</em></h2>' + doors() + "</div></section>"
)

# ---------------------------------------------------------------- SAAS
# Reader: problem aware. Lead: problem-solution, opens on a real customer line.
SAAS = hero(
    "For SaaS founders with a churn problem",
    '"I bought the app and then <em>never opened it again.</em>"',
    "A real SaaS customer said that. Some of your users think it too. Retention Rules finds where they drop off and writes the emails that bring them back.",
    btn("Book a call", BOOK),
    ("$2.4M+ in SaaS email revenue", "Revenue per lead doubled", "Free leak audit in 48 hours"),
) + logostrip() + sec(
    head("Sound familiar?", "Where <em>the money leaks.</em>", "You paid to get each of these people. Each one is still on your list.")
    + cards(
        ("", "Trials end with no sale", "People try the product. Then the trial ends and they go quiet."),
        ("", "Users never set it up", "They pay, then never get to the first win. They cancel soon after."),
        ("", "Webinars go nowhere", "People sign up and watch. Then they get a weak follow up."),
        ("", "You only email to launch", "Your list hears from you when you want money. So it stops reading."),
    cols="four")
) + sec(
    head("Why it stays broken", "More ads do not <em>fix churn.</em>")
    + compare("The usual fix", ["Buy more traffic", "Add a discount", "Send a monthly newsletter", "Guess what users want"],
              "What we do", ["Read your sales calls and tickets", "Find the biggest leak first", "Write each email for one job", "Check the numbers after launch"]), "panel"
) + sec(
    head("What gets built", "Four places <em>to stop the leak.</em>")
    + cards(
        ("", "Welcome emails", "They get a new user to the first win."),
        ("", "Trial and cart emails", "They reach people who were close to buying."),
        ("", "Webinar follow up", "It reaches people who showed up and did not buy."),
        ("", "Launch and promo emails", "They give people a reason to buy now."),
    cols="four")
) + sec(
    '<div class="split"><div><span class="label">The proof</span><h2>$2.4M+ for one SaaS. <em>Here is the message.</em></h2>'
    + ps("Passion.io sells an app to coaches. I wrote its emails for two years.",
         "Olly's team pulled these numbers. Webinar follow up alone brought in $1,115,407.",
         '<a href="/case-studies/saas/">Read the full case study</a>')
    + "</div>" + shot("olly-kpis.jpg", OLLY_ALT) + "</div>", "panel"
) + sec(
    '<div class="cards two">' + bars("Revenue per lead", [("2023", 13, "$13"), ("2024", 20, "$20"), ("2025", 27, "$27")], "Numbers from the Slack message above.")
    + bars("Webinar follow up revenue", [("2023", 108094, "$108,094"), ("2024", 658024, "$658,024"), ("2025", 349289, "$349,289")], "2025 is a partial year.")
    + "</div>"
) + sec(
    head("What SaaS clients say", "Read the <em>real reviews.</em>") + wall(T_MATT, T_STRAT, T_COPY, T_KIT), "panel"
) + sec(
    head("How it starts", "Three steps. <em>The first is free.</em>")
    + cards(
        ("Step 1", "Book a call", "We look at your funnel. I ask where you think it leaks."),
        ("Step 2", "Get your leaks", "Within 48 hours, you get 3 to 5 leaks by name. You keep the list."),
        ("Step 3", "Fix it", "If we are a fit, I write the emails. We launch them and check the numbers."),
    )
) + sec(
    head("Is this a fit?", "Who <em>this is for.</em>")
    + compare("Not a fit", ["No users yet", "No list to email", "You want a cheap writer"],
              "A good fit", ["$250K to $1M a year", "Real users and a list", "You want the leak found first"]), "panel"
) + sec(
    head("Questions", "What founders <em>ask first.</em>") + faq(
        ("What happens on the call?", "We look at your funnel. Then I go find the leaks. You get them within 48 hours."),
        ("What does the audit cost?", "It is free. You keep the list of leaks, even if we never work together."),
        ("What does the fix cost?", "You get a price after the audit, once we both know how big the leaks are."),
        ("Which email tools do you work in?", "Klaviyo, HubSpot, Kit, ActiveCampaign, Mailchimp and most others."),
    )
) + close(
    "Find out what your users <em>are telling you.</em>",
    "Book a call and get 3 to 5 leaks within 48 hours.",
    btn("Book a call", BOOK),
)

# ---------------------------------------------------------------- COACHES
# Reader: solution aware. Lead: promise lead (Muddassir's headline), then explain the offer.
COACHES = hero(
    "For coaches and experts with a list or a following",
    "Generate an extra <em>$20,000 to $200,000</em> within 10 days with my Post-paid Promo Campaigns.",
    "No retainer. No setup fee. You pay only from the sales the campaign makes.",
    btn("Book a call", BOOK_COACH),
    ("$1.25M+ from promo emails", "Nothing upfront", "Your list stays yours"),
) + logostrip() + sec(
    head("The offer", "What is a <em>Post-paid Promo Campaign?</em>", "I come up with the idea, write the campaign and launch it on your email list and socials. I work on commission only.")
    + compare("A normal retainer", ["You pay each month", "You pay if it flops", "You carry the risk"],
              "A Post-paid Promo", ["Nothing upfront", "No sales, no bill", "I carry the risk"])
) + sec(
    head("What you get", "The whole promo. <em>Done for you.</em>")
    + cards(
        ("", "The idea", "A real reason for your people to buy this week."),
        ("", "The emails and posts", "All of it is written in your voice."),
        ("", "The launch", "I load it into your email tool and get it live."),
        ("", "A page check", "I can review your sales page before the promo starts."),
    cols="four"), "panel"
) + sec(
    head("Pick your moment", "Three kinds <em>of promo.</em>", "We pick the one that fits your month.")
    + cards(
        ("Seasonal", "The big dates", "Black Friday, Christmas and the New Year."),
        ("Personal", "Your dates", "Your birthday or your years in business."),
        ("Business", "Your news", "A launch, a new bonus or an open door to your program."),
    )
) + sec(
    head("The proof", "$615,355 from three <em>Black Fridays.</em>", "These promos went to a list of coaches at Passion.io. Short promos made another $643,381.")
    + '<div class="split"><div>' + bars("Black Friday email revenue", [("2023", 168311, "$168,311"), ("2024", 256094, "$256,094"), ("2025", 190950, "$190,950")], "From the Slack message beside this chart.")
    + "</div>" + shot("olly-full.jpg", OLLY_ALT) + '</div><div class="action"><a href="/case-studies/coaches/">See the emails in the case study</a></div>', "panel"
) + sec(
    head("How it runs", "Your only job is <em>to read it.</em>")
    + timeline(("We talk", "We go over your list, your offer and your dates."),
               ("I build it", "I write the promo. You can say no at any time."),
               ("It runs", "A few short emails warm up the list. Then it goes live for 5 to 7 days."),
               ("You get paid first", "When it ends, we look at the sales. I bill my commission on the cash you got."))
) + sec(
    head("What clients say", "From the founder <em>who saw it work.</em>") + wall(T_MATT, T_BRAIN, T_KIT) + wide(T_AYMAN), "panel"
) + sec(
    head("Is this for you?", "Who <em>this is for.</em>", "A promo needs people to talk to.")
    + compare("Not a fit", ["No list and no following", "No proven program", "Your people do not know you yet"],
              "A good fit", ["An email list or a real following", "A program that sells without you on a call", "People who already trust you"])
) + sec(
    head("Questions", "What coaches <em>ask first.</em>") + faq(
        ("What does it cost?", "Nothing upfront. I take a commission on the sales from the promo. We go over the numbers on the call."),
        ("What if it makes no sales?", "You owe me nothing."),
        ("What stays mine?", "I only earn on sales from my promo, during the promo. Every sale after it ends is yours. Every upsell is yours too."),
        ("Will this burn out my list?", "No. Each email gives people something, so even those who do not buy are glad they read it."),
        ("Do you build sales pages?", "No. I write the promo and review your page. The page stays yours."),
        ("How much work is it for me?", "You read the copy and say yes or no."),
    ), "panel"
) + close(
    "See what your list can do <em>in 10 days.</em>",
    "Book a call. We will look at your list and your offer, and pick your first promo.",
    btn("Book a call", BOOK_COACH),
    "The range is a goal and depends on your list, your offer and your audience. It is not a guarantee. The Black Friday numbers above came in over 30 days.",
)

# ---------------------------------------------------------------- CASE STUDIES
CASES = hero(
    "Real numbers. Real screens.",
    "The work, <em>with the proof.</em>",
    "Pick your kind of business. Each case study shows what was wrong, what changed and what it made.",
) + '<section class="trust"><div class="wrap"><h2><em>$4M+</em> in tracked revenue.</h2>' + logos() + "</div></section>" + sec(
    '<div class="group" id="saas"><h3>SaaS</h3><div class="cases">' + case(
        "/case-studies/saas/", "olly-kpis.jpg", "$2.4M+", "Passion.io email revenue", "Revenue per lead doubled from $13 to $27 on the same traffic."
    ) + case(
        "/case-studies/webinar/", "buyer-persona-system.png", "$1,115,407", "Webinar follow up emails", "The biggest revenue line, built from customer research."
    ) + case(
        "/case-studies/nurture/", "nurture-email-faq.png", "4x", "Newsletter revenue", "From $9,712 to $42,423 on the same list, with no promos."
    ) + '</div></div><div class="group" id="coaches"><h3>Coaches</h3><div class="cases two">' + case(
        "/case-studies/coaches/", "bf-day3.png", "$615,355", "Three Black Fridays", "Promo emails to a list of coaches. The 2024 promo was a record."
    ) + case(
        "/case-studies/coaches/", "bf-final.png", "$643,381", "Short promos", "Mini promos to the same list, from 2023 to 2025."
    ) + '</div></div><div class="group" id="ecommerce"><h3>Ecommerce</h3><div class="cases">' + case(
        "/case-studies/ecommerce/", "word:Psychic Sharma", "10% to 34%", "Psychic Sharma open rate", "Same list. Same offers. The writing changed."
    ) + case(
        "", "logo:moonlamp-wordmark.png", "$784K", "The Original Moon Lamp", "Black Friday email revenue from an existing list."
    ) + case(
        "", "word:Oshun", "30+ emails", "Oshun", "A full email system, built from scratch before launch."
    ) + "</div></div>"
) + '<section class="close"><div class="wrap"><h2>Which one <em>is you?</em></h2>' + doors() + "</div></section>"

CASE_SAAS = hero(
    "SaaS case study: Passion.io",
    "Revenue per lead doubled <em>on the same traffic.</em>",
    "Each lead brought in $13. Two years later, each one brought in $27. Email made $2,442,707 along the way.",
    btn("Book a call", BOOK),
) + sec(stats(("$13 to $27", "revenue per lead, 2023 to 2025"),
              ("$2,442,707", "total email revenue"),
              ("3.5x", "email revenue from the newsletter")), "tight") + mid(
    "<h2>The client.</h2>" + ps(
        "Passion.io sells an app to coaches.",
        "Its founder ran a live workshop each Friday.",
        "I worked there as senior copywriter and wrote the emails.",
    ) + "<h2>Reading the chart.</h2><p>Before the emails changed, the research did.</p><ul>"
    "<li>I sat in on more than 20 sales calls and took down the words people used.</li>"
    "<li>I read the support tickets.</li>"
    "<li>I sent a short email with two questions to the list, again and again.</li>"
    "<li>After each Friday workshop, I logged new pains and doubts.</li></ul>"
    + shot("buyer-persona-system.png", "The buyer persona document built for Passion.io from sales calls.", "One of the research docs. Each email started here.")
    + "<h2>Finding the leak.</h2>" + ps("The biggest money sat in the days after a webinar. So I went to work on those emails.")
    + bars("Email revenue by source", [("Webinar", 1115407, "$1,115,407"), ("Promos", 643381, "$643,381"), ("Black Friday", 615355, "$615,355"), ("Nurture", 68564, "$68,564")])
    + "<h2>The fix.</h2><ul><li>The list got split into groups, so people got emails that fit them.</li>"
    "<li>The message got sharper and used the customers' own words.</li>"
    "<li>The emails got a voice that readers knew.</li></ul>"
    + "<h2>The result.</h2>" + bars("Revenue per lead", [("2023", 13, "$13"), ("2024", 20, "$20"), ("2025", 27, "$27")])
    + "<p>The traffic stayed the same. The leads became worth twice as much.</p><h2>The full message.</h2><p>Olly's team pulled every number on this page.</p>"
    + shot("olly-full.jpg", OLLY_ALT) + "<h2>What the founder said.</h2>" + shot(*T_MATT)
) + close("Find the leak <em>in your business.</em>", "Book a call and get 3 to 5 leaks within 48 hours.", btn("Book a call", BOOK))

CASE_WEBINAR = hero(
    "SaaS case study: Passion.io",
    "Webinar follow up emails made <em>$1,115,407.</em>",
    "People who watch a webinar have raised a hand. The emails after it are where the sale closes. So that is where I went to work.",
    btn("Book a call", BOOK),
) + sec(stats(("$1,115,407", "from webinar follow up emails"), ("6x", "growth from 2023 to 2024"), ("20+", "sales calls behind the copy")), "tight") + mid(
    bars("Webinar follow up revenue", [("2023", 108094, "$108,094"), ("2024", 658024, "$658,024"), ("2025", 349289, "$349,289")], "2025 is a partial year.")
    + "<h2>How the emails ran.</h2><ul>"
    "<li><strong>Same day.</strong> The first email went out within hours. It took on the top doubt from the live chat.</li>"
    "<li><strong>Days 2 to 4.</strong> Three emails. Each one explained one feature and tied it to one pain.</li>"
    "<li><strong>Day 5.</strong> A customer story that matched the reader.</li>"
    "<li><strong>Days 6 and 7.</strong> A clear deadline and the full bonus list.</li></ul>"
    + "<h2>Why it earned more each year.</h2><ul>"
    "<li>Cold traffic and the existing list each got their own follow up.</li>"
    "<li>Each cycle, the weakest email got swapped for a new idea from the research.</li>"
    "<li>Each email ran a subject line test. Weak ones got cut in the same campaign.</li></ul>"
    + shot("buyer-persona-system.png", "The buyer persona document behind the webinar emails.", "The research doc behind the emails.")
    + "<h2>The proof.</h2>" + shot("olly-full.jpg", OLLY_ALT)
) + close("Your webinar leads <em>are still on your list.</em>", "Book a call and get 3 to 5 leaks within 48 hours.", btn("Book a call", BOOK))

CASE_NURTURE = hero(
    "SaaS case study: Passion.io",
    "Newsletter revenue grew <em>4x on the same list.</em>",
    "No promos. No sale dates. The list did not grow to do it. The emails changed.",
    btn("Book a call", BOOK),
) + sec(stats(("$9,712", "in 2023"), ("$42,423", "in 2025"), ("24", "kinds of email opening tested")), "tight") + mid(
    bars("Newsletter email revenue", [("2023", 9712, "$9,712"), ("2024", 16429, "$16,429"), ("2025", 42423, "$42,423")])
    + "<h2>The two changes.</h2><ul>"
    "<li><strong>More sends.</strong> We went from one email a week to two or three. Unsubscribes stayed in the normal range.</li>"
    "<li><strong>New formats.</strong> Stories, reader questions, Reddit notes and customer reviews took turns.</li></ul>"
    "<h2>How each email worked.</h2>" + ps("First came a story worth reading on its own. Then came a soft plug at the end.", "The product never led. It always closed.")
    + shot("nurture-email-faq.png", "A reader question email written for Passion.io.", "One of the reader question emails.")
    + "<h2>The proof.</h2>" + shot("olly-full.jpg", OLLY_ALT)
) + close("Your newsletter could be <em>a revenue line.</em>", "Book a call and get 3 to 5 leaks within 48 hours.", btn("Book a call", BOOK))

CASE_COACH = hero(
    "Coaches case study: Passion.io",
    "Three Black Friday promos. <em>$615,355.</em>",
    "One list of coaches. One promo window a year. Here is what those emails did, and here are the emails.",
    btn("Book a call", BOOK_COACH),
) + sec(stats(("$256,094", "in 30 days, a record year"), ("11", "emails in the 7 day early access"), ("About $100K", "before any rival sale began")), "tight") + mid(
    bars("Black Friday email revenue", [("2023", 168311, "$168,311"), ("2024", 256094, "$256,094"), ("2025", 190950, "$190,950")])
    + "<h2>The plan.</h2>" + ps("Most sales open on Friday. We opened early for the people on the list.", "They could buy from us before they saw a single rival offer.")
    + "<h2>Each day had a job.</h2><ul>"
    "<li><strong>Day 1.</strong> A tease to warm up the list.</li>"
    "<li><strong>Day 2.</strong> The cart opens, then a new angle on burnout.</li>"
    "<li><strong>Day 3.</strong> A feature, with keeping clients as the angle.</li>"
    "<li><strong>Day 4.</strong> The top questions, then a short reminder.</li>"
    "<li><strong>Day 5.</strong> A second feature reveal.</li>"
    "<li><strong>Day 6.</strong> Customer wins, then three myths busted.</li>"
    "<li><strong>Day 7.</strong> The close, with all the bonuses laid out.</li></ul>"
    + "<h2>The real emails.</h2>" + '<div class="shots">' + shot("bf-day3.png", "A Passion.io Black Friday email: early access gone in 3 days.", "Three days to go.")
    + shot("bf-final.png", "A Passion.io Black Friday email: midnight deadline.", "The final day.") + "</div>"
    + "<h2>The numbers.</h2>" + shot("olly-full.jpg", OLLY_ALT) + "<h2>What the founder said.</h2>" + shot(*T_MATT)
) + close("See what a promo can do <em>for your list.</em>", "Book a call. We will look at your list and your offer.", btn("Book a call", BOOK_COACH))

CASE_ECOM = hero(
    "Ecommerce case study: Psychic Sharma",
    "Same list. Same offers. <em>Opens went from 10% to 34%.</em>",
    "Psychic Sharma had a list that barely opened its emails. The writing was the one thing that changed.",
    btn("Grow my email revenue", FLOWS),
) + sec(stats(("10% to 34%", "top open rate"), ("Under 1% to 3%", "click rate on the best sends"), ("5", "sends in one sprint, each with a new idea")), "tight") + mid(
    bars("Top open rate", [("Before", 10, "10%"), ("After", 34, "34%")])
    + "<h2>The client.</h2>" + ps("This brand sells readings online to women aged 35 to 60.", "Many of them were tired of dating.")
    + "<h2>The leak.</h2>" + ps("The old emails led with the offer. The open rate sat at 10%.")
    + "<h2>The fix.</h2><p>The new emails led with a story. Each of the five used a new idea.</p><ul>"
    "<li>A tale of two people with one small difference.</li><li>A mistake, told as a confession.</li>"
    "<li>A hook about a famous name.</li><li>A take on dating apps that broke the pattern.</li>"
    "<li>A quiet email about the fear of being alone.</li></ul>"
    + ps("The subject lines stopped selling and started to raise a question.", "The offer came in the last third of each email.")
    + "<h2>The result.</h2>" + ps("The best sends hit a 3% click rate, up from under 1%.", "The list, the offers and the platform stayed the same.")
) + close("Get emails that <em>bring buyers back.</em>", "See the flows, the price and the guarantee.", btn("Grow my email revenue", FLOWS))

# ---------------------------------------------------------------- ABOUT
# Story template: Pixar Story Spine (Kenn Adams, 1991).
ABOUT = hero(
    "The story",
    "I left medicine in 2019. <em>One rule came with me.</em>",
    "It is the rule behind every job at Retention Rules.",
    btn("Book a call", BOOK),
) + logostrip() + mid(
    '<div class="founder" style="margin-bottom:40px"><img src="/images/muddassir.png" alt="Muddassir Abdur Rub" width="120" height="120"><div><strong style="margin:0">Muddassir Abdur Rub</strong><span class="muted">Founder, ex doctor</span></div></div>'
    + ps(
        "In 2018, I graduated from medical school.",
        "Doctors live by one rule. You find out what is wrong before you treat it.",
        "In 2019, I left medicine and went into marketing.",
        "Marketing ran on the opposite rule. Sales dip, so the business buys more ads. Nobody checks the chart.",
        "Then I joined Passion.io as senior copywriter.",
        "I did what a doctor does. I read the chart.",
        "I sat in on more than 20 sales calls. I read the support tickets. I asked the list two questions by email.",
        "The chart pointed to one spot. The biggest money sat in the days after a webinar.",
        "So I went to work on those emails. They brought in $1,115,407.",
        "Because of that, each lead became worth more. Revenue per lead went from $13 to $27 on the same traffic.",
        "In all, email brought in $2,442,707.",
        "In April 2026, I left to build Retention Rules.",
        "Every job here starts the same way. Read the chart. Find the leak. Then fix it.",
    ) + "<h2>The message that sums it up.</h2>" + shot("olly-full.jpg", OLLY_ALT)
) + sec(
    head("Fit", "Who <em>this is for.</em>")
    + compare("Not a fit", ["No sales yet", "No list and no customers", "Agencies"],
              "A good fit", ["$250K to $1M a year", "SaaS, ecommerce and coaches", "A proven offer and a list"]), "panel"
) + sec(
    head("What clients say", "Read the <em>real reviews.</em>") + wall(T_MATT, T_KIT, T_BRAIN) + wide(T_AYMAN)
) + close("Let's <em>read your chart.</em>", "Book a call and get 3 to 5 leaks within 48 hours.", btn("Book a call", BOOK))

NOT_FOUND = hero(
    "Page not found",
    "This page <em>moved.</em>",
    "Pick your business and you will find what you came for.",
) + sec(doors())

PAGES = {
    "/": ("Retention Rules", "Most growth comes from the customers you already have. Retention Rules helps businesses at $250K to $1M a year earn more from the leads and customers they already paid for.", HOME, None),
    "/saas/": ("Retention for SaaS", "Retention Rules finds where your SaaS users drop off and writes the emails that bring them back. Book a call and get 3 to 5 leaks within 48 hours.", SAAS, BOOK),
    "/coaches/": ("Post-paid Promo Campaigns for Coaches", "Generate an extra $20,000 to $200,000 within 10 days with Post-paid Promo Campaigns. No retainer. No setup fee. Commission only.", COACHES, BOOK_COACH),
    "/case-studies/": ("Case Studies", "SaaS, ecommerce and coaching case studies from Retention Rules, with the numbers and the screens behind them.", CASES, None),
    "/case-studies/saas/": ("Passion.io Case Study", "How Passion.io took revenue per lead from $13 to $27 on the same traffic, with $2,442,707 in email revenue.", CASE_SAAS, BOOK),
    "/case-studies/webinar/": ("Webinar Follow Up Case Study", "How webinar follow up emails brought in $1,115,407 at Passion.io.", CASE_WEBINAR, BOOK),
    "/case-studies/nurture/": ("Newsletter Revenue Case Study", "How newsletter revenue grew 4x on the same list at Passion.io, with no promos.", CASE_NURTURE, BOOK),
    "/case-studies/coaches/": ("Black Friday Case Study", "Three Black Friday promos brought in $615,355 from a list of coaches at Passion.io.", CASE_COACH, BOOK_COACH),
    "/case-studies/ecommerce/": ("Psychic Sharma Case Study", "Same list, same offers. How Psychic Sharma took its open rate from 10% to 34%.", CASE_ECOM, None),
    "/about/": ("The Story", "I left medicine in 2019. One rule came with me. It is the rule behind every job at Retention Rules.", ABOUT, BOOK),
}

REDIRECTS = {
    "/ecommerce/": (FLOWS, "Retention Rules for Ecommerce"),
    "/newsletter/": (LETTERS, "Retention Rules Newsletter"),
}

# Old abdurrub.com URLs and where each one lands. Written to _abdurrub-redirects/
# and only copied over the abdurrub-com repo at go-live. CSOS, creative strategy,
# survey and story template pages are left alone on purpose.
OLD_MAP = {
    "/": "/",
    "/about/": "/about/",
    "/contact/": "/",
    "/work/": "/case-studies/",
    "/work-with-me/": "/",
    "/blog/": LETTERS,
    "/email-marketing/": "/saas/",
    "/email-marketing/passion-io/": "/case-studies/saas/",
    "/email-marketing/osum/": "/saas/",
    "/dtc/": FLOWS,
    "/dtc/qualify/": FLOWS + "qualify/",
    "/dtc-retention/": FLOWS,
    "/dtc-retention/moon-lamp/": "/case-studies/#ecommerce",
    "/dtc-retention/oshun/": "/case-studies/#ecommerce",
    "/dtc-retention/psychic-sharma/": "/case-studies/ecommerce/",
    "/product-marketing/": "/case-studies/saas/",
    "/productmarketing/": "/case-studies/saas/",
    "/product-marketing/black-friday/": "/case-studies/coaches/",
    "/product-marketing/blogs/": "/case-studies/saas/",
    "/product-marketing/cross-functional/": "/case-studies/saas/",
    "/product-marketing/customer-research/": "/case-studies/saas/",
    "/product-marketing/dogfooding/": "/case-studies/saas/",
    "/product-marketing/funnel-intent/": "/case-studies/saas/",
    "/product-marketing/notion-system/": "/case-studies/saas/",
    "/product-marketing/nurture-revenue/": "/case-studies/nurture/",
    "/product-marketing/positioning-pivot/": "/case-studies/saas/",
    "/product-marketing/webinar-followups/": "/case-studies/webinar/",
    "/product-marketing/youai-launch/": "/case-studies/saas/",
}


def write(path, text):
    out = ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


def plain_copy(html_text):
    """Page copy for the grade check: no quotes from others, no fine print, no nav."""
    s = re.sub(r"(?is)<(blockquote|cite)\b.*?</\1>", " ", html_text)
    s = re.sub(r'(?is)<p class="fine nocheck">.*?</p>', " ", s)
    s = re.sub(r"(?i)</(p|h1|h2|h3|li|div|td|th|strong|b)>", ". ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = htmllib.unescape(s)
    s = re.sub(r"(\.\s*){2,}", ". ", s)
    s = re.sub(r"[?!]\s*\.", "?", s)
    return re.sub(r"[ \t]+", " ", s)


def main():
    failed = False
    for path, (title, desc, body, book) in PAGES.items():
        write(path, page(path, title, desc, body, book))
        copy = plain_copy(body)
        if FK_TOOL.exists():
            res = subprocess.run([sys.executable, str(FK_TOOL)], input=copy, text=True, capture_output=True)
            first = res.stdout.strip().splitlines()[0] if res.stdout.strip() else ""
            print(f"{path:28} {first}")
            if res.returncode:
                failed = True
                print(res.stdout)
        for bad in ("—", "–"):
            assert bad not in body, f"dash in {path}"
    for path, (target, title) in REDIRECTS.items():
        write(path, redirect(target, title))

    (ROOT / "404.html").write_text(page("/404/", "Page moved", "Retention Rules", NOT_FOUND).replace(
        '<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">'), encoding="utf-8")
    urls = "".join(f"<url><loc>{SITE}{p}</loc></url>" for p in PAGES)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")

    # Prepared for go-live only. Not part of the published site.
    old_root = ROOT.parent / "RetentionRules-Main-Site-abdurrub-redirects"
    for old, new in OLD_MAP.items():
        target = new if new.startswith("http") else SITE + new
        out = old_root / old.strip("/") / "index.html" if old != "/" else old_root / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(redirect(target, "Retention Rules"), encoding="utf-8")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
