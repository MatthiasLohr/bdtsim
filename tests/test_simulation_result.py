# This file is part of the Blockchain Data Trading Simulator
#    https://gitlab.com/MatthiasLohr/bdtsim
#
# Copyright 2021 Matthias Lohr <mail@mlohr.com>
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

from unittest import TestCase

from bdtsim.account import Account
from bdtsim.simulation_result import SimulationResult, SimulationResultSerializer


buyer = Account('Buyer', '0x0633ee528dcfb901af1888d91ce451fc59a71ae7438832966811eb68ed97c173')
seller = Account('Seller', '0x3f2c7f45cb3014e2b9d12b7fb331bdfdad6170ce5e4a0d94890aa64162569756')
operator = Account('Operator', '0x3f2c7f45cb3014e2b9d12b7fb331bdfdad6170ce5e4a0d94890aa64162569756')


class SimulationResultSerializerTest(TestCase):
    def test_serialize_unserialize_defaults(self) -> None:
        sr_original = SimulationResult(operator, seller, buyer)
        serializer = SimulationResultSerializer()
        serialized = serializer.serialize(sr_original)
        sr_restored = serializer.unserialize(serialized)

        self.assertNotEqual(
            SimulationResult(operator, seller, buyer),
            SimulationResult(operator, buyer, seller)
        )

        self.assertEqual(sr_restored, sr_original)

    def test_serialize_unserialize_compression1_b64encoding1(self) -> None:
        sr_original = SimulationResult(operator, seller, buyer)
        serializer = SimulationResultSerializer(compression=True, b64encoding=True)
        serialized = serializer.serialize(sr_original)
        sr_restored = serializer.unserialize(serialized)
        self.assertEqual(sr_restored, sr_original)

    def test_serialize_unserialize_compression1_b64encoding0(self) -> None:
        sr_original = SimulationResult(operator, seller, buyer)
        serializer = SimulationResultSerializer(compression=True, b64encoding=False)
        serialized = serializer.serialize(sr_original)
        sr_restored = serializer.unserialize(serialized)
        self.assertEqual(sr_restored, sr_original)

    def test_serialize_unserialize_compression0_b64encoding1(self) -> None:
        sr_original = SimulationResult(operator, seller, buyer)
        serializer = SimulationResultSerializer(compression=False, b64encoding=True)
        serialized = serializer.serialize(sr_original)
        sr_restored = serializer.unserialize(serialized)
        self.assertEqual(sr_restored, sr_original)

    def test_serialize_unserialize_compression0_b64encoding0(self) -> None:
        sr_original = SimulationResult(operator, seller, buyer)
        serializer = SimulationResultSerializer(compression=False, b64encoding=False)
        serialized = serializer.serialize(sr_original)
        sr_restored = serializer.unserialize(serialized)
        self.assertEqual(sr_restored, sr_original)
