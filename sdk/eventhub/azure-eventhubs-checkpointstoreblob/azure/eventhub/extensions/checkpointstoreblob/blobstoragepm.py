# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Iterable, Dict, Any
import logging
from collections import defaultdict

from azure.eventhub import PartitionManager, OwnershipLostError  # type: ignore
from azure.core.exceptions import ResourceModifiedError, ResourceExistsError  # type: ignore
from azure.storage.blob import ContainerClient, BlobClient  # type: ignore

logger = logging.getLogger(__name__)
UPLOAD_DATA = ""


class BlobPartitionManager(PartitionManager):
    """An PartitionManager that uses Azure Blob Storage to store the partition ownership and checkpoint data.

    This class implements methods list_ownership, claim_ownership, and update_checkpoint that are defined in class
    azure.eventhub.eventprocessor.PartitionManager of package azure-eventhub.

    """
    def __init__(self, container_client: ContainerClient):
        """Create a BlobPartitionManager

        :param container_client: The Azure Blob Storage Container client that is used to save checkpoint data to Azure
        Blob Storage Container.
        """
        self._container_client = container_client
        self._cached_blob_clients = defaultdict()  # type:Dict[str, BlobClient]

    def _get_blob_client(self, blob_name):
        result = self._cached_blob_clients.get(blob_name)
        if not result:
            result = self._container_client.get_blob_client(blob_name)
            self._cached_blob_clients[blob_name] = result
        return result

    def _upload_ownership(self, ownership, metadata):
        etag = ownership.get("etag")
        if etag:
            etag_match = {"if_match": etag}
        else:
            etag_match = {"if_none_match": '*'}
        blob_name = "{}/{}/{}/ownership/{}".format(ownership["namespace"], ownership["eventhub_name"],
                                     ownership["consumer_group_name"], ownership["partition_id"])
        uploaded_blob_properties = self._get_blob_client(blob_name).upload_blob(
            data=UPLOAD_DATA, overwrite=True, metadata=metadata, **etag_match
        )
        ownership["etag"] = uploaded_blob_properties["etag"]
        ownership["last_modified_time"] = uploaded_blob_properties["last_modified"].timestamp()
        ownership.update(metadata)

    def list_ownership(self, namespace: str, eventhub_name: str, consumer_group_name: str) -> Iterable[Dict[str, Any]]:
        try:
            blobs = self._container_client.list_blobs(
                name_starts_with="{}/{}/{}/ownership".format(namespace, eventhub_name, consumer_group_name),
                include=['metadata'])
            result = []
            for b in blobs:
                ownership = {
                    "namespace": namespace,
                    "eventhub_name": eventhub_name,
                    "consumer_group_name": consumer_group_name,
                    "partition_id": b.name.split("/")[-1],
                    "owner_id": b.metadata["ownerId"],
                    "etag": b.etag,
                    "last_modified_time": b.last_modified.timestamp() if b.last_modified else None
                }
                result.append(ownership)
            return result
        except Exception as err:  # pylint:disable=broad-except
            logger.warning("An exception occurred during list_ownership for "
                           "namespace %r eventhub %r consumer group %r. "
                           "Exception is %r", namespace, eventhub_name, consumer_group_name, err)
            raise

    def _claim_one_partition(self, ownership):
        partition_id = ownership["partition_id"]
        namespace = ownership["namespace"]
        eventhub_name = ownership["eventhub_name"]
        consumer_group_name = ownership["consumer_group_name"]
        owner_id = ownership["owner_id"]
        metadata = {"ownerId": owner_id}
        try:
            self._upload_ownership(ownership, metadata)
            return ownership
        except (ResourceModifiedError, ResourceExistsError):
            logger.info(
                "EventProcessor instance %r of namespace %r eventhub %r consumer group %r lost ownership to partition %r",
                owner_id, namespace, eventhub_name, consumer_group_name, partition_id)
            raise OwnershipLostError()
        except Exception as err:  # pylint:disable=broad-except
            logger.warning("An exception occurred when EventProcessor instance %r claim_ownership for "
                           "namespace %r eventhub %r consumer group %r partition %r. The ownership is now lost. Exception "
                           "is %r", owner_id, namespace, eventhub_name, consumer_group_name, partition_id, err)
            return ownership  # Keep the ownership if an unexpected error happens

    def claim_ownership(self, ownership_list: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
        gathered_results = []
        for x in ownership_list:
            try:
                gathered_results.append(self._claim_one_partition(x))
            except (ResourceModifiedError, ResourceExistsError):
                pass
        return gathered_results

    def update_checkpoint(self, namespace, eventhub_name, consumer_group_name, partition_id,
                                offset, sequence_number) -> None:
        metadata = {
            "Offset": offset,
            "SequenceNumber": str(sequence_number),
        }
        blob_name = "{}/{}/{}/checkpoint/{}".format(namespace, eventhub_name,
                                     consumer_group_name, partition_id)
        self._get_blob_client(blob_name).upload_blob(
            data=UPLOAD_DATA, overwrite=True, metadata=metadata
        )

    def list_checkpoints(self, namespace, eventhub_name, consumer_group_name):
        blobs = self._container_client.list_blobs(
            name_starts_with="{}/{}/{}/checkpoint".format(namespace, eventhub_name, consumer_group_name),
            include=['metadata'])
        result = []
        for b in blobs:
            metadata = b.metadata
            checkpoint = {
                "namespace": namespace,
                "eventhub_name": eventhub_name,
                "consumer_group_name": consumer_group_name,
                "partition_id": b.name.split("/")[-1],
                "offset": metadata["Offset"],
                "sequence_number": metadata["SequenceNumber"]
            }
            result.append(checkpoint)
        return result
