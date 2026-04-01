import subprocess
import sys

def run_script(script_name):
    print(f"--- Starting {script_name} ---")
    try:
        # Running using the project's venv python interpreter
        result = subprocess.run(['./venv/bin/python3', script_name], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stderr)
    print(f"--- Completed {script_name} ---\n")

def main():
    scripts = [
        'scrape_new_members.py',
        'scrape_new_forum_posts.py',
        'translate_forum.py',
        'update_steam_visual.py'
    ]
    
    for script in scripts:
        run_script(script)

if __name__ == "__main__":
    main()
