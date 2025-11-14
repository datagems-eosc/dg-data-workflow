LOAD_DATASET_TEMPLATE = """
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
      "from": "{{ dmm_operator_node_id }}",
      "labels": [
        "input"
      ],
      "to": "{{ dataset_node_id }}"
    },
    {
      "from": "{{ user_node_id }}",
      "labels": [
        "intervene"
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
      "@id": "{{ analytical_pattern_node_id }}",
      "labels": [
        "Analytical_Pattern"
      ],
      "properties": {
        "Description": "Analytical Pattern to load a dataset",
        "Name": "Load Dataset AP",
        "Process": "load",
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
        "Description": "An operator to load a dataset into s3/dataset",
        "Name": "Load Operator",
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
      "@id": "{{ dataset_node_id }}",
      "labels": [
        "sc:Dataset"
      ],
      "properties": {
        "@type": "sc:Dataset",
        "archivedAt": "{{ dataset_archived_at }}",
        "citeAs": "{{ dataset_cite_as }}",
        "conformsTo": "{{ dataset_conforms_to }}",
        "country": "{{ dataset_country }}",
        "datePublished": "{{ dataset_date_published }}",
        "description": "{{ dataset_description }}",
        "fieldOfScience": {{ dataset_fields_of_science }},
        "headline": "{{ dataset_headline }}",
        "inLanguage": {{ dataset_languages }},
        "keywords": {{ dataset_keywords }},
        "license": "{{ dataset_license }}",
        "name": "{{ dataset_name }}",
        "url": "{{ dataset_url }}",
        "version": "{{ dataset_version }}"
      }
    },
    {
      "@id": "{{ user_node_id }}",
      "labels": [
        "User"
      ],
      "properties": {
        "UserId": "{{ user_id }}"
      }
    },
    {
      "@id": "{{ task_node_id }}",
      "labels": [
        "Task"
      ],
      "properties": {
        "Description": "Task to change storage location of a dataset",
        "Name": "Dataset Loading Task"
      }
    }
  ]
}
"""
