
import time
import random
import struct

from bitcoin.core.serialize import ser_read, VectorSerializer
from bitcoin.core import CTxIn, CScript
import bitcoin.core.script as script
from bitcoin.core.serialize import BytesSerializer
import bitcoin

class MainParams(bitcoin.core.CoreMainParams):
    #MESSAGE_START = b'\xbd\x6b\x0c\xbf'
    MESSAGE_START = b'\xbf\x0c\x6b\xbd'
    DEFAULT_PORT = 9999
    RPC_PORT = 9998
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR': 76,
                       'SCRIPT_ADDR': 16,
                       'SECRET_KEY': 204}

bitcoin.params = bitcoin.MainParams = MainParams

class TestNetParams(bitcoin.core.CoreTestNetParams):
    MESSAGE_START = b'\xce\xe2\xca\xff'
    DEFAULT_PORT = 19999
    RPC_PORT = 19998
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR':139,
                       'SCRIPT_ADDR': 19,
                       'SECRET_KEY' :239}

bitcoin.TestNetParams = TestNetParams

import bitcoin.net

bitcoin.net.PROTO_VERSION = 70103

class CInv(bitcoin.net.CInv):
    typemap = {
        0:  "Error",
        1:  "TX",
        2:  "Block",
        3:  "FILTERED_BLOCK",
        4:  "TXLOCK_REQUEST",
        5:  "TXLOCK_VOTE",
        6:  "SPORK",
        7:  "MASTERNODE_WINNER",
        8:  "MASTERNODE_SCANNING_ERROR",
        9:  "BUDGET_VOTE",
        10: "BUDGET_PROPOSAL",
        11: "BUDGET_FINALIZED",
        12: "BUDGET_FINALIZED_VOTE",
        13: "MASTERNODE_QUORUM",
        14: "MASTERNODE_ANNOUNCE",
        15: "MASTERNODE_PING",
        16: "DSTX" }

bitcoin.net.CInv = CInv

import bitcoin.messages

class CTransactionLock(bitcoin.core.ImmutableSerializable):
    """Dash transaction lock concensus: hash, vec(nodes), vec(signatures), block"""
    __slots__ = ['hash', 'vin', 'vsig', 'height']

    def __init__(self, hash=b'\x00'*32, vin=CTxIn(), vsig=CScript(), height=0):
        """Create a new transaction lock

        vin and vsig are iterables of transaction hashes and masternode
        signatures respectively. If their contents are not already immutable,
        immutable copies will be made.
        """
        if not len(hash) == 32:
            raise ValueError('CTransactionLock: hash must be exactly 32 bytes; got %d bytes' % len(hash))
        object.__setattr__(self, 'hash', hash)
        object.__setattr__(self, 'vin', vin)
        object.__setattr__(self, 'vsig', vsig)
        object.__setattr__(self, 'height', height)
        print repr(self)

    @classmethod
    def stream_deserialize(cls, f):
        hash = ser_read(f,32)
        vin = CTxIn.stream_deserialize(f)
        vsig = script.CScript(BytesSerializer.stream_deserialize(f))
        height = struct.unpack(b"<I", ser_read(f,4))[0]
        #print " CTransactionLock vinhash=%s - msg_tx(tx=%s)" % (bitcoin.core.b2lx(vin.GetHash()), repr(vin))
        return cls(hash, vin, vsig, height)

    def stream_serialize(self, f):
        f.write(self.hash)
        f.write(self.vin.stream_serialize())
        BytesSerializer.stream_serialize(self.vsig, f)
        f.write(struct.pack(b"<I", self.height))

    def __repr__(self):
        return "CTransactionLock(%r, %r, %r, %i)" % (
            self.hash, self.vin, self.vsig, self.height)

    @classmethod
    def from_tx(cls, tx):
        """Create an immutable copy of a pre-existing transaction

        If tx is already immutable (tx.__class__ is CTransaction) then it will
        be returned directly.
        """
        if tx.__class__ is CTransaction:
            return tx

        else:
            return cls(tx.vin, tx.vout, tx.nLockTime, tx.nVersion)


class msg_ix(bitcoin.messages.MsgSerializable):
    command = b"ix"

    def __init__(self, protover=bitcoin.net.PROTO_VERSION):
        super(msg_ix, self).__init__(protover)
        self.tx = bitcoin.core.CTransaction()

    @classmethod
    def msg_deser(cls, f, protover=bitcoin.net.PROTO_VERSION):
        c = cls()
        c.tx = bitcoin.core.CTransaction.stream_deserialize(f)
        return c

    def msg_ser(self, f):
        self.tx.stream_serialize(f)

    def __repr__(self):
        return "msg_ix(ix=%s)" % (repr(self.tx))


class msg_txlvote(bitcoin.messages.MsgSerializable):
    command = b"txlvote"

    def __init__(self, protover=bitcoin.net.PROTO_VERSION):
        super(msg_txlvote, self).__init__(protover)
        self.txlvote = CTransactionLock()

    @classmethod
    def msg_deser(cls, f, protover=bitcoin.net.PROTO_VERSION):
        c = cls()
        c.txlvote = CTransactionLock.stream_deserialize(f)
        return c

    def msg_ser(self, f):
        self.txlvote.stream_serialize(f)

    def __repr__(self):
        return "msg_txlvote(tx=%s)" % (repr(self.txlvote))

bitcoin.messages.msg_txlvote = msg_txlvote
bitcoin.messages.msg_ix = msg_ix
bitcoin.messages.messagemap["txlvote"] = msg_txlvote
bitcoin.messages.messagemap["ix"] = msg_ix


import bitcoin.core


"""
CTransaction::CTransaction() : hash(0),
nVersion(CTransaction::CURRENT_VERSION),
vin(),
vout(),
nLockTime(0) { }

class CConsensusVote
{
public:
    CTxIn vinMasternode;
    uint256 txHash;
    int nBlockHeight;
    std::vector<unsigned char> vchMasterNodeSignature;

    uint256 GetHash() const;

    bool SignatureValid();
    bool Sign();

    ADD_SERIALIZE_METHODS;

    template <typename Stream, typename Operation>
    inline void SerializationOp(Stream& s,
Operation ser_action, int nType, int nVersion) {
        READWRITE(txHash);
        READWRITE(vinMasternode);
        READWRITE(vchMasterNodeSignature);
        READWRITE(nBlockHeight);
    }
};


CTransaction::CTransaction() : hash(0),
nVersion(CTransaction::CURRENT_VERSION), vin(), vout(), nLockTime(0) { }


class CTransactionLock
{
public:
    int nBlockHeight;
    uint256 txHash;
    std::vector<CConsensusVote> vecConsensusVotes;
    int nExpiration;
    int nTimeout;

    bool SignaturesValid();
    int CountSignatures();
    void AddSignature(CConsensusVote& cv);

    uint256 GetHash()
    {
        return txHash;
    }
};
"""
