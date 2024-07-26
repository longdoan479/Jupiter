import threading
from typing import List
from solana.rpc.api import Client

from Include.AccountSol import AccountSol
from Include.Constant import g_RPC_SOL
from Include.Data import DataWallet
from Task.BuySellLstToken import BuySellLstToken
from Task.BuySellSolUsdc import BuySellSolUsdc


class ThreadDoTask(threading.Thread):
    def __init__(self, pThreadName, pListAccount: List[DataWallet]):
        super(ThreadDoTask, self).__init__()
        self.mThreadName = pThreadName
        self.mListAccount = pListAccount
    def run(self):
        for l_Account in self.mListAccount:
            print(f"\n{self.mThreadName}: Account {l_Account.mAddress} is running")
            l_sol_web3 = Client(g_RPC_SOL)
            lAccSol = AccountSol(l_Account.mPrivateKey, l_sol_web3, l_Account.mGroup)

            l_Task = BuySellSolUsdc(lAccSol, round(lAccSol.GetBalanceSOL(True)/1.05, 3))
            l_Task.DoTask()

            # l_Task = BuySellLstToken(lAccSol, round(lAccSol.GetBalanceSOL(True) / 1.15, 3))
            # l_Task.DoTask()
