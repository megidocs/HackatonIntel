begin;

create table clearpath.dispatch_drafts (
    draft_id uuid primary key,
    dispatcher_id uuid not null references clearpath.users(user_id),
    proposal jsonb not null check (jsonb_typeof(proposal) = 'object'),
    tool_trace jsonb not null check (jsonb_typeof(tool_trace) = 'array'),
    status text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
    selected_units uuid[],
    review_result jsonb,
    created_at timestamptz not null default now(),
    reviewed_at timestamptz
);
alter table clearpath.dispatch_drafts enable row level security;

create function clearpath.save_dispatch_draft(actor uuid, draft uuid, proposal jsonb, tool_trace jsonb)
returns jsonb
language plpgsql security definer
set search_path = ''
as $$
begin
    perform clearpath.require_role(actor, 'dispatcher');
    insert into clearpath.dispatch_drafts (draft_id, dispatcher_id, proposal, tool_trace)
    values (draft, actor, proposal, tool_trace);
    return jsonb_build_object('draft_id', draft, 'status', 'pending');
end
$$;

create function clearpath.review_dispatch_draft(actor uuid, draft uuid, decision text, chosen uuid[])
returns jsonb
language plpgsql security definer
set search_path = ''
as $$
declare
    entry clearpath.dispatch_drafts;
    event_id uuid;
    unit uuid;
    incident jsonb;
    result jsonb;
    assignments jsonb := '[]'::jsonb;
begin
    perform clearpath.require_role(actor, 'dispatcher');
    select * into strict entry from clearpath.dispatch_drafts
    where draft_id = draft and dispatcher_id = actor for update;

    if decision is null or decision not in ('approved', 'rejected') then
        raise check_violation using message = 'Invalid draft decision.';
    end if;
    if entry.status <> 'pending' then
        if entry.status = decision and entry.selected_units is not distinct from chosen then
            return entry.review_result;
        end if;
        raise check_violation using message = 'This draft has already been reviewed.';
    end if;

    if decision = 'approved' then
        if chosen is null or cardinality(chosen) not between 1 and 3
            or array_position(chosen, null) is not null
            or cardinality(chosen) <> (select count(distinct id) from unnest(chosen) as id)
            or exists (
                select 1 from unnest(chosen) as id
                where not exists (
                    select 1 from jsonb_array_elements(entry.proposal->'candidates') as candidate
                    where candidate->>'unit_id' = id::text
                )
            ) then
            raise check_violation using message = 'Select unique units from the draft candidates.';
        end if;

        event_id := gen_random_uuid();
        incident := entry.proposal->'incident';
        perform clearpath.open_incident(
            actor, event_id, incident->>'incident_type', (incident->>'severity')::smallint,
            (incident->>'lat')::double precision, (incident->>'lon')::double precision
        );
        for unit in select id from unnest(chosen) as id order by id loop
            assignments := assignments || jsonb_build_array(
                clearpath.assign_unit(actor, gen_random_uuid(), event_id, unit)
            );
        end loop;
    elsif chosen is distinct from '{}'::uuid[] then
        raise check_violation using message = 'A rejected draft cannot include units.';
    end if;

    result := jsonb_build_object(
        'draft_id', draft, 'status', decision, 'incident_id', event_id, 'assignments', assignments,
        'edited', decision = 'approved' and (
            select coalesce(jsonb_agg(id::text order by id::text), '[]'::jsonb) from unnest(chosen) as id
        ) <> (
            select coalesce(jsonb_agg(value order by value), '[]'::jsonb)
            from jsonb_array_elements_text(entry.proposal->'recommended_unit_ids')
        ),
        'review_seconds', extract(epoch from now() - entry.created_at)
    );
    update clearpath.dispatch_drafts set status = decision, selected_units = chosen,
        reviewed_at = now(), review_result = result where draft_id = draft;
    return result;
end
$$;

revoke all on function clearpath.save_dispatch_draft(uuid, uuid, jsonb, jsonb) from public;
revoke all on function clearpath.review_dispatch_draft(uuid, uuid, text, uuid[]) from public;
grant execute on function clearpath.save_dispatch_draft(uuid, uuid, jsonb, jsonb) to clearpath_app;
grant execute on function clearpath.review_dispatch_draft(uuid, uuid, text, uuid[]) to clearpath_app;

commit;
