#!/usr/bin/env python

import socket
import msgUtils
import time
from time import gmtime, strftime

import binascii
from pprint import pprint

import sys
sys.path.append('./python-bitcoinlib');

import dash # monkeypatches bitcoin lib

from bitcoin import SelectParams
from bitcoin.core import CTxOut, COIN, b2lx
from bitcoin.wallet import P2PKHBitcoinAddress
from bitcoin.messages import CAddress, msg_version, msg_tx, msg_block, msg_mempool, msg_inv, msg_getdata, msg_pong, MsgSerializable
from bitcoin.net import CInv

from cStringIO import StringIO as BytesIO

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 19999))

SelectParams('testnet')

msg = msg_version()
print binascii.hexlify(msg.to_bytes())

print "sending version"
sock.send(msg_version().to_bytes())


def JSONtoAmount(value):
        return long(round(value * 1e8))
def AmountToJSON(amount):
        return float(amount / 1e8)

while True:
    data = sock.recv(100000)
    time.sleep(0.1)
    if len(data):
        f = BytesIO(data)
        msg = MsgSerializable.stream_deserialize(f)
        if msg is None:
            print strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " NONE " + binascii.hexlify(data)
            continue
        if msg.command == 'ping':
            pong = msg_pong(nonce=msg.nonce)
            print strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " " + str(pong)
            sock.send(pong.to_bytes())
            time.sleep(5)
        elif msg.command == 'inv':
            for i in msg.inv:
                if i.type in (15,14,13,12,7,6):
                    continue
                elif i.type in (1,3,4,5): # transaction/instantx
#                    Command ''ix'' not in messagemap
#                    Command ''txlvote'' not in messagemap
#                    gd = msg_getdata()
#                    gd.inv.append(i)
#                    sock.send(gd.to_bytes())
                    #print strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " --- " + str(i)
                    print " inv txid=%s - msg_inv(tx=%s)" % (b2lx(i.GetHash()), repr(i))
                else:
                    continue
        elif msg.command == 'ix':
            print " ix txid=%s - msg_tx(tx=%s)" % (b2lx(msg.GetHash()), repr(msg))
        elif msg.command == 'tx':
            for vout in msg.tx.vout:
                print strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " " + str("%.8f" % AmountToJSON(vout.nValue)) + " -> " + str(P2PKHBitcoinAddress.from_scriptPubKey(vout.scriptPubKey))
        else:
            print strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " xxx " + str(msg.command) + "\n    " + str(msg)
            continue

quit()
