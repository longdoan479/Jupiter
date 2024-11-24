from datetime import datetime
import os
import random

from solana.rpc.api import Client

from IncludeAsync.Dex.Jupiter import Jupiter
from Helper import GetRandomRPC
from Include.AccountSol import AccountSol
from Constant import TokenAltContract, TokenContract, strLoggingPath
from Logging import Logging


class BuyRandomToken:
    def __init__(self, pAccountSOL: AccountSol, pAmountIn: float):
        self.mAccountSOL = pAccountSOL
        self.mAmountIn = pAmountIn

    def DoTask(self, pInputMint: str = None):
        l_RandomRPC = GetRandomRPC()

        # -------------- Connect to solana ---------------
        l_Client = Client(l_RandomRPC)
        l_TokenRandom = self.GetListTokenToDoTask()
        # --------------- Swap ---------------------------
        l_Jupiter = Jupiter(l_Client)

        if pInputMint is not None:
            l_Swap = l_Jupiter.swap(pInputMint, l_TokenRandom, self.mAmountIn, self.mAccountSOL)
        else:
            l_Swap = l_Jupiter.swap(TokenContract.SOL, l_TokenRandom, self.mAmountIn, self.mAccountSOL)

        # --------------- Logging ---------------------------
        l_FilePath = os.getcwd() + strLoggingPath.format(str(self.mAccountSOL.GetPublicKey()))
        l_TextToLog = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Swap Altcoin on Jupiter \n => {l_Swap}'
        Logging.WriteLog(l_FilePath, l_TextToLog)

    def GetListTokenToDoTask(self):
        l_lstToken = TokenAltContract.getListToken()
        l_RandomIndexToken = random.randint(0, int(len(l_lstToken)-1))

        return l_lstToken[l_RandomIndexToken]
