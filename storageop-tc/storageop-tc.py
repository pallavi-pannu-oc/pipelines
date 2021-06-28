import json
import os

import kfp

search_path = os.path.dirname(os.path.abspath(__file__)) + "/../components"
component_store = kfp.components.ComponentStore(local_search_paths=[search_path])
storage_op = component_store.load_component("storage")


@kfp.dsl.pipeline(name="StorageOp-test", description="StorageOp component")
def storageop_testcases(dataset,code, preprocessing_script, dataset_mount_points,output_dataset, output_mount_path, model, dataset_version, model_version,):
    with kfp.dsl.ExitHandler(
        exit_op=storage_op("reclaim", namespace="kubeflow", uid="{{workflow.uid}}")
    ):
    
        download_data = dkube_preprocessing_op(
            auth_token=str(token),
            container=json.dumps({"image": "ocdr/d3-datascience-sklearn:v0.23.2-1"}),
            program=str(code),
            run_script=str(preprocessing_script),
            datasets=json.dumps([str(dataset)]),
            input_dataset_mounts=json.dumps([str(dataset_mount_points)]),
            outputs=json.dumps([str(output_dataset)]),
            output_mounts=json.dumps([str(output_mount_path)])
        )
        input_volumes = json.dumps(
            [
                "{{workflow.uid}}-dataset@dataset://"
                + str(dataset)
                + "/"
                + str(dataset_version),
                "{{workflow.uid}}-model@model://"
                + str(model)
                + "/"
                + str(model_version),
            ]
        )
        output_volumes = json.dumps(
            [
                "{{workflow.uid}}-dataset@dataset://" + str(dataset),
                "{{workflow.uid}}-model@model://" + str(model),
            ]
        )
        storage = storage_op(
            "export",
            namespace="kubeflow",
            input_volumes=input_volumes,
            output_volumes=output_volumes,
        ).after(download_data)
        train = kfp.dsl.ContainerOp(
            name="container-op",
            image="docker.io/ocdr/dkube-datascience-tf-cpu:v2.0.0-3",
            command="bash",
            arguments=["-c", "ls /dataset"],
            pvolumes={
                "/dataset": kfp.dsl.PipelineVolume(pvc="{{workflow.uid}}-dataset"),
                "/model": kfp.dsl.PipelineVolume(pvc="{{workflow.uid}}-model"),
            },
        ).after(storage)
