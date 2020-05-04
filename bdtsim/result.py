# This file is part of the Blockchain Data Trading Simulator
#    https://gitlab.com/MatthiasLohr/bdtsim
#
# Copyright 2020 Matthias Lohr <mail@mlohr.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from json import JSONEncoder
from typing import Any, Dict, List, Optional

from hexbytes.main import HexBytes
from web3.datastructures import AttributeDict

from bdtsim.environment import TransactionLogEntry
from .participant import Participant
from .protocol_path import Decision, ProtocolPath


class PreparationResult(object):
    def __init__(self, transaction_logs: Optional[List[TransactionLogEntry]] = None) -> None:
        self._transaction_logs = transaction_logs or []

    @property
    def transaction_logs(self) -> List[TransactionLogEntry]:
        return self._transaction_logs

    @property
    def transaction_count(self) -> int:
        return len(self.transaction_logs)

    @property
    def transaction_cost_sum(self) -> int:
        return sum([int(str(entry.transaction_receipt.get('gasUsed'))) for entry in self.transaction_logs])


class IterationResult(object):
    def __init__(self, protocol_path: ProtocolPath,
                 preparation_transaction_logs: Optional[List[TransactionLogEntry]] = None,
                 execution_transaction_logs: Optional[List[TransactionLogEntry]] = None,
                 cleanup_transaction_logs: Optional[List[TransactionLogEntry]] = None) -> None:
        self._protocol_path = protocol_path
        self._preparation_transaction_logs = preparation_transaction_logs or []
        self._execution_transaction_logs = execution_transaction_logs or []
        self._cleanup_transaction_logs = cleanup_transaction_logs or []

    @property
    def protocol_path(self) -> ProtocolPath:
        return self._protocol_path

    @property
    def preparation_transaction_logs(self) -> List[TransactionLogEntry]:
        return self._preparation_transaction_logs

    @property
    def execution_transaction_logs(self) -> List[TransactionLogEntry]:
        return self._execution_transaction_logs

    @property
    def cleanup_transaction_logs(self) -> List[TransactionLogEntry]:
        return self._cleanup_transaction_logs

    @property
    def transaction_logs(self) -> List[TransactionLogEntry]:
        return self._preparation_transaction_logs + self._execution_transaction_logs + self._cleanup_transaction_logs

    def all_participants_were_honest(self) -> bool:
        return self.protocol_path.all_participants_were_honest()

    def transaction_fee_sum_by_participant(self, participant: Participant) -> int:
        return sum([
            int(str(log.transaction_receipt.get('gasUsed')))
            for log in filter(lambda x: x.account == participant, self.transaction_logs)
        ])

    def transaction_count_by_participant(self, participant: Participant) -> int:
        return len(list(filter(lambda x: x.account == participant, self.transaction_logs)))


class SimulationResult(object):
    def __init__(self, operator: Participant, seller: Participant, buyer: Participant,
                 preparation_result: Optional[PreparationResult] = None,
                 iteration_results: Optional[List[IterationResult]] = None) -> None:
        self._participants_by_address: Dict[str, Participant] = {}
        for participant in operator, seller, buyer:
            self._participants_by_address.update({participant.wallet_address: participant})

        self._preparation_result = preparation_result
        self._iteration_results = iteration_results or []

    @property
    def preparation_result(self) -> Optional[PreparationResult]:
        return self._preparation_result

    @property
    def iteration_results(self) -> List[IterationResult]:
        return self._iteration_results

    @property
    def completely_honest_iteration_result(self) -> IterationResult:
        for ir in self.iteration_results:
            if ir.all_participants_were_honest():
                return ir
        raise RuntimeError('Impossible result: There MUST be a completely honest iteration')


class ResultSerializer(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, AttributeDict):
            return dict(obj)
        elif isinstance(obj, Decision):
            return {
                'account': obj.account,
                'variant': obj.variant,
                'timestamp': obj.timestamp
            }
        elif isinstance(obj, HexBytes):
            return obj.hex()
        elif isinstance(obj, IterationResult):
            return {
                'protocol_path': obj.protocol_path,
                'transaction_logs': obj.transaction_logs
            }
        elif isinstance(obj, Participant):
            return {
                'name': obj.name,
                'wallet_address': obj.wallet_address
            }
        elif isinstance(obj, PreparationResult):
            return {
                'transaction_logs': obj.transaction_logs
            }
        elif isinstance(obj, ProtocolPath):
            return obj.decisions
        elif isinstance(obj, SimulationResult):
            return {
                'preparation_result': obj.preparation_result,
                'iteration_results': obj.iteration_results
            }
        elif isinstance(obj, TransactionLogEntry):
            return {
                'account': obj.account,
                'transaction_receipt': obj.transaction_receipt,
                'timestamp': obj.timestamp
            }
        else:
            return JSONEncoder.default(self, obj)
