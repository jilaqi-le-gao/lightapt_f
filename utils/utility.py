# coding=utf-8

"""

Copyright(c) 2022 Max Qian  <astroair.cn>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

# #################################################################
# Switch (just like c++)
# #################################################################
class switch(object):
    """switch function NOTE : must call break after all"""
    def __init__(self, value):
        self.value = value
        self.fall = False
 
    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False

# #################################################################
# Thread Pool (custom)
# #################################################################

from concurrent.futures import ThreadPoolExecutor
import threading

class ThreadPool:
    def __init__(self, max_thread_num=5):
        # 记录全部线程是否已经结束
        self.over = False
        # 记录所有的子线程完成后的返回值
        self.results = []
 
        # 子线程函数体
        self.func = None
        # 需要传进子线程的参数，数组中每一个元素都是一个元组
        # 例如有一个函数定义add(a,b)，返回a和b的和
        # 则数组表现为[(1,2),(3,10),...]
        # 可以依据数组中的每一个元组建立一个线程
        self.args_list = None
        # 需要完成的任务的数量，获取自参数数组的长度
        self.task_num = 0
        # 线程池同时容纳的最大线程数，默认为5
        self.max_thread_num = max_thread_num
        # 初始化线程池
        self.pool = ThreadPoolExecutor(max_workers=max_thread_num)
        self.cond = threading.Condition()
 
    # 设置线程池中执行任务的各项参数
    def set_tasks(self, func, args_list):
        # 需要完成的任务的数量，获取自参数数组的长度
        self.task_num = len(args_list)
        # 参数数组
        self.args_list = args_list
        # 线程中执行的函数体
        self.func = func
 
    # 线程完成后的回调，功能有3
    # 1:监控所有任务的完成进度
    # 2:收集任务完成后的结果
    # 3.继续向线程池中添加新的任务
    def get_result(self, future):
        # 监控线程完成进度
        self.show_process('任务完成进度', self.task_num - len(self.args_list), self.task_num)
        # 将函数处理的返回值添加到结果集合当中，若没有返回值，则future.result()的值是None
        self.results.append(future.result())
        # 若参数数组中含有元素，则说明还有后续的任务
        if len(self.args_list):
            # 提取出将要执行的一个任务的参数
            args = self.args_list.pop()
            # 向线程池中提交一个新任务，第一个参数是函数体，第二个参数是执行函数时所需要的各项参数
            task = self.pool.submit(self.func, *args)
            # 绑定任务完成后的回调
            task.add_done_callback(self.get_result)
        else:
            # 若结果的数量与任务的数量相等，则说明所有的任务已经完成
            if self.task_num == len(self.results):
                print('\n', '任务完成')
                # 获取锁
                self.cond.acquire()
                # 通知
                self.cond.notify()
                # 释放锁
                self.cond.release()
            return
 
    def _start_tasks(self):
        # 向线程池中添加到最大数量的线程
        for i in range(self.max_thread_num):
            # 作出所有任务是否已经完成的判断，原因如下：
            # 如果直接向线程池提交巨大数量的任务，线程池会创建任务队列，占用大量内存
            # 为减少创建任务队列的巨大开销，本类中所有子线程在完成后的回调中，会向线程池中提交新的任务
            # 循环往复，直到所有任务全部完成，而任务队列几乎不存在
            # 1：当提交的任务数量小于线程池容纳的最大线程数，在本循环中，必会出现所有任务已经提交的情况
            # 2：当函数执行速度非常快的时候，也会出现所有任务已经提交的情况
 
            # 如果参数数组中还有元素，则说明没有到达线程池的上限
            if len(self.args_list):
                # 取出一组参数，同时删除该任务
                args = self.args_list.pop()
                # 向线程池中提交新的任务
                task = self.pool.submit(self.func, *args)
                # 绑定任务完成后的回调
                task.add_done_callback(self.get_result)
            # 所有任务已经全部提交，跳出循环
            else:
                break
 
    # 获取最终所有线程完成后的处理结果
    def final_results(self):
        # 开始执行所有任务
        self._start_tasks()
        # 获取结果时，会有两种情况
        # 所有的任务都已经完成了，直接返回结果就行
        if self.task_num == len(self.results):
            return self.results
        # 线程池中还有未完成的线程，只有当线程池中的任务全部结束才能够获取到最终的结果
        # 这种情况会在线程池容量过大或者线程极度耗时时才会出现
        else:
            # 获取锁
            self.cond.acquire()
            # 阻塞当前线程，等待通知
            self.cond.wait()
            # 已经获取到通知，释放锁
            self.cond.release()
            # 返回结果集
            return self.results

# #################################################################
# JSON Processing
# #################################################################

import json

def json2python(_json) -> object:
    """
        Convert a JSON message to Python object
        Args: _json
        Returns: Python object
    """
    if not isinstance(_json,str):
        print("Given message is not a JSON object")
        return None
    try:
        return json.loads(_json)
    except json.JSONDecodeError as exception:
        print(exception)
        return None

def python2json(_python) -> object:
    """
        Convert a Python object to JSON message
        Args: _python
        Returns: JSON message
    """
    try:
        return json.dumps(_python)
    except json.JSONDecodeError as exception:
        print(exception)
        return None