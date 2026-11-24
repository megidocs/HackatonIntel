begin;

create schema clearpath;

create table clearpath.users (
    user_id uuid primary key references auth.users(id),
    role text not null check (role in ('dispatcher', 'rescue', 'citizen')),
    display_name text not null check (length(display_name) between 1 and 100)
);

create table clearpath.units (
    unit_id uuid primary key default gen_random_uuid(),
    unit_type text not null check (unit_type in ('medical', 'fire', 'police')),
    user_id uuid not null unique references clearpath.users(user_id)
);

create table clearpath.incidents (
    incident_id uuid primary key,
    opened_by uuid not null references clearpath.users(user_id),
    incident_type text not null check (incident_type in ('medical', 'fire', 'police')),
    severity smallint not null check (severity between 1 and 5),
    latitude double precision not null check (latitude between -90 and 90),
    longitude double precision not null check (longitude between -180 and 180),
    status text not null default 'open' check (status in ('open', 'closed')),
    created_at timestamptz not null default now()
);
create index clearpath_open_incidents on clearpath.incidents (status, created_at desc);

create table clearpath.dispatches (
    dispatch_id uuid primary key,
    incident_id uuid not null references clearpath.incidents(incident_id),
    unit_id uuid not null references clearpath.units(unit_id),
    assigned_by uuid not null references clearpath.users(user_id),
    dispatched_at timestamptz not null default now(),
    arrived_at timestamptz
);
create unique index clearpath_one_active_dispatch_per_unit
    on clearpath.dispatches (unit_id) where arrived_at is null;
create index clearpath_dispatch_incident on clearpath.dispatches (incident_id);

create table clearpath.intersections (
    osm_node_id bigint primary key,
    latitude double precision not null check (latitude between -90 and 90),
    longitude double precision not null check (longitude between -180 and 180)
);

create table clearpath.preemption_log (
    request_id uuid primary key,
    user_id uuid not null references clearpath.users(user_id),
    dispatch_id uuid not null references clearpath.dispatches(dispatch_id),
    osm_node_id bigint not null references clearpath.intersections(osm_node_id),
    requested_at timestamptz not null default now()
);
create index clearpath_preemption_dispatch on clearpath.preemption_log (dispatch_id);

alter table clearpath.users enable row level security;
alter table clearpath.units enable row level security;
alter table clearpath.incidents enable row level security;
alter table clearpath.dispatches enable row level security;
alter table clearpath.intersections enable row level security;
alter table clearpath.preemption_log enable row level security;

-- The deployment administrator can provision a password separately. No password is in Git.
do $$
begin
    if not exists (select 1 from pg_catalog.pg_roles where rolname = 'clearpath_app') then
        create role clearpath_app nologin;
    end if;
end
$$;

create function clearpath.require_role(actor uuid, expected text)
returns void
language plpgsql
set search_path = ''
as $$
begin
    if not exists (select 1 from clearpath.users where user_id = actor and role = expected) then
        raise insufficient_privilege using message = 'Role not permitted.';
    end if;
end
$$;

create function clearpath.open_incident(
    actor uuid, event_id uuid, kind text, level smallint, lat double precision, lon double precision
)
returns jsonb
language plpgsql security definer
set search_path = ''
as $$
declare
    event clearpath.incidents;
begin
    perform clearpath.require_role(actor, 'dispatcher');
    insert into clearpath.incidents (incident_id, opened_by, incident_type, severity, latitude, longitude)
    values (event_id, actor, kind, level, lat, lon)
    on conflict (incident_id) do nothing;
    select * into strict event from clearpath.incidents where incident_id = event_id;
    if (event.opened_by, event.incident_type, event.severity, event.latitude, event.longitude)
        is distinct from (actor, kind, level, lat, lon) then
        raise unique_violation using message = 'Incident identifier is already in use.';
    end if;
    return to_jsonb(event);
end
$$;

create function clearpath.assign_unit(actor uuid, assignment_id uuid, event_id uuid, vehicle_id uuid)
returns jsonb
language plpgsql security definer
set search_path = ''
as $$
declare
    assignment clearpath.dispatches;
begin
    perform clearpath.require_role(actor, 'dispatcher');
    select * into assignment from clearpath.dispatches where dispatch_id = assignment_id;
    if not found then
        perform 1 from clearpath.incidents where incident_id = event_id and status = 'open' for update;
        if not found then
            raise no_data_found using message = 'Open incident not found.';
        end if;
        perform 1 from clearpath.units as u
        join clearpath.users as p on p.user_id = u.user_id
        where u.unit_id = vehicle_id and p.role = 'rescue'
        for update of u;
        if not found then
            raise no_data_found using message = 'Rescue unit not found.';
        end if;
        insert into clearpath.dispatches (dispatch_id, incident_id, unit_id, assigned_by)
        values (assignment_id, event_id, vehicle_id, actor)
        on conflict (dispatch_id) do nothing;
        select * into strict assignment from clearpath.dispatches where dispatch_id = assignment_id;
    end if;
    if (assignment.assigned_by, assignment.incident_id, assignment.unit_id)
        is distinct from (actor, event_id, vehicle_id) then
        raise unique_violation using message = 'Assignment identifier is already in use.';
    end if;
    return to_jsonb(assignment);
