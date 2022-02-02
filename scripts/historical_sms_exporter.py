import logging
from datetime import datetime, timezone

from brownie import chain
from yearn.historical_helper import export_historical, time_tracking
from yearn.networks import Network
from yearn.treasury.treasury import StrategistMultisig
from yearn.utils import closest_block_after_timestamp

logger = logging.getLogger('yearn.historical_sms_exporter')


def main():
    start = datetime.now(tz=timezone.utc)
    
    end = {
        Network.Mainnet: datetime(2021, 1, 28, 9, 10, tzinfo=timezone.utc), # first inbound sms tx
        Network.Fantom: datetime(2021, 6, 17, tzinfo=timezone.utc), # Fantom SMS deployed
    }[chain.id]

    data_query = {
        Network.Mainnet: 'sms_assets{network="ETH"}',
        Network.Fantom: 'sms_assets{network="FTM"}',
    }[chain.id]
        
    export_historical(
        start,
        end,
        export_chunk,
        export_snapshot,
        data_query
    )
    
    
def export_chunk(chunk, export_snapshot_func):
    sms = StrategistMultisig()
    for snapshot in chunk:
        ts = snapshot.timestamp()
        export_snapshot_func(
            {
                'treasury': sms,
                'snapshot': snapshot,
                'ts': ts,
                'exporter_name': 'historical_sms'
            }
        )   


@time_tracking
def export_snapshot(sms, snapshot, ts, exporter_name):
    block = closest_block_after_timestamp(ts)
    assert block is not None, "no block after timestamp found"
    sms.export(block, ts)
    logger.info("exported SMS snapshot %s", snapshot)


