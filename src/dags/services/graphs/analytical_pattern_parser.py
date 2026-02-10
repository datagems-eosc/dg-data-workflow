import ast
import uuid
from datetime import datetime
from typing import Any

from jinja2 import Template

from common.extensions.utils import is_iterable
from common.types import AnalyticalPatternNode, AnalyticalPatternGraph, AnalyticalPatternEdge
from common.types.profiled_dataset import DatasetResponse
from configurations.analytical_pattern_templates import REGISTER_DATASET_TEMPLATE, LOAD_DATASET_TEMPLATE


class AnalyticalPatternParser:
    def __init__(self):
        pass

    def gen_register_dataset(self, values: dict[str, Any]) -> dict[str, Any]:
        template = Template(REGISTER_DATASET_TEMPLATE)
        return ast.literal_eval(template.render(**values))

    def gen_load_dataset(self, values: dict[str, Any]) -> dict[str, Any]:
        template = Template(LOAD_DATASET_TEMPLATE)
        return ast.literal_eval(template.render(**values))

    def gen_update_dataset(self, values: DatasetResponse, date: datetime) -> dict[str, Any]:
        ap_node = AnalyticalPatternNode(labels=["Analytical_Pattern"], properties={
            "Description": "Analytical Pattern to update a dataset",
            "Name": "Update Dataset AP",
            "Process": "update",
            "PublishedDate": date.strftime("%d-%m-%Y"),
            "StartTime": date.strftime("%H:%M:%S")
        }, excluded_properties=[])
        operator_node = AnalyticalPatternNode(labels=["DataModelManagement_Operator"], properties={
            "Description": "An operator to update a dataset into DataGEMS",
            "Name": "Update Operator",
            "command": "update",
            "PublishedDate": date.strftime("%d-%m-%Y"),
            "Software": {},
            "StartTime": date.strftime("%H:%M:%S"),
            "Step": 1
        }, excluded_properties=[])
        user_node = AnalyticalPatternNode(labels=["User"], properties={
            "UserId": getattr(values, "uploadedBy", "")
        }, excluded_properties=[])
        task_node = AnalyticalPatternNode(labels=["Task"], properties={
            "Description": "Task to update a dataset",
            "Name": "Dataset Updating Task"
        }, excluded_properties=[])
        dataset_node = AnalyticalPatternNode(labels=[values.type], properties=values.model_dump(),
                                             id=uuid.UUID(values.id), excluded_properties=["context", "id", "distribution", "recordSet"])
        graph = AnalyticalPatternGraph(nodes=[ap_node, operator_node, user_node, task_node, dataset_node], edges=[
            AnalyticalPatternEdge.from_nodes(frm=ap_node, to=operator_node, labels=["consist_of"]),
            AnalyticalPatternEdge.from_nodes(frm=dataset_node, to=operator_node, labels=["input"]),
            AnalyticalPatternEdge.from_nodes(frm=user_node, to=task_node, labels=["request"]),
            AnalyticalPatternEdge.from_nodes(frm=task_node, to=ap_node, labels=["is_achieved"])
        ])
        if hasattr(values, "distribution") and values.distribution and is_iterable(values.distribution):
            for i in values.distribution:
                i_node = AnalyticalPatternNode(labels=[i.type], properties=i.model_dump(),
                                               id=uuid.UUID(i.id), excluded_properties=["id"])
                graph.nodes.append(i_node)
                graph.edges.append(AnalyticalPatternEdge.from_nodes(frm=dataset_node, to=i_node, labels=["distribution"]))
        if hasattr(values, "recordSet") and values.recordSet and is_iterable(values.recordSet):
            for i in values.recordSet:
                i_node = AnalyticalPatternNode(labels=[i.type], properties=i.model_dump(), id=uuid.UUID(i.id), excluded_properties=["id", "field"])
                graph.nodes.append(i_node)
                graph.edges.append(AnalyticalPatternEdge.from_nodes(frm=dataset_node, to=i_node, labels=["recordSet"]))
                if hasattr(i, "field") and i.field and is_iterable(i.field):
                    for j in i.field:
                        j_node = AnalyticalPatternNode(labels=[j.name, j.type], properties=j.model_dump(), id=uuid.UUID(j.id), excluded_properties=["id"])
                        graph.nodes.append(j_node)
                        graph.edges.append(AnalyticalPatternEdge.from_nodes(frm=i_node, to=j_node, labels=["field"]))

        return graph.to_dict()
