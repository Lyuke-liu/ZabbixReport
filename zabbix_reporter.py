# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from zabbix_data import *
from pyecharts import *
from collections import OrderedDict
import time
import webbrowser
import datetime
from send_email import *

start_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
end_date = datetime.datetime.now().strftime('%Y-%m-%d')
reporter_path = "/home/zabbix_report/report_%s.html" %(start_date)

# 定义供报表使用的数组与字典
hosts_arr = []
max_mem_arr = []
min_mem_arr = []
ave_mem_arr = []
total_mem_arr = []
max_core_arr = []
min_core_arr = []
ave_core_arr = []
total_core_arr = []
mem_dict = {}
core_dict = {}
disk_dict = {}

hosts = zabbix_hosts()
#print "正在获取历史信息"
for i in hosts:
    hostid = i['hostid']
    des = get_des(hostid)  # 获取每个主机的别称
    # 获取主机内存信息并存入字典
    mem = get_mem_api(hostid,start_date, end_date)
    mem_dict[des] = mem
    #time.sleep(1)
    # 获取主机负载信息并存入字典
    core = get_core_api(hostid,start_date, end_date)
    core_dict[des] = core
    #time.sleep(1)
    # 获取主机磁盘使用信息并存入字典
    disk_list = get_disk_api(hostid)
    len_disk = len(disk_list)

    if len_disk == 1:
        disk1 = disk_list[0]
        disk_name1 = disk1.split(":", 1)[0]
        disk_per = float(disk1.split(":", 1)[1])
        disk_freed = ("%.2f" % (disk_per))
        disk_used = ("%.2f" % (100 - disk_per))
        v1 = [disk_freed, disk_used]
        disk_name2 = ""
        v2 = [0, 0]
        disk_name3 = ""
        v3 = [0, 0]
        disk_dict[des] = [disk_name1,v1,disk_name2,v2,disk_name3,v3]

    elif len_disk == 2:
        disk1 = disk_list[0]
        disk_name1 = disk1.split(":", 1)[0]
        disk_per = float(disk1.split(":", 1)[1])
        disk_freed = ("%.2f" % (disk_per))
        disk_used = ("%.2f" % (100 - disk_per))
        v1 = [disk_freed, disk_used]

        disk2 = disk_list[1]
        disk_name2 = disk2.split(":", 1)[0]
        disk_per = float(disk2.split(":", 1)[1])
        disk_freed = ("%.2f" % (disk_per))
        disk_used = ("%.2f" % (100 - disk_per))
        v2 = [disk_freed, disk_used]
        disk_name3 = ""
        v3 = [0, 0]
        disk_dict[des] = [disk_name1,v1,disk_name2,v2,disk_name3,v3]
    elif len_disk == 3:
        disk1 = disk_list[0]
        disk_name1 = disk1.split(":", 1)[0]
        disk_per = float(disk1.split(":", 1)[1])
        disk_freed = ("%.2f" % (disk_per))
        disk_used = ("%.2f" % (100 - disk_per))
        v1 = [disk_freed, disk_used]

        disk2 = disk_list[1]
        disk_name2 = disk2.split(":", 1)[0]
        disk_per = float(disk2.split(":", 1)[1])
        disk_freed = ("%.2f" % (disk_per))
        disk_used = ("%.2f" % (100 - disk_per))
        v2 = [disk_freed, disk_used]

        disk3 = disk_list[2]
        disk_name3 = disk3.split(":", 1)[0]
        disk_per = float(disk3.split(":", 1)[1])
        disk_freed = ("%.2f" % (disk_per))
        disk_used = ("%.2f" % (100 - disk_per))
        v3 = [disk_freed, disk_used]
        disk_dict[des] = [disk_name1,v1,disk_name2,v2,disk_name3,v3]
    else:
        print "error"
    #time.sleep(1)
#    print "成功获取主机 %s 信息" %(des)


# 对字典中的主机进行冒泡排序，使得图表更加美观
mem_dict = OrderedDict(sorted(mem_dict.items(), key=lambda t: t[0]))
for k, v in mem_dict.items():
    hosts_arr.append(k)
    max_mem_arr.append(v[0])
    min_mem_arr.append(v[1])
    ave_mem_arr.append(v[2])
    total_mem_arr.append(v[3])
core_dict = OrderedDict(sorted(core_dict.items(), key=lambda t: t[0]))
for k, v in core_dict.items():
    max_core_arr.append(v[0])
    min_core_arr.append(v[1])
    ave_core_arr.append(v[2])
    total_core_arr.append(v[3])

dick_dict = OrderedDict(sorted(disk_dict.items(), key=lambda t: t[0]))



