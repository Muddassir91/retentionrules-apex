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
    ext = href.startswith("http")
    attrs = ' target="_blank" rel="noopener"' if "calendar.app.google" in href else ""
    return f'<a class="btn" href="{href}"{attrs}>{label}</a>'


def ps(*lines):
    return "".join(f"<p>{x}</p>" for x in lines)


def sec(body, cls=""):
    return f'<section class="sec {cls}">{body}</section>'


def narrow(body, cls=""):
    return sec(f'<div class="narrow">{body}</div>', cls)


def hero(h1, lead, cta="", eyebrow=""):
    eb = f'<span class="eyebrow">{eyebrow}</span>' if eyebrow else ""
    return (f'<section class="hero"><div class="wrap">{eb}<h1>{h1}</h1>'
            f'<p class="lead">{lead}</p>{cta}</div></section>')


def stats(*items, note=""):
    cells = "".join(f'<div class="stat"><b>{a}</b><span>{b}</span></div>' for a, b in items)
    extra = f'<p class="note">{note}</p>' if note else ""
    return f'<div class="stats">{cells}</div>{extra}'


def steps3(*items):
    cells = "".join(
        f'<div class="step"><b>STEP {i}</b><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(items, 1))
    return f'<div class="steps">{cells}</div>'


def steplist(*items):
    rows = "".join(
        f'<li><b>{i}</b><div><strong>{t}</strong>{d}</div></li>'
        for i, (t, d) in enumerate(items, 1))
    return f'<ol class="step-list">{rows}</ol>'


def ticks(*items):
    return '<ul class="ticks">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def figs(*rows):
    body = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    return f'<table class="figs"><tbody>{body}</tbody></table>'


def quote(text, who):
    return f'<blockquote class="quote nocheck"><p>"{text}"</p><cite>{who}</cite></blockquote>'


def faq(*items):
    return '<div class="faq">' + "".join(f"<div><h3>{q}</h3><p>{a}</p></div>" for q, a in items) + "</div>"


def door(title, text, label, href):
    return f'<div class="door"><h3>{title}</h3><p>{text}</p>{btn(label, href)}</div>'


def cta(h2, text, button, fine=""):
    f = f'<p class="fine nocheck">{fine}</p>' if fine else ""
    return f'<section class="sec cta"><div class="wrap"><h2>{h2}</h2><p>{text}</p>{button}{f}</div></section>'


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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
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


# ---------------------------------------------------------------- HOME
# Reader: problem aware founder. Lead: proclamation. One action: pick your business.
HOME = hero(
    "Most growth comes from the customers you already have.",
    "Retention Rules helps businesses at $250K to $1M a year earn more from the leads and customers they already paid for.",
) + sec('<div class="wrap"><div class="sec-head"><h2>Pick your business.</h2></div><div class="doors">' + door(
    "SaaS", "If you're a SaaS founder losing more than 5% of your customers to churn each month, this is for you.", "Fix my churn", "/saas/"
) + door(
    "Ecommerce", "If you run an ecommerce brand and email brings in less than 20% of your revenue, this is for you.", "Grow my email revenue", FLOWS
) + door(
    "Coaches", "If you're a coach who wants to make more money from the subscribers you already have, this is for you.", "Make money from my list", "/coaches/"
) + '</div></div>', "tint") + sec('<div class="wrap"><div class="sec-head"><h2>The numbers behind the work.</h2></div>' + stats(
    ("$2.5M", "in email revenue"),
    ("$13 to $27", "revenue per lead, on the same traffic"),
    ("$256K", "from one Black Friday, in 30 days"),
    note="All three come from one coaching app company.",
) + '</div>') + sec('<div class="wrap"><div class="sec-head"><h2>Every job runs the same way.</h2></div>' + steps3(
    ("Read the chart", "Sales calls. Support tickets. Replies. Revenue by email. Your customers tell you what is wrong."),
    ("Find the leak", "Each leak gets a name and a place. The biggest one goes first."),
    ("Fix it", "The emails get written and launched in your voice. Then the numbers get checked."),
) + '</div>') + narrow(
    "<h2>A doctor's rule, used on your marketing.</h2>" + ps(
        "In 2018, I graduated from medical school.",
        "Doctors find out what is wrong before they treat it.",
        "Marketing does the opposite. Sales dip, so the business buys more ads.",
        "I brought the doctor's rule with me. At a coaching app company, I read the sales calls and the support tickets first.",
        "Revenue per lead went from $13 to $27 on the same traffic.",
        "Retention Rules runs on that one rule.",
    ) + '<div class="sig"><img src="/images/muddassir.png" alt="" width="64" height="64"><div><strong>Muddassir Abdur Rub</strong><span>Founder, ex doctor. <a href="/about/">Read the full story</a></span></div></div>'
) + cta(
    "Pick the problem you want fixed.",
    "Each page shows how the fix works.",
    '<div class="btns">' + btn("Fix my churn", "/saas/") + btn("Grow my email revenue", FLOWS) + btn("Make money from my list", "/coaches/") + "</div>",
)

# ---------------------------------------------------------------- SAAS
# Reader: problem aware. Lead: problem-solution, opens on a real customer line.
SAAS = hero(
    '"I bought the app and then never opened it again."',
    "A real SaaS customer said that. Some of your users think it too. Retention Rules finds where they drop off and writes the emails that bring them back.",
    btn("Book a call", BOOK), "For SaaS founders",
) + narrow(
    "<h2>Where the money leaks.</h2>" + ticks(
        "Trials end and no sale comes.",
        "Users pay, then never set up the app.",
        "People sign up for a webinar, then go quiet.",
        "Your list only hears from you when you launch.",
    ) + "<p>You paid to get each of these people. Each one is still on your list.</p>"
) + sec('<div class="wrap"><div class="sec-head"><h2>How the work runs.</h2></div>' + steps3(
    ("Read the chart", "I read your sales calls, support tickets and customer replies. Then I check the revenue by email."),
    ("Find the leak", "Within 48 hours, you get 3 to 5 leaks. Each one is named. The audit is free."),
    ("Fix it", "I write the emails in your voice. We launch them. Then we check the numbers."),
) + '</div>', "tint") + narrow(
    "<h2>What gets built.</h2>" + ticks(
        "<strong>Welcome emails</strong> that get a new user to the first win.",
        "<strong>Trial and cart emails</strong> for people who were close to buying.",
        "<strong>Webinar follow-up</strong> for people who showed up and did not buy.",
        "<strong>Launch and promo emails</strong> that give people a reason to buy now.",
    )
) + sec('<div class="wrap"><div class="sec-head"><h2>What this did for one coaching app company.</h2></div>' + stats(
    ("$2.5M", "in email revenue"),
    ("$13 to $27", "revenue per lead, on the same traffic"),
    ("$1.11M", "from webinar follow-up emails"),
    note='<a href="/case-studies/saas/">Read how it happened</a>',
) + '</div>') + narrow(
    "<h2>Is this a fit?</h2>" + ps(
        "This fits a SaaS business doing $250K to $1M a year, with real users and a list.",
        "It does not fit a product with no users yet. There is no chart to read.",
    ) + "<h2>Questions.</h2>" + faq(
        ("What happens on the call?", "We look at your funnel. Then I go find the leaks. You get them within 48 hours."),
        ("What does the audit cost?", "It is free. You keep the list of leaks, even if we never work together."),
        ("What does the fix cost?", "You get a price after the audit, once we both know how big the leaks are."),
    )
) + cta(
    "Find out what your users are telling you.",
    "Book a call and get 3 to 5 leaks within 48 hours.",
    btn("Book a call", BOOK),
)

# ---------------------------------------------------------------- COACHES
# Reader: solution aware. Lead: promise lead (Muddassir's headline), then explain the offer.
COACHES = hero(
    "Generate an extra $20,000 to $200,000 within 10 days with my Post-paid Promo Campaigns.",
    "No retainer. No setup fee. You pay only from the sales the campaign makes.",
    btn("Book a call", BOOK_COACH), "For coaches and experts",
) + narrow(
    "<h2>What is a Post-paid Promo Campaign?</h2>" + ps(
        "It means I come up with the idea, write the campaign and launch it for you.",
        "It runs on your email list and your socials.",
        "I work on commission only.",
        "You pay nothing upfront. If the promo makes no sales, you pay nothing at all.",
    )
) + sec('<div class="narrow"><h2>What you get.</h2>' + ticks(
    "<strong>The idea.</strong> A real reason for your people to buy this week.",
    "<strong>The emails and social posts.</strong> All of it is written in your voice.",
    "<strong>The launch.</strong> I load it into your email platform and get it live.",
    "<strong>A page check.</strong> I can review your sales page before the promo starts.",
) + '</div>', "tint") + narrow(
    "<h2>Three kinds of promo.</h2>" + ticks(
        "<strong>Seasonal.</strong> Black Friday, Christmas, the New Year.",
        "<strong>Personal.</strong> Your birthday or your years in business.",
        "<strong>Business.</strong> A launch, a new bonus or an open door to your program.",
    ) + "<p>We pick the one that fits your month.</p>"
    + "<h2>How it works.</h2>" + steplist(
        ("We talk.", "On the call, we go over your list, your offer and your dates."),
        ("I build the promo.", "I pick the idea and write the copy. You choose the product with me."),
        ("You read it.", "That is your only job. You can say no at any time. The risk is on me."),
        ("We warm up the list.", "A few short emails get your people ready."),
        ("The promo runs.", "It goes live for 5 to 7 days."),
        ("You get paid first.", "When it ends, we look at the sales. I bill my commission on the cash you got."),
    ) + "<h2 >What stays yours.</h2>" + ps(
        "I only earn on sales from my promo, during the promo.",
        "Every sale after it ends is yours. Every upsell is yours too.",
    )
) + sec('<div class="wrap"><div class="sec-head"><h2>What a promo can do.</h2><p>Black Friday for one coaching app company, three years running.</p></div>' + stats(
    ("$168,314", "in 2023"),
    ("$256,096", "in 2024"),
    ("$190,950", "in 2025"),
    note='<a href="/case-studies/coaches/">Read the case study</a>',
) + '</div>', "tint") + narrow(
    "<h2>Is this for you?</h2>" + ticks(
        "You are a coach or expert with an email list or a real following.",
        "You sell a program that sells without you on a call.",
        "Your people already trust you.",
    ) + "<p>If you have no list and no following yet, this will not work. A promo needs people to talk to.</p>"
    + "<h2>Questions.</h2>" + faq(
        ("What does it cost?", "Nothing upfront. I take a commission on the sales from the promo. We go over the numbers on the call."),
        ("What if it makes no sales?", "You owe me nothing."),
        ("Will this burn out my list?", "No. Each email gives people something, so even those who do not buy are glad they read it."),
        ("Do you build sales pages?", "No. I write the promo and review your page. The page stays yours."),
        ("How much work is it for me?", "You read the copy and say yes or no."),
    )
) + cta(
    "See what your list can do in 10 days.",
    "Book a call. We will look at your list and your offer, and pick your first promo.",
    btn("Book a call", BOOK_COACH),
    "The range is a goal and depends on your list, your offer and your audience. It is not a guarantee.",
)

# ---------------------------------------------------------------- CASE STUDIES
CASES = hero(
    "The work, with the numbers.",
    "One case study for each kind of business. Client names stay private. The numbers are real.",
) + sec('<div class="wrap"><div class="doors">' + door(
    "SaaS", "A coaching app company took revenue per lead from $13 to $27 on the same traffic.", "See how leads doubled in value", "/case-studies/saas/"
) + door(
    "Ecommerce", "A readings brand took its open rate from 10% to 34%. The list and the offers stayed the same.", "See how opens hit 34%", "/case-studies/ecommerce/"
) + door(
    "Coaches", "Three Black Friday promos brought in $615,360 from a list of coaches.", "See how promos made $615,360", "/case-studies/coaches/"
) + '</div></div>', "tint")

CASE_SAAS = hero(
    "A coaching app company doubled revenue per lead on the same traffic.",
    "Each lead brought in $13. The goal was to earn more from each one.",
    btn("Book a call", BOOK), "SaaS case study",
) + sec('<div class="wrap">' + stats(
    ("$13 to $27", "revenue per lead"),
    ("$2.5M", "in email revenue"),
    ("$1.13M", "in email revenue in 2024, up from $547K in 2023"),
) + '</div>', "tint") + narrow(
    "<h2>The client.</h2>" + ps(
        "This company sells an app to coaches.",
        "Its founder ran a live workshop every Friday.",
        "I worked there as senior copywriter and wrote the emails.",
    ) + "<h2>Reading the chart.</h2>" + ps(
        "Before the emails changed, the research did.",
    ) + ticks(
        "I sat in on more than 20 sales calls and took down the words people used.",
        "I read the support tickets.",
        "I sent a short email with two questions to the list, again and again.",
        "After each Friday workshop, I logged new pains and doubts.",
    ) + "<p>All of it went into one place: what people want, what they fear and why they say no. Each email started there.</p>"
    + "<h2>Finding the leak.</h2>" + ps(
        "The biggest money sat in the days after a webinar.",
        "So I went to work on the follow-up emails.",
    ) + figs(
        ("Webinar follow-up emails", "$1.11M"),
        ("Promo emails", "$643K"),
        ("Black Friday emails", "$615K"),
    ) + "<h2>The fix.</h2>" + ticks(
        "The list got split into groups, so people got emails that fit them.",
        "The message got sharper and used the customers' own words.",
        "The emails got a voice that readers knew.",
    ) + "<h2>The result.</h2>" + ps(
        "Revenue per lead went from $13 to $27.",
        "Email brought in $547K in 2023, then $1.13M in 2024.",
        "The traffic stayed the same. The leads became worth twice as much.",
    ) + '<div style="margin-top:56px">' + quote(
        "[He] has been a key player in crafting some of [our] most impactful marketing campaigns.",
        "Founder of the company",
    ) + "</div>"
) + cta(
    "Find the leak in your business.",
    "Book a call and get 3 to 5 leaks within 48 hours.",
    btn("Book a call", BOOK),
)

CASE_COACH = hero(
    "Three Black Friday promos. $615,360.",
    "One list of coaches. One promo window a year. Here is what those emails did.",
    btn("Book a call", BOOK_COACH), "Coaches case study",
) + narrow(
    "<h2>The numbers.</h2>" + figs(
        ("Black Friday 2023", "$168,314"),
        ("Black Friday 2024", "$256,096"),
        ("Black Friday 2025", "$190,950"),
        ("Total", "$615,360"),
    ) + "<p>The 2024 promo was the best. It made $256,096 in 30 days.</p>"
    + "<h2>The client.</h2>" + ps(
        "This is a coaching app company. Its buyers are coaches.",
        "The founder ran live workshops, so the list knew the founder well.",
    ) + "<h2>What these emails did.</h2>" + "<p>A weak promo says the same thing again and again. It says the sale ends soon. These emails did not repeat the same discount.</p>" + "<p>Each email had its own job.</p>" + ticks(
        "<strong>The offer.</strong> One email made the deal plain.",
        "<strong>Proof.</strong> Another showed that it works.",
        "<strong>Doubts.</strong> Another took on the reasons people say no.",
        "<strong>Timing.</strong> Another gave a reason to buy now.",
    ) + "<p>Readers got something new each time.</p>"
    + "<h2>What this means for you.</h2>" + ps(
        "This was in-house work. I was on the team.",
        "A Post-paid Promo Campaign runs the same way on your list. The one change is how you pay. You pay nothing upfront.",
    ) + '<div style="margin-top:56px">' + quote(
        "Our Head of Acquisition even referred to his work as outstanding... during what he called the 'best week of the year in marketing.'",
        "LinkedIn recommendation, April 14, 2026",
    ) + "</div>"
) + cta(
    "See what a promo can do for your list.",
    "Book a call. We will look at your list and your offer.",
    btn("Book a call", BOOK_COACH),
)

CASE_ECOM = hero(
    "Same list. Same offers. The open rate went from 10% to 34%.",
    "An online readings brand had a list that barely opened its emails. The writing was the one thing that changed.",
    btn("Grow my email revenue", FLOWS), "Ecommerce case study",
) + sec('<div class="wrap">' + stats(
    ("10% to 34%", "top open rate"),
    ("Under 1% to 3%", "click rate on the best sends"),
    ("5", "sends in one sprint, each with a new idea"),
) + '</div>', "tint") + narrow(
    "<h2>The client.</h2>" + ps(
        "This brand sells readings online to women aged 35 to 60.",
        "Many of them were tired of dating.",
    ) + "<h2>The leak.</h2>" + ps(
        "The old emails led with the offer.",
        "The open rate sat at 10%.",
    ) + "<h2>The fix.</h2>" + "<p>The new emails led with a story. Each of the five used a new idea.</p>" + ticks(
        "A tale of two people with one small difference.",
        "A mistake, told as a confession.",
        "A hook about a famous name.",
        "A take on dating apps that broke the pattern.",
        "A quiet email about the fear of being alone.",
    ) + ps(
        "The subject lines stopped selling and started to raise a question.",
        "The offer came in the last third of each email.",
    ) + "<h2>The result.</h2>" + ps(
        "The top open rate went from 10% to 34%.",
        "The best sends hit a 3% click rate, up from under 1%.",
        "The list, the offers and the platform stayed the same.",
    )
) + cta(
    "Get emails that bring buyers back.",
    "See the flows, the price and the guarantee.",
    btn("Grow my email revenue", FLOWS),
)

# ---------------------------------------------------------------- ABOUT
# Story template: Pixar Story Spine (Kenn Adams, 1991). Once upon a time, every day,
# until one day, because of that, because of that, until finally, ever since then.
ABOUT = hero(
    "I left medicine in 2019. One rule came with me.",
    "It is the rule behind every job at Retention Rules.",
    "", "The story",
) + narrow(
    ps(
        "In 2018, I graduated from medical school.",
        "Doctors live by one rule. You find out what is wrong before you treat it.",
        "In 2019, I left medicine and went into marketing.",
        "Marketing ran on the opposite rule. Sales dip, so the business buys more ads. Nobody checks the chart.",
        "Then I joined a coaching app company as senior copywriter.",
        "I did what a doctor does. I read the chart.",
        "I sat in on more than 20 sales calls. I read the support tickets. I asked the list two questions by email.",
        "The chart pointed to one spot. The biggest money sat in the days after a webinar.",
        "So I went to work on those emails. They brought in $1.11M.",
        "Because of that, each lead became worth more. Revenue per lead went from $13 to $27 on the same traffic.",
        "Because of that, email grew from $547K in 2023 to $1.13M in 2024. In all, it brought in $2.5M.",
        "In April 2026, I left to build Retention Rules.",
        "Every job here starts the same way. Read the chart. Find the leak. Then fix it.",
    ) + '<div class="sig"><img src="/images/muddassir.png" alt="" width="64" height="64"><div><strong>Muddassir Abdur Rub</strong><span>Founder, ex doctor</span></div></div>'
) + sec('<div class="wrap"><div class="doors" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">'
        '<div class="door"><h3>Who this is for</h3>' + ticks(
            "Businesses at $250K to $1M a year.",
            "SaaS, ecommerce and coaches.",
            "A proven offer and a list or a customer base.",
        ) + '</div><div class="door"><h3>Who this is not for</h3>' + ticks(
            "Businesses with no sales yet.",
            "Businesses with no list and no customers.",
            "Agencies.",
        ) + '</div></div></div>', "tint") + narrow(
    quote("So much thought went into this project. Very refreshing to work with someone who thought like a marketer.", "Client review")
    + '<div style="margin-top:56px">' + quote("Hire him. Muddassir is one of the most intelligent and strategic humans I've ever worked with.", "Client review") + "</div>"
) + cta(
    "Let's read your chart.",
    "Book a call and get 3 to 5 leaks within 48 hours.",
    btn("Book a call", BOOK),
)

NOT_FOUND = hero(
    "This page moved.",
    "Pick your business and you will find what you came for.",
) + sec('<div class="wrap"><div class="doors">' + door(
    "SaaS", "If you're a SaaS founder losing more than 5% of your customers to churn each month, this is for you.", "Fix my churn", "/saas/"
) + door(
    "Ecommerce", "If you run an ecommerce brand and email brings in less than 20% of your revenue, this is for you.", "Grow my email revenue", FLOWS
) + door(
    "Coaches", "If you're a coach who wants to make more money from the subscribers you already have, this is for you.", "Make money from my list", "/coaches/"
) + '</div></div>', "tint")

PAGES = {
    "/": ("Retention Rules", "Most growth comes from the customers you already have. Retention Rules helps businesses at $250K to $1M a year earn more from the leads and customers they already paid for.", HOME, None),
    "/saas/": ("Retention for SaaS", "Retention Rules finds where your SaaS users drop off and writes the emails that bring them back. Book a call and get 3 to 5 leaks within 48 hours.", SAAS, BOOK),
    "/coaches/": ("Post-paid Promo Campaigns for Coaches", "Generate an extra $20,000 to $200,000 within 10 days with Post-paid Promo Campaigns. No retainer. No setup fee. Commission only.", COACHES, BOOK_COACH),
    "/case-studies/": ("Case Studies", "SaaS, ecommerce and coaching case studies from Retention Rules, with the numbers.", CASES, None),
    "/case-studies/saas/": ("SaaS Case Study", "How a coaching app company took revenue per lead from $13 to $27 on the same traffic.", CASE_SAAS, BOOK),
    "/case-studies/coaches/": ("Coaches Case Study", "Three Black Friday promos brought in $615,360 from a list of coaches.", CASE_COACH, BOOK_COACH),
    "/case-studies/ecommerce/": ("Ecommerce Case Study", "Same list, same offers. How an online readings brand took its open rate from 10% to 34%.", CASE_ECOM, None),
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
    "/dtc-retention/moon-lamp/": FLOWS,
    "/dtc-retention/oshun/": FLOWS,
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
    "/product-marketing/nurture-revenue/": "/case-studies/saas/",
    "/product-marketing/positioning-pivot/": "/case-studies/saas/",
    "/product-marketing/webinar-followups/": "/case-studies/saas/",
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
