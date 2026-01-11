import json
from pathlib import Path
import typer
from rich import print, style
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

def parse_date(date_str):
    date_formats = ["%Y/%m/%d", "%m/%d/%Y"]
    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format).strftime("%Y/%m/%d")
        except ValueError:
            pass
    raise ValueError("Date format not supported. Please use one of the following formats: yyyy/mm/dd or mm/dd/yyyy")

@app.command()
def add(description: str, due_date: str = typer.Option(None, "--due-date", help="Due date for the task in YYYY-MM-DD format")):
    """Add a new task."""
    if due_date is None:
        tasks = load_tasks()
        tasks.append({"description": description, "completed": False})
        save_tasks(tasks)
        custom_echo(f"Task added: {description}", command="Add")
    else:
        try:
            formatted_due_date = parse_date(due_date)
            tasks = load_tasks()
            tasks.append({"description": description, "completed": False, "due_date": formatted_due_date})
            save_tasks(tasks)
            custom_echo(f"Task added: {description} due on {formatted_due_date}", command="Add")
        except ValueError as e:
            custom_echo(str(e), command="Error")
            return 

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
            
            # Apply red color for tasks that are not completed and have a past due date
            current_date = datetime.now()
            if not task['completed']:
                due_date = task.get('due_date')
                if due_date:
                    due_date_obj = datetime.strptime(due_date, "%Y/%m/%d")
                    if current_date > due_date_obj:
                        style_obj = style.Style(color='red')
                    else:
                        style_obj = style.Style()
                else:
                    style_obj = style.Style()
            else:
                style_obj = style.Style(color='green')
            
            items.append((item, style_obj))
        
        content = '\n'.join([f"[{style_obj}]{item}[/{style_obj}]" for item, style_obj in items])
    
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