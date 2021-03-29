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

from hashlib import sha256
from typing import Any, Optional
from unittest import TestCase

from ecdsa.curves import SECP256k1  # type: ignore
from ecdsa.keys import SigningKey  # type: ignore


class EcdsaVulnerabilityTest(TestCase):
    HASH_FUNC = sha256
    DEFAULT_N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

    @staticmethod
    def to_int(data: Any) -> int:
        return int(data, 16)

    @staticmethod
    def hash_int(data: bytes) -> int:
        h = EcdsaVulnerabilityTest.HASH_FUNC()
        h.update(data)
        return EcdsaVulnerabilityTest.to_int(h.hexdigest())

    @staticmethod
    def mod_inv(x: int, n: Optional[int] = None) -> int:
        if n is None:
            n = EcdsaVulnerabilityTest.DEFAULT_N
        """modular multiplicative inverse (requires that n is prime)"""
        return pow(x, n - 2, n)

    def test_vulnerability(self) -> None:
        signing_key = SigningKey.generate(curve=SECP256k1)  # private key
        verifying_key = signing_key.verifying_key  # public key

        m1 = b'foo'
        m2 = b'bar'
        z1 = self.hash_int(m1)
        z2 = self.hash_int(m2)

        signature = signing_key.sign(m1, k=2, hashfunc=EcdsaVulnerabilityTest.HASH_FUNC)
        r = self.to_int(signature[:32].hex())
        s1 = self.to_int(signature[32:].hex())

        self.assertTrue(verifying_key.verify(signature, m1, hashfunc=EcdsaVulnerabilityTest.HASH_FUNC))

        signature2 = signing_key.sign(m2, k=2, hashfunc=EcdsaVulnerabilityTest.HASH_FUNC)
        s2 = self.to_int(signature2[32:].hex())

        self.assertTrue(verifying_key.verify(signature2, m2, hashfunc=EcdsaVulnerabilityTest.HASH_FUNC))

        k = (z1 - z2) * self.mod_inv(s1 - s2) % self.DEFAULT_N

        self.assertEqual(
            (s1 * k - z1) * self.mod_inv(r) % self.DEFAULT_N,
            (s2 * k - z2) * self.mod_inv(r) % self.DEFAULT_N
        )
