{% macro classify_segment(metric_name) %}
  case
    when {{ metric_name }} > 500 then 'high'
    when {{ metric_name }} >= 200 then 'mid'
    else 'low'
  end
{% endmacro %}
