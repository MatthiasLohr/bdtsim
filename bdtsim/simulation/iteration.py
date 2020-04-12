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


class Iteration(object):
    def __init__(self, seller_honesty_decision_list=None, buyer_honesty_decision_list=None):
        self._seller_honesty_decision_list = seller_honesty_decision_list or []
        self._buyer_honesty_decision_list = buyer_honesty_decision_list or []

    @property
    def seller_honesty_decision_list(self):
        return self._seller_honesty_decision_list

    @property
    def buyer_honesty_decision_list(self):
        return self._buyer_honesty_decision_list
