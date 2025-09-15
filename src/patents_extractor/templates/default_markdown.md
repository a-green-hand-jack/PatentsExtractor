# 专利信息提取结果

## 问题
{{ question }}

## 答案
{{ answer }}

## 置信度
{{ confidence_score }}

## 相关文档片段
{% for section in relevant_sections %}
- {{ section }}
{% endfor %}

## 引用来源
{% for citation in source_citations %}
- {{ citation }}
{% endfor %}

## 处理信息
- 处理时间: {{ processing_time }}s
- 使用模型: {{ model_used }}
- Token使用: {{ tokens_used }}

---
*生成时间: {{ completed_steps[-1] if completed_steps else 'unknown' }}*
