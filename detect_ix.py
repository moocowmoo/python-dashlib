#!/usr/bin/env python

import socket
import time
from cStringIO import StringIO as BytesIO

import dash # noqa - monkeypatches bitcoin lib
from bitcoin import SelectParams
from bitcoin.core import b2lx
from bitcoin.messages import msg_version, msg_getdata, msg_pong, MsgSerializable
from bitcoin.wallet import P2PKHBitcoinAddress

SelectParams('testnet')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect and announce peer version
sock.connect(("127.0.0.1", 19999))
sock.send(msg_version().to_bytes())

if sock:
    print "connected to dashd"

# mempool/ixstats
mempool = {}


def print_transaction(*d):
    print "%s txid=%s amount=%s to=%s locks=%s" % d

# comm loop
while True: # noqa
    data = sock.recv(100000)
    time.sleep(0.1)
    if len(data):
        f = BytesIO(data)
        msg = MsgSerializable.stream_deserialize(f)
        if msg is None:
            continue
        if msg.command == 'ping':
            pong = msg_pong(nonce=msg.nonce)
            sock.send(pong.to_bytes())
        elif msg.command == 'txlvote':
            # increment lock count
            # TODO these signatures need to be validated
            txid = b2lx(msg.txlvote.hash)
            vin = b2lx(msg.txlvote.vin.prevout.hash)
            if 'vins' not in mempool[txid]:
                mempool[txid]['vins'] = set()
            mempool[txid]['vins'].add(vin)
            msg = mempool[txid]['msg']
            for vout in msg.tx.vout:
                print_transaction(
                    msg.command,
                    txid,
                    str("%.8f" % dash.AmountToJSON(vout.nValue)),
                    str(P2PKHBitcoinAddress.from_scriptPubKey(
                        vout.scriptPubKey)),
                    len(mempool[txid]['vins'])
                )
        elif msg.command == 'inv':
            for i in msg.inv:
                if i.type in (1, 5):  # transaction/txlock
                    gd = msg_getdata()
                    gd.inv.append(i)
                    sock.send(gd.to_bytes())
        elif msg.command == 'ix' or msg.command == 'tx':
            txid = b2lx(msg.tx.GetHash())
            mempool[txid] = {"msg": msg, "locks": 0}
            for vout in msg.tx.vout:
                print_transaction(
                    msg.command,
                    txid,
                    str("%.8f" % dash.AmountToJSON(vout.nValue)),
                    str(P2PKHBitcoinAddress.from_scriptPubKey(
                        vout.scriptPubKey)),
                    0
                )
        else:
            continue

quit()
