from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional
import requests
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_VERSION = "2022-06-28"

app = FastAPI()

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

class TaskCreate(BaseModel):
    name: str
    status: Optional[str] = "Offen"
    due_date: Optional[str] = None
    priority: Optional[str] = None

@app.get("/tasks")
def get_tasks(status: Optional[str] = None):
    filter_payload = {
        "filter": {
            "property": "Status",
            "status": {
                "equals": status
            }
        }
    } if status else {}

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers, json=filter_payload)
    return response.json()

@app.post("/tasks")
def create_task(task: TaskCreate):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name der Aufgabe": {
                "title": [{"text": {"content": task.name}}]
            },
            "Status": {
                "status": {"name": task.status}
            }
        }
    }

    if task.due_date:
        data["properties"]["Fällig"] = {"date": {"start": task.due_date}}

    if task.priority:
        data["properties"]["Priorität"] = {"select": {"name": task.priority}}

    response = requests.post(url, headers=headers, json=data)
    return response.json()