#print "正在生成报告"
# 报表部分
# 内存使用信息
# 柱状图
bar = Bar("                                  内存使用情况")  # 设置图表标题
bar.add("最大使用内存", hosts_arr, max_mem_arr,
        is_label_show=True,  # 显示数值标签
        bar_category_gap='50%',  # 类目轴的柱状距离，当设置为 0 时柱状是紧挨着
        # mark_point=["max","min"],                             #显示最值
        xaxis_interval=0,
        xaxis_rotate=40,  # X轴元素倾斜程度
        legend_pos="20%",is_toolbox_show=False
        )
# 折线图
line = Line("内存使用情况")
line.add("内存上限", hosts_arr, total_mem_arr,
         line_type="dashed",  # 折线类型  solid-实线, dashed-虚线, dotted-点线。
         is_smooth=True,  # 折线是否平滑
         is_label_show=False,
         legend_pos="20%"
         )
line.add("平均使用内存", hosts_arr, ave_mem_arr, is_smooth=True, line_type='dashed',legend_pos="20%",is_toolbox_show=False)
# 将柱状图与折线图整个为一个图
overlap = Overlap(width=950, height=450)  # 设置图表尺寸
overlap.add(bar)
overlap.add(line)


#负载信息
bar2 = Bar("                                  负载情况",title_pos="50%")
bar2.add("最大负载", hosts_arr, max_core_arr,
         is_label_show=True,
         bar_category_gap='50%',
         # mark_point=["max"],
         xaxis_interval=0,
         xaxis_rotate=40,
         legend_pos="70%",
         is_toolbox_show=False
         )
line2 = Line()
line2.add("负载上限", hosts_arr, total_core_arr,
          line_type='dashed',
          # is_step=True,
          is_smooth=True,
          is_label_show=False,
          legend_pos="70%")
line2.add("平均负载", hosts_arr, ave_core_arr, is_smooth=True, line_type='dashed', legend_pos="70%",is_toolbox_show=False)


overlap2 = Overlap(width=950, height=450)
overlap2.add(bar2)
overlap2.add(line2)


#磁盘信息饼图
timeline = Timeline('',timeline_bottom=0,width=1900, height=450,timeline_left="center")
attr = ["剩余磁盘空间", "已使用磁盘空间"]
for k, v in dick_dict.items():
    des = k
    disk_name1 = v[0]
    v1 = v[1]
    disk_name2 = v[2]
    v2 = v[3]
    disk_name3 = v[4]
    v3 = v[5]
    if disk_name2 == "" and disk_name3 == "":
        pie = Pie("                                  磁盘使用情况 "+des + "   磁盘:" + disk_name1 + disk_name2, title_pos="left")
        pie.add(disk_name1, attr, v1, is_label_show=True, radius=[0, 50], rosetype="radius",
                is_random=True,
                label_text_color=None
                )
        pie.add(disk_name2, attr, v2, radius=[0, 0], rosetype="radius",
                legend_pos="center",
                )
        pie.add(disk_name3, attr, v3, radius=[0, 0], rosetype="radius",
                legend_pos="center",
                )
    elif disk_name2 != "" and disk_name3 == "":
        pie = Pie("                                  磁盘使用情况 "+des + "   磁盘:" + disk_name1 + " 左" + "   磁盘:" + disk_name2 + " 右", title_pos="left")
        pie.add(disk_name1, attr, v1, is_label_show=True, center=[30, 50], radius=[0, 50], rosetype="radius",
                )
        pie.add(disk_name2, attr, v2, is_label_show=True, center=[70, 50], radius=[0, 50], rosetype="radius",
                legend_pos="center",
                )
        pie.add(disk_name3, attr, v3, radius=[0, 0], rosetype="radius",
                legend_pos="center",
                )
    else:
        pie = Pie("                                  磁盘使用情况 "+des + "  磁盘:" + disk_name1 + " 左" + "  磁盘:" + disk_name2 + " 中"+ "  磁盘:" + disk_name3 + " 右", title_pos="left")
        pie.add(disk_name1, attr, v1, is_label_show=True, center=[20, 50], radius=[0, 50], rosetype="radius",
                )
        pie.add(disk_name2, attr, v2, is_label_show=True, center=[50, 50], radius=[0, 50], rosetype="radius",
                )
        pie.add(disk_name3, attr, v3, is_label_show=True, center=[80, 50], radius=[0, 50], rosetype="radius",
                is_random=True,
                legend_pos="center",
                )


    timeline.add(pie, des)

# 将所有图表整个为一个页面
page = Page("服务器性能报告")

grid = Grid("",width=1900,height=450)
grid.add(overlap,grid_left="2%",grid_right="52%")
grid.add(overlap2,grid_right="2%",grid_left="52%")
page.add(grid)
page.add(timeline)
page.render(reporter_path)




#发送邮件
try:
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_email(reporter_path)
except Exception as e:
    print e




