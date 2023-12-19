import streamlit as st
import pandas as pd
import datetime as dt
import math

st.set_page_config(layout="wide")

# sidebar 설정
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 350px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# excel 파일 받기
uploaded_file = st.sidebar.file_uploader("물량표 excel 파일 업로드", type='xlsx')
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

# 날짜 입력받기 (평일/주말 물량 선택)
start_date = st.sidebar.date_input('시작 날짜')
end_date = st.sidebar.date_input('끝 날짜')
if start_date > end_date:
    st.error('시작 날짜와 끝 날짜를 확인하세요')
delta = (end_date - start_date).days
date = start_date
with st.sidebar.expander('평일/주말 선택'):
    for i in range(delta+1):
        st.write(f'{date}')
        globals()[f'isWeekday_{i}'] = st.radio('Type', ['평일','토요일','일요일'], horizontal=True, label_visibility="collapsed", key=f'date_{i}')
        date = date + dt.timedelta(days=1)

dates = []
date = start_date
for i in range(delta+1):
    dates.append(date)
    date = date + dt.timedelta(days=1)
st.sidebar.markdown('\n')
sel_date = st.sidebar.multiselect('물량 합칠 날짜 선택', dates)


# main page
if uploaded_file is not None:
    st.title('물량표')
    st.dataframe(df)
    
    for cls in df['분류'].unique():
        st.divider()
        st.header(cls)
        cls_df = df[df['분류']==cls]
        cls_df.reset_index(inplace=True)
        
        with st.expander(f'{cls}'):
            col1, col2, col3 = st.columns(3)
            for i in range(len(cls_df)):
                menu_df = pd.DataFrame(columns=['날짜', '잔여수량', '당일물량', '필요봉지수'])

                date = start_date
                rest = cls_df['잔여수량'][i]
                bong = cls_df['1봉개수'][i]
                for j in range(delta+1):
                    if globals()[f'isWeekday_{j}'] == '평일':
                        supplies = cls_df['평일물량'][i]
                    elif globals()[f'isWeekday_{j}'] == '토요일':
                        supplies = cls_df['주말(토)물량'][i]
                    else:
                        if pd.isna(cls_df['주말(일)물량'][i]):
                            supplies = cls_df['주말(토)물량'][i]
                        else:
                            supplies = int(cls_df['주말(일)물량'][i])
                    
                    today_bong = math.ceil((supplies - rest) / bong)
                    menu_df.loc[j] = [date, rest, supplies, today_bong]

                    rest = (today_bong * bong + rest) % supplies
                    date = date + dt.timedelta(days=1)

                sel_date_sum = menu_df[menu_df['날짜'].isin(sel_date)]['필요봉지수'].sum()
                if i % 3 == 0:
                    col1.subheader(f"{cls_df['품목'][i]} ({sel_date_sum})")
                    # col1.markdown(f"**{cls_df['품목'][i]}**")
                    # col1.metric('합', sel_date_sum)
                    col1.dataframe(menu_df, hide_index=True)
                elif i % 3 == 1:
                    col2.subheader(f"{cls_df['품목'][i]} ({sel_date_sum})")
                    # col2.markdown(f"**{cls_df['품목'][i]}**")
                    # col2.metric('합', sel_date_sum)
                    col2.dataframe(menu_df, hide_index=True)
                else:
                    col3.subheader(f"{cls_df['품목'][i]} ({sel_date_sum})")
                    # col3.markdown(f"**{cls_df['품목'][i]}**")
                    # col3.metric('합', sel_date_sum)
                    col3.dataframe(menu_df, hide_index=True)
            



