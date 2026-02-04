from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from parser import ScoringEngine
from termcolor import colored, cprint
from colorama import init
init()
from pprint import pprint


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Model ---
class ScoreResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Boolean, nullable=False) # True = UP, False = DOWN
    timestamp = db.Column(db.DateTime, default=datetime.now)


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
scheduler = BackgroundScheduler()
scheduler.add_job(func=run_scoring_round, trigger="interval", seconds=30)
scheduler.start()


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
    
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port='8000') # use_reloader=False prevents double scheduler start