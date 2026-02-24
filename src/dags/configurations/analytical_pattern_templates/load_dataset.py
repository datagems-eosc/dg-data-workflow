LOAD_DATASET_TEMPLATE = """
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
        "description": "Analytical Pattern to load a dataset",
        "name": "Load Dataset AP",
        "process": "load",
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
        "description": "An operator to load a dataset into s3/dataset",
        "name": "Load Operator",
        "command": "update",
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
        "sc:archivedAt": "{{ dataset_archived_at }}",
        "dg:status": "{{ analytical_pattern_node_status }}"
      }
    },
    {
      "id": "{{ user_node_id }}",
      "labels": [
        "User"
      ],
      "properties": {
        "UserId": "{{ user_id }}"
      }
    },
    {
      "id": "{{ task_node_id }}",
      "labels": [
        "Task"
      ],
      "properties": {
        "description": "Task to change storage location of a dataset",
        "name": "Dataset Loading Task"
      }
    }
  ]
  }
}
"""
