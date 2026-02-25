REGISTER_DATASET_TEMPLATE = """
{
  "ap": {
  "edges": [
    {
      "from": "{{ analytical_pattern_node_id }}",
      "labels": [
        "consist_of"
      ],
      "to": "{{ dmm_operator_node_id }}"
    },
    {
      "from": "{{ dataset_node_id }}",
      "labels": [
        "input"
      ],
      "to": "{{ dmm_operator_node_id }}"
    },
    {
      "from": "{{ task_node_id }}",
      "labels": [
        "is_accomplished"
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
      "id": "{{ analytical_pattern_node_id }}",
      "labels": [
        "Analytical_Pattern"
      ],
      "properties": {
        "description": "Analytical Pattern to register a dataset",
        "name": "Register Dataset AP",
        "process": "register",
        "publishedDate": "{{ published_date }}",
        "startTime": "{{ start_time }}"
      }
    },
    {
      "id": "{{ dmm_operator_node_id }}",
      "labels": [
        "DataModelManagement_Operator"
      ],
      "properties": {
        "description": "An operator to register a dataset into DataGEMS",
        "name": "Register Operator",
        "command": "create",
        "publishedDate": "{{ published_date }}",
        "startTime": "{{ start_time }}",
        "step": 1
      }
    },
    {
      "id": "{{ dataset_node_id }}",
      "labels": [
        "sc:Dataset"
      ],
      "properties": {
        "type": "sc:Dataset"
        {% if dataset_archived_at %}
            ,"sc:archivedAt": "{{ dataset_archived_at }}"
        {% endif %}
        {% if dataset_cite_as %}
            ,"citeAs": "{{ dataset_cite_as }}"
        {% endif %}
        {% if dataset_conforms_to %}
            ,"conformsTo": "{{ dataset_conforms_to }}"
        {% endif %}
        {% if dataset_country %}
            ,"country": "{{ dataset_country }}"
        {% endif %}
        {% if dataset_date_published %}
            ,"datePublished": "{{ dataset_date_published }}"
        {% endif %}
        {% if dataset_description %}
            ,"description": "{{ dataset_description }}"
        {% endif %}
        {% if dataset_fields_of_science %}
            ,"dg:fieldOfScience": {{ dataset_fields_of_science }}
        {% endif %}
        {% if dataset_headline %}
            ,"dg:headline": "{{ dataset_headline }}"
        {% endif %}
        {% if dataset_languages %}
            ,"inLanguage": {{ dataset_languages }}
        {% endif %}
        {% if dataset_keywords %}
            ,"dg:keywords": {{ dataset_keywords }}
        {% endif %}
        {% if dataset_license %}
            ,"license": "{{ dataset_license }}"
        {% endif %}
        {% if dataset_name %}
            ,"name": "{{ dataset_name }}"
        {% endif %}
        {% if dataset_doi %}
            ,"dg:doi": "{{ dataset_doi }}"
        {% endif %}
        {% if analytical_pattern_node_status %}
            ,"dg:status": "{{ analytical_pattern_node_status }}"
        {% endif %}
        {% if dataset_url %}
            ,"url": "{{ dataset_url }}"
        {% endif %}
        {% if dataset_version %}
            ,"version": "{{ dataset_version }}"
        {% endif %}
      }
    },
    {
      "id": "{{ user_node_id }}",
      "labels": [
        "User"
      ]
      {% if user_id %}
          ,"properties": {
            "UserId": "{{ user_id }}"
          }
      {% endif %}
    },
    {
      "id": "{{ task_node_id }}",
      "labels": [
        "Task"
      ],
      "properties": {
        "description": "Task to register a dataset",
        "name": "Dataset Registering Task"
      }
    }
  ]
  }
}
"""
