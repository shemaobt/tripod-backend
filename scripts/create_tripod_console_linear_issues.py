#!/usr/bin/env python3
"""
Create Tripod Console equivalent tasks in Linear from OBT-48 and its children.

OBT-48 is used only to get the team ID (same team, but Tripod Console is a
separate top-level issue with no parent). Creates a standalone issue "Tripod
Console" (no parent, not a child of OBT-48) and sub-issues under it. Uses
LINEAR_API_KEY from the environment.

Usage:
  export LINEAR_API_KEY=lin_api_...
  python scripts/create_tripod_console_linear_issues.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"
OBT48_IDENTIFIER = "OBT-48"
TRIPOD_CONSOLE_PARENT_TITLE = "Tripod Console"

TRIPOD_CONSOLE_TASKS = [
    {
        "title": "Setup Tripod Console frontend (React/Vite, Tailwind)",
        "description": """Create the Tripod Console web app from scratch. Use React with Vite and Tailwind (or match the stack used by Tripod Studio for consistency). Set up project structure, routing (e.g. React Router), and a simple layout (sidebar or top nav). Add a README with: how to install deps, run in dev, and build for production. No backend calls yet; the app should be ready for the next task (auth and API base URL). Consider adding an AGENTS.md or conventions doc if the repo will have multiple contributors.""",
        "obt48_match": "Setup Flutter project",
    },
    {
        "title": "Add REST APIs for languages, organizations, projects",
        "description": """tripod-backend already has models and services for languages, organizations, and projects. Add REST API routes that expose them and protect with the existing auth middleware. Implement: (1) Languages — list, create (name, code), get by id, get by code; return 409 when code already exists. (2) Organizations — list, create (name, slug), get by id/slug, add member (user_id, role). (3) Projects — list (optionally filter), create (name, description, language_id), get by id, grant user access, grant organization access. Use the existing NotFoundError and ConflictError where appropriate. Add request/response schemas and document the new endpoints in http/ with .http examples.""",
        "obt48_match": "Define data model for projects",
    },
    {
        "title": "Auth and RBAC integration in Tripod Console",
        "description": """Wire Tripod Console to tripod-backend auth. Implement: login screen (email + password) calling POST /api/auth/login; store access_token and refresh_token (e.g. in memory or secure storage). Send Authorization: Bearer <access_token> on all API requests. When the backend returns 401, attempt token refresh (POST /api/auth/refresh); on failure redirect to login. Add logout (optional: call POST /api/auth/logout and clear tokens). Restrict admin screens to users who are platform admins or have an admin role for a relevant app — use GET /api/auth/me and /api/auth/my-roles or a dedicated check endpoint. Show a clear “unauthorized” state when the user lacks permission.""",
        "obt48_match": "Implement role model",
    },
    {
        "title": "Languages CRUD UI",
        "description": """Build the Languages management section in Tripod Console. List all languages in a table (columns: name, code, created). Provide “Create language” with form fields: name (required), code (required, 3 chars, e.g. kos). Validate code uniqueness; show backend error (e.g. 409) if the code already exists. Allow editing an existing language (name and/or code) with the same validation. Use the new languages REST API (list, create, get, update if implemented). Ensure the UI is only accessible to authenticated users with the right permissions.""",
        "obt48_match": "Load and display predefined genres",
    },
    {
        "title": "Organizations CRUD and members UI",
        "description": """Build the Organizations section. List organizations in a table (name, slug, member count or link to detail). “Create organization” form: name, slug (unique, URL-friendly). Edit organization (name, slug) with validation. On organization detail: list members (user email, role, joined date). “Add member” flow: select or search user (by email or user id from backend), choose role (e.g. member); call backend add-member API and show 409 if already a member. Allow removing a member with confirmation. Use the new organizations REST API (list, create, get, update, add member; remove member if the backend exposes it).""",
        "obt48_match": "Project Admin can invite users",
    },
    {
        "title": "Projects CRUD UI",
        "description": """Build the Projects section. List projects in a table: name, description (truncated), language (name or code from languages API), created/updated. “Create project” form: name, description (optional), language (dropdown from languages list). Edit project (name, description, language). Project detail view can link to the “Project access” task for granting user/org access. Use the new projects REST API (list, create, get, update). Ensure the language dropdown is populated from the languages API. Handle 404 when a project or language is missing.""",
        "obt48_match": "Project Admin can create a project",
    },
    {
        "title": "Users list and app-role assignment UI",
        "description": """Build the Users and roles section. List users (e.g. from a dedicated list endpoint or by aggregating from existing auth/roles data). Per user row: email, display name, active status, platform admin flag if available. Drill into a user to see their app roles (app_key, role_key). Allow “Assign role”: choose app (e.g. tripod-studio), choose role (admin, member), call POST /api/roles/assign. Allow “Revoke role” with confirmation, call POST /api/roles/revoke. Restrict this entire section to platform admins or users with admin role on the relevant app. Use existing backend endpoints: GET /api/roles/check, POST /api/roles/assign, POST /api/roles/revoke, and auth/me / my-roles.""",
        "obt48_match": "Admin can manage system and change user roles",
    },
    {
        "title": "Project access: grant user and grant organization",
        "description": """From a project’s detail page, add an “Access” (or “Permissions”) area. Show two lists: (1) Users with direct access — user email/id, granted date; (2) Organizations with access — org name/slug, granted date. “Grant to user”: pick user (by email or id), call backend grant_user_access; show message if already granted. “Grant to organization”: pick organization, call backend grant_organization_access. Optionally allow revoking user or org access if the backend supports it. Use the new project access REST APIs (grant user, grant organization; list if the backend exposes them). Ensure only authorized users (e.g. platform admin or project admin) can manage access.""",
        "obt48_match": None,
    },
]


def _ssl_context():
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        pass
    return ctx


def linear_request(api_key: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LINEAR_GRAPHQL_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=_ssl_context()) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"HTTP {e.code}: {e.reason}. Response: {err_body[:500]}")


def get_obt48(api_key: str) -> dict:
    query = """
    query FindOBT48 {
      issues(first: 100) {
        nodes {
          id
          identifier
          title
          team { id name }
        }
      }
    }
    """
    resp = linear_request(api_key, {"query": query})
    if "errors" in resp:
        raise RuntimeError("Linear API errors: " + json.dumps(resp["errors"], indent=2))
    nodes = resp.get("data", {}).get("issues", {}).get("nodes", [])
    issue = next((n for n in nodes if n.get("identifier") == OBT48_IDENTIFIER), None)
    if not issue:
        raise RuntimeError(
            f"Parent issue {OBT48_IDENTIFIER} not found. Ensure LINEAR_API_KEY has access to it."
        )
    return issue


def get_children(api_key: str, parent_id: str) -> list[dict]:
    query = """
    query GetChildIssues($parentId: String!) {
      issue(id: $parentId) {
        id
        children(first: 50) {
          nodes {
            id
            identifier
            title
            sortOrder
          }
        }
      }
    }
    """
    resp = linear_request(api_key, {"query": query, "variables": {"parentId": parent_id}})
    if "errors" in resp:
        raise RuntimeError("Linear API errors: " + json.dumps(resp["errors"], indent=2))
    issue = resp.get("data", {}).get("issue")
    if not issue:
        return []
    return issue.get("children", {}).get("nodes", [])


def find_or_create_tripod_console_parent(
    api_key: str, team_id: str, dry_run: bool
) -> str | None:
    """Find or create top-level issue 'Tripod Console' (no parent; not under OBT-48)."""
    query = """
    query FindTripodConsole($teamId: String!) {
      team(id: $teamId) {
        issues(first: 100) {
          nodes {
            id
            identifier
            title
            parent { id }
          }
        }
      }
    }
    """
    resp = linear_request(api_key, {"query": query, "variables": {"teamId": team_id}})
    if "errors" in resp:
        raise RuntimeError("Linear API errors: " + json.dumps(resp["errors"], indent=2))
    nodes = resp.get("data", {}).get("team", {}).get("issues", {}).get("nodes", [])
    existing = next(
        (
            n
            for n in nodes
            if (n.get("title") or "").strip() == TRIPOD_CONSOLE_PARENT_TITLE
            and n.get("parent") is None
        ),
        None,
    )
    if existing:
        print(f"  Using existing parent: {existing.get('identifier', '?')} — {existing.get('title', '')}")
        return existing["id"]

    mutation = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        issue { id identifier title }
        success
      }
    }
    """
    variables = {
        "input": {
            "teamId": team_id,
            "title": TRIPOD_CONSOLE_PARENT_TITLE,
            "description": "Admin UI for tripod-backend: manage users, organizations, projects, languages, and app roles. Consumes tripod-backend REST API.",
        }
    }
    if dry_run:
        print(f"  [dry-run] Would create top-level issue (no parent): {TRIPOD_CONSOLE_PARENT_TITLE}")
        return None
    resp = linear_request(api_key, {"query": mutation, "variables": variables})
    if "errors" in resp:
        raise RuntimeError("Linear API errors: " + json.dumps(resp["errors"], indent=2))
    result = resp.get("data", {}).get("issueCreate", {})
    if not result.get("success"):
        raise RuntimeError("issueCreate returned success: false")
    issue = result.get("issue", {})
    print(f"  Created parent: {issue.get('identifier', '?')} — {issue.get('title', '')}")
    return issue.get("id")


