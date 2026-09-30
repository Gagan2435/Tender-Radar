"""One command: migrate -> crawl -> open the dashboard.   python run.py [--sample]"""
import subprocess
import sys
import threading
import webbrowser


def manage(*args):
    subprocess.check_call([sys.executable, "manage.py", *args])


if __name__ == "__main__":
    source = "sample" if "--sample" in sys.argv else "auto"
    manage("makemigrations", "tenders")
    manage("migrate")
    manage("crawl", "--source", source)
    manage("evaluate_classifier")
    print("\nDashboard: http://127.0.0.1:8000   (Ctrl+C to stop)")
    threading.Timer(2, lambda: webbrowser.open("http://127.0.0.1:8000")).start()
    try:
        manage("runserver", "--noreload")
    except KeyboardInterrupt:
        pass
