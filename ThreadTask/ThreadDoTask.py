from datetime import datetime
import os
import random
import threading
import time
from typing import List
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient

from Include.AccountSol import AccountSol
from Include.Constant import g_RPC_SOL, gRandomTimeMax, gRandomTimeMin, strLoggingPath, gTotalVolEachAccount
from Include.Data import DataWallet
from Include.Logging import Logging
from Task.BuySellLstToken import BuySellLstToken
from Task.BuySellLstTokenWithPath import BuySellLstTokenWithPath
from Task.BuySellSolUsdc import BuySellSolUsdc


class ThreadDoTask(threading.Thread):
    def __init__(self, pThreadName, pListAccount: List[DataWallet]):
        super(ThreadDoTask, self).__init__()
        self.mThreadName = pThreadName
        self.mListAccount = pListAccount
        self.mDictAccVol = {}
    def run(self):
        l_NumOfAccReachTarget = 0
        while l_NumOfAccReachTarget < len(self.mListAccount): # if tổng số acc đạt target < len(self.mListAccount) => chạy tiếp
            for l_Account in self.mListAccount:
                l_sol_web3 = Client(g_RPC_SOL)
                lAccSol = AccountSol(l_Account.mPrivateKey, l_sol_web3, l_Account.mGroup)
                l_BalanceSol = lAccSol.GetBalanceSOL(True)
                if str(lAccSol.GetPublicKey()) not in self.mDictAccVol:
                    self.mDictAccVol[str(lAccSol.GetPublicKey())] = 0
                else:
                    # if Total Vol hiện tại đã vượt mức, chạy ví tiếp theo
                    if self.mDictAccVol[str(lAccSol.GetPublicKey())] > gTotalVolEachAccount:
                        continue

                print(f"\n{self.mThreadName}: Account {l_Account.mAddress} is running")

                l_Task = BuySellLstTokenWithPath(lAccSol, round(l_BalanceSol/1.05, 3))
                l_TotalVolumn = l_Task.DoTask()

                self.mDictAccVol[str(lAccSol.GetPublicKey())] += l_TotalVolumn
                if self.mDictAccVol[str(lAccSol.GetPublicKey())] > gTotalVolEachAccount:
                    l_NumOfAccReachTarget += 1

                # ================== Logging =========================
                l_FilePath = os.getcwd() + strLoggingPath.format(str(lAccSol.GetPublicKey()))
                l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: ' \
                              f'Total Volumn account {lAccSol.GetPublicKey()}: ' \
                              f'{self.mDictAccVol[str(lAccSol.GetPublicKey())]} usd'
                Logging.WriteLog(l_FilePath, l_TextToLog)
                # ===========================================

            random.shuffle(self.mListAccount)

            l_Sleep = random.randint(1800, 3600)
            print(f"\n{self.mThreadName}: Sleeping {l_Sleep}s before new round")
            time.sleep(l_Sleep)
