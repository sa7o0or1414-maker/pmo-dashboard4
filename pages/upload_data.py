import streamlit as st

# 1) لازم أول سطر Streamlit
st.set_page_config(page_title="رفع البيانات", layout="wide")

from core.ui import hide_streamlit_default_nav
from core.sidebar import render_sidebar
from core.data_io import save_uploaded_excel, load_latest_data

# 2) اخفاء قائمة ستريملت الافتراضية
hide_streamlit_default_nav()
# 3) سايدبارنا العربي
render_sidebar()

st.markdown("## رفع البيانات")
st.write("ارفعي ملف Excel وسيتم تحديث الصفحة الرئيسية تلقائيًا.")

uploaded = st.file_uploader("اختاري ملف Excel", type=["xlsx"])

if uploaded:
    save_uploaded_excel(uploaded)
    st.success("تم رفع الملف وحفظه بنجاح ✅")

    # عرض معاينة سريعة للتأكد
    df = load_latest_data()
    st.write("معاينة من البيانات بعد الرفع:")
    st.dataframe(df.head(30), use_container_width=True)

    # زر يفتح لك الصفحة الرئيسية بعد الحفظ
    st.page_link("pages/dashboard.py", label="الانتقال إلى الصفحة الرئيسية", icon="🏠")
