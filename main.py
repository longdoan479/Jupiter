#
# # # ------------------ Run multi acc ----------------------
#
# l_FileKey = FileProcessing("key.xlsx")
# l_lstAccount = l_FileKey.ReadDataWallet()
#
# l_FileProxy = FileProcessing("proxy.xlsx")
# Cons.g_Data_Proxy = l_FileProxy.ReadDataProxyJSON()
#
#
# l_MaxGroup = max(l_lstAccount, key=lambda obj: obj.mGroup).mGroup
#
# l_lstAccountRandom = []
# groups_Account = {}
#
# for i in range(1, l_MaxGroup+1):
#     group = i
#
#     l_lstAccountFilter = list(filter(lambda acc: acc.mGroup == group, l_lstAccount))
#
#     # Nhóm dữ liệu theo giá trị group
#     if group not in groups_Account:
#         groups_Account[group] = []
#
#     random.shuffle(l_lstAccountFilter)
#     groups_Account[group].extend(l_lstAccountFilter)
#
#
# # Chia các nhóm thành 5 mảng
# l_Results = [[] for _ in range(1)]
# group_list = list(groups_Account.values())
#
# for i, group in enumerate(group_list):
#     l_Results[i % 1].extend(group)
#
# # Danh sách các luồng
# threads = []
#
# # Tạo và khởi động 20 luồng
# for i in range(0, 1):
#     # thread = threading.Thread(target=task, args=(i,))
#     thread = ThreadDoTask(f"Thread {i+1}", l_Results[i])
#     threads.append(thread)
#     thread.start()
#
# # Đảm bảo tất cả các luồng hoàn thành
# for thread in threads:
#     thread.join()

import asyncio
import random


from FileProcessing import FileProcessing
import Constant as Cons
from IncludeAsync.AsyncTaskQueue import AsyncTaskQueue
from ThreadTask.AsyncDoTask import AsyncDoTask



# Hàm khởi chạy tất cả các tác vụ không đồng bộ
async def main():
    l_FileProxy = FileProcessing("proxy.xlsx")
    Cons.g_Data_Proxy = l_FileProxy.ReadDataProxyJSON()

    l_FileKey1 = FileProcessing("key/key1.xlsx")
    l_FileKey2 = FileProcessing("key/key2.xlsx")
    l_FileKey3 = FileProcessing("key/key3.xlsx")
    l_FileKey4 = FileProcessing("key/key4.xlsx")

    l_lstAccount = []
    l_lstAccount.extend(l_FileKey1.ReadDataWallet())
    l_lstAccount.extend(l_FileKey2.ReadDataWallet())
    l_lstAccount.extend(l_FileKey3.ReadDataWallet())
    l_lstAccount.extend(l_FileKey4.ReadDataWallet())

    l_MaxGroup = max(l_lstAccount, key=lambda obj: obj.mGroup).mGroup

    l_lstAccountRandom = []
    groups_Account = {}

    for i in range(1, l_MaxGroup + 1):
        group = i

        l_lstAccountFilter = list(filter(lambda acc: acc.mGroup == group, l_lstAccount))

        # Nhóm dữ liệu theo giá trị group
        if group not in groups_Account:
            groups_Account[group] = []

        random.shuffle(l_lstAccountFilter)
        groups_Account[group].extend(l_lstAccountFilter)

    l_randomThreadNumber = random.randint(25, 50)

    # Chia các nhóm thành 5 mảng
    l_Results = [[] for _ in range(l_randomThreadNumber)]
    group_list = list(groups_Account.values())

    for i, group in enumerate(group_list):
        l_Results[i % l_randomThreadNumber].extend(group)

    tasks = []

    # Tạo một hàng đợi xử lý với giới hạn tối đa 5 tác vụ đồng thời
    task_queue = AsyncTaskQueue(max_concurrent_tasks=l_randomThreadNumber)

    # Thêm 20 tác vụ vào hàng đợi
    for i in range(0, l_randomThreadNumber):
        task_obj = AsyncDoTask(f"Task {i}", l_Results[i])  # Khởi tạo đối tượng AsyncDoTask
        task_queue.add_task(task_obj)  # Thêm tác vụ vào hàng đợi
        await asyncio.sleep(0.1)  # Giả lập việc thêm tác vụ theo thời gian thực

    # Chờ cho đến khi tất cả các tác vụ hoàn thành
    await task_queue.run()


# Chạy chương trình asyncio
asyncio.run(main())
