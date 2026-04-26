with session_steps as (
    select
        session_id,
        min(funnel_step) as min_step,
        max(funnel_step) as max_step,
        count(distinct funnel_step) as distinct_steps
    from {{ ref('stg_events') }}
    where session_id <> 'unknown_session'
    group by session_id
)

select *
from session_steps
where min_step <> 1
   or max_step not between 1 and 5
   or distinct_steps <> max_step
