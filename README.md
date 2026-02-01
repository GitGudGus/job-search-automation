# 🎯 Job Search Automation

> **Stop wasting hours on job boards. Let Python find jobs for you.**

Automatically scrape Indeed & LinkedIn, filter by your keywords, and get instant alerts when new jobs match your criteria.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ What It Does

🔍 **Auto-searches job boards** (Indeed, LinkedIn)  
⚡ **Instant alerts** when new jobs are posted  
🎯 **Smart filtering** (include/exclude keywords)  
📊 **Tracks everything** in CSV (no duplicates)  
⏰ **Runs on autopilot** (hourly, daily, or custom)

**Perfect for:**
- Job seekers tired of manual searching
- Career switchers looking for entry-level roles
- Anyone who wants to apply before the competition

---

## 🚀 Quick Start

### 1. Install

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure

```bash
python3 job_tracker.py --setup
```

Edit `config.json` with your job search preferences:

```json
{
  "searches": [
    {
      "keywords": "python developer",
      "location": "Remote",
      "sources": ["linkedin"]
    }
  ],
  "excluded_keywords": ["senior", "manager"]
}
```

### 3. Run

```bash
python3 job_tracker.py
```

---

## 📋 Example Output

```
🚀 JOB TRACKER STARTING
🔍 Searching LinkedIn: python developer in Remote
   ✓ Extracted 12 new jobs

📊 RESULTS:
   Found: 12 total jobs
   New: 8 after filtering

📋 PREVIEW:
   • Python Developer at TechCorp (LinkedIn)
   • Software Engineer at StartupXYZ (LinkedIn)
   • Backend Developer at BigCo (LinkedIn)

✅ COMPLETE
```

All jobs saved to `jobs_data.csv` with direct apply links.

---

## ⚙️ Configuration Examples

### Filter by Experience Level

```json
{
  "excluded_keywords": ["senior", "lead", "principal", "5+ years"]
}
```

### Multiple Job Searches

```json
{
  "searches": [
    {
      "keywords": "data analyst",
      "location": "New York"
    },
    {
      "keywords": "python developer",
      "location": "Remote"
    }
  ]
}
```

### Email Alerts (Optional)

Get notified instantly via email:

```json
{
  "email_alerts": {
    "enabled": true,
    "from_email": "your-email@gmail.com",
    "password": "your-gmail-app-password",
    "to_email": "your-email@gmail.com"
  }
}
```

---

## 🤔 Common Questions

**Is this legal?**  
Yes. It only accesses public job listings that anyone can view.

**Will it auto-apply to jobs?**  
No. It finds jobs and alerts you. You still apply manually (as you should—personalized applications get better results).

**How do I avoid duplicates?**  
The script automatically tracks which jobs you've already seen.

**Can I customize it?**  
Absolutely. MIT licensed—modify it however you want.

---

## 🛠️ Need Help?

**Installation issues?** Check that Python 3.11+ is installed.  
**Not finding jobs?** Broaden your keywords or try different job boards.  
**Want more features?** Fork the repo and extend it!

---

## 💼 Professional Setup Service

**Don't want to deal with installation and configuration?**

I offer custom setup services:

- ✅ **Basic Setup ($100)** - I configure it for your exact job search
- ✅ **Premium Setup ($200)** - Hosted version + email/Discord alerts + 30-day support
- ✅ **Business Package ($500+)** - White-label solution for recruiters/agencies

**Contact:** [https://www.fiverr.com/s/jjD5m0w] |

---

## 📄 License

MIT License - Use it, modify it, sell it. Do whatever you want.

---

## ⭐ Star This Repo

If this saved you time, give it a star! It helps others find it.

**Built for job seekers who work smarter, not harder.**
