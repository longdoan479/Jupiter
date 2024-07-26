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


class BuySellLstToken:
    def __init__(self, pAccountSOL: AccountSol, pAmountIn: float):
        self.mAccountSOL = pAccountSOL
        self.mAmountIn = pAmountIn
        self.TotalDecision = 1
    def DoTask(self):
        # -------------- Connect to solana ---------------
        l_Client = Client(g_RPC_SOL)
        l_TokenLSTRandom = self.GetListTokenToDoTask()

        # ------------------------ Buy meme ---------------------
        self.MakeDecisionBuyMeme(TokenContract.SOL, self.mAmountIn)

        # --------------- Swap ---------------------------
        l_Jupiter = Jupiter(l_Client)

        l_SolToLST = l_Jupiter.swap(TokenContract.SOL, l_TokenLSTRandom, self.mAmountIn, self.mAccountSOL)

        # --------------- Logging ---------------------------
        l_FilePath = os.getcwd() + strLoggingPath.format(self.mAccountSOL.mGroup, str(self.mAccountSOL.GetPublicKey()))
        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap SOL to TokenLST on Jupiter \n => {l_SolToLST}'
        Logging.WriteLog(l_FilePath, l_TextToLog)

        l_Timesleep = random.randint(gRandomTimeMin, gRandomTimeMax)
        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Time sleep {l_Timesleep} seconds after Swap SOL to TokenLST on Jupiter'
        Logging.WriteLog(l_FilePath, l_TextToLog)
        time.sleep(l_Timesleep)

        l_LstToken = Token(l_Client, Pubkey.from_string(l_TokenLSTRandom))
        l_LST_Balance = l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())
        if l_LST_Balance > 0:

            # ======================= random buy meme =======================
            self.MakeDecisionBuyMeme(TokenContract.SOL, l_LST_Balance)
            # =============================================================

            l_LST_Balance = l_LstToken.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())
            l_LstToSOL = l_Jupiter.swap(l_TokenLSTRandom, TokenContract.SOL, l_LST_Balance, self.mAccountSOL)

            l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap TokenLST to SOL on Jupiter \n => {l_LstToSOL}'
            Logging.WriteLog(l_FilePath, l_TextToLog)

        # ------------------------ Buy meme ---------------------
        self.MakeDecisionBuyMeme(TokenContract.SOL, self.mAmountIn)


    def MakeDecisionBuyMeme(self, pInputMint: str, pAmountToSwap: float) -> True:
        l_RandomNumber = random.randint(1, 100)

        # init rate 20%
        # the more self.TotalDecision, the less rate
        if l_RandomNumber < (20/self.TotalDecision):
            l_Timesleep = random.randint(gRandomTimeMin, gRandomTimeMax)

            # ================ logging ====================
            l_FilePath = os.getcwd() + strLoggingPath.format(self.mAccountSOL.mGroup, str(self.mAccountSOL.GetPublicKey()))
            l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Time sleep {l_Timesleep} seconds, ready for Swap MEME coin on Jupiter'
            Logging.WriteLog(l_FilePath, l_TextToLog)
            time.sleep(l_Timesleep)

            # ================== swap meme =======================
            l_BuyRandomToken = BuyRandomToken(self.mAccountSOL, round(pAmountToSwap / random.randint(5000, 10000), 8))
            l_BuyRandomToken.DoTask(pInputMint)
            self.TotalDecision = self.TotalDecision + 1

    def GetListTokenToDoTask(self):
        l_lstToken = TokenLSTContract.getListToken()
        l_RandomIndexToken = random.randint(0, int(len(l_lstToken) - 1))

        return l_lstToken[l_RandomIndexToken]