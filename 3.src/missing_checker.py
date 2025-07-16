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
