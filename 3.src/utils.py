from IPython.display import display
import numpy as np


def eda_report(df, name=""):
    print(f"EDA Report for {name}")
    print(f"Shape: {df.shape}")
    display(df.head())
    df.info()
    display(df.describe())
    print(df.isnull().sum())


def building_age(df, year_col='건축년도', new_col='building_age'):
    df[new_col] = 2025 - df[year_col]
    return df


def cal_date_diff_weight(df, col='계약년월', new_col='date_diff'):
    df[col] = df[col].astype(str).str[:4].astype(int)
    df[new_col] = 2025 - df[col]
    return df


def prepare_submission(predictions, test_df):
    
    predictions_rounded = np.round(predictions).astype(int)
    
    # ② 행 수 일치 여부 확인
    assert len(predictions_rounded) == len(test_df), f"제출 행의 갯수 불일치! test_df={len(test_df)}, predictions={len(predictions_rounded)}"
    
    print(f"제출용 예측값 생성 완료. 행 개수 일치: {len(predictions_rounded)}")
    
    return predictions_rounded
