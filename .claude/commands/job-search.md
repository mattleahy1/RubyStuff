Search for new executive engineering job opportunities matching Matt Leahy's profile. Do the full search and analysis right now in this session.

## Candidate profile (from resume.txt)
- **Name:** Matthew Leahy, M.B.A.
- **Current role:** Senior Director of Software Engineering, Walmart Global Tech (Agentic AI, 200+ engineer org, $40B Pharmacy business)
- **Previous:** Sr. Director Microsoft Azure ($75M budget, 100+ SDEs, 320B rows/day telemetry), Sr. SDM Amazon AWS (Vetting platform)
- **Specializations:** Agentic AI, LLMs, multi-agent systems, hyperscale cloud (AWS/Azure/GCP), large eng org leadership
- **Target TC:** $700,000 – $2,000,000 annually
- **Target locations:** Seattle/Bellevue, San Francisco Bay Area, Los Angeles, San Diego, Portland — or fully Remote
- **Target seniority:** VP Engineering, SVP Engineering, CTO, Head of Engineering, Distinguished Engineer, or equivalent Director-level+

## Step 1 — Fetch job listings

Use WebFetch to query the Greenhouse and Lever public APIs for each company below. These APIs require no authentication.

**Greenhouse API format:** `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs`

Check these Greenhouse slugs (fetch 8–10 at a time):
anthropic, openai, databricks, stripe, airbnb, coinbase, figma, notion, cloudflare, snowflake, confluent, elastic, mongodb, brex, rippling, ramp, plaid, robinhood, doordash, instacart, lyft, waymo, cohere, perplexity, groq, scaleai, glean, moveworks, cresta, writer, anyscale, replit, huggingface, vanta, drata, retool, vercel, linear, mercury, amplitude, mixpanel, segment, attentive, benchling, asana, pagerduty, okta, zendesk, twilio

**Lever API format:** `https://api.lever.co/v0/postings/{slug}?mode=json`

Check these Lever slugs:
netflix, square, dropbox, box, lattice, coda, weights-and-biases, modal-labs, modern-treasury, persona, sardine, finix

## Step 2 — Filter listings

From all fetched jobs, keep only those where:
- **Title** contains any of: VP, Vice President, SVP, Head of Engineering, Head of Software, Head of AI, CTO, Chief Technology, Distinguished Engineer, Fellow, Senior Director, Director of Engineering, Director of AI, Director of Platform, Director of Infrastructure
- **Location** is: Seattle, Bellevue, San Francisco, Bay Area, San Jose, Palo Alto, Los Angeles, San Diego, Portland, Remote, Distributed — OR location is blank/unspecified (Claude will judge)

## Step 3 — Score and analyze each listing

For each filtered listing, score it 1–10 against Matt's profile:

| Score | Meaning |
|-------|---------|
| 9–10 | Near-perfect: right seniority, right location/remote, company pays $700K+ at this level, strong background fit |
| 7–8 | Strong: most criteria met, minor gaps |
| 5–6 | Decent: worth reviewing, some uncertainty |
| ≤ 4 | Skip — don't include in report |

Also assign TC likelihood: **Very Likely** / **Likely** / **Possible** / **Unlikely**

Companies very likely to pay $700K+ at VP level: Anthropic, OpenAI, Google, Meta, Apple, Amazon, Microsoft, Databricks, Stripe, Coinbase, Snowflake, Airbnb, Lyft, Waymo, Cloudflare, Netflix, and well-funded AI startups with $500M+ raised.

## Step 4 — Check for previously seen jobs

Read the file `results/seen_jobs.json` if it exists. Skip any job IDs already in that list.

## Step 5 — Output the report

Print a clean Markdown report:

```
# Job Search Report — [today's date]
**New listings scored ≥ 5:** N

---

## [Job Title]
**[Company]** · [Location]
Fit: [score]/10 | TC: [likelihood] | Remote: Yes/No
[2-sentence rationale]
Apply: [URL]

---
```

Sort by score descending. Include only scores ≥ 5.

## Step 6 — Update seen_jobs.json

After outputting the report, update `results/seen_jobs.json` with all job IDs from this run (both reported and skipped) so they won't appear in future searches. Write the file and commit it.
