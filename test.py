import os
import time

import qrcode
from solana.rpc.api import Client

# Chuỗi ký tự cần tạo QR code
from Include.AccountSol import AccountSol
from Include.Constant import g_RPC_SOL, strLoggingPath
from Include.FileProcessing import FileProcessing

# l_FileKey = FileProcessing("key.xlsx")
# l_lstAccount = l_FileKey.ReadDataWallet()
#
# for i in range(0, len(l_lstAccount)):
#     acc = AccountSol(l_lstAccount[i].mPrivateKey, Client(g_RPC_SOL))
#     time.sleep(1)
#     print(f"{i}. {str(acc.GetPublicKey())}: {str(round(acc.GetBalanceSOL(True) / 1.1, 3))}")

# print(os.getcwd() + strLoggingPath.format())
# print(os.path.exists("/root/SOL/Jupiter"))
# os.makedirs(os.path.dirname("/root/SOL/Jupiter/Logging/Group/1/FLqHisTMgrj4DJNPJhkibtYmkrK8kSt2zq51fVN2fTLn.txt"), exist_ok=True)
# with open("/root/SOL/Jupiter/Logging/Group/1/FLqHisTMgrj4DJNPJhkibtYmkrK8kSt2zq51fVN2fTLn.txt", 'a') as f:
#     f.write("pText" + '\n')

# Khởi tạo các giá trị
initial_sol = 1.0
min_sol = 0.05
sol_price_usd = 180

current_sol = initial_sol
total_usdc_swapped = 0
step = 0

while current_sol > min_sol:
    previous_sol = current_sol
    current_sol = current_sol * 0.998  # giảm 0.2%
    # sol_swapped = previous_sol - current_sol
    usdc_received = current_sol * float(sol_price_usd)
    total_usdc_swapped += usdc_received
    step += 1
    print(f"Step {step}: SOL before swap = {previous_sol}, SOL after swap = {current_sol}, Total USDC received = {total_usdc_swapped}")

print(f"Total USDC swapped: {total_usdc_swapped}")
