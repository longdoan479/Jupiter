import os
import random


from Include.FileProcessing import FileProcessing
import Include.Constant as Cons
from ThreadTask.ThreadDoTask import ThreadDoTask


# # ------------------ Run multi acc ----------------------

l_FileKey = FileProcessing("key.xlsx")
l_lstAccount = l_FileKey.ReadDataWallet()

l_FileProxy = FileProcessing("proxy.xlsx")
Cons.g_Data_Proxy = l_FileProxy.ReadDataProxyJSON()


l_MaxGroup = max(l_lstAccount, key=lambda obj: obj.mGroup).mGroup

l_lstAccountRandom = []
groups_Account = {}

for i in range(1, l_MaxGroup+1):
    group = i

    l_lstAccountFilter = list(filter(lambda acc: acc.mGroup == group, l_lstAccount))

    # Nhóm dữ liệu theo giá trị group
    if group not in groups_Account:
        groups_Account[group] = []

    random.shuffle(l_lstAccountFilter)
    groups_Account[group].extend(l_lstAccountFilter)


# Chia các nhóm thành 5 mảng
l_Results = [[] for _ in range(25)]
group_list = list(groups_Account.values())

for i, group in enumerate(group_list):
    l_Results[i % 25].extend(group)

# Danh sách các luồng
threads = []

# Tạo và khởi động 20 luồng
for i in range(0, 25):
    # thread = threading.Thread(target=task, args=(i,))
    thread = ThreadDoTask(f"Thread {i+1}", l_Results[i])
    threads.append(thread)
    thread.start()

# Đảm bảo tất cả các luồng hoàn thành
for thread in threads:
    thread.join()

