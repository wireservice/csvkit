#!/usr/bin/env python

# 1. 필요한 모듈들을 임포트합니다.
import agate
import sys
from tqdm import tqdm

from csvkit.cli import CSVKitUtility, parse_column_identifiers


# 2. ignore_case_sort 함수 (원본과 동일)
def ignore_case_sort(key):
    """
    Helper function to generate a case-insensitive sort key function.
    """
    def inner(row):
        return tuple(
            agate.NullOrder() if row[n] is None else (row[n].upper() if isinstance(row[n], str) else row[n])
            for n in key
        )
    return inner


# 3. CSVSort 클래스 (원본과 동일)
class CSVSort(CSVKitUtility):
    description = 'Sort CSV files. Like the Unix "sort" command, but for tabular data.'

    # 4. add_arguments 메소드 (원본과 동일)
    def add_arguments(self):
        self.argparser.add_argument(
            '-n', '--names', dest='names_only', action='store_true',
            help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument(
            '-c', '--columns', dest='columns',
            help='A comma-separated list of column indices, names or ranges to sort by, e.g. "1,id,3-5". '
                 'Defaults to all columns.')
        self.argparser.add_argument(
            '-r', '--reverse', dest='reverse', action='store_true',
            help='Sort in descending order.')
        self.argparser.add_argument(
            '-i', '--ignore-case', dest='ignore_case', action='store_true',
            help='Perform case-independent sorting.')
        self.argparser.add_argument(
            '-y', '--snifflimit', dest='snifflimit', type=int, default=1024,
            help='Limit CSV dialect sniffing to the specified number of bytes. '
                 'Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.')
        self.argparser.add_argument(
            '-I', '--no-inference', dest='no_inference', action='store_true',
            help='Disable type inference when parsing the input.')

    # 5. main 메소드 (모든 오류가 수정된 최종본)
    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        # ================================================================= #
        #               진행률 표시기 최종 수정 코드
        # ================================================================= #
        
        # +++ 1. (새로 추가!) 총 줄 수 계산을 위한 변수 초기화 +++
        total_lines = None

        # +++ 2. (새로 추가!) 입력이 실제 파일이고, 되감을 수 있는지 확인 +++
        # (파이프로 받는 stdin은.seek()가 불가능하므로, 이 로직을 타지 않음)
        if self.input_file is not sys.stdin and self.input_file.seekable():
            try:
                # 3. 첫 번째 읽기: 파일의 총 줄 수를 셈
                total_lines = sum(1 for _ in self.input_file)
                # 4. 파일 포인터를 다시 맨 앞으로 되돌림
                self.input_file.seek(0)
            except Exception:
                # (혹시라도 실패하면, 총 줄 수 없이 진행)
                total_lines = None

        # 5. tqdm으로 입력 스트림 감싸기
        progress_bar_input = tqdm(
            self.input_file,
            desc="Loading data",
            file=sys.stderr,
            disable=not sys.stderr.isatty(),
            total=total_lines  # <--- +++ 여기에 계산한 총 줄 수를 전달 +++
        )

        # 6. agate.Table.from_csv() 대신, agate.csv.reader를 사용합니다.
        reader = agate.csv.reader(progress_bar_input, **self.reader_kwargs)

        # 7. 헤더(첫 줄)를 수동으로 추출합니다.
        try:
            header = next(reader)
        except StopIteration:
            # 파일이 비어있으면 (헤더조차 없으면) 여기서 종료합니다.
            return

        # 8. agate.Table 생성자를 직접 호출하여,
        #    tqdm으로 감싸진 'reader'와 'header'를 전달합니다.
        table = agate.Table(
            rows=reader,
            column_names=header,
            column_types=self.get_column_types(),
        )

        # ================================================================= #

        key = parse_column_identifiers(
            self.args.columns,
            table.column_names,
            self.get_column_offset(),
        )

        if self.args.ignore_case:
            key = ignore_case_sort(key)

        table = table.order_by(key, reverse=self.args.reverse)
        table.to_csv(self.output_file, **self.writer_kwargs)


# 6. 실행 함수 (원본과 동일)
def launch_new_instance():
    utility = CSVSort()
    utility.run()


# 7. 메인 실행 블록 (원본과 동일)
if __name__ == '__main__':
    launch_new_instance()