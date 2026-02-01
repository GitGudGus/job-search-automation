# 🎯 Job Application Tracker & Alert System

**Automatically find jobs, filter by your criteria, and get instant alerts.**

Stop manually checking job boards. This script does it for you.

---

## What It Does

✅ Scrapes **Indeed** and **LinkedIn** for jobs  
✅ Filters by keywords (required + excluded)  
✅ Saves all results to CSV  
✅ Sends email alerts for new matches  
✅ Runs automatically on a schedule  

---

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install browser for automation
playwright install chromium
```

### 2. Setup Configuration

```bash
python job_tracker.py --setup
```

This creates `config.json` - edit it with your preferences.

### 3. Run It

```bash
python job_tracker.py
```

---

## Configuration Guide

Edit `config.json` to customize your job search.

### Basic Example

```json
{
  "searches": [
    {
      "keywords": "python developer",
      "location": "Remote",
      "sources": ["indeed", "linkedin"]
    }
  ],
  "required_keywords": ["python", "remote"],
  "excluded_keywords": ["senior", "manager"],
  "email_alerts": {
    "enabled": false
  }
}
```

### Multiple Searches

```json
{
  "searches": [
    {
      "keywords": "data analyst",
      "location": "New York",
      "sources": ["indeed"]
    },
    {
      "keywords": "machine learning",
      "location": "Remote",
      "sources": ["linkedin"]
    }
  ]
}
```

### Filtering Options

**required_keywords**: Job title must contain at least ONE of these  
**excluded_keywords**: Job title must NOT contain ANY of these

```json
{
  "required_keywords": ["python", "javascript", "developer"],
  "excluded_keywords": ["senior", "lead", "principal", "manager", "director"]
}
```

---

## Email Alerts Setup

Get notified immediately when new jobs are found.

### Step 1: Enable Gmail App Password

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Enable 2-Factor Authentication
3. Generate an "App Password" for mail
4. Copy the 16-character password

### Step 2: Configure Email

```json
{
  "email_alerts": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "youremail@gmail.com",
    "password": "your-16-char-app-password",
    "to_email": "youremail@gmail.com"
  }
}
```

---

## Automation (Run Every Hour)

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 1 hour
4. Action: Start a program
   - Program: `python`
   - Arguments: `C:\path\to\job_tracker.py`
   - Start in: `C:\path\to\`

### Mac/Linux (Cron)

```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * cd /path/to/script && /usr/bin/python3 job_tracker.py
```

### Docker (Advanced)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN playwright install chromium --with-deps

CMD python job_tracker.py
```

---

## Output Format

Jobs are saved to `jobs_data.csv`:

| job_id | title | company | location | url | source | found_date |
|--------|-------|---------|----------|-----|--------|------------|
| indeed_abc123 | Python Developer | TechCorp | Remote | https://... | Indeed | 2024-01-15 10:30:00 |

---

## Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### "Config file not found"
```bash
python job_tracker.py --setup
```

### Email not sending
- Check Gmail app password (not regular password)
- Enable "Less secure app access" if needed
- Try port 465 instead of 587

### No jobs found
- Broaden keywords
- Check spelling
- Remove too many excluded keywords

---

## Advanced Customization

### Add More Job Boards

Edit the `JobTracker` class to add scrapers for:
- ZipRecruiter
- Glassdoor  
- Remote.co
- AngelList

### Discord Webhooks (Instead of Email)

```python
import requests

def send_discord_alert(jobs):
    webhook_url = "YOUR_WEBHOOK_URL"
    message = f"🎯 {len(jobs)} new jobs found!\n\n"
    
    for job in jobs:
        message += f"**{job['title']}** at {job['company']}\n{job['url']}\n\n"
    
    requests.post(webhook_url, json={"content": message})
```

### Slack Notifications

```python
from slack_sdk import WebClient

def send_slack_alert(jobs):
    client = WebClient(token="YOUR_SLACK_TOKEN")
    
    for job in jobs:
        client.chat_postMessage(
            channel="#job-alerts",
            text=f"New job: {job['title']} at {job['company']}\n{job['url']}"
        )
```

---

## FAQ

**Q: Is this legal?**  
A: Yes. Public job listings are publicly accessible. Don't violate rate limits.

**Q: Will this auto-apply to jobs?**  
A: No. This finds and alerts. YOU apply manually.

**Q: Can I sell this?**  
A: Yes. MIT License. Customize and charge what you want.

**Q: How do I avoid duplicates?**  
A: The script tracks seen job IDs automatically.

---

## Support

- **Issues**: Check existing job IDs in `jobs_data.csv`
- **Rate Limits**: Add `time.sleep()` between searches
- **Customization**: Modify `job_tracker.py` as needed

---

## License

MIT - Do whatever you want with it.

---

**Built for job seekers who are tired of manual searching.**

Run it once. Get alerts forever.
