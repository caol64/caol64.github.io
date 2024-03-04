---
author: 路边的阿不
title: 从PS2记忆卡中导出存档文件
slug: exporting-file-from-ps2-memcard
description: Dive into the exciting world of PS2 memory card filesystems and learn how to extract specific game saves using Python. Fully executable code provided. Step into our in-depth analysis!
date: 2023-09-29 17:49:16
draft: false
ShowToc: true
TocOpen: true
tags:
  - ps2mc-browser
  - Python
categories:
  - 教程
---
上一篇文章中我们解析了PS2存储卡的文件系统，这次直接实战，编写`python`代码导出指定的游戏存档。本篇文章完整代码可以访问：[ps2mc-browser](https://github.com/caol64/ps2mc-browser)。

## 01 解析`SuperBlock`
`SuperBlock`结构如下，大小为340字节：
```c++
struct SuperBlock {
    char magic[28];
    char version[12];
    uint16 page_size;
    uint16 pages_per_cluster;
    uint16 pages_per_block;
    uint16 unknown; // ignore
    uint32 clusters_per_card;
    uint32 alloc_offset;
    uint32 alloc_end;
    uint32 rootdir_cluster;
    uint32 backup_block1; // ignore
    uint32 backup_block2; // ignore
    uint32 unknown[2]; // ignore
    uint32 ifc_list[32];
    uint32 bad_block_list[32]; // ignore
    byte card_type;
    byte card_flags;
    byte unknown; // ignore
    byte unknown; // ignore
};
```
使用`struct.unpack()`解包：
```python
struct.Struct("<28s12sHHH2xLLLL4x4x8x128s128xbbxx").unpack(byte_val)
```
得到`page_size`和`pages_per_cluster`。

## 02 读取`page`和`cluster`
根据公式计算`page`和`cluster`大小：
```python
self.spare_size = (self.page_size // 128) * 4 # 备用区域字节数
self.raw_page_size = self.page_size + self.spare_size # 算上备用区域的page字节数
self.cluster_size = self.page_size * self.pages_per_cluster # 簇字节数
```

读取`page`和`cluster`，`spare area`里的内容是被舍弃掉的：
```python
def read_page(self, n): # n为page编号
    offset = self.raw_page_size * n
    return self.byte_val[offset: offset + self.page_size]

def read_cluster(self, n): # n为cluster编号
    page_index = n * self.pages_per_cluster
    byte_buffer = bytearray()
    for i in range(self.pages_per_cluster):
        byte_buffer += self.read_page(page_index + i)
    return bytes(byte_buffer)
```

## 03 构建`FAT`矩阵
从上一篇文章知道`FAT`矩阵的构建方式如下：
![](imgs/posts/2023-09-29-exporting-file-from-ps2-memcard/%E5%AD%98%E5%82%A8%E5%8D%A1-FAT2.jpg)

```python
def __build_fat_matrix(self):
    # 从ifc_list构建间接FAT
    indirect_fat_matrix = self.__build_matrix(self.ifc_list)
    # 间接FAT是个一维数组
    indirect_fat_matrix = indirect_fat_matrix.reshape(indirect_fat_matrix.size)
    # 排除掉0xFFFFFFFF这种未分配的
    indirect_fat_matrix = [x for x in indirect_fat_matrix if x != Fat.UNALLOCATED]
    # 从间接FAT构建直接FAT
    fat_matrix = self.__build_matrix(indirect_fat_matrix)
    return fat_matrix

def __build_matrix(self, cluster_list):
     # 初始化矩阵
    matrix = np.zeros((len(cluster_list), self.fat_per_cluster), np.uint32)
     # 遍历cluster
    for index, v in enumerate(cluster_list):
        # 读出每个cluster的256个FAT
        cluster_value = self.read_cluster(v)
        cluster_value_unpacked = np.frombuffer(cluster_value, np.uint32)
        for index0, v0 in enumerate(cluster_value_unpacked):
             # 给矩阵赋值
            matrix[index, index0] = v0
    return matrix

# 给出簇编号n，找到其对应的FAT的值
def get_fat_value(self, n):
    value = self.fat_matrix[(n // self.fat_per_cluster) % self.fat_per_cluster,
                            n % self.fat_per_cluster]
    # 最高位为8代表正常使用的簇，其它值代表簇未分配，最高位为8时，取低31位的整形值
    return value ^ Fat.ALLOCATED_BIT if value & Fat.ALLOCATED_BIT > 0 else value
```

## 04 条目数据结构
条目是所有文件和目录的元数据，条目的数据结构如下：
```c++
struct Entry {
    uint16 mode;
    uint16 unknown; // ignore
    uint32 length;
    char created[8];
    uint32 cluster;
    uint32 dir_entry; // ignore
    char modified[8];
    uint32 attr; // ignore
    char padding[28]; // ignore
    char name[32];
    char padding[416]; // ignore
};
```
使用`struct.unpack()`解包：
```python
struct.Struct("<H2xL8sL4x8s4x28x32s416x").unpack(byte_val)
```
每个条目的大小为512字节，条目里最重要的字段是`cluster`，标识了该条目对应的文件或目录的簇编号。如果本条目是目录，则对应的簇编号是“条目簇”；如果本条目是文件，则对应的簇编号是“文件簇”。另一个重要字段是`length`，如果本条目是目录，则对应的是目录下的条目数；如果本条目是文件，则对应的是文件的字节数。

## 05 解析“条目簇”和“数据簇”
```python
# 读取条目，条目是512字节，一个簇可以包含多个条目
def read_entry_cluster(self, cluster_offset):
    cluster_value = self.read_cluster(cluster_offset + self.alloc_offset)
    return Entry.build(cluster_value)

# 读取数据，要从第一个簇开始读取到文件结束
def read_data_cluster(self, entry):
    byte_buffer = bytearray()
    chain_start = entry.cluster
    bytes_read = 0
    while chain_start != Fat.CHAIN_END:
        to_read = min(entry.length - bytes_read, self.cluster_size)
        byte_buffer += self.read_cluster(chain_start + self.alloc_offset)[:to_read]
        bytes_read += to_read
        chain_start = self.get_fat_value(chain_start)
    return bytes(byte_buffer)

def build(byte_val):
    entry_count = len(byte_val) // Entry.__size
    entries = []
    for i in range(entry_count):
        entries.append(Entry(byte_val[i * Entry.__size:
                                      i * Entry.__size + Entry.__size]))
    return entries
```

## 06 读取存储卡中的所有文件
上一篇文章说过，根目录没有条目，它的首个“条目簇”在超级块的`rootdir_cluster`中，它的“包含条目数”在`.`这个条目中。

要读取存储卡中的所有文件，第一步是解析根目录下所有条目，再解析条目下所有文件。因此只要循环调用以下方法：
```python
def find_sub_entries(self, parent_entry):
    chain_start = parent_entry.cluster
    sub_entries = []
    while chain_start != Fat.CHAIN_END:
        entries = self.read_entry_cluster(chain_start)
        for e in entries:
            if len(sub_entries) < parent_entry.length:
                sub_entries.append(e.unpack())
        chain_start = self.get_fat_value(chain_start)
    return [x for x in sub_entries if not x.name.startswith('.')]
```
结果如下：
```
BISCPS-15119sv01
    GameData
    BISCPS-15119sv01
    icon00.ico
    icon.sys
BISCPS-15116sv01
    GameData
    BISCPS-15116sv01
    icon00.ico
    icon.sys
BASLUS-21441DBZT2
    icon.sys
    dbzsn.ico
    BASLUS-21441DBZT2
...
```

## 07 导出游戏存档
既然所有文件条目都已经读取出来了，我们只要写个方法，根据输入的游戏名称，即可导出目录下的所有文件。
```python
def export(self, name, dest):
    dir_path = dest + os.sep + name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    entries = self.lookup_entry_by_name(name)
    for e in entries:
        if e.is_file():
            with open(dir_path + os.sep + e.name, 'wb') as f:
                f.write(self.ps2mc.read_data_cluster(e))
```

## 08 结尾
至此，我们已经可以把一个游戏的存档从存储卡中导出来了。如果你有`python`运行环境，可以直接运行文章一开始提供的`github`链接里的代码。

下一篇我们将分析一下每个存档文件里的`icon.sys`和`xxx.ico`文件，这两个文件是存档3d特效的数据文件。

## 09 参考文献
- [Ross Ridge - PlayStation 2 Memory Card File System](https://www.ps2savetools.com/ps2memcardformat.html)
- [Florian Märkl - mymcplus](https://git.sr.ht/~thestr4ng3r/mymcplus)
