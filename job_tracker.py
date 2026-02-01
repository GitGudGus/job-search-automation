#!/usr/bin/env python3
"""
Job Application Tracker & Alert System v2.0
Improved with stealth mode and better error handling
"""

import json
import csv
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import re

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("⚠️  Playwright not installed. Run: pip3 install playwright && playwright install")
    exit(1)


class JobTracker:
    def __init__(self, config_file="config.json"):
        """Initialize tracker with configuration"""
        self.config = self.load_config(config_file)
        self.data_file = Path("jobs_data.csv")
        self.seen_jobs = self.load_existing_jobs()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        if not Path(config_file).exists():
            print(f"❌ Config file '{config_file}' not found!")
            print("Run setup first: python3 job_tracker.py --setup")
            exit(1)
            
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def load_existing_jobs(self):
        """Load previously seen job IDs to avoid duplicates"""
        seen = set()
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    seen.add(row['job_id'])
        return seen
    
    def create_stealth_browser(self, p):
        """Create a browser that looks more human"""
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        return browser, context
    
    def scrape_indeed(self, keywords, location):
        """Scrape Indeed for jobs with improved reliability"""
        jobs = []
        search_url = f"https://www.indeed.com/jobs?q={keywords.replace(' ', '+')}&l={location.replace(' ', '+')}"
        
        print(f"🔍 Searching Indeed: {keywords} in {location}")
        
        with sync_playwright() as p:
            browser, context = self.create_stealth_browser(p)
            page = context.new_page()
            
            try:
                # Longer timeout and load strategy
                page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                
                # Wait for job listings to appear
                try:
                    page.wait_for_selector('.job_seen_beacon, .jobsearch-ResultsList', timeout=10000)
                except:
                    print("⚠️  Indeed may be showing CAPTCHA or blocking. Trying alternative selectors...")
                
                time.sleep(3)  # Let page settle
                
                # Try multiple selector strategies
                job_cards = page.query_selector_all('.job_seen_beacon')
                if not job_cards:
                    job_cards = page.query_selector_all('.jobsearch-ResultsList li')
                
                print(f"   Found {len(job_cards)} potential job cards")
                
                for i, card in enumerate(job_cards[:20]):  # Limit to first 20
                    try:
                        # Multiple selector strategies for title
                        title_elem = (card.query_selector('h2.jobTitle span') or 
                                     card.query_selector('h2.jobTitle a') or
                                     card.query_selector('h2'))
                        
                        company_elem = (card.query_selector('span[data-testid="company-name"]') or
                                       card.query_selector('.companyName'))
                        
                        location_elem = (card.query_selector('div[data-testid="text-location"]') or
                                        card.query_selector('.companyLocation'))
                        
                        link_elem = card.query_selector('h2.jobTitle a')
                        
                        if title_elem and company_elem:
                            # Extract job ID from link or use position
                            job_id = None
                            job_url = ""
                            
                            if link_elem:
                                href = link_elem.get_attribute('href') or ""
                                job_id_match = re.search(r'jk=([a-zA-Z0-9]+)', href)
                                if job_id_match:
                                    job_id = job_id_match.group(1)
                                    job_url = f"https://www.indeed.com/viewjob?jk={job_id}"
                                elif href.startswith('/'):
                                    job_url = f"https://www.indeed.com{href}"
                            
                            if not job_id:
                                job_id = f"indeed_{i}_{int(time.time())}"
                            
                            job = {
                                'job_id': f"indeed_{job_id}",
                                'title': title_elem.inner_text().strip(),
                                'company': company_elem.inner_text().strip(),
                                'location': location_elem.inner_text().strip() if location_elem else location,
                                'url': job_url,
                                'source': 'Indeed',
                                'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            # Skip if already seen
                            if job['job_id'] not in self.seen_jobs:
                                jobs.append(job)
                                self.seen_jobs.add(job['job_id'])
                    except Exception as e:
                        # Silently skip individual parsing errors
                        continue
                
            except Exception as e:
                print(f"⚠️  Indeed scraping issue: {str(e)[:100]}")
                print("   Tip: Indeed often blocks scrapers. Try running at different times or use LinkedIn only.")
            finally:
                context.close()
                browser.close()
        
        print(f"   ✓ Extracted {len(jobs)} new jobs from Indeed")
        return jobs
    
    def scrape_linkedin(self, keywords, location):
        """Scrape LinkedIn with improved parsing"""
        jobs = []
        # LinkedIn public job search
        keywords_encoded = keywords.replace(' ', '%20')
        location_encoded = location.replace(' ', '%20')
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords_encoded}&location={location_encoded}"
        
        print(f"🔍 Searching LinkedIn: {keywords} in {location}")
        
        with sync_playwright() as p:
            browser, context = self.create_stealth_browser(p)
            page = context.new_page()
            
            try:
                page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(4)
                
                # Scroll to load more jobs
                for _ in range(2):
                    page.evaluate("window.scrollBy(0, window.innerHeight)")
                    time.sleep(1)
                
                # Try multiple selectors
                job_cards = page.query_selector_all('div.base-card')
                if not job_cards:
                    job_cards = page.query_selector_all('li.jobs-search-results__list-item')
                
                print(f"   Found {len(job_cards)} potential job cards")
                
                for i, card in enumerate(job_cards[:20]):
                    try:
                        title_elem = (card.query_selector('h3.base-search-card__title') or
                                     card.query_selector('h3'))
                        
                        company_elem = (card.query_selector('h4.base-search-card__subtitle') or
                                       card.query_selector('a.hidden-nested-link') or
                                       card.query_selector('h4'))
                        
                        location_elem = card.query_selector('span.job-search-card__location')
                        
                        link_elem = (card.query_selector('a.base-card__full-link') or
                                    card.query_selector('a[href*="/jobs/view/"]'))
                        
                        if title_elem and company_elem and link_elem:
                            job_url = link_elem.get_attribute('href') or ""
                            
                            # Extract job ID more safely
                            job_id = None
                            job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
                            if job_id_match:
                                job_id = job_id_match.group(1)
                            else:
                                # Fallback: use timestamp
                                job_id = f"{i}_{int(time.time())}"
                            
                            job = {
                                'job_id': f"linkedin_{job_id}",
                                'title': title_elem.inner_text().strip(),
                                'company': company_elem.inner_text().strip(),
                                'location': location_elem.inner_text().strip() if location_elem else location,
                                'url': job_url if job_url.startswith('http') else f"https://www.linkedin.com{job_url}",
                                'source': 'LinkedIn',
                                'found_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            if job['job_id'] not in self.seen_jobs:
                                jobs.append(job)
                                self.seen_jobs.add(job['job_id'])
                    except Exception as e:
                        # Silently skip parsing errors
                        continue
                        
            except Exception as e:
                print(f"⚠️  LinkedIn scraping issue: {str(e)[:100]}")
            finally:
                context.close()
                browser.close()
        
        print(f"   ✓ Extracted {len(jobs)} new jobs from LinkedIn")
        return jobs
    
    def filter_jobs(self, jobs):
        """Filter jobs by keywords (required and excluded)"""
        required = [kw.lower() for kw in self.config.get('required_keywords', [])]
        excluded = [kw.lower() for kw in self.config.get('excluded_keywords', [])]
        
        filtered = []
        
        for job in jobs:
            title_lower = job['title'].lower()
            
            # Check excluded keywords first
            if any(ex in title_lower for ex in excluded):
                continue
            
            # Check required keywords (empty list = no filtering)
            if not required or any(req in title_lower for req in required):
                filtered.append(job)
        
        return filtered
    
    def save_jobs(self, jobs):
        """Save jobs to CSV file"""
        if not jobs:
            return
        
        file_exists = self.data_file.exists()
        
        with open(self.data_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['job_id', 'title', 'company', 'location', 'url', 'source', 'found_date']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for job in jobs:
                writer.writerow(job)
    
    def send_email_alert(self, jobs):
        """Send email alert with new jobs"""
        if not jobs or not self.config.get('email_alerts', {}).get('enabled', False):
            return
        
        email_config = self.config['email_alerts']
        
        # Build HTML email
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🎯 {len(jobs)} New Job(s) Found!</h2>
            <p>Found on {datetime.now().strftime('%Y-%m-%d at %I:%M %p')}</p>
            <hr>
        """
        
        for job in jobs:
            html_body += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #0066cc; background: #f5f5f5;">
                <h3 style="margin: 0; color: #0066cc;">{job['title']}</h3>
                <p style="margin: 5px 0;"><strong>{job['company']}</strong> - {job['location']}</p>
                <p style="margin: 5px 0;">Source: {job['source']}</p>
                <a href="{job['url']}" style="color: #0066cc;">View Job →</a>
            </div>
            """
        
        html_body += """
        </body>
        </html>
        """
        
        # Send email
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎯 {len(jobs)} New Jobs Found!"
            msg['From'] = email_config['from_email']
            msg['To'] = email_config['to_email']
            
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['from_email'], email_config['password'])
                server.send_message(msg)
            
            print(f"✅ Email alert sent to {email_config['to_email']}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
    
    def run(self):
        """Main execution - scrape all sources and process"""
        print("=" * 60)
        print("🚀 JOB TRACKER STARTING")
        print("=" * 60)
        
        all_jobs = []
        
        # Scrape each configured search
        for search in self.config.get('searches', []):
            keywords = search['keywords']
            location = search['location']
            sources = search.get('sources', ['indeed', 'linkedin'])
            
            if 'indeed' in sources:
                jobs = self.scrape_indeed(keywords, location)
                all_jobs.extend(jobs)
            
            if 'linkedin' in sources:
                jobs = self.scrape_linkedin(keywords, location)
                all_jobs.extend(jobs)
            
            time.sleep(3)  # Rate limiting between searches
        
        # Filter jobs
        filtered_jobs = self.filter_jobs(all_jobs)
        
        print(f"\n📊 RESULTS:")
        print(f"   Found: {len(all_jobs)} total jobs")
        print(f"   New: {len(filtered_jobs)} after filtering")
        
        if filtered_jobs:
            # Save to CSV
            self.save_jobs(filtered_jobs)
            print(f"   ✓ Saved to: {self.data_file}")
            
            # Preview first 3 jobs
            print(f"\n📋 PREVIEW (first 3):")
            for job in filtered_jobs[:3]:
                print(f"   • {job['title']} at {job['company']} ({job['source']})")
            
            # Send alerts
            self.send_email_alert(filtered_jobs)
        else:
            print("   No new jobs matching your criteria")
            print("   💡 Tip: Try broadening your keywords or check again later")
        
        print("=" * 60)
        print("✅ COMPLETE")
        print("=" * 60)


def create_sample_config():
    """Create a sample configuration file"""
    config = {
        "searches": [
            {
                "keywords": "python developer",
                "location": "Remote",
                "sources": ["linkedin"]
            }
        ],
        "required_keywords": [],
        "excluded_keywords": ["senior", "lead", "manager", "principal"],
        "email_alerts": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "from_email": "your-email@gmail.com",
            "password": "your-app-password",
            "to_email": "your-email@gmail.com"
        }
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created config.json")
    print("\n📝 Quick Start:")
    print("1. Edit config.json with your job search preferences")
    print("2. Run: python3 job_tracker.py")
    print("\n💡 Tips:")
    print("- Start with LinkedIn only (more reliable)")
    print("- Leave required_keywords empty to see all jobs")
    print("- Use excluded_keywords to filter out unwanted roles")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        create_sample_config()
    else:
        tracker = JobTracker()
        tracker.run()