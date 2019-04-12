# -*- coding=utf-8 -*-
from zabbix_tools import *
import time
import sys

hosts = zabbix_hosts()

#获取某个主机的最大内存数据
def get_max_mem(hostid):
    sql = """\
        select total_mem from hosts_info where hostid = %s;
        """ % (hostid)
    result = conn_db_fetchone(sql)
    return result[0]

#查询一段时间内某个主机的内存信息，返回 最大使用内存，最小使用内存，平均使用内存 ，最大内存
def get_mem(hostid,start_id,end_id):
    sql = """\
    select c_memery from host_%s where id between %d and %d;
    """ % (hostid,start_id,end_id)               #通过host_hostid表中的“id”列，定位查询的范围
    result = conn_db_fetchall(sql)
    a = []
    total_mem = get_max_mem(hostid)
    for i in result:
        used_mem = total_mem - i[0]
        a.append(used_mem)
    a = sorted(a)                               #对历史内存数据进行冒泡排序
    max_used_mem = a[-1]                        #最大使用内存为冒泡排序后的最后一个值
    min_used_mem = a[1]                         #最小使用内存为冒泡排序后的第一个值
    #计算平均使用内存
    sum_mem = sum(a)
    lenth = len(a)
    ave_used_mem =sum_mem/lenth
    return max_used_mem,min_used_mem,ave_used_mem,total_mem

#获取某个主机的最大CPU核数
def get_max_core(hostid):
    sql = """\
        select total_core from hosts_info where hostid = %s;
        """ % (hostid)
    result = conn_db_fetchone(sql)
    return result[0]

#查询一段时间内某个主机的CPU负载信息，返回 最大负载，最小负载，平均负载 ，最大CPU核数
def get_core(hostid,start_id,end_id):
    sql = """\
    select c_coreload from host_%s where id between %d and %d;
    """ % (hostid,start_id,end_id)
    result = conn_db_fetchall(sql)
    a = [0,0]
    total_core = get_max_core(hostid)
    for i in result:
        cpu_load = i[0]
        a.append(cpu_load)
    a = sorted(a)             #对历史内存数据进行冒泡排序
    max_core_load = a[-1]     #最大负载为冒泡排序后的最后一个值
    min_core_load = a[1]      #最小负载为冒泡排序后的第一个值
    #计算平均负载
    lenth = len(a)
    sum_coreload = sum(a)
    ave_core_load = ('%.2f' % (sum_coreload/lenth))      #取2位小数
    return max_core_load,min_core_load,ave_core_load,total_core

#通过年月信息，查询获得该月份在host_hostid表中开始日期与结束日期对应的“id”列的值
def get_ts_id_monthly(hostid,c_year,c_month):
    sql = """\
    select id,c_timestramp from host_%s
    """ % hostid

    host_data = conn_db_fetchall(sql)
    id_arr = [0,0]
    for i in host_data:
        if i[1] == 1146:
            print "请在zabbix中更新主机信息"
        else:
            start_ts = i[1]
            if start_ts.year == c_year and start_ts.month == c_month and start_ts.day == 1:
                    ts_id = i[0]
                    id_arr[0] = ts_id
                    break
    #判断每个月的天数，没有对闰年作区分
    for j in host_data:
        end_ts = j[1]
        if c_month in (1,3,5,7,8,10,12):
            if end_ts.year == c_year and end_ts.month == c_month and end_ts.day == 31:
                ts_id = j[0]
                id_arr[1] = ts_id
                break
        elif c_month in (4,6,9,11):
            if end_ts.year == c_year and end_ts.month == c_month and end_ts.day == 30:
                ts_id = j[0]
                id_arr[1] = ts_id
                break
        else:
            if end_ts.year == c_year and end_ts.month == c_month and end_ts.day == 28:
                ts_id = j[0]
                id_arr[1] = ts_id
                break
    #判断是否获得了所有的返回值
    if id_arr[1] > 0 and id_arr[0] > 0:
        return id_arr
    else:
        return False



def get_ts_id_daily(hostid,c_year,c_month,c_day):
    sql = """\
    select id,c_timestramp from host_%s
    """ % hostid

    host_data = conn_db_fetchall(sql)
    id_arr = [0,0]
    for i in host_data:
        if i[1] == 1146:
            print "请在zabbix中更新主机信息"
        else:
            start_ts = i[1]
            if start_ts.year == c_year and start_ts.month == c_month and start_ts.day == c_day:
                    ts_id = i[0]
                    id_arr[0] = ts_id
                    break
    id_arr[1] = id_arr[0] + 96
    #判断是否获得了所有的返回值
    if id_arr[0] > 0:
        return id_arr
    else:
        return False

def get_hostos(hostid):
    sql = """\
        select hostos from hosts_info where hostid = %s;
        """ % (hostid)
    result = conn_db_fetchone(sql)
    return result[0]


