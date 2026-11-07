# retentionrules.com site rules

Set by Muddassir on November 6, 2026.

## Copy and design
- Design system comes from flows.retentionrules.com: Inter Display, one italic Instrument Serif phrase per headline, teal and mint, centred section openers. Set November 7, 2026.
- Every claim shows proof. Case studies carry real screenshots, and numbers match the screenshot exactly (total email revenue $2,442,707, not $2.5M). The overall total is $4M+. Never $40M.
- This site may show real client names and logos. Social posts still may not. Set November 7, 2026.
- Only use testimonials that have a screenshot. Only use real logo files or plain text wordmarks. Never call an email sample his work until he confirms it.
- Page order: hero, trust, proof, problem, method, cases, testimonials, fit, FAQ, CTA. Case studies: result, client, problem, fix, result, proof, next step.
- Brand first. No big photos of him. Only a small round photo next to the story.
- Only story facts that relate to the work. The 2022 debt story stays off the site.
- Looks like an agency without saying so. Never show the commission rate.
- White space between every sentence. Clear readable messaging comes before any effect. No animation.
- One page, one type of CTA. Home and Case Studies route to further pages. Inner pages book a call. Ecommerce goes to flows.retentionrules.com, whose page is not edited unless he asks.
- Before each routing button, one or two lines call out the buyer in their own words (SaaS: churn. Ecommerce: email share of revenue. Coaches: money from existing subscribers). The button names the fix. Never a label like "See SaaS".
- Routing choices are three fully clickable cards, never a row of buttons with a shared headline. Each card lets the reader self-identify first ("I run a SaaS"), then names the problem in their words. Set by him on November 7, 2026.
- A button says what happens when you click it. No clever labels like "Find my leak". Set by him on November 7, 2026.
- The founder story is his own words, about the reader and not a career timeline: doctor turned marketer, AI makes starting easy and growing hard, failure rates, retention, the sanctuary mission. Failure rates come from BLS Table 7; recheck when a new cohort is out. Set by him on November 7, 2026.
- Buttons are raised and pressable like dropkickcopy.com: 12px corners, darker 4px bottom edge, bold uppercase, brand teal. Cards are flat: a dark top rule, no box, no rounded corners, no shadow. Set by him on November 7, 2026.
- Every page must pass the copy gate. `python3 _build/build.py` checks the grade.

## Editing
Copy lives in `_build/build.py`. Change it, run it, and all pages update. Do not edit the generated HTML.

## Go-live status
Done November 7, 2026. One gap: the www DNS record points to GitHub and http://www redirects to the main domain, but the GitHub certificate covers only retentionrules.com, so https://www fails. Removing and re-adding the Pages domain twice did not add www. GoDaddy asks for a new email code on every DNS save, so warn him first. Rollback values from before the move: ../retentionrules-dns-snapshot-2026-11-07.txt.

## Go-live order used (needs his OK at each step)
1. Push this repo (Muddassir91/retentionrules-apex). DNS still points at GoDaddy, so nothing shows yet.
2. In GoDaddy, remove the Domain Forwarding on retentionrules.com. He handles the one-time password.
3. Set apex A records to 185.199.108.153, .109.153, .110.153, .111.153. Set www CNAME to muddassir91.github.io. Leave flows and letters alone.
4. Turn on Enforce HTTPS in GitHub Pages once the certificate is ready. Rollback: retentionrules-dns-snapshot-2026-08-17.txt.
5. Copy ../RetentionRules-Main-Site-abdurrub-redirects/ over the abdurrub-com repo and push. Do not touch its CNAME or the abdurrub.com Google MX records. CSOS, creative strategy, survey and story template pages stay as they are unless he says otherwise.
6. Retest share previews on the live URLs.
