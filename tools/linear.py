import os
import requests

LINEAR_API_URL = "https://api.linear.app/graphql"


def _headers() -> dict:
    return {
        "Authorization": os.environ["LINEAR_API_KEY"],
        "Content-Type": "application/json",
    }


def fetch_ticket(ticket_id: str) -> dict:
    """Fetch a Linear ticket by its ID (e.g. 'QA-123'). Returns title, description, state."""
    query = """
    query($id: String!) {
        issue(id: $id) {
            id
            title
            description
            state { name }
            assignee { name }
            labels { nodes { name } }
        }
    }
    """
    resp = requests.post(
        LINEAR_API_URL,
        headers=_headers(),
        json={"query": query, "variables": {"id": ticket_id}}
    )
    resp.raise_for_status()
    issue = resp.json()["data"]["issue"]
    return {
        "id": issue["id"],
        "title": issue["title"],
        "description": issue.get("description", ""),
        "state": issue["state"]["name"],
        "assignee": issue.get("assignee", {}).get("name", "Unassigned"),
        "labels": [l["name"] for l in issue["labels"]["nodes"]],
    }


def create_subtask(parent_id: str, title: str, description: str) -> str:
    """Create a Linear subtask under parent_id. Returns the new issue ID."""
    mutation = """
    mutation($title: String!, $description: String!, $parentId: String!) {
        issueCreate(input: {
            title: $title,
            description: $description,
            parentId: $parentId
        }) {
            issue { id title }
        }
    }
    """
    resp = requests.post(
        LINEAR_API_URL,
        headers=_headers(),
        json={"query": mutation, "variables": {
            "title": title,
            "description": description,
            "parentId": parent_id
        }}
    )
    resp.raise_for_status()
    return resp.json()["data"]["issueCreate"]["issue"]["id"]


def update_ticket_status(ticket_id: str, state_name: str) -> None:
    """Update the status of a Linear ticket by state name."""
    mutation = """
    mutation($id: String!, $stateName: String!) {
        issueUpdate(id: $id, input: { stateName: $stateName }) {
            issue { id state { name } }
        }
    }
    """
    resp = requests.post(
        LINEAR_API_URL,
        headers=_headers(),
        json={"query": mutation, "variables": {"id": ticket_id, "stateName": state_name}}
    )
    resp.raise_for_status()
