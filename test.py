import os
import random
import time

import qrcode
import requests
from solana.rpc.api import Client

# Chuỗi ký tự cần tạo QR code
from Include.AccountSol import AccountSol
from Include.Constant import g_RPC_SOL, strLoggingPath
from Include.FileProcessing import FileProcessing

l_FileKey = FileProcessing("key.xlsx")
l_lstAccount = l_FileKey.ReadDataWallet()

l_clietn = Client(g_RPC_SOL)
for i in range(0, len(l_lstAccount)):
    acc = AccountSol(l_lstAccount[i].mPrivateKey, l_clietn)
    time.sleep(0.25)
    # transactions = l_clietn.get_signatures_for_address(acc.GetPublicKey(), limit=1000).value

    # print(f"{i}. {str(acc.GetPublicKey())}: {acc.GetBalanceSOL(True)}, total txn: {len(transactions)}")
    l_bal = acc.GetBalanceSOL(True)
    if l_bal < 0.1:
        print(f"{i}. {str(acc.GetPublicKey())}: {l_bal}")

