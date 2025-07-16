from IPython.display import display
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from tqdm import tqdm


def eda_report(df, name=""):
    print(f"EDA Report for {name}")
    print(f"Shape: {df.shape}")
    display(df.head())
    df.info()
    display(df.describe())
    print(df.isnull().sum())

def prepare_submission(predictions, test_df):
    
    predictions_rounded = np.round(predictions).astype(int)
    
    # 행 수 일치 여부 확인
    assert len(predictions_rounded) == len(test_df), f"제출 행의 갯수 불일치! test_df={len(test_df)}, predictions={len(predictions_rounded)}"
    
    print(f"제출용 예측값 생성 완료. 행 개수 일치: {len(predictions_rounded)}")
    
    return predictions_rounded


def get_lat_lon(original_df):

    new_df = original_df.copy()

    if 'full_address' not in new_df.columns:
        new_df['full_address'] = new_df['시군구'].astype(str) + " " + new_df['도로명'].astype(str)

    geolocator = Nominatim(user_agent="my_app")    
    tqdm.pandas()

    def geocode_address(address):
        try:
            location = geolocator.geocode(address)
            if location:
                return pd.Series({'좌표X': location.longitude, '좌표Y': location.latitude})
            else:
                return pd.Series({'좌표X': None, '좌표Y': None})
        except Exception as e:
            print(f"Error geocoding {address}: {e}")
            return pd.Series([None, None])
        
    mask = new_df['좌표X'].isnull() | new_df['좌표Y'].isnull()

    if mask.sum() > 0:
        coords = new_df.loc[mask, 'full_address'].progress_apply(geocode_address)
        coords.index = new_df.loc[mask].index  
        new_df.loc[mask, ['좌표X', '좌표Y']] = coords

    return new_df