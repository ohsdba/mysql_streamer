# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from yelp_batch import Batch

from replication_handler import config
from replication_handler.components.heartbeat_searcher import HeartbeatSearcher
from replication_handler.environment_configs import is_avoid_internal_packages_set
from replication_handler.models.database import get_connection


class MySQLHeartbeatSearchBatch(Batch):
    """Batch which runs the heartbeat searcher component from the command line.
    Useful for manual testing.

    To use from the command line:
        python -m replication_handler.batch.mysql_heartbeat_search \
            {heartbeat_time_stamp} {heartbeat_serial}
    Note that the heartbeat_time_stamp should be utc timestamp, eg, 1447354877
    Prints information about the heartbeat or None if the heartbeat could
    not be found.
    """

    notify_emails = [
        "bam+replication+handler@yelp.com"
    ]

    def __init__(self, hb_timestamp, hb_serial):
        super(MySQLHeartbeatSearchBatch, self).__init__()
        self.hb_timestamp = hb_timestamp
        self.hb_serial = hb_serial
        self.db_connections = get_connection(
            config.env_config.topology_path,
            config.env_config.rbr_source_cluster,
            config.env_config.schema_tracker_cluster,
            config.env_config.rbr_state_cluster,
            is_avoid_internal_packages_set()
        )

    def run(self):
        """Runs the batch by calling out to the heartbeat searcher component"""
        print HeartbeatSearcher(
            source_cursor=self.db_connections.get_source_cursor(),
            source_database_config=self.db_connections.source_database_config
        ).get_position(self.hb_timestamp, self.hb_serial)


if __name__ == '__main__':
    MySQLHeartbeatSearchBatch(int(sys.argv[1]), int(sys.argv[2])).start()
