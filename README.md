这是用python项目，用于读取并不同券商/银行的交易确认单(pdf或eml格式)，然后输出 JSON 格式的股票交易记录。

要求为每一个券商/银行生成一个 .py 脚本文件，用于对特定券商/银行的交易确认单进行分析，并输出 JSON 格式的交易记录。

## 执行逻辑
1. 脚本主程序从命令行接受一个文件名，然后通过调用函数 xxx_yyy2tx() 完成分析和数据读取，输出返回结果，函数命名中的 xxx 为券商/银行的缩写，yyy 为文件的格式(pdf或eml)。
2. xxx_yyy2tx() 函数签名为：接受一个 str 参数作为输入的文件名，返回一个包含一条或多条交易记录的列表；每条交易记录为一个 dict 对象，具体格式参见以下示例。
3. 按以下各个券商/银行的交易确认单示例进行分析。

### Huatai
    文件名 "OtherAT_Huatai_026.08.26 江苏神通 & 华明装备.pdf", 应返回的列表如下：
        [
            {
            "type": "S",
            "ticker": "002438",
            "volume": 327100,
            "price": 13.938,
            "net_amount": 4556193.90,
            "trans_fee": 646.11,
            "tax": 2279.79
            },
            {
            "type": "S",
            "ticker": "002270",
            "volume": 562000,
            "price": 19.382,
            "net_amount": 10886129.53,
            "trans_fee": 1107.68,
            "tax": 5446.79
            }
        ]

    其中的 trans_fee 由 price * volume - net_amount - tax 或 net_amount - price * volume - tax (分别对应 Sell/Buy 的情形) 计算而来。

    另一个示例文件名为 "OtherAT_Huatai_2026.05.14 中际旭创.pdf"，应返回的列表如下：
        [
            {
            "type": "B",
            "ticker": "300308",
            "volume": 9400,
            "price": 1055.351,
            "net_amount": 9921541.03,
            "trans_fee": 1241.63,
            "tax": 0.0
            }
        ]

### Huatai_HK
    文件名 "Huatai_HK_1.pdf", 应返回的列表如下：
        [
            {
            "type": "S",
            "date": "2026-07-22",
            "settlement_date": "2026-07-22",
            "ticker": "600887",
            "volume": 500000,
            "price": 27.1436,
            "net_amount": 13554372.45,
            "trans_fee": 10641.65,
            "tax": 6785.90
            }
        ]

    其中的 trans_fee 的计算与上一节相同，但 date 和 settlement_date 字段则从文件中读取。

### HSBC
    文件名 “HSBC-8088-620351-0001_Trade Confirmation as of 28 July 2025.pdf", 应返回的列表如下：
        [
            {
            "broker": "HSBC",
            "type": "S",
            "date": "2025-07-28",
            "settlement_date": "2025-07-30",
            "ticker": "0386.HK",
            "volume": 13582000,
            "price": 4.521900,
            "net_amount": 61257683.75,
            "trans_fee": 158762.05,
            "tax": 0.0
            }
        ]

    文件名 “HSBC-8088-624122-0001_Trade Confirmation as of 28 July 2025.pdf", 应返回的列表如下：
        [
            {
            "broker": "HSBC HK",
            "type": "S",
            "date": "2025-07-28",
            "settlement_date": "2025-07-30",
            "ticker": "0386.HK",
            "volume": 6250000,
            "price": 4.522800,
            "net_amount": 28194428.02,
            "trans_fee": 73071.98,
            "tax": 0.0
            }
        ]

    其中的 broker 字段由文件中的 ACCOUNT NAME 决定，如果 ACCOUNT NAME 为 IKARIA GROUP (HK) LIMITED, 则 broker 字段填 HSBC HK, 否则填 HSBC。

### Maybank
    文件名 “Maybank_0114460klsusd_eml_20260225174351.pdf", 应返回的列表如下：
        [
            {
            "type": "B",
            "date": "2026-02-25",
            "settlement_date": "2026-02-27",
            "ticker": "0215.KL",
            "volume": 165000,
            "price": 2.3302,
            "net_amount": 385463.95,
            "trans_fee": 595.95,
            "tax": 385.0
            }
        ]

    文件名 “Maybank_0114460klsusd_eml_20260505175106.pdf", 应返回的列表如下：
        [
            {
            "type": "S",
            "date": "2026-05-05",
            "settlement_date": "2026-05-07",
            "ticker": "5264.KL",
            "volume": 1020800,
            "price": 0.9038,
            "net_amount": 920246.01,
            "trans_fee": 1430.03,
            "tax": 923.0
            }
        ]

    其中 ticker 字段要从文件中给出的 ISIN. Code 代码转换而来，具体的转换方法可从网上查找。