def create_subissue(
    api_key: str,
    team_id: str,
    parent_id: str,
    title: str,
    description: str,
    dry_run: bool,
) -> dict | None:
    mutation = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        issue { id identifier title }
        success
      }
    }
    """
    variables = {
        "input": {
            "teamId": team_id,
            "parentId": parent_id,
            "title": title,
            "description": description,
        }
    }
    if dry_run:
        print(f"    [dry-run] Would create: {title[:60]}...")
        return None
    resp = linear_request(api_key, {"query": mutation, "variables": variables})
    if "errors" in resp:
        raise RuntimeError("Linear API errors: " + json.dumps(resp["errors"], indent=2))
    result = resp.get("data", {}).get("issueCreate", {})
    if not result.get("success"):
        raise RuntimeError("issueCreate returned success: false")
    return result.get("issue")


def issue_update(api_key: str, issue_id: str, input_dict: dict, dry_run: bool) -> bool:
    if dry_run:
        return True
    mutation = """
    mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) { success }
    }
    """
    resp = linear_request(
        api_key, {"query": mutation, "variables": {"id": issue_id, "input": input_dict}}
    )
    if "errors" in resp and resp["errors"]:
        raise RuntimeError("Linear API: " + json.dumps(resp["errors"], indent=2))
    return resp.get("data", {}).get("issueUpdate", {}).get("success", False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create Tripod Console equivalent tasks in Linear from OBT-48"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without calling the API",
    )
    args = parser.parse_args()

    api_key = (os.environ.get("LINEAR_API_KEY") or "").strip()
    if not api_key:
        print("LINEAR_API_KEY is required. Set it in the environment.", file=sys.stderr)
        return 1

    try:
        parent = get_obt48(api_key)
    except Exception as e:
        print(f"Failed to find {OBT48_IDENTIFIER}: {e}", file=sys.stderr)
        return 1

    team_id = parent["team"]["id"]
    team_name = parent["team"].get("name", team_id)
    obt48_id = parent["id"]
    print(f"Found {OBT48_IDENTIFIER} (team: {team_name}) — used only for team ID; Tripod Console will be a separate top-level issue.")

    children = get_children(api_key, obt48_id)
    print(f"Found {len(children)} child issues under {OBT48_IDENTIFIER} (for reference only).")

    parent_console_id = find_or_create_tripod_console_parent(api_key, team_id, args.dry_run)
    if not parent_console_id and not args.dry_run:
        print("Could not create or find Tripod Console parent.", file=sys.stderr)
        return 1
    if args.dry_run and not parent_console_id:
        parent_console_id = "dry-run-parent-id"

    print(f"\nCreating {len(TRIPOD_CONSOLE_TASKS)} Tripod Console sub-issues in order...")
    created = []
    created_ids = []
    for i, task in enumerate(TRIPOD_CONSOLE_TASKS, start=1):
        issue = create_subissue(
            api_key,
            team_id,
            parent_console_id,
            task["title"],
            task.get("description", ""),
            args.dry_run,
        )
        if issue:
            created.append(issue.get("identifier", issue.get("id", "")))
            created_ids.append((issue.get("id"), 1000.0 * i))
            print(f"    → {issue.get('identifier', '?')} — {task['title'][:50]}...")
    if not args.dry_run and created_ids:
        print("\nSetting sortOrder for correct display order...")
        for issue_id, sort_order in created_ids:
            try:
                issue_update(api_key, issue_id, {"sortOrder": sort_order}, False)
            except Exception as e:
                print(f"    Warning: could not set order for {issue_id[:8]}...: {e}")
    if args.dry_run:
        print("\nDry-run done. Run without --dry-run to create issues in Linear.")
    else:
        print(f"\nDone. Created {len(created)} sub-issues under Tripod Console: {', '.join(created)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
