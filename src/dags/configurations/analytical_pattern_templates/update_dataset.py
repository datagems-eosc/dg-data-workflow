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
    },
    {
      "from": "{{ dataset_node_id }}",
      "labels": [
        "distribution"
      ],
      "to": "{{ file_object_node_id }}"
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
      "@id": "{{ dataset_node_id }}",
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
        "fieldOfScience": {{ payload.fieldOfScience }},
        "headline": "{{ payload.headline }}",
        "inLanguage": {{ payload.inLanguage }},
        "keywords": {{ payload.keywords }},
        "license": "{{ payload.license }}",
        "name": "{{ payload.name }}",
        "url": "{{ payload.url }}",
        "version": "{{ payload.version }}",
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
        "UserId": "{{ user_user_id }}",
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
