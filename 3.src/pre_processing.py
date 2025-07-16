import pandas as pd
import numpy as np

def housing_data_load(path:str):

    train = pd.read_csv(path + 'train.csv')
    test = pd.read_csv(path + 'test.csv')
    return train, test



def clean_rename(df):
    import re
    key_list = {}

    for text in list(df.columns):
            if text.startswith('k-전용면적별세대'): # 그냥 괄호를 제거하면 중복된 이름이 발생하기 때문에 처리한 예외 처리 
                cleaned = re.sub(r'^k-', '', text).strip()

            else :
                cleaned = re.sub(r'\(.*?\)','',text)
                cleaned = re.sub(r'^k-','',cleaned)
                cleaned = cleaned.strip()
            key_list[text] = cleaned
    print(key_list)
    return key_list



def detect_fake_nulls(df, suspect_values=['-', ' ', '', '.', '없음', 'nan']):
    result = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            val_counts = df[col].value_counts(dropna=False)
            found = val_counts[val_counts.index.isin(suspect_values)]
            temp = val_counts.index[val_counts.index.isin(suspect_values)]
            if not found.empty:
                result[col] = [found, temp]
    return result

def clean_nulls(df, result):
    for col, vals in result.items():
        print(f"🔎 {col} 컬럼에서 의미 없는 값 발견:")
        print(vals[0])
        print()
        df[col] = df[col].replace(vals[1], np.nan)

# categorical column name, numerical column name return function
def split_categorical_numerical(df:pd.DataFrame, verbose:bool = True):
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    if verbose:
        print("📌 범주형 변수:", categorical_cols)
        print("📌 연속형 변수:", numerical_cols)
    return categorical_cols, numerical_cols



def dataset_label_encoding(train, test, cat_cols):
    # 각 변수에 대한 LabelEncoder를 저장할 딕셔너리
    label_encoders = {}

    # Implement Label Encoding
    for col in tqdm(cat_cols):
        lbl = LabelEncoder()

        # Label-Encoding을 fit
        lbl.fit( train[col].astype(str) )
        train[col] = lbl.transform(train[col].astype(str))
        label_encoders[col] = lbl           # 나중에 후처리를 위해 레이블인코더를 저장해주겠습니다.

        # Test 데이터에만 존재하는 새로 출현한 데이터를 신규 클래스로 추가해줍니다.
        for label in np.unique(test[col]):
            if label not in lbl.classes_: # unseen label 데이터인 경우
                lbl.classes_ = np.append(lbl.classes_, label) # 미처리 시 ValueError발생하니 주의하세요!

        test[col] = lbl.transform(test[col].astype(str))
    return train, test

def pre_processing(path):
    train, test = housing_data_load(path) # load data train test set
    
    train['is_test'] = 0
    test['is_test'] = 1
    
    # train, test merge
    concat = pd.concat([train, test])

    # variable name cleaning 
    key_list = clean_rename(concat)
    concat = concat.rename(columns = key_list)

    # detect fake null and transformation fake null 
    clean_nulls(concat, detect_fake_nulls(concat))

    # drop high missing value rate variable
    concat.drop(axis = 1, columns = list(concat.columns[concat.isnull().sum()/concat.shape[0] >= 0.3]), inplace=True)

    # create Derived Variable
    concat['contract_month'] = concat['계약년월'] % 100 # month
    concat['contract_date'] = concat['계약년월']//100 + concat['contract_month'] / 12 # time

    concat['covid'] = (concat['계약년월'] >= 202001).astype(int) # covid
    concat['apt_age'] = 2025 - concat['건축년도'] # building age

    concat['구'] = list(map(lambda x : x.split(' ')[1],concat['시군구']))
    concat['동'] = list(map(lambda x : x.split(' ')[2],concat['시군구']))

    concat.drop(axis = 1, columns = list(concat.columns[concat.isnull().sum()/concat.shape[0] >= 0.3]), inplace = True)

    drop_list = ['번지', '본번', '부번', '아파트명', '시군구', '계약년월', '계약일', '건축년도', '도로명']
    concat.drop(axis = 1, columns= drop_list,inplace = True)

    cat_cols, num_cols = split_categorical_numerical(concat)

    # 각 변수에 대한 LabelEncoder를 저장할 딕셔너리
    label_encoders = {}

    from tqdm import tqdm
    from sklearn.preprocessing import LabelEncoder

    df_train = concat.query('is_test == 0')
    df_test = concat.query('is_test == 1')

    df_train.drop(['is_test'], axis = 1, inplace=True)
    df_test.drop(['is_test'], axis = 1, inplace=True)

    # Implement Label Encoding
    for col in tqdm(cat_cols):
        lbl = LabelEncoder()

        # Label-Encoding을 fit
        lbl.fit( df_train[col].astype(str) )
        df_train[col] = lbl.transform(df_train[col].astype(str))
        label_encoders[col] = lbl           # 나중에 후처리를 위해 레이블인코더를 저장해주겠습니다.

        # Test 데이터에만 존재하는 새로 출현한 데이터를 신규 클래스로 추가해줍니다.
        for label in np.unique(df_test[col]):
            if label not in lbl.classes_: # unseen label 데이터인 경우
                lbl.classes_ = np.append(lbl.classes_, label) # 미처리 시 ValueError발생하니 주의하세요!

        df_test[col] = lbl.transform(df_test[col].astype(str))


    df_test.drop(axis = 1, columns=['target'], inplace = True)

    return df_train, df_test
