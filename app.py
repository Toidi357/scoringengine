from flask import Flask, render_template, request, jsonify
from models import db, ScoreResult
from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor
import subprocess
from datetime import datetime
from parser import ScoringEngine
from termcolor import colored, cprint
from colorama import init
init()
from pprint import pprint


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

engine = None

def run_scoring_round():
    """Executed every 30 seconds by the scheduler."""
    cprint(f"Starting scoring round: {datetime.now()}", "yellow")
    
    with app.app_context():
        # Use a ThreadPool to run checks in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            # map the check.run method across all active checks
            futures = {executor.submit(c.run): c for c in engine.active_checks}
            
            for future in futures:
                check_obj = futures[future]
                try:
                    success = future.result()
                    
                    # Write to Database
                    new_result = ScoreResult(
                        check_name=check_obj.name,
                        host=check_obj.host,
                        status=success
                    )
                    db.session.add(new_result)
                except Exception as e:
                    cprint(f"Critical failure on {check_obj.name}: {e}", "red")
            
            db.session.commit()
    cprint(f"Scoring round complete {datetime.now()}", "green")

# --- Scheduler Setup ---
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_scoring_round, trigger="interval", seconds=30)
    scheduler.start()

# debugging
""" shell_executor = ThreadPoolExecutor(max_workers=5)
@app.route('/hello', methods=['POST'])
def run_powershell():
    content = request.get_json()
    command = content.get('data') if content else None

    if not command:
        return jsonify({"error": "No command provided"}), 400

    def execute_shell(cmd):
        # We use shell=True carefully here for PowerShell string parsing
        return subprocess.run(
            ["powershell.exe", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=15  # Optional: prevent a command from running forever
        )

    try:
        # Offload the execution to the thread pool
        future = shell_executor.submit(execute_shell, command)
        
        # result() will block this specific request thread, but 
        # NOT the main Flask process or other incoming requests.
        result = future.result()

        return jsonify({
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr
        })

    except TimeoutError:
        return jsonify({"status": "error", "message": "Command timed out after 15s"}), 408
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "stdout": e.stdout, "stderr": e.stderr}), 500
    except Exception as e:
        return jsonify({"status": "exception", "message": str(e)}), 500 """

@app.route('/')
def dashboard():
    all_data = {}
    check_names = [c.name for c in engine.active_checks]
    
    for name in check_names:
        history = ScoreResult.query.filter_by(check_name=name)\
                                   .order_by(ScoreResult.timestamp.desc())\
                                   .limit(10).all()
        # We store the list of results for each check name
        all_data[name] = history

    return render_template('dashboard.html', data=all_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Initialize DB
        
        # --- Engine Initialization ---
        engine = ScoringEngine("scoring.conf")
        checks = engine.parse_config()
        pprint(checks)
        
        start_scheduler()
    
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port='8000') # use_reloader=False prevents double scheduler start