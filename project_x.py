#!/usr/bin/env python

import socket
import subprocess
import sys
import time
import yaml
from cStringIO import StringIO as BytesIO

from config import cli

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

import dash # noqa - monkeypatches bitcoin lib
from bitcoin import SelectParams
from bitcoin.core import b2lx
from bitcoin.messages import msg_version, msg_getdata, msg_pong, MsgSerializable
from bitcoin.wallet import P2PKHBitcoinAddress
# from bitcoin.net import CInv

from products import products, LOCK_THRESHOLD

SelectParams('testnet')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect and announce peer version
sock.connect(("127.0.0.1", 19999))
sock.send(msg_version().to_bytes())

# if sock:
#     print "connected to dashd"

# mempool/ixstats
mempool = {}


def trigger_sale(addr):
    sys.stdout.write(" --> SALE! product %s\n" % products[addr]['label'])
    sys.stdout.flush()
    # products[addr]['callback']()


def run_command(cmd):
    return subprocess.check_output(cmd, shell=True)


# qnd
def get_txn(txid):
    cmd = '%s decoderawtransaction `%s getrawtransaction %s`' % (cli, cli, txid)
    y = yaml.load(run_command(cmd))
    return y


def send_to(addr, value):
    cmd = '%s sendtoaddress %s %s' % (cli, addr, value)
    run_command(cmd)


# qnd
def select_return_address(txid):
    # txid -> vin[0],vout -> txid -> vout[prevout[vout]], n, addresses[0]
    prevout = get_txn(txid)['vin'][0]
    source = get_txn(prevout['txid'])['vout']
    return source[prevout['vout']]['scriptPubKey']['addresses'][0]


def check_ix_signature_depth(txid, msg):
    for vout in msg.tx.vout:
        addr = str(P2PKHBitcoinAddress.from_scriptPubKey(
            vout.scriptPubKey))
        if addr in products and len(mempool[txid]['vins']) >= LOCK_THRESHOLD:
            # right address, right ix lock count
            cost = products[addr]['cost'] * 1e8
            if vout.nValue >= cost:
                # if vout.nValue > cost:
                #     return_address = select_return_address(txid, vout)
                # right amount, do it to it
                if not mempool[txid]['sold']:
                    # mempool[txid]['sold'] = True
                    del mempool[txid]
                    # we sold something
                    trigger_sale(addr)


def process_txlvote(msg):
    # TODO masternode vote signatures need to be validated
    txid = b2lx(msg.txlvote.hash)
    vin = b2lx(msg.txlvote.vin.prevout.hash)
    if txid not in mempool:
        mempool[txid] = {}
    if 'vins' not in mempool[txid]:
        mempool[txid]['vins'] = set()
    if 'sold' not in mempool[txid]:
        mempool[txid]['sold'] = False
    mempool[txid]['vins'].add(vin)
    if 'msg' in mempool[txid]:
        check_ix_signature_depth(txid, mempool[txid]['msg'])


def process_p2p(data):
    f = BytesIO(data)
    msg = MsgSerializable.stream_deserialize(f)
    if msg is None:
        return
    # print "got msg %s" % (msg.command)
    if msg.command == 'ping':
        pong = msg_pong(nonce=msg.nonce)
        sock.send(pong.to_bytes())
    elif msg.command == 'txlvote':
        process_txlvote(msg)
    elif msg.command == 'inv':
        for i in msg.inv:
            # print " -- got type %s" % (CInv.typemap[i.type])
            if i.type in (1, 4, 5):  # transaction/txlrequest/txlvote
                sys.stderr.write(str(msg) + "\n")
                gd = msg_getdata()
                gd.inv.append(i)
                sock.send(gd.to_bytes())
    elif msg.command == 'tx' or msg.command == 'ix':
        txid = b2lx(msg.tx.GetHash())
        for vout in msg.tx.vout:
            addr = str(P2PKHBitcoinAddress.from_scriptPubKey(
                vout.scriptPubKey))
            if addr in products:
                if msg.command == 'tx':
                    # refund tx
                    send_to(select_return_address(txid),
                            dash.AmountToJSON(vout.nValue))
                else:
                    sys.stderr.write(str(msg) + "\n")
                    if txid not in mempool:
                        mempool[txid] = {"msg": msg}
                    elif 'msg' in mempool[txid]:
                        check_ix_signature_depth(txid, mempool[txid]['msg'])


# comm loop
while True:
    data = sock.recv(4096)
    time.sleep(0.01)
    if len(data):
        process_p2p(data)

quit()