### GF
    文件名 “GF-20260826-10821237-BG20260826000033-2026051200000011.pdf", 应返回的列表如下：
        [
            {
            "type": "B",
            "date": "2026-08-26",
            "settlement_date": "2026-08-27",
            "ticker": "002270",
            "volume": 562000,
            "price": 19.3949,
            "net_amount": 10909589.65,
            "trans_fee": 9655.85,
            "tax": 0.0
            },
            {
                "type": "B",
                "date": "2026-08-26",
                "settlement_date": "2026-08-27",
                "ticker": "002438",
                "volume": 860900,
                "price": 13.9591,
                "net_amount": 12028014.57,
                "trans_fee": 10625.38,
                "tax": 0.0,
            }
        ]

### JPMorgan
    文件名 “JPM_62856134_3839260_2026-09-01.pdf", 应返回的列表如下：
        [
            {
            "broker": "JPM",
            "type": "B",
            "date": "2026-09-01",
            "sec_name": "ZHEJIANG JIULI HI-TECH METALS CO LT",
            "ticker": "002318.SZ",
            "volume": 235600,
            "price": 20.6448,
            "net_amount": 4871619.81,
            "trans_fee": 7704.93,
            "tax": 0.0
            }
        ]

    文件名 “JPM_62884986_5179260_2026-09-02.pdf", 应返回的列表如下：
        [
            {
            "broker": "JPM HK",
            "type": "B",
            "date": "2026-09-02",
            "sec_name": "MEITUAN",
            "ticker": "3690.HK",
            "volume": 200000,
            "price": 78.5935,
            "net_amount": 15759333.14,
            "trans_fee": 24914.14,
            "tax": 15719.0
            }
        ]

    其中 ticker 字段要从文件中给出的 ISIN Number 转换而来，具体的转换方法可从网上查找。如果确实无法找到从 ISIN 转换到 ticker 的方法，可以将 ticker 字段置为空字符串。

### IIFL
    文件名 “IIFL_23062026.pdf", 应返回的列表如下：
        [
            {
            "type": "B",
            "date": "2026-06-23",
            "settlement_date": "2026-06-24",
            "sec_name": "POWER GRID CORP. LTD.",
            "isin": "INE752E01010",
            "ticker": "POWERGRID.NS",
            "volume": 613689,
            "price": 291.811,
            "trans_fee": 268621.80,
            "tax": 228454.75
            }
        ]

    其中 trans_fee 字段由文件中直接读取，不通过其它字段计算得到。ticker 字段要从 ISIN 转换而来，具体的转换方法可从网上查找。如果确实无法找到从 ISIN 转换到 ticker 的方法，可以将 ticker 字段置为空字符串。

### SCB
    文件名 “SCB-08-Apr-2026.pdf", 应返回的列表如下：
        [
            {
            "type": "S",
            "date": "2026-04-08",
            "settlement_date": "2026-04-10",
            "ticker": "0857.HK",
            "volume": 2000000,
            "amount": 21066200.0,
            "price": 10.5331,
            "trans_fee": 48137.07,
            "tax": 0.0
            }
        ]

    其中 price 字段由 amount / volume 计算得到。

### JPMorgan_eml
    文件名 “JPM- Unofficial Order Summary.eml", 应返回的列表如下：
        [
            {
            "broker": "JPM HK",
            "type": "B",
            "date": "2026-09-02",
            "settlement_date": "2026-09-04",
            "sec_name": "MEITUAN",
            "ticker": "3690.HK",
            "volume": 100000,
            "price": 78.0840
            },
            {
            "broker": "JPM HK",
            "type": "B",
            "date": "2026-09-02",
            "settlement_date": "2026-09-04",
            "sec_name": "MEITUAN",
            "ticker": "3690.HK",
            "volume": 200000,
            "price": 78.5935
            }
        ]

    文件名 “JPM- Unofficial Order Summary[1].eml", 应返回的列表如下：
        [
            {
            "broker": "JPM HK",
            "type": "B",
            "date": "2026-09-01",
            "settlement_date": "2026-09-03",
            "sec_name": "DONGFANG ELECTRIC CORP LTD-H",
            "ticker": "1072.HK",
            "volume": 200000,
            "price": 20.4473
            },
            {
            "broker": "JPM",
            "type": "B",
            "date": "2026-09-01",
            "settlement_date": "2026-09-01",
            "sec_name": "ZHEJIANG JIULI HI-TECH-A",
            "ticker": "002318",
            "volume": 235600,
            "price": 20.6448
            }
        ]

    其中的 broker 字段由文件中的 Acc Number 决定，如果 Acc Number 为 51***60, 则 broker 字段填 JPM HK, 否则填 JPM。

## 代码要求
1. 使用 pymupdf 库来分析 pdf 文件。
2. 生成相应的测试代码。
