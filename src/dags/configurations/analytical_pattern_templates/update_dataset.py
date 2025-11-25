# TODO: refactor file object node to accept variable extension and possibly expand AP to many such nodes?
UPDATE_DATASET_TEMPLATE = """
{
  "edges": [
    {
      "from": "{{ analytical_pattern_node_id }}",
      "labels": [
        "consist_of"
      ],
      "to": "{{ dmm_operator_node_id }}"
    },
    {
      "from": "{{ user_node_id }}",
      "labels": [
        "intervene"
      ],
      "to": "{{ dmm_operator_node_id }}"
    },
    
    {# =============================================================== #}
    {# 1) OPERATOR → DATASET (input edge)                              #}
    {# =============================================================== #}
    {
      "from": "{{ dmm_operator_node_id }}",
      "labels": ["input"],
      "to": "{{ payload.id }}"
    },

    {# =============================================================== #}
    {# 2) DATASET → DISTRIBUTION                                       #}
    {# =============================================================== #}
    {% for dist in payload.distribution %}
    {
      "from": "{{ payload.id }}",
      "labels": ["distribution"],
      "to": "{{ dist['@id'] }}"
    },
    {% endfor %}

    {# =============================================================== #}
    {# 3) DATASET → RECORDSET                                         #}
    {# =============================================================== #}
    {% for rs in payload.recordSet %}
    {
      "from": "{{ payload.id }}",
      "labels": ["recordSet"],
      "to": "{{ rs['@id'] }}"
    },
    {% endfor %}

    {# =============================================================== #}
    {# 4) RECORDSET → FIELD                                           #}
    {# =============================================================== #}
    {% for rs in payload.recordSet %}
        {% for field in rs.field %}
        {
          "from": "{{ rs['@id'] }}",
          "labels": ["field"],
          "to": "{{ field['@id'] }}"
        },
        {% endfor %}
    {% endfor %}
    
    {
      "from": "{{ task_node_id }}",
      "labels": [
        "is_achieved"
      ],
      "to": "{{ analytical_pattern_node_id }}"
    },
    {
      "from": "{{ user_node_id }}",
      "labels": [
        "request"
      ],
      "to": "{{ task_node_id }}"
    }
  ],
  "nodes": [
    {
      "@id": "{{ analytical_pattern_node_id }}",
      "labels": [
        "Analytical_Pattern"
      ],
      "properties": {
        "Description": "Analytical Pattern to update a dataset",
        "Name": "Update Dataset AP",
        "Process": "update",
        "PublishedDate": "{{ published_date }}",
        "StartTime": "{{ start_time }}"
      }
    },
    {
      "@id": "{{ dmm_operator_node_id }}",
      "labels": [
        "DataModelManagement_Operator"
      ],
      "properties": {
        "Description": "An operator to update a dataset into DataGEMS",
        "Name": "Update Operator",
        "Parameters": {
          "command": "update"
        },
        "PublishedDate": "{{ published_date }}",
        "Software": {},
        "StartTime": "{{ start_time }}",
        "Step": 1
      }
    },
    {
      "@id": "{{ payload.id }}",
      "labels": [
        "sc:Dataset"
      ],
      "properties": {
        "@type": "sc:Dataset",
        "archivedAt": "{{ dataset_archived_at }}",
        "archivedBy": "{{ dataset_archived_by }}",
        "citeAs": "{{ dataset_cite_as }}",
        "conformsTo": "{{ dataset_conforms }}",
        "country": "{{ payload.country }}",
        "datePublished": "{{ payload.datePublished }}",
        "description": "{{ payload.description }}",
        "fieldOfScience": {{ payload.fieldOfScience | tojson }},
        "headline": "{{ payload.headline }}",
        "inLanguage": {{ payload.inLanguage | tojson }},
        "keywords": {{ payload.keywords | tojson }},
        "license": "{{ payload.license }}",
        "name": "{{ payload.name }}",
        "url": "{{ payload.url }}",
        "version": "{{ payload.version }}"
      }
    },
    {% for dist in payload.distribution %}
    {{ dist | tojson }},
    {% endfor %}
    
    {% for rs in payload.recordSet %}
        {{ rs | tojson }},
        {% for f in rs.field %}
            {{ f | tojson }},
        {% endfor %}
    {% endfor %}
    {
      "@id": "{{ user_node_id }}",
      "labels": [
        "User"
      ],
      "properties": {
        "UserId": "{{ user_user_id }}"
      }
    },
    {
      "@id": "{{ task_node_id }}",
      "labels": [
        "Task"
      ],
      "properties": {
        "Description": "Task to update a dataset",
        "Name": "Dataset Updating Task"
      }
    }
  ]
}"""
