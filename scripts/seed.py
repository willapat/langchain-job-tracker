"""Populate jobs.db with realistic demo data so the board/analytics aren't empty on first run.

Usage: python -m scripts.seed [--reset]
"""

import argparse
import os
import sys
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, select

from app import crud
from app.db import Base, engine, init_db, session_scope
from app.models import Application

APPLICATIONS = [
    dict(company="Spotify", role="Senior Backend Engineer", salary="$170,000 - $200,000",
         location="Hybrid, New York", status="interview", days_ago=21,
         source_url="https://www.lifeatspotify.com/jobs/senior-backend-engineer",
         requirements=["4+ years of Python or Go", "Experience with microservices", "Strong system design skills"]),
    dict(company="Stripe", role="Software Engineer, Payments", salary="$180,000 - $220,000",
         location="Remote (US)", status="applied", days_ago=4,
         requirements=["Distributed systems experience", "Strong CS fundamentals", "Ownership mindset"]),
    dict(company="Figma", role="Frontend Engineer", salary="$150,000 - $190,000",
         location="San Francisco, CA", status="screening", days_ago=9,
         requirements=["React/TypeScript", "Design systems experience", "Attention to detail"]),
    dict(company="Datadog", role="Site Reliability Engineer", salary="$160,000 - $195,000",
         location="Remote (US)", status="rejected", days_ago=35,
         requirements=["Kubernetes", "On-call experience", "Observability tooling"]),
    dict(company="Anthropic", role="ML Infrastructure Engineer", salary="$210,000 - $260,000",
         location="San Francisco, CA", status="offer", days_ago=48,
         source_url="https://job-boards.greenhouse.io/anthropic/jobs/4017331008",
         requirements=["Distributed training", "PyTorch", "Large-scale systems"]),
    dict(company="Notion", role="Full Stack Engineer", salary="$155,000 - $185,000",
         location="Remote (US)", status="applied", days_ago=2,
         requirements=["React", "Node.js", "Product sense"]),
    dict(company="Airbnb", role="Backend Engineer, Trust", salary="$175,000 - $210,000",
         location="San Francisco, CA", status="screening", days_ago=12,
         requirements=["Java or Go", "Fraud/risk systems", "High-scale services"]),
    dict(company="Duolingo", role="Software Engineer, Growth", salary="$140,000 - $170,000",
         location="Pittsburgh, PA", status="applied", days_ago=6,
         requirements=["A/B testing experience", "Python", "Data-driven mindset"]),
    dict(company="Cloudflare", role="Systems Engineer", salary="$165,000 - $200,000",
         location="Remote (US)", status="interview", days_ago=18,
         requirements=["Rust or C++", "Networking fundamentals", "Performance tuning"]),
    dict(company="Snowflake", role="Data Platform Engineer", salary="$170,000 - $205,000",
         location="Remote (US)", status="rejected", days_ago=40,
         requirements=["SQL engines", "Distributed storage", "Cloud infrastructure"]),
    dict(company="Robinhood", role="Software Engineer, Risk", salary="$165,000 - $195,000",
         location="Menlo Park, CA", status="applied", days_ago=1,
         requirements=["Financial systems experience a plus", "Python", "Strong testing discipline"]),
    dict(company="Vercel", role="Frontend Platform Engineer", salary="$150,000 - $180,000",
         location="Remote (US)", status="screening", days_ago=7,
         requirements=["Next.js internals", "Build tooling", "DX focus"]),
    dict(company="Discord", role="Backend Engineer, Voice", salary="$160,000 - $195,000",
         location="San Francisco, CA", status="applied", days_ago=3,
         requirements=["Real-time systems", "WebRTC or similar", "Elixir or Go a plus"]),
    dict(company="Ramp", role="Software Engineer, Platform", salary="$175,000 - $210,000",
         location="New York, NY", status="interview", days_ago=15,
         requirements=["TypeScript", "API design", "Fast iteration"]),
    dict(company="Linear", role="Product Engineer", salary="$160,000 - $190,000",
         location="Remote (US)", status="applied", days_ago=5,
         requirements=["Full-stack TypeScript", "Craft and polish", "Small team experience"]),
]

NOTES = {
    "Spotify": [("interview", "Phone screen with recruiter went well, moving to technical round next week."),
                ("note", "Recruiter contact: jill.k@spotify.com")],
    "Anthropic": [("interview", "Onsite loop completed — 4 rounds, felt strong on systems design."),
                  ("note", "Offer expected by end of week per recruiter.")],
    "Cloudflare": [("interview", "Take-home exercise submitted, awaiting feedback.")],
    "Ramp": [("interview", "Hiring manager call scheduled for next Tuesday.")],
}


def seed(reset: bool = False) -> None:
    if reset:
        Base.metadata.drop_all(bind=engine)
    init_db()

    with session_scope() as session:
        existing = session.scalar(select(func.count(Application.id))) or 0
        if not reset and existing > 0:
            print("Database already has applications; pass --reset to wipe and reseed.")
            return

        for entry in APPLICATIONS:
            days_ago = entry.pop("days_ago")
            application = crud.create_application(session, **entry)
            application.applied_date = date.today() - timedelta(days=days_ago)
            for kind, content in NOTES.get(entry["company"], []):
                crud.add_note(session, application.id, content, kind)

    print(f"Seeded {len(APPLICATIONS)} applications.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Drop all tables before seeding.")
    args = parser.parse_args()
    seed(reset=args.reset)
