"""List or enroll explicitly selected, verified Supabase accounts on Hackathon-supa."""

import argparse
import json
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

from psycopg import sql

PROJECT_REF = "uodbkiyevjwgmjnofcpj"
VERIFIED_ACCOUNTS = sql.SQL("""
select u.id, lower(u.email) as email from auth.users as u
where lower(u.email) in ({addresses}) and u.email_confirmed_at is not null
""")


def query(statement, *, write=False):
    with NamedTemporaryFile(dir="C:/Temp", suffix=".sql", mode="w", encoding="utf-8", delete=False) as temp:
        temp.write(statement.as_string())
        path = Path(temp.name)
    try:
        command = ["npx.cmd", "--yes", "supabase", "db", "query", f"--remote={PROJECT_REF}",
                   "--output-format", "json", "--yes" if write else "--read-only", "--file", str(path)]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    finally:
        path.unlink(missing_ok=True)
    if result.returncode:
        raise RuntimeError("The Supabase CLI query failed. Check the CLI session and project access.")
    return json.loads(result.stdout)["rows"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email", nargs="+", help="The exact account address authorized for Rescue.")
    parser.add_argument("--vehicle", choices=("medical", "fire", "police"), default="medical")
    parser.add_argument("--apply", action="store_true", help="Enroll the already-verified Supabase accounts.")
    args = parser.parse_args()
    addresses = sorted({address.strip().casefold() for address in args.email})
    if any(not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", address) for address in addresses):
        parser.error("Provide complete email addresses.")
    accounts = VERIFIED_ACCOUNTS.format(addresses=sql.SQL(", ").join(map(sql.Literal, addresses)))
    if not args.apply:
        rows = query(sql.SQL("""
            select g.email, r.role, u.unit_type from ({accounts}) as g
            left join clearpath.users as r on r.user_id = g.id
            left join clearpath.units as u on u.user_id = g.id
        """).format(accounts=accounts))
    else:
        rows = query(sql.SQL("""
            with verified as ({accounts}), eligible as (
                select g.id, g.email from verified g
                left join clearpath.users r on r.user_id = g.id
                where r.role is distinct from 'dispatcher'
            ), rescues as (
                insert into clearpath.users (user_id, role, display_name)
                select id, 'rescue', left(email, 100) from eligible
                on conflict (user_id) do update set role = 'rescue'
                where clearpath.users.role in ('rescue', 'citizen')
                returning user_id, role
            ), added_units as (
                insert into clearpath.units (user_id, unit_type)
                select user_id, {vehicle} from rescues on conflict (user_id) do nothing
                returning user_id, unit_type
            )
            select verified.email, coalesce(rescues.role, existing.role) as role,
                coalesce(added_units.unit_type, existing_unit.unit_type) as unit_type
            from verified left join rescues on rescues.user_id = verified.id
            left join added_units on added_units.user_id = verified.id
            left join clearpath.users existing on existing.user_id = verified.id
            left join clearpath.units existing_unit on existing_unit.user_id = verified.id
        """).format(accounts=accounts, vehicle=sql.Literal(args.vehicle)), write=True)
    by_email = {row["email"]: row for row in rows}
    for address in addresses:
        account = by_email.get(address)
        if account is None:
            print(f"{address}: waiting for a verified Supabase account")
        else:
            print(f"{address}: role={account['role'] or 'unassigned'}, unit={account['unit_type'] or 'unassigned'}")


if __name__ == "__main__":
    main()
