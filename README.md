# 🧠 AI & Tech Weekly Brief

An automated weekly briefing that turns raw tech headlines into a real, readable summary — written by an LLM, delivered straight to your inbox.

## What it does

Every Monday at 08:30 (Turkey time), this project automatically:

1. **Fetches top stories** from [Hacker News](https://news.ycombinator.com/)
2. **Fetches the latest AI articles** from [TechCrunch's AI section](https://techcrunch.com/category/artificial-intelligence/)
3. Sends all of that raw content to **Google's Gemini API**, with a prompt asking it to act as an analyst writing a briefing for a Product Manager
4. Emails the resulting summary — grouped by theme, focused on business impact, under 400 words

Unlike a plain list of headlines, this delivers an actual **written brief**, as if an analyst read everything for you.

## Why

Raw news feeds are noisy — dozens of headlines a day, most of them irrelevant to any one person's job. This project demonstrates a simple but powerful pattern: use an LLM as the last step in an automation pipeline to turn raw data into a judgment call, not just a list. For a Product Manager, that means less scrolling and a briefing that's already filtered for what matters.

## How it works

- **Language:** Python
- **Automation:** [GitHub Actions](https://github.com/features/actions) scheduled workflow (cron job)
- **AI summarization:** [Google Gemini API](https://ai.google.dev/) (`gemini-2.5-flash`, free tier)
- **Email delivery:** Gmail SMTP
- **No server required** — runs entirely on GitHub's free infrastructure

## Architecture

```
.github/workflows/brief.yml   → Defines the weekly schedule (cron)
brief.py                      → Fetches data, calls Gemini, sends the email
requirements.txt              → Python dependencies
```

## Setup

If you want to run your own copy of this brief:

1. Fork or clone this repository
2. Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com/) — no credit card required
3. Go to **Settings → Secrets and variables → Actions** and add the following repository secrets:

   | Secret | Description |
   |---|---|
   | `GEMINI_API_KEY` | Your free Gemini API key from Google AI Studio |
   | `MAIL_FROM` | The Gmail address the brief will be sent from |
   | `MAIL_PASSWORD` | A Gmail [App Password](https://myaccount.google.com/apppasswords) (not your regular password) |
   | `MAIL_TO` | The email address that should receive the brief |

4. That's it — the workflow will run automatically every Monday. You can also trigger it manually from the **Actions** tab using **Run workflow**.

## Customization

- **Change the schedule:** edit the `cron` expression in `.github/workflows/brief.yml` ([crontab.guru](https://crontab.guru/) is helpful for this)
- **Change the prompt:** edit the `prompt` string inside `summarize_with_gemini()` in `brief.py` — this is the easiest way to change tone, length, focus area, or target audience
- **Add or remove sources:** each source is its own function in `brief.py` (`get_hn_top_stories`, `get_techcrunch_ai`) — add a new function following the same pattern to pull in another source, then include its output in `raw_content` inside `main()`

## Notes

- All credentials are stored securely as GitHub Actions secrets — nothing is hardcoded in the source code.
- If a data source or the Gemini API call fails, the script still sends an email with whatever it could gather rather than failing silently.
- The Gemini free tier has rate limits (requests per minute/day) — for a weekly job like this one, usage stays comfortably within the free quota.
