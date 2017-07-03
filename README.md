# FileMonitor
文件监控清除
# 用法
```
usage: defend_filewatch.py [options]

        作者：End1ng blog:end1ng.wordpress.com
        --------------------------------
            简单的一个文件监控脚本
            删除新增文件和文件夹
            恢复被修改的文件

optional arguments:
  -h, --help            显示当前帮助
  --version             show program's version number and exit

Necessary arguments:
  -w 目录 [目录 ...], --watchlist 目录 [目录 ...]
                        要监控的目录 多个用空格分隔
  -i 后缀 [后缀 ...], --ignore 后缀 [后缀 ...]
                        允许的后缀,修改会覆盖。 默认jpg,png,gif

other arguments:
  -b 目录, --backupdir 目录
                        备份的位置 默认/var/var
  --logfile 文件          日志位置 默认/var/log/filewatch.log
  --debug               输出详细的debug信息
```

# fileWatchLite
useage:
        python fileWatchList 目录
        -w 仅监控
        -d 开启debug
