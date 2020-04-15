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


class Participant(object):
    def __init__(self, wallet_address: str, wallet_private_key: str):
        self._wallet_address = wallet_address
        self._wallet_private_key = wallet_private_key

    @property
    def wallet_address(self) -> str:
        return self._wallet_address

    @property
    def wallet_private_key(self) -> str:
        return self._wallet_private_key


operator = Participant(
    wallet_address='0x3ed8424aaE568b3f374e94a139D755982800a4a2',
    wallet_private_key='0xe67518b4d5255ec708d2bf9cd4222adda89fcc07037c614d7787a694fbb47692'
)

seller = Participant(
    wallet_address='0x5Afa5874959ff249103c2043fB45d68B2768Fef8',
    wallet_private_key='0x3df2d74ceb3c58a8fdb1f0ecf45e2ceb10511469d9c20691333d666fa557899a'
)

buyer = Participant(
    wallet_address='0x00c382926f098566EA6F1707296eC342E7C8A5DC',
    wallet_private_key='0x7d96e8fbe712cf25f141adb6bc5e3244d7a19d9c406ab6ed6a097585d01b93ac'
)
