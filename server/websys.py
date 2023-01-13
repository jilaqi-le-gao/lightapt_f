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

import datetime
from flask_login import login_required
from flask import Flask,render_template
import psutil
import os 

def create_web_sysinfo(app : Flask):

    @app.route('/system', methods=['GET'])
    @login_required
    def web_sysinfo():
        """
            Web system information build on psutil and os
            Args : None
            Returns : Template
        """
        # Get basic information
        sysinfo = os.uname()
        sysname = sysinfo.sysname
        nodename = sysinfo.nodename
        release = sysinfo.release
        version = sysinfo.version
        machine = sysinfo.machine
        # Get the boot time
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        # Get the current time
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get the CPU cores count
        cpu_count = psutil.cpu_count()

        # Get the status of memory
        memory = psutil.virtual_memory()

        # Get the disk usage and information
        disk = psutil.disk_partitions()
        disk_list = []

        for physical_disk_partition in disk:
            physical_disk_usage = psutil.disk_usage(physical_disk_partition.mountpoint)
            physical_disk = {
                'device': physical_disk_partition.device,
                'mount_point': physical_disk_partition.mountpoint,
                'type': physical_disk_partition.fstype,
                'options': physical_disk_partition.opts,
                'space_total': physical_disk_usage.total,
                'space_used': physical_disk_usage.used,
                'used_percent': physical_disk_usage.percent,
                'space_free': physical_disk_usage.free
            }
            disk_list.append(physical_disk)

        # Get the process infomation

        processes = []
        for p in psutil.process_iter():
            process_info = {
                'name': p.name(),
                'pid': p.pid,
                'username': p.username(),
                'cpu': p.cpu_percent(),
                'memory': p.memory_percent(),
                'memory_rss': p.memory_info().rss,
                'memory_vms': p.memory_info().vms,
                'status': p.status(),
                'created_time': p.create_time(),
                'cmdline': ' '.join(p.cmdline())
            }
            processes.append(process_info)
            processes.sort(key=lambda proc: proc.get('cpu'),reverse=True)

        return render_template("system.html", 
                            sys_name = sysname,
                            kernel_name = nodename,
                            kernel_no = release,
                            kernel_version = version,
                            sys_framework = machine,
                            now_time = now_time,
                            boot_time = boot_time,
                            cpu_count = cpu_count,
                            memory = memory,
                            disk_list = disk_list,
                            processes = processes)

    @app.route("/system/api/memory", methods=["GET"])
    @login_required
    def system_api_memory():
        """
            System Refresh Memory API method
        """
        return {"used" : psutil.virtual_memory().percent}

    @app.route("/system/api/cpu", methods=["GET"])
    @login_required
    def system_api_cpu():
        """
            System Refresh CPU Usage API method
        """
        return {"used" : psutil.cpu_percent()}
