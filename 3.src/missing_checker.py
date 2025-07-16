# missing_checker.py

def check_missing(df):
    """
    데이터프레임의 열별 결측치 개수, 비율, 고유값 수, 데이터 타입을 출력하는 함수
    """
    for col in df.columns:
        nunique = df[col].nunique(dropna=False)
        missing_ratio = df[col].isna().mean()
        missing_count = df[col].isnull().sum()
        col_type = df.dtypes[col]
        print(f"📌 {col:30} | 데이터타입: {col_type} | 고유값: {nunique:6} | 결측개수: {missing_count} | 결측률: {missing_ratio:.2%}")


def detect_fake_nulls(df, suspect_values=None):
    """
    결측치는 아니지만 의미 없는 형식적 값(예: '-', ' ', '없음')을 찾아 반환
    suspect_values: 의미 없는 값으로 간주할 리스트
    """
    if suspect_values is None:
        suspect_values = ['-', ' ', '', '.', '없음', 'nan', 'NaN', 'None']

    result = {}

    for col in df.columns:
        if df[col].dtype == 'object':
            val_counts = df[col].value_counts(dropna=False)
            found = val_counts[val_counts.index.isin(suspect_values)]
            if not found.empty:
                result[col] = found.to_dict()

    return result
