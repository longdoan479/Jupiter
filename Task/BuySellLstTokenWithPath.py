import os
import random
import time
from datetime import datetime

from solana.rpc.api import Client
from solders.pubkey import Pubkey

from Include.AccountSol import AccountSol
from Include.Constant import g_RPC_SOL, TokenContract, strLoggingPath, gRandomTimeMax, gRandomTimeMin, TokenLSTContract
from Dex.Jupiter import Jupiter
from Include.Logging import Logging
from Include.Token import Token
from Task.BuyRandomToken import BuyRandomToken


class BuySellLstTokenWithPath:
    def __init__(self, pAccountSOL: AccountSol, pAmountIn: float):
        self.mAccountSOL = pAccountSOL
        self.mAmountIn = pAmountIn
        self.TotalDecision = 1
    def DoTask(self) -> float:
        # -------------- define ----------------
        l_TotalVolumne = 0
        # -------------- Connect to solana ---------------
        l_Client = Client(g_RPC_SOL)
        l_ListTokenLSTRandom = self.GetListTokenToDoTask()

        # --------------- Swap ---------------------------
        l_Jupiter = Jupiter(l_Client)

        l_SolToLST = l_Jupiter.swap(TokenContract.SOL, l_ListTokenLSTRandom[0], self.mAmountIn, self.mAccountSOL)
        l_TotalVolumne += Jupiter.GetTokenPriceInUSD(TokenContract.SOL, self.mAccountSOL) * self.mAmountIn
        # --------------- Logging ---------------------------
        time.sleep(5)
        l_FilePath = os.getcwd() + strLoggingPath.format(self.mAccountSOL.mGroup, str(self.mAccountSOL.GetPublicKey()))
        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap SOL to TokenLST on Jupiter \n => {l_SolToLST}'
        Logging.WriteLog(l_FilePath, l_TextToLog)
        # ------------------------------------------

        l_LstToken = Token(l_Client, Pubkey.from_string(l_ListTokenLSTRandom[0]))
        l_LST_Balance = l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())
        if l_LST_Balance > 0:
            for i in range(1, len(l_ListTokenLSTRandom)):
                l_SwapLST = l_Jupiter.swap(l_ListTokenLSTRandom[i-1], l_ListTokenLSTRandom[i], l_LST_Balance, self.mAccountSOL)
                l_TotalVolumne += Jupiter.GetTokenPriceInUSD(l_ListTokenLSTRandom[i-1], self.mAccountSOL) * l_LST_Balance

                l_LstToken = Token(l_Client, Pubkey.from_string(l_ListTokenLSTRandom[i]))
                l_LST_Balance = l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())

                # --------------- Logging ---------------------------
                l_FilePath = os.getcwd() + strLoggingPath.format(self.mAccountSOL.mGroup, str(self.mAccountSOL.GetPublicKey()))
                l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap TokenLST to TokenLST on Jupiter \n => {l_SwapLST}'
                Logging.WriteLog(l_FilePath, l_TextToLog)
                # ------------------------------------------

                l_Timesleep = random.randint(gRandomTimeMin, gRandomTimeMax)
                time.sleep(l_Timesleep)

            l_LstToSol = l_Jupiter.swap(l_ListTokenLSTRandom[len(l_ListTokenLSTRandom)-1], TokenContract.SOL, l_LST_Balance, self.mAccountSOL)
            l_TotalVolumne += Jupiter.GetTokenPriceInUSD(l_ListTokenLSTRandom[len(l_ListTokenLSTRandom)-1], self.mAccountSOL) * l_LST_Balance

            # --------------- Logging ---------------------------
            l_FilePath = os.getcwd() + strLoggingPath.format(self.mAccountSOL.mGroup, str(self.mAccountSOL.GetPublicKey()))
            l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap TokenLST to SOL on Jupiter \n => {l_LstToSol}'
            Logging.WriteLog(l_FilePath, l_TextToLog)

        return l_TotalVolumne

    def GetListTokenToDoTask(self):
        l_lstToken = TokenLSTContract.getListToken()
        random.shuffle(l_lstToken)

        l_RandomNumOfLST = random.randint(4, int(len(l_lstToken) - 1))

        # --------------- Logging ---------------------------
        l_FilePath = os.getcwd() + strLoggingPath.format(self.mAccountSOL.mGroup, str(self.mAccountSOL.GetPublicKey()))
        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Execute {l_RandomNumOfLST+1} transaction, start with {self.mAmountIn} SOL'
        Logging.WriteLog(l_FilePath, l_TextToLog)
        # ------------------------------------------

        return l_lstToken[0:l_RandomNumOfLST]

