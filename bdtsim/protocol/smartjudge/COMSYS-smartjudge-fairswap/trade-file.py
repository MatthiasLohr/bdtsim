from web3 import Web3, HTTPProvider
import web3
import json

def printBalances(w3, alice, bob):
    balance = w3.fromWei(w3.eth.getBalance(alice), 'ether' );
    print("Alice: {} Eth".format(balance))
    balance = w3.fromWei(w3.eth.getBalance(bob), 'ether' );
    print("Bob: {} Eth".format(balance))

def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

w3 = Web3( HTTPProvider("http://127.0.0.1:8545") )

alice = w3.eth.accounts[0]
bob = w3.eth.accounts[1]

f = open("./mediator.abi", "r")
mediator_abi = json.load(f)
f.close()
f = open("./mediator.addr", "r")
mediator_addr = f.read()
f.close()
mediator = w3.eth.contract( address=mediator_addr, abi=mediator_abi)

f = open("./fairswap-verifier.abi", "r")
verifier_abi = json.load(f)
f.close()
f = open("./fairswap-verifier.addr", "r")
verifier_addr = f.read()
f.close()
verifier = w3.eth.contract( address=verifier_addr, abi=verifier_abi)


worst_case_cost_fairswap = 271000
tx_hash = mediator.functions.register_verifier( verifier_addr, worst_case_cost_fairswap ).transact({'from':alice})
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
verifier_id = int(receipt['logs'][0]['data'], 16 )
print("Registered Fairswap verifier")

# WE DEMONSTRATE THE CASE OF ALICE TRANSFERING A FILE TO BOB THAT DOES NOT MATCH THE AGREED UPON HASH
print("")
printBalances(w3,alice,bob)

# START OF DESCRIPTION OF TRADED FILE

pt_data  = [Web3.toBytes(hexstr="0x34cfe6e8a7143a7dc343e9d9b416c39fff15c69b1d2a761c9e716f3958a6fc39"), Web3.toBytes(hexstr="0x0cecc3208215cb9cd4887bca9e5d417f00b4b08bcd5ddcb3a70abd6e6a3945a0"), Web3.toBytes(hexstr="0x1a8b6cea32149ec73e18e14df4e30ce4a6c58dc3becbc2b5387eb40dab2930c7"), Web3.toBytes(hexstr="0xd252fc44f9345f594b8c5fa7eaec1d4a04ecdcf2759ee4d7cba332121221039e")]
pt_root  = Web3.toBytes(hexstr="0x996454c9ca11f9b5ace833f73695637babd6b57b7541242370743620e7690357")
key      = Web3.toBytes(hexstr="0x2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683")
z        = [    Web3.toBytes(hexstr="0x315cb9cec8f058767a324242299a3ad882e2cadaf0c62f5a77e4b272a5a3fa0b"), 
                Web3.toBytes(hexstr="0xb0db4219b77570d0051a2170e5c25b0ea5471646a37f8847777f9a991b9042e7"), 
                Web3.toBytes(hexstr="0x9f8ce923111bb868cf3056287a49f35d36b685d6eb514c23184b2fbd4143edf4"), 
                Web3.toBytes(hexstr="0x122afea9eb9efc00c85ea46327f2baf9e8c6d98db7cd0b17db0a9780f6fdf561")]

for i in range(2):
    z.append( byte_xor(Web3.soliditySha3(['uint256', 'bytes32'], [ 4+i, key ]), Web3.soliditySha3(['bytes32', 'bytes32'], [pt_data[2*i], pt_data[2*i+1] ])))

# We manipulate one value of the ciphertext. Alice later verifies the inconsistency of this part of the ciphertext
z[4] = Web3.toBytes(hexstr="0x1000000000000000000000000000000000000000000000000000000000000001")
                            
z.append( byte_xor(Web3.soliditySha3(['uint256', 'bytes32'], [ 4+i, key ]), Web3.soliditySha3(['bytes32', 'bytes32'], [z[4], z[5] ])))

z.append(Web3.toBytes(hexstr="0x20b7bddec55e1f306d929054a20033356e8839eeb16722e2c89cb326830cf717"))


z_merkle_nodes = []
for i in range(4):
    z_merkle_nodes.append(Web3.soliditySha3(['bytes32'], [z[i]]))

for i in range(4):
    z_merkle_nodes.append(z[4+i])

for i in range(7):
    z_merkle_nodes.append(Web3.soliditySha3(['bytes32', 'bytes32'], [z_merkle_nodes[2*i], z_merkle_nodes[2*i+1] ]))

z_root = z_merkle_nodes[14]

# END OF FILE DESCRIPTION

eth_price = 1000000000000000000
gas_price = w3.eth.gasPrice
security_deposit = 400000*gas_price

trade_conditions = Web3.soliditySha3(['bytes32', 'bytes32', 'bytes32'],[key, z_root,pt_root])
agreement = Web3.soliditySha3(['uint32','bytes32'],[verifier_id, trade_conditions])

# This creates new storage for this trade in the smart contract. Using create(id, agreement) for an id that represents a concluded trade is significantly cheaper.
tx_hash = mediator.functions.create( agreement ).transact({'from':alice, 'value':eth_price+security_deposit})
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
trade_id = int(receipt['logs'][0]['data'], 16 )
print("Alice created new trade")

tx_hash = mediator.functions.accept( trade_id ).transact({'from':bob, 'value':security_deposit})
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Bob accepted the trade")

# BOB IS EXPECTED TO TRANSFER THE CORRECT DECRYPTION KEY TO ALICE OFF CHAIN, BUT WE ASSUME HERE THAT THIS DOES NOT HAPPEN

# In order to not timeout, Bob is forced to reveal the key on chain after a while and contest the trade
decryption_key = "0x2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683"
tx_hash = mediator.functions.contest( trade_id, key ).transact({'from':bob, 'value':gas_price*worst_case_cost_fairswap})
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Bob revealed the decryption key and contested the trade")

'''
Note: There exist two design possibilities here. Either Bob announces the decrytion key
through a call to reveal() or as protocol witness when contending the trade. The verifier has
to implement the corresponding init_verification call in order to read the key from the right
location. This trade uses latter possibility and our verifier also only implements the init_verification()
function when no addition data is appended.

- reveal() is cheaper if both parties do not want to set up on off-chain communication channel (e.g., to preserve anonymity)
- immediately calling contend() is cheaper for Bob if Alice malicious (yes, Bob is reimboursed anyway but he can save the costs to execute reveal() on top of this)
'''

# Now Alice is forced to initiate the verification
tx_hash = mediator.functions.init_verification( trade_id, verifier_id, trade_conditions ).transact({'from':alice, 'value':gas_price*worst_case_cost_fairswap})
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Alice initiated verification")


tx_hash = verifier.functions.verify_initial_agreement( trade_id, z_root, pt_root ).transact({'from':bob})
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Bob verified the initial agreement")

indexOut = 4
indexIn = 0
Zout = z[4]
Zin1 = [ z[0] ]
Zin2 = [ z[1] ]
proofOut = [ z_merkle_nodes[5], z_merkle_nodes[11], z_merkle_nodes[12] ]
proofIn = [ z_merkle_nodes[1], z_merkle_nodes[9], z_merkle_nodes[13] ]
tx_hash = verifier.functions.complainAboutLeaf( trade_id, indexOut, indexIn, Zout, Zin1, Zin2, proofOut, proofIn).transact({'from':alice})
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Alice complains successfuly about inconsitent data transfer")
printBalances(w3,alice,bob)