def get_mem_api(hostid,start_date,end_date):
    hostos = get_hostos(hostid)
    s_ts = int(time.mktime(time.strptime(start_date, "%Y-%m-%d")))
    e_ts = int(time.mktime(time.strptime(end_date, "%Y-%m-%d")))
    if hostos == "linux":
        itemid = zabbix_items(hostid, "vm.memory.size[available]")
    elif hostos == "windows":
        itemid = zabbix_items(hostid, "vm.memory.size[free]")
    else:
        print "未知操作系统类型"
    mem_value = zabbix_history(itemid,3,s_ts,e_ts)
    total_mem = get_max_mem(hostid)
    a = []
    for i in mem_value:
        used_mem = total_mem - int(i["value"])/1024/1024/1024
        a.append(used_mem)
    if len(a) == 0:
        print "数据不全"
        sys.exit()
    else:
        pass
    a = sorted(a)                                    #对历史内存数据进行冒泡排序
    max_used_mem = int(a[-1])                        #最大使用内存为冒泡排序后的最后一个值
    min_used_mem = int(a[1])                         #最小使用内存为冒泡排序后的第一个值
    #计算平均使用内存
    sum_mem = sum(a)
    lenth = len(a)
    ave_used_mem =int(sum_mem/lenth)
    return max_used_mem,min_used_mem,ave_used_mem,total_mem

def get_last_mem_api(hostid):
    hostos = get_hostos(hostid)
    if hostos == "linux":
        itemid = zabbix_items(hostid, "vm.memory.size[available]")
    elif hostos == "windows":
        itemid = zabbix_items(hostid, "vm.memory.size[free]")
    else:
        print "未知操作系统类型"

    total_mem = get_max_mem(hostid)
    mem_value = total_mem - int(zabbix_last_history(itemid, 3)[0]["value"])/1024/1024/1024

    return mem_value,total_mem

def get_core_api(hostid,start_date,end_date):
    hostos = get_hostos(hostid)
    s_ts = int(time.mktime(time.strptime(start_date, "%Y-%m-%d")))
    e_ts = int(time.mktime(time.strptime(end_date, "%Y-%m-%d")))
    if hostos == "linux":
        itemid = zabbix_items(hostid,"system.cpu.load[all,avg1]")
    elif hostos == "windows":
        itemid = zabbix_items(hostid, "system.cpu.load[all,avg1]")
    else:
        print "未知操作系统类型"
    core_value = zabbix_history(itemid,0 ,s_ts,e_ts)
    total_core = get_max_core(hostid)
    a = []
    for i in core_value:
        cpu_load = float(i["value"])
        a.append(cpu_load)
    if len(a) == 0:
        print "数据不全"
        sys.exit()
    else:
        pass
    a = sorted(a)             #对历史内存数据进行冒泡排序
    max_core_load = ('%.1f' % (a[-1] ))   #最大负载为冒泡排序后的最后一个值
    min_core_load = ('%.1f' % (a[1]  ))    #最小负载为冒泡排序后的第一个值
    #计算平均负载
    lenth = len(a)
    sum_coreload = sum(a)
    ave_core_load = ('%.1f' % (sum_coreload/lenth))      #取2位小数
    return max_core_load,min_core_load,ave_core_load,total_core

def get_last_core_api(hostid):
    hostos = get_hostos(hostid)
    if hostos == "linux":
        itemid = zabbix_items(hostid,"system.cpu.load[all,avg1]")
    elif hostos == "windows":
        itemid = zabbix_items(hostid, "system.cpu.load[all,avg1]")
    else:
        print "未知操作系统类型"
    core_value = ('%.1f' % float(zabbix_last_history(itemid,0)[0]["value"]))
    total_core = get_max_core(hostid)
    return core_value,total_core


def get_disk_api(hostid):
    def win_disk(dick_num):
        key = "vfs.fs.size[%s:,pfree]" %dick_num
        id = zabbix_items(hostid, key)
        if id:
            value = zabbix_last_history(id, 0)
            return value
    def linux_disk(dick_num):
        key = "vfs.fs.size[%s,pfree]" %dick_num
        id = zabbix_items(hostid, key)
        if id:
            value = zabbix_last_history(id, 0)
            return value

    a = []
    hostos = get_hostos(hostid)
    if hostos == "linux":
        list = ["/","/home","/data"]
        for i in list:
            disk_value = linux_disk(i)
            if disk_value:
                a.append(i + ":" + disk_value[0]['value'])
    elif hostos == "windows":
        list = ["C","D","E"]
        for i in list:
            disk_value = win_disk(i)
            if disk_value:
                a.append(i + ":" + disk_value[0]['value'])
    else:
        print "未知操作系统类型"
    return a

def get_des(hostid):
    sql = """\
     select description from hosts_info where hostid = %s;
     """ % (hostid)
    if len(conn_db_fetchall(sql)) == 0:
        print "主机信息不全，请更新主机信息"
        sys.exit()
    else:
        pass
    des = conn_db_fetchall(sql)[0][0]
    return des