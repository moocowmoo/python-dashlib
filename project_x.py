#!/usr/bin/env python

import sys
sys.path.append('./python-bitcoinlib')

import socket
import subprocess
import time
import yaml
from cStringIO import StringIO as BytesIO

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
    print "sale! product %s" % products[addr]['label']
    # products[addr]['callback']()


def run_command(cmd):
    return subprocess.check_output(cmd, shell=True)


# qnd
def get_txn(txid, vout):
    cli = 'dash-cli -datadir=/home/ubuntu/testnet/testnet'
    cmd = '%s decoderawtransaction `%s getrawtransaction %s`' % (cli, cli, txid)
    y = yaml.load(run_command(cmd))
    return y


# qnd
def select_return_address(txid, vout):
    # txid -> vin[0],vout -> txid -> vout[prevout[vout]], n, addresses[0]
    prevout = get_txn(txid, vout)['vin'][vout]
    source = get_txn(prevout['txid'], prevout['vout'])['vout']
    return source[prevout['vout']]['scriptPubKey']['addresses'][0]


# txid = 'fed66063f6d285413cf76f889231aad60f010dee2305f2511957467ad736a20e'
# vout = 0
# return_address = select_return_address(txid, vout)
# quit()

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
                    mempool[txid]['sold'] = True
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
                gd = msg_getdata()
                gd.inv.append(i)
                sock.send(gd.to_bytes())
    elif msg.command == 'ix' or msg.command == 'tx':
        txid = b2lx(msg.tx.GetHash())
        if txid not in mempool:
            mempool[txid] = {"msg": msg}
        elif 'msg' in mempool[txid]:
            check_ix_signature_depth(txid, mempool[txid]['msg'])

# comm loop
while True:
    data = sock.recv(100000)
    time.sleep(0.1)
    if len(data):
        process_p2p(data)

quit()
