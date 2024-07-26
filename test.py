import os
import time

import qrcode
from solana.rpc.api import Client

# Chuỗi ký tự cần tạo QR code
from Include.AccountSol import AccountSol
from Include.Constant import g_RPC_SOL, strLoggingPath
from Include.FileProcessing import FileProcessing

l_FileKey = FileProcessing("key.xlsx")
l_lstAccount = l_FileKey.ReadDataWallet()

for i in range(0, len(l_lstAccount)):
    acc = AccountSol(l_lstAccount[i].mPrivateKey, Client(g_RPC_SOL))
    time.sleep(1)
    print(f"{i}. {str(acc.GetPublicKey())}: {str(round(acc.GetBalanceSOL(True) / 1.1, 3))}")
