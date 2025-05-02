from datetime import datetime
from pathlib import Path

import pandas as pd


class Scrayping_Setting:
    def __init__(self, file_type: str, is_test: bool = False) -> None:
        can_be_taken = ["multi", "child"]
        if file_type not in can_be_taken:
            raise ValueError(
                "file_typeにmultiまたはchild以外の文字列が入力されています。"
            )
        self.file_type = file_type

        self.now = datetime.now()
        self.nowstr = self.now.strftime("%Y%m%d%H%M%S")

        self.process_csv_path = self._get_process_csv(is_test)
        self.df = pd.read_csv(self.process_csv_path, index_col=None)

        if is_test:
            self._insert_date_to_advertising_name()

    def _get_process_csv(self, is_test: bool = False) -> str:
        """
        広告枠作成の種類に応じたファイルパス文字列を返す

        Args:
            file_type (str): multi | child のどちらかを取りうる (複数原稿配信タイプor子枠)
            is_test (bool): デフォルトはFalseでテストではない。テストの場合はTrueを入力

        Returns:
            PROCESS_CSV_MULTI = str(Path("./csv/fam8_general_multi_create.csv").resolve())

        """

        if is_test:
            path_str = f"./test/fam8_general_{self.file_type}_create.csv"
        else:
            path_str = f"./csv/fam8_general_{self.file_type}_create.csv"

        return str(Path(path_str).resolve())

    def _insert_date_to_advertising_name(self) -> None:

        def add_timestamp(s: str):
            return s.replace("尾関_テスト_", f"尾関_テスト_{self.nowstr}_")

        if self.file_type == "multi":
            self.df["親枠"] = self.df["親枠"].apply(add_timestamp)
            self.df["レクタングル用"] = self.df["レクタングル用"].apply(add_timestamp)
            self.df["インフィード小"] = self.df["インフィード小"].apply(add_timestamp)

        elif self.file_type == "child":
            self.df["登録広告枠名"] = self.df["登録広告枠名"].apply(add_timestamp)
