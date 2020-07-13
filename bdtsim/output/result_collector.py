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

import logging
from types import TracebackType
from typing import Any, Dict, Optional, Type

from bdtsim.account import Account
from bdtsim.environment import Environment
from bdtsim.funds_diff_collection import FundsDiffCollection
from bdtsim.protocol_path import ProtocolPath, Decision
from .simulation_result import SimulationResult, ResultNode, TransactionLogEntry, TransactionLogList


logger = logging.getLogger(__name__)


class SimpleTransactionMonitor(object):
    def __init__(self, environment: Environment, transactions_target: TransactionLogList) -> None:
        self._environment = environment
        self._transactions_target = transactions_target

    def _transaction_callback(self, account: Account, tx_dict: Dict[str, Any], tx_receipt: Dict[str, Any],
                              funds_diff_collection: FundsDiffCollection) -> None:
        self._transactions_target.append(TransactionLogEntry(account, tx_dict, tx_receipt, funds_diff_collection))

    def __enter__(self) -> None:
        self._environment.transaction_callback = self._transaction_callback

    def __exit__(self, exception_type: Optional[Type[BaseException]], exception: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        self._environment.transaction_callback = None


class ExecutionTransactionMonitor(object):
    def __init__(self, environment: Environment, protocol_path: ProtocolPath,
                 execution_result_root: ResultNode) -> None:
        self._environment = environment
        self._protocol_path = protocol_path
        self._execution_result_root = execution_result_root

        self._current_execution_result_node: Optional[ResultNode] = None
        self._current_transactions: TransactionLogList = TransactionLogList()

    def _decision_callback(self, decision: Decision) -> None:
        if self._current_execution_result_node is None:
            raise RuntimeError()
        self._current_execution_result_node.tx_collection.append(self._current_transactions)
        self._current_transactions = TransactionLogList()
        self._current_execution_result_node = self._current_execution_result_node.child(decision)

    def _transaction_callback(self, account: Account, tx_dict: Dict[str, Any], tx_receipt: Dict[str, Any],
                              funds_diff_collection: FundsDiffCollection) -> None:
        self._current_transactions.append(TransactionLogEntry(account, tx_dict, tx_receipt, funds_diff_collection))

    def __enter__(self) -> None:
        self._current_execution_result_node = self._execution_result_root
        self._environment.transaction_callback = self._transaction_callback
        self._protocol_path.decision_callback = self._decision_callback

    def __exit__(self, exception_type: Optional[Type[BaseException]], exception: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        if self._current_execution_result_node is None:
            raise RuntimeError()
        self._current_execution_result_node.tx_collection.append(self._current_transactions)
        self._protocol_path.decision_callback = None
        self._environment.transaction_callback = None


class ResultCollector(object):
    def __init__(self, operator: Account, seller: Account, buyer: Account) -> None:
        self.simulation_result = SimulationResult(operator, seller, buyer)

    def monitor_preparation(self, environment: Environment) -> SimpleTransactionMonitor:
        return SimpleTransactionMonitor(environment, self.simulation_result.preparation_transactions)

    def monitor_execution(self, environment: Environment, protocol_path: ProtocolPath) -> ExecutionTransactionMonitor:
        return ExecutionTransactionMonitor(environment, protocol_path, self.simulation_result.execution_result_root)

    def monitor_cleanup(self, environment: Environment) -> SimpleTransactionMonitor:
        return SimpleTransactionMonitor(environment, self.simulation_result.cleanup_transactions)
