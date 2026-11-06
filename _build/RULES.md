# retentionrules.com site rules

Set by Muddassir on November 6, 2026.

## Copy and design
- Brand first. No big photos of him. Only a small round photo next to the story.
- Only story facts that relate to the work. The 2022 debt story stays off the site.
- Looks like an agency without saying so. Never name a client. Never show the commission rate.
- White space between every sentence. Clear readable messaging comes before any effect. No animation.
- One page, one type of CTA. Home and Case Studies route to further pages. Inner pages book a call. Ecommerce goes to flows.retentionrules.com, whose page is not edited unless he asks.
- Before each routing button, one or two lines call out the buyer in their own words (SaaS: churn. Ecommerce: email share of revenue. Coaches: money from existing subscribers). The button names the fix. Never a label like "See SaaS".
- Every page must pass the copy gate. `python3 _build/build.py` checks the grade.
- Story template: Pixar Story Spine, from storytelling-lecture.html.

## Editing
Copy lives in `_build/build.py`. Change it, run it, and all pages update. Do not edit the generated HTML.

## Go-live status
Done November 7, 2026, except the www record in step 3. www.retentionrules.com still points at Substack and fails. GoDaddy asks for a new email code on every DNS save, so warn him first. Current rollback values: ../retentionrules-dns-snapshot-2026-11-07.txt.

## Go-live order used (needs his OK at each step)
1. Push this repo (Muddassir91/retentionrules-apex). DNS still points at GoDaddy, so nothing shows yet.
2. In GoDaddy, remove the Domain Forwarding on retentionrules.com. He handles the one-time password.
3. Set apex A records to 185.199.108.153, .109.153, .110.153, .111.153. Set www CNAME to muddassir91.github.io. Leave flows and letters alone.
4. Turn on Enforce HTTPS in GitHub Pages once the certificate is ready. Rollback: retentionrules-dns-snapshot-2026-08-17.txt.
5. Copy ../RetentionRules-Main-Site-abdurrub-redirects/ over the abdurrub-com repo and push. Do not touch its CNAME or the abdurrub.com Google MX records. CSOS, creative strategy, survey and story template pages stay as they are unless he says otherwise.
6. Retest share previews on the live URLs.
