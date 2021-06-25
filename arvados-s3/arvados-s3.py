import json
import os

import kfp

search_path = os.path.dirname(os.path.abspath(__file__)) + "/../components"
component_store = kfp.components.ComponentStore(local_search_paths=[search_path])

dkube_preprocessing_op = component_store.load_component("preprocess")
dkube_training_op = component_store.load_component("training")
storage_op = component_store.load_component("storage")
dkube_serving_op = component_store.load_component("serving")


@kfp.dsl.pipeline(name="arv-s3", description="arvados-s3-pipeline")
def arv_pipeline(
    code,
    preprocessing_script,
    dataset,
    featureset,
    model,
    dataset_mount_points,
    featureset_mount_points,
    train_out_mount_points,
    training_script,
    token,
):

    with kfp.dsl.ExitHandler(
        exit_op=storage_op("reclaim", namespace="kubeflow", uid="{{workflow.uid}}")
    ):
        preprocessing = dkube_preprocessing_op(
            auth_token=str(token),
            container=json.dumps({"image": "ocdr/d3-datascience-sklearn:v0.23.2-1"}),
            program=str(code),
            run_script=str(preprocessing_script),
            datasets=json.dumps([str(dataset)]),
            output_featuresets=json.dumps([str(featureset)]),
            input_dataset_mounts=json.dumps([str(dataset_mount_points)]),
            output_featureset_mounts=json.dumps([str(featureset_mount_points)]),
        )
        dataset_volume = json.dumps(
            ["{{workflow.uid}}-dataset@dataset://" + str(dataset)]
        )

        storage = storage_op(
            "export", namespace="kubeflow", input_volumes=dataset_volume
        ).after(preprocessing)

        list_dataset = kfp.dsl.ContainerOp(
            name="container-op",
            image="docker.io/ocdr/dkube-datascience-tf-cpu:v2.0.0-3",
            command="bash",
            arguments=["-c", "ls /dataset/CMU-1"],
            pvolumes={
                "/dataset": kfp.dsl.PipelineVolume(pvc="{{workflow.uid}}-dataset")
            },
        ).after(storage)

        train = dkube_training_op(
            auth_token=str(token),
            container='{"image":"docker.io/ocdr/d3-datascience-sklearn:v0.23.2"}',
            framework="sklearn",
            version="0.23.2",
            program=str(code),
            run_script=str(training_script),
            datasets=json.dumps([str(dataset)]),
            outputs=json.dumps([str(model)]),
            input_dataset_mounts=json.dumps([str(dataset_mount_points)]),
            output_mounts=json.dumps([str(train_out_mount_points)]),
        ).after(preprocessing)

        serving = dkube_serving_op(
            model=model,
            device="cpu",
            serving_image='{"image":"ocdr/sklearnserver:0.23.2"}',
        ).after(train)
