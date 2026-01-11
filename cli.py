import json
from pathlib import Path
import typer
from rich import print
from rich.panel import Panel
from datetime import datetime

app = typer.Typer()

# Define the path for the tasks file
TASKS_FILE = "tasks.json"

def load_tasks():
    if not Path(TASKS_FILE).exists():
        return []
    with open(TASKS_FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

@app.command()
def add(description: str, due_date: str = typer.Option(None, "--due-date", help="Due date for the task in YYYY-MM-DD format")):
    """Add a new task."""
    tasks = load_tasks()
    tasks.append({"description": description, "completed": False, "due_date": due_date})
    save_tasks(tasks)
    custom_echo(f"Task added: {description}", command="Add")

@app.command()
def list():
    """List all tasks."""
    tasks = load_tasks()
    if not tasks:
        content = "No tasks found."
    else:
        items = []
        for index, task in enumerate(tasks, start=1):
            status = '✓' if task['completed'] else '✗'
            due_date_info = f" due on {task.get('due_date', '')}" if 'due_date' in task and task['due_date'] is not None else ""
            item = f"{index}. {status} {task['description']}{due_date_info}"
            items.append(item)
        
        content = '\n'.join(items)
    
    custom_echo(content, command="List")

@app.command()
def complete(index: int):
    """Complete a task by its index."""
    tasks = load_tasks()
    if index < 1 or index > len(tasks):
        custom_echo("Invalid task index.", command="Complete")
        return
    tasks[index - 1]["completed"] = True
    save_tasks(tasks)
    custom_echo(f"Task {index} completed.", command="Complete")

@app.command()
def delete(index: int):
    """Delete a task by its index."""
    tasks = load_tasks()
    if index < 1 or index > len(tasks):
        custom_echo("Invalid task index.", command="Delete")
        return
    del tasks[index - 1]
    save_tasks(tasks)
    custom_echo(f"Task {index} deleted.", command="Delete")

def custom_echo(content: str, command: str = "Todos"):
    panel = Panel(content, title=command, title_align="left", expand=False)
    print(panel)

if __name__ == "__main__":
    app()