import os
import random
import time
from datetime import datetime

from solana.rpc.api import Client
from solders.pubkey import Pubkey

from Helper import GetRandomRPC
from Include.AccountSol import AccountSol
from Constant import TokenContract, strLoggingPath, gRandomTimeMax, gRandomTimeMin
from Dex.Jupiter import Jupiter
from Logging import Logging
from Include.Token import Token
from Task.BuyRandomToken import BuyRandomToken


class BuySellSolUsdc:
    def __init__(self, pAccountSOL: AccountSol, pAmountIn: float):
        self.mAccountSOL = pAccountSOL
        self.mAmountIn = pAmountIn
        self.TotalDecision = 1
    def DoTask(self):
        # -------------- Connect to solana ---------------
        l_RandomRPC = GetRandomRPC()
        l_Client = Client(l_RandomRPC)

        # ------------------------ Buy meme ---------------------
        self.MakeDecisionBuyMeme(TokenContract.SOL, self.mAmountIn)

        # --------------- Swap ---------------------------
        l_Jupiter = Jupiter(l_Client)

        l_SolToUSDC = l_Jupiter.swap(TokenContract.SOL, TokenContract.USDC, self.mAmountIn, self.mAccountSOL)

        # --------------- Logging ---------------------------
        l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))
        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap SOL to USDC on Jupiter \n => {l_SolToUSDC}'
        Logging.WriteLog(l_FilePath, l_TextToLog)

        l_Timesleep = random.randint(gRandomTimeMin, gRandomTimeMax)
        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Time sleep {l_Timesleep} seconds after Swap SOL to USDC on Jupiter'
        Logging.WriteLog(l_FilePath, l_TextToLog)
        time.sleep(l_Timesleep)

        l_USDC = Token(l_Client, Pubkey.from_string(TokenContract.USDC))
        l_USDC_Balance = l_USDC.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())
        if l_USDC_Balance > 0:

            # ======================= random buy meme =======================
            l_RandomContract = random.choice([TokenContract.USDC, TokenContract.SOL])
            l_BalanceToBuyMeme = l_USDC_Balance if  l_RandomContract == TokenContract.USDC else self.mAmountIn
            self.MakeDecisionBuyMeme(TokenContract.USDC, l_USDC_Balance)
            # =============================================================

            l_USDC_Balance = l_USDC.getBalanceTokenByOwner(self.mAccountSOL.GetPublicKey())
            l_UsdcToSOL = l_Jupiter.swap(TokenContract.USDC, TokenContract.SOL, l_USDC_Balance, self.mAccountSOL)

            l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap USDC to SOL on Jupiter \n => {l_UsdcToSOL}'
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
            l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))
            l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Time sleep {l_Timesleep} seconds, ready for Swap MEME coin on Jupiter'
            Logging.WriteLog(l_FilePath, l_TextToLog)
            time.sleep(l_Timesleep)

            # ================== swap meme =======================
            l_BuyRandomToken = BuyRandomToken(self.mAccountSOL, round(pAmountToSwap / random.randint(5000, 10000), 8))
            l_BuyRandomToken.DoTask(pInputMint)
            self.TotalDecision = self.TotalDecision + 1

