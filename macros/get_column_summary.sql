{% macro get_column_summary(relation, column_name) %}
  select
    '{{ relation }}' as relation_name,
    '{{ column_name }}' as column_name,
    count(*) as total_rows,
    sum(case when {{ column_name }} is null then 1 else 0 end) as null_rows,
    count(distinct {{ column_name }}) as distinct_values
  from {{ relation }}
{% endmacro %}
