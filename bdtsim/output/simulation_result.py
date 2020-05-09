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

from typing import Any, Dict, List, Optional

from bdtsim.participant import Participant
from bdtsim.protocol_path import Decision


class TransactionLogEntry(object):
    def __init__(self, account: Participant, tx_dict: Dict[str, Any], tx_receipt: Dict[str, Any]) -> None:
        self._account = account
        self._tx_dict = tx_dict
        self._tx_receipt = tx_receipt


class ResultNode(object):
    def __init__(self, parent: Optional['ResultNode'] = None):
        self.parent = parent
        self.children: Dict[Decision, ResultNode] = {}
        self.transactions: List[List[TransactionLogEntry]] = []

    def child(self, decision: Decision) -> 'ResultNode':
        child = self.children.get(decision)
        if child is None:
            child = ResultNode(self)
            self.children.update({decision: child})
        return child


class SimulationResult(object):
    def __init__(self) -> None:
        self.preparation_transactions: List[TransactionLogEntry] = []
        self.execution_result_root = ResultNode()
        self.cleanup_transactions: List[TransactionLogEntry] = []
