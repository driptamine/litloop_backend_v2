import os
from django.conf import settings
from google.cloud import compute_v1


def launch_spot_transcriber(voice_msg_id: int, gcs_path: str):
    project_id = getattr(settings, 'GCS_PROJECT_ID', None) or os.environ.get('GCS_PROJECT_ID')
    zone = os.environ.get('GCP_ZONE', 'us-central1-a')
    callback_url = os.environ.get('CALLBACK_URL', 'https://litloop.duckdns.org/chats/voice/transcribe-callback/')
    api_key = os.environ.get('TRANSCRIBER_API_KEY', '')
    bucket_name = getattr(settings, 'GCS_BUCKET_NAME', 'litloop_bucket_free')
    model_size = os.environ.get('WHISPER_MODEL_SIZE', 'base')
    image_project = os.environ.get('GCP_IMAGE_PROJECT', 'cos-cloud')
    image_family = os.environ.get('GCP_IMAGE_FAMILY', 'cos-stable')
    container_image = os.environ.get('TRANSCRIBER_CONTAINER_IMAGE', 'gcr.io/{}/transcription-service:latest'.format(project_id))
    machine_type = os.environ.get('GCP_MACHINE_TYPE', 'g2-standard-4')
    accelerator_type = os.environ.get('GCP_ACCELERATOR', 'nvidia-l4')

    instance_name = f"transcriber-{voice_msg_id}-{os.urandom(4).hex()}"

    startup_script = f"""#!/bin/bash
set -e
INSTANCE_NAME=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/name)
cleanup() {{
  gcloud compute instances delete "$INSTANCE_NAME" --zone="{zone}" --quiet || true
}}
trap cleanup EXIT
docker pull {container_image}
docker run --gpus all \\
  -e AUDIO_GCS_PATH="{gcs_path}" \\
  -e CALLBACK_URL="{callback_url}" \\
  -e API_KEY="{api_key}" \\
  -e VOICE_MSG_ID="{voice_msg_id}" \\
  -e WHISPER_MODEL_SIZE="{model_size}" \\
  -e GCS_BUCKET_NAME="{bucket_name}" \\
  {container_image}
"""

    instance = compute_v1.Instance()
    instance.name = instance_name
    instance.machine_type = f"zones/{zone}/machineTypes/{machine_type}"

    disk = compute_v1.AttachedDisk()
    initialize_params = compute_v1.AttachedDiskInitializeParams()
    initialize_params.source_image = f"projects/{image_project}/global/images/family/{image_family}"
    initialize_params.disk_size_gb = 50
    initialize_params.disk_type = f"zones/{zone}/diskTypes/pd-ssd"
    disk.initialize_params = initialize_params
    disk.boot = True
    instance.disks = [disk]

    network_interface = compute_v1.NetworkInterface()
    network_interface.name = "global/networks/default"
    access_config = compute_v1.AccessConfig()
    access_config.name = "External NAT"
    network_interface.access_configs = [access_config]
    instance.network_interfaces = [network_interface]

    accelerator = compute_v1.AcceleratorConfig()
    accelerator.accelerator_type = f"zones/{zone}/acceleratorTypes/{accelerator_type}"
    accelerator.accelerator_count = 1
    instance.guest_accelerators = [accelerator]

    scheduling = compute_v1.Scheduling()
    scheduling.preemptible = True
    scheduling.on_host_maintenance = "TERMINATE"
    instance.scheduling = scheduling

    service_account = compute_v1.ServiceAccount()
    service_account.email = "default"
    service_account.scopes = [
        "https://www.googleapis.com/auth/cloud-platform",
    ]
    instance.service_accounts = [service_account]

    metadata = compute_v1.Metadata()
    metadata_item = compute_v1.Items()
    metadata_item.key = "startup-script"
    metadata_item.value = startup_script
    metadata.items = [metadata_item]
    instance.metadata = metadata

    client = compute_v1.InstancesClient()
    operation = client.insert(
        project=project_id,
        zone=zone,
        instance_resource=instance,
    )
    operation.result()

    return instance_name
