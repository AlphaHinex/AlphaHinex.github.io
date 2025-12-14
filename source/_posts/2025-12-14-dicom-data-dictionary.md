---
id: dicom-data-dictionary
title: "DICOM 数据字典"
description: "引用 DICOM 标准数据字典文档，及使用 Python 库解析相关内容"
date: 2025.12.14 10:26
categories:
    - Python
tags: [DICOM, Python]
keywords: DICOM, Data Dictionary, Data Elements, Tag, VR, VM, Modality, pydicom, matplotlib
cover: /contents/dicom-data-dictionary/cover.png
---

# DICOM

[DICOM](https://www.dicomstandard.org/about)（Digital Imaging and Communications in Medicine，医学数字成像和通信）是一种用于存储和传输医学影像数据的国际标准。

## 版本

自从 1985 年首次发布以来，DICOM 标准已经经历了多次修订和扩展，以适应不断发展的医学影像技术和需求。当前最新版本为 [2025e](https://dicom.nema.org/medical/dicom/2025e/)，历史版本可见 [历史版本](https://www.dicomstandard.org/disclaimer/standard/prior) 和 [各版本多种文件格式归档](https://dicom.nema.org/medical/dicom/)。

## 数据字典

DICOM 数据字典定义了 DICOM 文件中使用的各种数据元素及其属性。以下是一些常见的数据元素及其含义：

| 标签 (Tag)       | 名称 (Name)                | VR (Value Representation) | VM (Value Multiplicity) | 说明 (Description)                         |
|-----------------|----------------------------|---------------------------|-------------------------|-------------------------------------------|
| (0010,0010)      | Patient's Name            | PN                       | 1                       | 患者姓名                                    |
| (0010,0020)      | Patient ID                | LO                       | 1                       | 患者标识                                    |
| (0008,0060)      | Modality                  | CS                       | 1                       | [检查模态][CID-33]（如 CT、MR、US 等）        |
| (0028,0010)      | Rows                      | US                       | 1                       | 图像的行数                                  |
| (0028,0011)      | Columns                   | US                       | 1                       | 图像的列数                                  |
| (0028,0030)      | Pixel Spacing             | DS                       | 2                       | 像素间距（行间距和列间距，单位为毫米）           |
| (0028,1050)      | Window Center             | DS                       | 1-n                     | 窗口中心值                                  |
| (0028,1051)      | Window Width              | DS                       | 1-n                     | 窗口宽度值                                  |
| (0028,0008)      | Number of Frames          | IS                       | 1                       | 图像的帧数（对于多帧图像）                     |

以上仅为部分常见的数据元素，DICOM 数据字典包含了数千个数据元素，涵盖了医学影像的各个方面。完整的数据字典可以在 DICOM 标准的第 6 部分 [DICOM PS3.6 2025e - Data Dictionary](https://dicom.nema.org/medical/dicom/current/output/html/part06.html) 中找到。

标准中将数据元素分成了四类：

1. [DICOM Data Elements](https://dicom.nema.org/medical/dicom/current/output/html/part06.html#chapter_6)
1. [DICOM File Meta Elements](https://dicom.nema.org/medical/dicom/current/output/html/part06.html#chapter_7)
1. [DICOM Directory Structuring Elements](https://dicom.nema.org/medical/dicom/current/output/html/part06.html#chapter_8)
1. [DICOM Dynamic RTP Payload Elements](https://dicom.nema.org/medical/dicom/current/output/html/part06.html#chapter_9)

每类均以表格形式列出，如：

| Tag          | Name                    | Keyword                | VR  | VM   |     |
|--------------|-------------------------|------------------------|-----|------|-----|
| (0008,0001)  | Length to End           | Length​To​End            | UL  | 1    | RET |
| (0008,0005)  | Specific Character Set  | Specific​Character​Set   | CS  | 1-n  |     |
| ...          | ...                     | ...                    | ... | ...  | ... |

其中：

* Tag：数据元素的标签，相当于唯一 ID，由两个十六进制数字组成，分别表示组号和元素号，标准数据元素的组号为偶数，私有数据元素组号为奇数。
* Name：数据元素的名称，描述了该元素的含义。
* Keyword：数据元素的关键字，通常是名称的简写形式。
* VR (Value Representation)：数据元素的值表示，定义了该元素的数据类型，如：UL（Unsigned Long）、CS（Code String）、PN（Person Name）等，完整的 VR 值列表可见 [Table 6.2-1. DICOM Value Representations](https://dicom.nema.org/medical/dicom/current/output/html/part05.html#table_6.2-1)。
* VM (Value Multiplicity)：数据元素的值多重性，表示该元素可以包含多少个值（如单值、多值等）。

# pydicom

[pydicom](https://github.com/pydicom/pydicom) 是一个用于处理 DICOM 文件的 Python 库。它允许用户读取、修改和创建 DICOM 文件，支持大部分 DICOM 标准的数据元素和功能。

pydicom 使用内置的数据字典来解释 DICOM 文件中的数据元素。该数据字典包含了 DICOM 标准中定义的（除 Dynamic RTP Payload Elements 外）所有数据元素及其属性，可在 [_dicom_dict.py](https://github.com/pydicom/pydicom/blob/v3.0.1/src/pydicom/_dicom_dict.py) 文件中对照标准查看。

## 示例代码

下面的代码演示了如何使用 pydicom 读取 DICOM 文件中的元素及图像。

```bash
# 安装依赖
$ pip install pydicom matplotlib
$ pip list|grep -E 'pydicom|matplotlib'
matplotlib                 3.10.7
pydicom                    3.0.1
# 下载公开测试 DICOM 文件，如在 https://gitcode.com/open-source-toolkit/5f5718/blob/main/dicom%E6%96%87%E4%BB%B6.zip 获取的下载链接
$ wget https://raw-cdn.gitcode.com/open-source-toolkit/5f5718/blobs/45a5e793685ff145a3658c8dd9b1d728cefb6391/dicom%E6%96%87%E4%BB%B6.zip
$ unzip -j dicom文件.zip
$ ls *.dcm
1.2.840.113564.192168156.2012101911104793780.1003000225002.dcm GH177_D_CLUNIE_CT1_IVRLE_BigEndian_ELE_undefinded_length.dcm
1.2.840.113619.2.25.4.2420019.1350725419.624.dcm               GH177_D_CLUNIE_CT1_IVRLE_BigEndian_undefined_length.dcm
1.2.840.113619.2.25.4.2420019.1350725419.646.dcm               GH178.dcm
1.2.840.113619.2.25.4.2420019.1350725419.658.dcm               GH179A.dcm
1.2.840.113619.2.25.4.2420019.1350725419.667.dcm               GH179B.dcm
1.2.840.113619.2.25.4.2420019.1350725419.675.dcm               GH184.dcm
1.2.840.113619.2.25.4.2420019.1350725419.684.dcm               GH195.dcm
1.2.840.113619.2.25.4.2420019.1350725419.693.dcm               GH220.dcm
1.2.840.113619.2.25.4.2420019.1350725419.709.dcm               GH223.dcm
1.2.840.113619.2.25.4.2420019.1350725419.718.dcm               GH227.dcm
1.2.840.113619.2.25.4.2420019.1350725419.750.dcm               GH340.dcm
1.2.840.113619.2.25.4.2420019.1350725419.787.dcm               GH342.dcm
1.2.840.113619.2.25.4.2420019.1350725419.796.dcm               GH355.dcm
1.dcm                                                          GH364.dcm
10200904.dcm                                                   GH487.dcm
2.dcm                                                          GH538-jpeg1.dcm
3.dcm                                                          GH538-jpeg14sv1.dcm
4.dcm                                                          GH610.dcm
5.dcm                                                          GH626.dcm
6.dcm                                                          IM-0001-0001-0001.dcm
7.dcm                                                          TestPattern_Palette.dcm
8.dcm                                                          TestPattern_Palette_16.dcm
CR-ModalitySequenceLUT.dcm                                     TestPattern_RGB.dcm
D_CLUNIE_CT1_RLE_FRAGS.dcm                                     genFile.dcm
ETIAM_video_002.dcm                                            test2.dcm
GH064.dcm                                                      test_720.dcm
GH133.dcm
```

```python
import matplotlib.pyplot as plt
import pydicom

file_name = './1.2.840.113619.2.25.4.2420019.1350725419.684.dcm'

ds = pydicom.dcmread(file_name)
print(f"{len(ds.file_meta.keys())} + {len(ds.keys())} Tags：")

for key in ds.file_meta.keys():
    print(f"{key}: {ds.file_meta.get(key)}")

for key in ds.keys():
    print(f"{key}: {ds.get(key)}")

print('\n---\n')

print(f"SOP类..........: {ds.SOPClassUID} ({ds.SOPClassUID.name})")
print(f"患者姓名........: {ds.PatientName.family_comma_given()}")
print(f"检查模态........: {ds.Modality}")
print(f"图像尺寸........: {ds.get(0x00280010).value} x {ds[0x0028, 0x0011].value}")
print(f"像素数组维度.....: {ds.pixel_array.ndim}")
print(f"像素数组形状.....: {ds.pixel_array.shape}")
print(f"图像帧数........: {ds.NumberOfFrames}")
print(f"协议名称........: {ds.get('ProtocolName', '(缺失)')}")
print(f"检查部位........: {ds.get('BodyPartExamined', '(缺失)')}")
print(f"切片位置........: {ds.get('SliceLocation', '(缺失)')}")

if ds.pixel_array.ndim == 2:
    plt.imsave('./test.jpg', ds.pixel_array, cmap='gray')
else:
    for i in range(ds.pixel_array.shape[0]):
        png_file = f'./test/test_{i:03d}.jpg'
        plt.imsave(png_file, ds.pixel_array[i, :, :], cmap='gray')
```

```bash
$ python pydicom_test.py
8 + 304 Tags：
(0002,0000): (0002,0000) File Meta Information Group Length  UL: 196
(0002,0001): (0002,0001) File Meta Information Version       OB: b'\x00\x01'
(0002,0002): (0002,0002) Media Storage SOP Class UID         UI: MR Image Storage
(0002,0003): (0002,0003) Media Storage SOP Instance UID      UI: 1.2.840.113619.2.25.4.2420019.1350725419.684
(0002,0010): (0002,0010) Transfer Syntax UID                 UI: Implicit VR Little Endian
(0002,0012): (0002,0012) Implementation Class UID            UI: 1.2.826.0.1.3680043.1.1.4.3.82.2
(0002,0013): (0002,0013) Implementation Version Name         SH: 'DCMOBJ4.3.82.2'
(0002,0016): (0002,0016) Source Application Entity Title     AE: ''
(0008,0005): (0008,0005) Specific Character Set              CS: 'ISO_IR 100'
(0008,0008): (0008,0008) Image Type                          CS: ['ORIGINAL', 'PRIMARY', 'OTHER']
(0008,0016): (0008,0016) SOP Class UID                       UI: MR Image Storage
(0008,0018): (0008,0018) SOP Instance UID                    UI: 1.2.840.113619.2.25.4.2420019.1350725419.684
(0008,0020): (0008,0020) Study Date                          DA: '20121020'
(0008,0021): (0008,0021) Series Date                         DA: '20121020'
(0008,0022): (0008,0022) Acquisition Date                    DA: '20121020'
(0008,0023): (0008,0023) Content Date                        DA: '20121020'
(0008,0030): (0008,0030) Study Time                          TM: '095222'
(0008,0031): (0008,0031) Series Time                         TM: '100609'
(0008,0032): (0008,0032) Acquisition Time                    TM: '100609'
(0008,0033): (0008,0033) Content Time                        TM: '100609'
(0008,0050): (0008,0050) Accession Number                    SH: '270355'
(0008,0060): (0008,0060) Modality                            CS: 'MR'
(0008,0070): (0008,0070) Manufacturer                        LO: 'GE MEDICAL SYSTEMS'
(0008,0080): (0008,0080) Institution Name                    LO: 'ALYOUSSEF RC SUEZ'
(0008,0090): (0008,0090) Referring Physician's Name          PN: ''
(0008,1010): (0008,1010) Station Name                        SH: 'gehcgehc'
(0008,1030): (0008,1030) Study Description                   LO: 'e+1 L-SPINE'
(0008,103E): (0008,103E) Series Description                  LO: 'Ax T2 FSE'
(0008,1060): (0008,1060) Name of Physician(s) Reading Study  PN: ''
(0008,1070): (0008,1070) Operators' Name                     PN: 'S'
(0008,1090): (0008,1090) Manufacturer's Model Name           LO: 'SIGNA Profile EXCITE'
(0009,0010): (0009,0010) Private Creator                     LO: 'GEMS_IDEN_01'
(0009,1002): (0009,1002) [Suite id]                          SH: 'gehc'
(0009,1004): (0009,1004) [Product id]                        SH: 'SIGNA'
(0009,1027): (0009,1027) [Image actual date]                 SL: 1350727569
(0009,1030): (0009,1030) [Service id]                        SH: 'gehc'
(0009,1031): (0009,1031) [Mobile location number]            SH: '9999'
(0009,10E3): (0009,10E3) [Equipment UID]                     UI: 1.2.840.113619.1.217.5.6945.224376
(0009,10E7): (0009,10E7) [Exam Record checksum]              UL: 541419025
(0009,10E9): (0009,10E9) [Actual series data time stamp]     SL: 1350727569
(0010,0010): (0010,0010) Patient's Name                      PN: 'ABD.ALLAH MOHAMMED ABD.ABLLAH'
(0010,0020): (0010,0020) Patient ID                          LO: '138629'
(0010,0030): (0010,0030) Patient's Birth Date                DA: '19880101'
(0010,0040): (0010,0040) Patient's Sex                       CS: 'M'
(0010,1010): (0010,1010) Patient's Age                       AS: '024Y'
(0010,1030): (0010,1030) Patient's Weight                    DS: '90'
(0010,21B0): (0010,21B0) Additional Patient History          LT: ''
(0018,0020): (0018,0020) Scanning Sequence                   CS: 'SE'
(0018,0021): (0018,0021) Sequence Variant                    CS: ['SK', 'OSP']
(0018,0022): (0018,0022) Scan Options                        CS: ['FAST_GEMS', 'NPW', 'VB_GEMS', 'EDR_GEMS', 'FILTERED_GEMS']
(0018,0023): (0018,0023) MR Acquisition Type                 CS: '2D'
(0018,0025): (0018,0025) Angio Flag                          CS: 'N'
(0018,0050): (0018,0050) Slice Thickness                     DS: '6'
(0018,0080): (0018,0080) Repetition Time                     DS: '3000'
(0018,0081): (0018,0081) Echo Time                           DS: '99.24'
(0018,0082): (0018,0082) Inversion Time                      DS: '0'
(0018,0083): (0018,0083) Number of Averages                  DS: '4'
(0018,0084): (0018,0084) Imaging Frequency                   DS: '8.532733'
(0018,0085): (0018,0085) Imaged Nucleus                      SH: '1H'
(0018,0086): (0018,0086) Echo Number(s)                      IS: '1'
(0018,0087): (0018,0087) Magnetic Field Strength             DS: '0.2'
(0018,0088): (0018,0088) Spacing Between Slices              DS: '7'
(0018,0091): (0018,0091) Echo Train Length                   IS: '12'
(0018,0093): (0018,0093) Percent Sampling                    DS: '100'
(0018,0094): (0018,0094) Percent Phase Field of View         DS: '75'
(0018,0095): (0018,0095) Pixel Bandwidth                     DS: '150.234'
(0018,1000): (0018,1000) Device Serial Number                LO: '000000EG1736MR01'
(0018,1020): (0018,1020) Software Versions                   LO: ['14', 'LX', 'MR Software release:PROFILEHD.0_M4_0736.a']
(0018,1030): (0018,1030) Protocol Name                       LO: 'L.Spine Routine*/4'
(0018,1088): (0018,1088) Heart Rate                          IS: '60'
(0018,1090): (0018,1090) Cardiac Number of Images            IS: '0'
(0018,1094): (0018,1094) Trigger Window                      IS: '0'
(0018,1100): (0018,1100) Reconstruction Diameter             DS: '260'
(0018,1250): (0018,1250) Receive Coil Name                   SH: 'CTL PA-L'
(0018,1310): (0018,1310) Acquisition Matrix                  US: [224, 0, 0, 128]
(0018,1312): (0018,1312) In-plane Phase Encoding Direction   CS: 'COL'
(0018,1314): (0018,1314) Flip Angle                          DS: '90'
(0018,1315): (0018,1315) Variable Flip Angle Flag            CS: 'N'
(0018,1316): (0018,1316) SAR                                 DS: '0.1446'
(0018,5100): (0018,5100) Patient Position                    CS: 'HFS'
(0019,0010): (0019,0010) Private Creator                     LO: 'GEMS_ACQU_01'
(0019,100F): (0019,100F) [Horiz. Frame of ref.]              DS: '723.900024'
(0019,1011): (0019,1011) [Series contrast]                   SS: 0
(0019,1012): (0019,1012) [Last pseq]                         SS: 56
(0019,1017): (0019,1017) [Series plane]                      SS: 16
(0019,1018): (0019,1018) [First scan ras]                    LO: 'S'
(0019,1019): (0019,1019) [First scan location]               DS: '107.456'
(0019,101A): (0019,101A) [Last scan ras]                     LO: 'I'
(0019,101B): (0019,101B) [Last scan loc]                     DS: '-47.7672'
(0019,101E): (0019,101E) [Display field of view]             DS: '195.000000'
(0019,105A): (0019,105A) [Acquisition Duration]              FL: 198400000.0
(0019,107D): (0019,107D) [Second echo]                       DS: '0'
(0019,107E): (0019,107E) [Number of echoes]                  SS: 1
(0019,107F): (0019,107F) [Table delta]                       DS: '0.000000'
(0019,1081): (0019,1081) [Contiguous]                        SS: 1
(0019,1084): (0019,1084) [Peak SAR]                          DS: '0.289394'
(0019,1087): (0019,1087) [Cardiac repetition time]           DS: '0.000000'
(0019,1088): (0019,1088) [Images per cardiac cycle]          SS: 0
(0019,108A): (0019,108A) [Actual receive gain analog]        SS: 13
(0019,108B): (0019,108B) [Actual receive gain digital]       SS: 27
(0019,108D): (0019,108D) [Delay after trigger]               DS: '0'
(0019,108F): (0019,108F) [Swappf]                            SS: 0
(0019,1090): (0019,1090) [Pause Interval]                    SS: 0
(0019,1091): (0019,1091) [Pause Time]                        DS: '0.000000'
(0019,1092): (0019,1092) [Slice offset on freq axis]         SL: 0
(0019,1093): (0019,1093) [Auto Prescan Center Frequency]     DS: '85327330'
(0019,1094): (0019,1094) [Auto Prescan Transmit Gain]        SS: 132
(0019,1095): (0019,1095) [Auto Prescan Analog receiver gain] SS: 13
(0019,1096): (0019,1096) [Auto Prescan Digital receiver gain SS: 27
(0019,1097): (0019,1097) [Bitmap defining CVs]               SL: 4177
(0019,109B): (0019,109B) [Pulse Sequence Mode]               SS: 1
(0019,109C): (0019,109C) [Pulse Sequence Name]               LO: 'fse-xl'
(0019,109D): (0019,109D) [Pulse Sequence Date]               DT: '20070905123237'
(0019,109E): (0019,109E) [Internal Pulse Sequence Name]      LO: 'FSE-XL'
(0019,109F): (0019,109F) [Transmitting Coil Type]            SS: 3
(0019,10A0): (0019,10A0) [Surface Coil Type]                 SS: 0
(0019,10A1): (0019,10A1) [Extremity Coil flag]               SS: 0
(0019,10A2): (0019,10A2) [Raw data run number]               SL: 1546
(0019,10A3): (0019,10A3) [Calibrated Field strength]         UL: 0
(0019,10A4): (0019,10A4) [SAT fat/water/bone]                SS: 0
(0019,10A7): (0019,10A7) [User data 0]                       DS: '1.000000'
(0019,10A8): (0019,10A8) [User data 1]                       DS: '0.000000'
(0019,10A9): (0019,10A9) [User data 2]                       DS: '0.000000'
(0019,10AA): (0019,10AA) [User data 3]                       DS: '1.000000'
(0019,10AB): (0019,10AB) [User data 4]                       DS: '0.000000'
(0019,10AC): (0019,10AC) [User data 5]                       DS: '0.000000'
(0019,10AD): (0019,10AD) [User data 6]                       DS: '0.000000'
(0019,10AE): (0019,10AE) [User data 7]                       DS: '0.000000'
(0019,10AF): (0019,10AF) [User data 8]                       DS: '0.000000'
(0019,10B0): (0019,10B0) [User data 9]                       DS: '0.000000'
(0019,10B1): (0019,10B1) [User data 10]                      DS: '0.000000'
(0019,10B2): (0019,10B2) [User data 11]                      DS: '0.000000'
(0019,10B3): (0019,10B3) [User data 12]                      DS: '0.000000'
(0019,10B4): (0019,10B4) [User data 13]                      DS: '0.000000'
(0019,10B5): (0019,10B5) [User data 14]                      DS: '0.000000'
(0019,10B6): (0019,10B6) [User data 15]                      DS: '0.000000'
(0019,10B7): (0019,10B7) [User data 16]                      DS: '0.000000'
(0019,10B8): (0019,10B8) [User data 17]                      DS: '0.000000'
(0019,10B9): (0019,10B9) [User data 18]                      DS: '0.000000'
(0019,10BA): (0019,10BA) [User data 19]                      DS: '0.000000'
(0019,10BB): (0019,10BB) [User data 20]                      DS: '0.000000'
(0019,10BC): (0019,10BC) [User data 21]                      DS: '0.000000'
(0019,10BD): (0019,10BD) [User data 22]                      DS: '0.000000'
(0019,10BE): (0019,10BE) [Projection angle]                  DS: '0.000000'
(0019,10C0): (0019,10C0) [Saturation planes]                 SS: 0
(0019,10C2): (0019,10C2) [SAT location R]                    SS: 9990
(0019,10C3): (0019,10C3) [SAT location L]                    SS: 9990
(0019,10C4): (0019,10C4) [SAT location A]                    SS: 9990
(0019,10C5): (0019,10C5) [SAT location P]                    SS: 9990
(0019,10C6): (0019,10C6) [SAT location H]                    SS: 9990
(0019,10C7): (0019,10C7) [SAT location F]                    SS: 9990
(0019,10C8): (0019,10C8) [SAT thickness R/L]                 SS: 0
(0019,10C9): (0019,10C9) [SAT thickness A/P]                 SS: 0
(0019,10CA): (0019,10CA) [SAT thickness H/F]                 SS: 0
(0019,10CB): (0019,10CB) [Phase Contrast flow axis]          SS: 0
(0019,10CC): (0019,10CC) [Velocity encoding]                 SS: 0
(0019,10CD): (0019,10CD) [Thickness disclaimer]              SS: 0
(0019,10CE): (0019,10CE) [Prescan type]                      SS: 2
(0019,10CF): (0019,10CF) [Prescan status]                    SS: 0
(0019,10D2): (0019,10D2) [Projection Algorithm]              SS: 0
(0019,10D3): (0019,10D3) [Projection Algorithm Name]         SH: ''
(0019,10D5): (0019,10D5) [Fractional echo]                   SS: 2
(0019,10D7): (0019,10D7) [Cardiac phase number]              SS: 0
(0019,10D8): (0019,10D8) [Variable echoflag]                 SS: 0
(0019,10D9): (0019,10D9) [Concatenated SAT {# DTI Diffusion  DS: '0.000000'
(0019,10DF): (0019,10DF) [User data 23 {# DTI Diffusion Dir. DS: '0.000000'
(0019,10E0): (0019,10E0) [User data 24 {# DTI Diffusion Dir. DS: '0.000000'
(0019,10E2): (0019,10E2) [Velocity Encode Scale]             DS: '0.000000'
(0019,10F2): (0019,10F2) [Fast phases]                       SS: 0
(0019,10F9): (0019,10F9) [Transmit gain]                     DS: '132'
(0020,000D): (0020,000D) Study Instance UID                  UI: 1.2.840.113619.2.25.4.2420019.1350725418.739
(0020,000E): (0020,000E) Series Instance UID                 UI: 1.2.840.113619.2.25.4.2420019.1350725419.584
(0020,0010): (0020,0010) Study ID                            SH: '12693'
(0020,0011): (0020,0011) Series Number                       IS: '4'
(0020,0012): (0020,0012) Acquisition Number                  IS: '1'
(0020,0013): (0020,0013) Instance Number                     IS: '11'
(0020,0032): (0020,0032) Image Position (Patient)            DS: [-122.569, -74.361, -30.5999]
(0020,0037): (0020,0037) Image Orientation (Patient)         DS: [0.999656, 0.0136111, -0.0224004, -0.00833165, 0.975172, 0.221293]
(0020,0052): (0020,0052) Frame of Reference UID              UI: 1.2.840.113619.2.217.6945.224376.6992.1350719275.409
(0020,0060): (0020,0060) Laterality                          CS: ''
(0020,1002): (0020,1002) Images in Acquisition               IS: '16'
(0020,1040): (0020,1040) Position Reference Indicator        LO: ''
(0020,1041): (0020,1041) Slice Location                      DS: '-4.845304012'
(0020,9056): (0020,9056) Stack ID                            SH: '4'
(0021,0010): (0021,0010) Private Creator                     LO: 'GEMS_RELA_01'
(0021,1035): (0021,1035) [Series from which prescribed]      SS: 2
(0021,1036): (0021,1036) [Image from which prescribed]       SS: 5
(0021,1037): (0021,1037) [Screen Format]                     SS: 16
(0021,104F): (0021,104F) [Locations in acquisition]          SS: 16
(0021,1050): (0021,1050) [Graphically prescribed]            SS: 0
(0021,1051): (0021,1051) [Rotation from source x rot]        DS: '0.000000'
(0021,1052): (0021,1052) [Rotation from source y rot]        DS: '0.000000'
(0021,1053): (0021,1053) [Rotation from source z rot]        DS: '0.000000'
(0021,1056): (0021,1056) [Num 3D slabs]                      SL: 0
(0021,1057): (0021,1057) [Locs per 3D slab]                  SL: 0
(0021,1058): (0021,1058) [Overlaps]                          SL: 0
(0021,1059): (0021,1059) [Image Filtering 0.5/0.2T]          SL: 0
(0021,105A): (0021,105A) [Diffusion direction]               SL: 0
(0021,105B): (0021,105B) [Tagging Flip Angle]                DS: '0.000000'
(0021,105C): (0021,105C) [Tagging Orientation]               DS: '0.000000'
(0021,105D): (0021,105D) [Tag Spacing]                       DS: '0.000000'
(0021,105E): (0021,105E) [RTIA_timer]                        DS: '0.000000'
(0021,105F): (0021,105F) [Fps]                               DS: '0.000000'
(0021,1081): (0021,1081) [Auto window/level alpha]           DS: '0'
(0021,1082): (0021,1082) [Auto window/level beta]            DS: '0'
(0021,1083): (0021,1083) [Auto window/level window]          DS: '0'
(0021,1084): (0021,1084) [Auto window/level level]           DS: '0'
(0023,0010): (0023,0010) Private Creator                     LO: 'GEMS_STDY_01'
(0023,1070): (0023,1070) [Start time(secs) in first axial]   FD: 0.0
(0023,1074): (0023,1074) [No. of updates to header]          SL: 0
(0023,107D): (0023,107D) [Indicates study has complete info  SS: 0
(0025,0010): (0025,0010) Private Creator                     LO: 'GEMS_SERS_01'
(0025,1006): (0025,1006) [Last pulse sequence used]          SS: 56
(0025,1007): (0025,1007) [Images in Series]                  SL: 16
(0025,1010): (0025,1010) [Landmark Counter]                  SL: 0
(0025,1011): (0025,1011) [Number of Acquisitions]            SS: 1
(0025,1014): (0025,1014) [Indicates no. of updates to header SL: 0
(0025,1017): (0025,1017) [Series Complete Flag]              SL: 0
(0025,1018): (0025,1018) [Number of images archived]         SL: 0
(0025,1019): (0025,1019) [Last image number used]            SL: 16
(0025,101A): (0025,101A) [Primary Receiver Suite and Host]   SH: 'gehcgehc'
(0025,101B): (0025,101B) [Protocol Data Block (compressed)]  OB: Array of 1054 elements
(0027,0010): (0027,0010) Private Creator                     LO: 'GEMS_IMAG_01'
(0027,1006): (0027,1006) [Image archive flag]                SL: 0
(0027,1010): (0027,1010) [Scout Type]                        SS: 0
(0027,1030): (0027,1030) [Foreign Image Revision]            SH: ''
(0027,1031): (0027,1031) [Imaging Mode]                      SS: 1
(0027,1032): (0027,1032) [Pulse Sequence]                    SS: 56
(0027,1033): (0027,1033) [Imaging Options]                   SL: 1073745024
(0027,1035): (0027,1035) [Plane Type]                        SS: 16
(0027,1040): (0027,1040) [RAS letter of image location]      SH: 'I'
(0027,1041): (0027,1041) [Image location]                    FL: -4.845304012298584
(0027,1060): (0027,1060) [Image dimension - X]               FL: 224.0
(0027,1061): (0027,1061) [Image dimension - Y]               FL: 128.0
(0027,1062): (0027,1062) [Number of Excitations]             FL: 8.0
(0028,0002): (0028,0002) Samples per Pixel                   US: 1
(0028,0004): (0028,0004) Photometric Interpretation          CS: 'MONOCHROME2'
(0028,0008): (0028,0008) Number of Frames                    IS: '1'
(0028,0010): (0028,0010) Rows                                US: 256
(0028,0011): (0028,0011) Columns                             US: 256
(0028,0030): (0028,0030) Pixel Spacing                       DS: [1.0156, 1.0156]
(0028,0100): (0028,0100) Bits Allocated                      US: 16
(0028,0101): (0028,0101) Bits Stored                         US: 16
(0028,0102): (0028,0102) High Bit                            US: 15
(0028,0103): (0028,0103) Pixel Representation                US: 1
(0028,0106): (0028,0106) Smallest Image Pixel Value          SS: 0
(0028,0107): (0028,0107) Largest Image Pixel Value           SS: 158
(0028,1050): (0028,1050) Window Center                       DS: '79'
(0028,1051): (0028,1051) Window Width                        DS: '158'
(0028,1052): (0028,1052) Rescale Intercept                   DS: '0'
(0028,1053): (0028,1053) Rescale Slope                       DS: '1'
(0029,0010): (0029,0010) Private Creator                     LO: 'GEMS_IMPS_01'
(0029,1015): (0029,1015) [Lower range of Pixels1]            SL: 0
(0029,1016): (0029,1016) [Upper range of Pixels1]            SL: 0
(0029,1017): (0029,1017) [Lower range of Pixels2]            SL: 0
(0029,1018): (0029,1018) [Upper range of Pixels2]            SL: 0
(0029,1026): (0029,1026) [Version of the hdr struct]         SS: 2
(0029,1034): (0029,1034) [Advantage comp. Overflow]          SL: 16384
(0029,1035): (0029,1035) [Advantage comp. Underflow]         SL: 0
(0040,0253): (0040,0253) Performed Procedure Step ID         SH: ''
(0040,0254): (0040,0254) Performed Procedure Step Descriptio LO: ''
(0043,0010): (0043,0010) Private Creator                     LO: 'GEMS_PARM_01'
(0043,1001): (0043,1001) [Bitmap of prescan options]         SS: 6
(0043,1002): (0043,1002) [Gradient offset in X]              SS: 4
(0043,1003): (0043,1003) [Gradient offset in Y]              SS: -6
(0043,1004): (0043,1004) [Gradient offset in Z]              SS: 114
(0043,1006): (0043,1006) [Number of EPI shots]               SS: 0
(0043,1007): (0043,1007) [Views per segment]                 SS: 0
(0043,1008): (0043,1008) [Respiratory rate, bpm]             SS: 0
(0043,1009): (0043,1009) [Respiratory trigger point]         SS: 0
(0043,100A): (0043,100A) [Type of receiver used]             SS: 1
(0043,100B): (0043,100B) [DB/dt Peak rate of change of gradi DS: '0.000000'
(0043,100C): (0043,100C) [dB/dt Limits in units of percent]  DS: '80.000000'
(0043,100D): (0043,100D) [PSD estimated limit]               DS: '0.000000'
(0043,100E): (0043,100E) [PSD estimated limit in tesla per s DS: '0.000000'
(0043,1010): (0043,1010) [Window value]                      US: 0
(0043,101C): (0043,101C) [GE image integrity]                SS: 0
(0043,101D): (0043,101D) [Level value]                       SS: 0
(0043,1028): (0043,1028) [Unique image iden]                 OB: Array of 80 elements
(0043,1029): (0043,1029) [Histogram tables]                  OB: Array of 2068 elements
(0043,102A): (0043,102A) [User defined data]                 OB: Array of 3600 elements
(0043,102C): (0043,102C) [Effective echo spacing]            SS: 0
(0043,102D): (0043,102D) [Filter Mode (String slop field 1 i SH: '06'
(0043,102E): (0043,102E) [String slop field 2]               SH: ''
(0043,102F): (0043,102F) [Image Type (real, imaginary, phase SS: 0
(0043,1030): (0043,1030) [Vas collapse flag]                 SS: 0
(0043,1032): (0043,1032) [Vas flags]                         SS: 2
(0043,1033): (0043,1033) [Neg_scanspacing]                   FL: 0.0
(0043,1034): (0043,1034) [Offset Frequency]                  IS: '0'
(0043,1035): (0043,1035) [User_usage_tag]                    UL: 0
(0043,1036): (0043,1036) [User_fill_map_MSW]                 UL: 0
(0043,1037): (0043,1037) [User_fill_map_LSW]                 UL: 0
(0043,1038): (0043,1038) [User data 25...User data 48 {User4 FL: Array of 24 elements
(0043,1039): (0043,1039) [Slop_int_6... slop_int_9]          IS: [0, 2, 0, 0]
(0043,1060): (0043,1060) [Slop_int_10...slop_int_17]         IS: [0, 0, 0, 0, 0, 0, 0, 0]
(0043,1061): (0043,1061) [Scanner Study Entity UID]          UI: 1.2.840.113619.2.217.6945.224376.6992.1350719275.410
(0043,1062): (0043,1062) [Scanner Study ID]                  SH: '12693'
(0043,106F): (0043,106F) [Scanner Table Entry (single gradie DS: [2, 0, 0, 0]
(0043,107D): (0043,107D) [Recon mode flag word]              US: 0
(0043,1080): (0043,1080) [Coil ID Data]                      LO: ['116', '0000000000000000']
(0043,1081): (0043,1081) [GE Coil Name]                      LO: 'GE_CTL PA-L'
(0043,1082): (0043,1082) [System Configuration Information]  LO: ['SRMode=34', 'GCoilType=105', 'gradientAmp=8295', 'lineFreq=50', 'RFampType=103']
(0043,1083): (0043,1083) [Asset R Factors]                   DS: [1, 1]
(0043,1084): (0043,1084) [Additional Asset Data]             LO: ['10000', '0', '-1', '0', '']
(0043,1089): (0043,1089) [Governing Body, dB/dt, and SAR def LO: ['IEC', 'IEC_NORMAL', 'IEC_NORMAL']
(0043,108A): (0043,108A) [Private In-Plane Phase Encoding Di CS: 'COL'
(0043,1090): (0043,1090) [SAR Definition]                    LO: ['WHOLE_BODY_6_MIN', 'LOCAL_PEAK_6_MIN', 'PARTIAL_BODY_6MIN']
(0043,1095): (0043,1095) [Prescan Reuse String]              LO: ''
(0043,1096): (0043,1096) [Content Qualification]             CS: 'PRODUCT'
(0043,1097): (0043,1097) [Image Filtering Parameters]        LO: ['', '', '0', '0', '0', '100', '0', '0', 'rev=1;a=75;b=2;c=32;d=8;e=3;f=2;g=1;h=0']
(0043,109A): (0043,109A) [Rx Stack Identification]           IS: '5'
(7FE0,0010): (7FE0,0010) Pixel Data                          OW: Array of 131072 elements

---

SOP类..........: 1.2.840.10008.5.1.4.1.1.4 (MR Image Storage)
患者姓名........: ABD.ALLAH MOHAMMED ABD.ABLLAH,
检查模态........: MR
图像尺寸........: 256 x 256
像素数组维度.....: 2
像素数组形状.....: (256, 256)
图像帧数........: 1
协议名称........: L.Spine Routine*/4
检查部位........: (缺失)
切片位置........: -4.845304012
```

![test.jpg](https://alphahinex.github.io/contents/dicom-data-dictionary/test.jpg)

[CID-33]:https://dicom.nema.org/medical/dicom/current/output/html/part16.html#sect_CID_33

[Table CID 33. Modality]:https://dicom.nema.org/medical/dicom/current/output/html/part16.html#sect_CID_33
[Table CID 29. Acquisition Modality]:https://dicom.nema.org/medical/dicom/current/output/html/part16.html#sect_CID_29
[Table CID 34. Waveform Acquisition Modality]:https://dicom.nema.org/medical/dicom/current/output/html/part16.html#sect_CID_34
[Table CID 32. Non-Acquisition Modality]:https://dicom.nema.org/medical/dicom/current/output/html/part16.html#sect_CID_32
[_uid_dict.py]:https://github.com/pydicom/pydicom/blob/v3.0.1/src/pydicom/_uid_dict.py
[_private_dict.py]:https://github.com/pydicom/pydicom/blob/v3.0.1/src/pydicom/_private_dict.py