end
$$;

create function clearpath.mark_arrived(actor uuid, assignment_id uuid)
returns jsonb
language plpgsql security definer
set search_path = ''
as $$
declare
    assignment clearpath.dispatches;
begin
    update clearpath.dispatches as d
    set arrived_at = coalesce(d.arrived_at, now())
    from clearpath.units as u, clearpath.users as p
    where d.dispatch_id = assignment_id and d.unit_id = u.unit_id and p.user_id = actor
      and (p.role = 'dispatcher' or (p.role = 'rescue' and u.user_id = actor))
    returning d.* into assignment;
    if not found then
        raise no_data_found using message = 'Assignment not found.';
    end if;
    return to_jsonb(assignment);
end
$$;

create function clearpath.close_incident(actor uuid, event_id uuid)
returns jsonb
language plpgsql security definer
set search_path = ''
as $$
declare
    event clearpath.incidents;
begin
    perform clearpath.require_role(actor, 'dispatcher');
    select * into strict event from clearpath.incidents where incident_id = event_id for update;
    if exists (select 1 from clearpath.dispatches where incident_id = event_id and arrived_at is null) then
        raise check_violation using message = 'Incident has an active assignment.';
    end if;
    update clearpath.incidents set status = 'closed' where incident_id = event_id returning * into event;
    return to_jsonb(event);
end
$$;

create function clearpath.dispatch_board(actor uuid)
returns jsonb
language plpgsql security definer
set search_path = ''
as $$
declare
    actor_role text;
    incidents jsonb;
    units jsonb;
begin
    select role into actor_role from clearpath.users where user_id = actor;
    if actor_role is null or actor_role not in ('dispatcher', 'rescue') then
        raise insufficient_privilege using message = 'Role not permitted.';
    end if;
    select coalesce(jsonb_agg(to_jsonb(rows) order by rows.created_at desc), '[]'::jsonb) into incidents
    from (
        select i.incident_id, i.incident_type, i.severity, i.latitude, i.longitude, i.created_at
        from clearpath.incidents as i where i.status = 'open' and (
            actor_role = 'dispatcher' or exists (
                select 1 from clearpath.dispatches as d join clearpath.units as u on u.unit_id = d.unit_id
                where d.incident_id = i.incident_id and d.arrived_at is null and u.user_id = actor
            )
        ) order by i.created_at desc limit 100
    ) as rows;
    select coalesce(jsonb_agg(to_jsonb(rows) order by rows.unit_id), '[]'::jsonb) into units
    from (
        select u.unit_id, u.unit_type, d.dispatch_id, d.incident_id
        from clearpath.units as u left join clearpath.dispatches as d on d.unit_id = u.unit_id and d.arrived_at is null
        where actor_role = 'dispatcher' or u.user_id = actor order by u.unit_id limit 100
    ) as rows;
    return jsonb_build_object('incidents', incidents, 'units', units);
end
$$;

create function clearpath.record_preemption(
    actor uuid, command_id uuid, assignment_id uuid, node bigint, lat double precision, lon double precision
)
returns jsonb
language plpgsql security definer
set search_path = ''
as $$
declare
    entry clearpath.preemption_log;
begin
    perform clearpath.require_role(actor, 'rescue');
    select * into entry from clearpath.preemption_log where request_id = command_id;
    if not found then
        perform 1 from clearpath.dispatches as d
        join clearpath.units as u on u.unit_id = d.unit_id
        join clearpath.incidents as i on i.incident_id = d.incident_id
        where d.dispatch_id = assignment_id and u.user_id = actor
          and d.arrived_at is null and i.status = 'open'
        for update of d, i;
        if not found then
            raise insufficient_privilege using message = 'Active assignment required.';
        end if;
        insert into clearpath.intersections (osm_node_id, latitude, longitude)
        values (node, lat, lon) on conflict (osm_node_id) do nothing;
        insert into clearpath.preemption_log (request_id, user_id, dispatch_id, osm_node_id)
        values (command_id, actor, assignment_id, node)
        on conflict (request_id) do nothing;
        select * into strict entry from clearpath.preemption_log where request_id = command_id;
    end if;
    if (entry.user_id, entry.dispatch_id, entry.osm_node_id)
        is distinct from (actor, assignment_id, node) then
        raise unique_violation using message = 'Priority request identifier is already in use.';
    end if;
    return to_jsonb(entry);
end
$$;

-- The app can read a user's role but cannot change it or directly write any table.
revoke all on schema clearpath from public;
revoke all on all functions in schema clearpath from public;
grant usage on schema clearpath to clearpath_app;
grant select (user_id, role) on clearpath.users to clearpath_app;
create policy clearpath_backend_identity on clearpath.users for select to clearpath_app using (true);
grant execute on function clearpath.open_incident(uuid, uuid, text, smallint, double precision, double precision),
    clearpath.assign_unit(uuid, uuid, uuid, uuid),
    clearpath.mark_arrived(uuid, uuid),
    clearpath.close_incident(uuid, uuid),
    clearpath.dispatch_board(uuid),
    clearpath.record_preemption(uuid, uuid, uuid, bigint, double precision, double precision)
    to clearpath_app;

commit;
