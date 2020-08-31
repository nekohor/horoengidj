import pandas as pd
import numpy as np
import cx_Oracle
from dateutil.parser import parse


class TempoStats():

    def __init__(self, mill_line_tag, start_time, end_time):
        self.mill_line_tag = mill_line_tag
        self.start_time = parse(start_time).strftime("%Y-%m-%d %H:%M:%S")
        self.end_time = parse(end_time).strftime("%Y-%m-%d %H:%M:%S")

        self.stds = [1, 2, 3, 4, 5, 6, 7]

        self.put_col = "F{}_BITE_ON"
        self.done_col = "F{}_CAST_ON"
        self.cur_put_col = "F{}_BITE_ON_CUR"
        self.cur_done_col = "F{}_CAST_ON_CUR"
        self.last_put_col = "F{}_BITE_ON_LAST"
        self.last_done_col = "F{}_CAST_ON_LAST"

        self.r1_bite_cols = ["R1_BITE_ON1", "R1_BITE_ON2", "R1_BITE_ON3"]
        self.r2_bite_cols = [
            "R2_BITE_ON1",
            "R2_BITE_ON2",
            "R2_BITE_ON3",
            "R2_BITE_ON4",
            "R2_BITE_ON5",
            "R2_BITE_ON6",
            "R2_BITE_ON7",
        ]

    def get_sql(self):
        start_time_str = parse(self.start_time).strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = parse(self.end_time).strftime("%Y-%m-%d %H:%M:%S")
        sql = ("SELECT * FROM \"{}_TEMPO_DATA\" ".format(self.mill_line_tag) +
               "WHERE TO_CHAR(PRODUCT_TIME, 'yyyy-mm-dd hh24:mi:ss') >= '{}' ".format(start_time_str) +
               "AND TO_CHAR(PRODUCT_TIME, 'yyyy-mm-dd hh24:mi:ss') <= '{}' ".format(end_time_str) +
               "ORDER BY COIL_ID")
        return sql

    def get_tempo_data_from_db(self):
        conn = cx_Oracle.connect("qms", "system", "172.27.36.1/qmsdb")
        sql = self.get_sql()
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df

    def get_fm_cols(self):
        cols = []
        for std in self.stds:
            cols.append("F{}_BITE_ON".format(std))
            cols.append("F{}_CAST_ON".format(std))
        return cols

    def get_tempo_cols_dict(self, std):
        tempo_cols_dict = {
            "f{}_pure_time".format(std): {
                "start_col": self.cur_put_col.format(std),
                "end_col": self.cur_done_col.format(std),
                "col_name": "F{}纯轧时间".format(std),
            },
            "f{}_gap_time".format(std): {
                "start_col": self.last_done_col.format(std),
                "end_col": self.cur_put_col.format(std),
                "col_name": "F{}间隙时间".format(std),
            },
            "f{}_ent_rhythm".format(std): {
                "start_col": self.last_put_col.format(std),
                "end_col": self.cur_put_col.format(std),
                "col_name": "F{}咬钢节奏".format(std),
            },
            "f{}_ext_rhythm".format(std): {
                "start_col": self.last_done_col.format(std),
                "end_col": self.cur_done_col.format(std),
                "col_name":  "F{}抛钢节奏".format(std),
            }
        }
        return tempo_cols_dict

    def get_total_tempo_cols_dict(self):
        tempo_cols_dict = {}
        tempo_cols_dict["fm_pure_time"] = {
            "start_col": "F1_BITE_ON",
            "end_col": "F7_CAST_ON",
            "col_name": "精轧纯轧时间",
        }
        tempo_cols_dict["fm_gap_time"] = {
            "start_col": "F7_CAST_ON_LAST",
            "end_col": "F1_BITE_ON_CUR",
            "col_name": "精轧间隙时间",
        }
        return tempo_cols_dict

    def wash_fm_data(self, df):

        for std in self.stds:
            df = df.loc[df["F{}_BITE_ON".format(std)].notnull()]
            df = df.loc[df["F{}_CAST_ON".format(std)].notnull()]

        # 整理为时间格式
        for col in self.get_fm_cols():
            df[col] = df[col].apply(lambda x: parse(str(x)))

        for std in self.stds:
            df[self.cur_put_col.format(std)] = df[
                self.put_col.format(std)]
            df[self.cur_done_col.format(std)] = df[
                self.done_col.format(std)]
            df[self.last_put_col.format(std)] = df[
                self.put_col.format(std)].shift(axis=0)
            df[self.last_done_col.format(std)] = df[
                self.done_col.format(std)].shift(axis=0)

        return df

    def wash_rm_data(self, df):

        for r1_bit_col in self.r1_bite_cols:
            df["{}_count".format(r1_bit_col)] = df[r1_bit_col].notnull().apply(
                lambda x: 1 if x == True else 0)

        for r2_bit_col in self.r2_bite_cols:
            df["{}_count".format(r2_bit_col)] = df[r2_bit_col].notnull().apply(
                lambda x: 1 if x == True else 0)

        r1_count_cols = ["{}_count".format(x) for x in self.r1_bite_cols]
        r2_count_cols = ["{}_count".format(x) for x in self.r2_bite_cols]

        df["r1_total_pass"] = df[r1_count_cols].apply(
            lambda x: x.sum(), axis=1)
        df["r2_total_pass"] = df[r2_count_cols].apply(
            lambda x: x.sum(), axis=1)

        df["last_pass_r1_bite_col"] = df["r1_total_pass"].apply(
            lambda x: "R1_BITE_ON{}".format(int(x)))
        df["last_pass_r2_bite_col"] = df["r2_total_pass"].apply(
            lambda x: "R2_BITE_ON{}".format(int(x)))

        df["last_pass_r1_bite"] = np.nan
        df["last_pass_r2_bite"] = np.nan
        for i in range(df.shape[0]):
            r1_total_pass = df.loc[i, "r1_total_pass"]
            r2_total_pass = df.loc[i, "r2_total_pass"]
            last_pass_r1_bite_col = df.loc[i, "last_pass_r1_bite_col"]
            last_pass_r2_bite_col = df.loc[i, "last_pass_r2_bite_col"]

            if int(r1_total_pass) != 0:
                df.loc[i, "last_pass_r1_bite"] = df.loc[i, last_pass_r1_bite_col]

            if int(r2_total_pass) != 0:
                df.loc[i, "last_pass_r2_bite"] = df.loc[i, last_pass_r2_bite_col]

        df["last_pass_r1_bite_last"] = df["last_pass_r1_bite"].shift(axis=0)
        df["last_pass_r2_bite_last"] = df["last_pass_r2_bite"].shift(axis=0)

        return df

    def get_result_data(self, df):
        result = pd.DataFrame()
        result["热卷号"] = df["COIL_ID"]

        # 精轧赋值给结果
        for std in self.stds:

            tempo_cols_dict = self.get_tempo_cols_dict(std)
            for _, tempo_cols_relastionship in tempo_cols_dict.items():
                start_time_col = tempo_cols_relastionship["start_col"]
                end_time_col = tempo_cols_relastionship["end_col"]
                col_name = tempo_cols_relastionship["col_name"]
                result[col_name] = (
                    df[end_time_col] - df[start_time_col]
                ).apply(lambda x: x.total_seconds())

        tempo_cols_dict = self.get_total_tempo_cols_dict()
        for _, tempo_cols_relastionship in tempo_cols_dict.items():
            start_time_col = tempo_cols_relastionship["start_col"]
            end_time_col = tempo_cols_relastionship["end_col"]
            col_name = tempo_cols_relastionship["col_name"]
            result[col_name] = (
                df[end_time_col] - df[start_time_col]
            ).apply(lambda x: x.total_seconds())

        # 粗轧赋值给结果
        result["R1总道次"] = df["r1_total_pass"]
        result["R2总道次"] = df["r2_total_pass"]
        result["粗轧末道次咬钢间隙时间"] = (
            df["last_pass_r1_bite"] - df["last_pass_r2_bite_last"]
        ).apply(lambda x: x.total_seconds())

        return result

    def get_data(self):
        df = self.get_tempo_data_from_db()
        df = self.wash_fm_data(df)
        df = self.wash_rm_data(df)
        res = self.get_result_data(df)
        return res


if __name__ == "__main__":
    tps = TempoStats("HSM1", "2020-08-31 16:00:00", "2020-09-01 00:00:00")
    res = tps.get_data()
    print(res)
    res.to_excel("test.xlsx", index=False)
