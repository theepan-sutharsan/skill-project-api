"""Run database seeders without starting the web server."""

from app import create_app
from app.seeds import run_seeds

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        results = run_seeds()
        print("Seeding complete.")
        print(f"  Admin:   created={results['admin']['created']}, skipped={results['admin']['skipped']}")
        print(f"  Users:   created={results['users']['created']}, skipped={results['users']['skipped']}")
        print(f"  Skills:  created={results['skills']['created']}, skipped={results['skills']['skipped']}")
