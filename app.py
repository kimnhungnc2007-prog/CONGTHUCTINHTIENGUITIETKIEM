
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# CẤU HÌNH ỨNG DỤNG
# =========================
st.set_page_config(
    page_title="Công cụ tính lãi tiết kiệm",
    page_icon="💰",
    layout="wide"
)

st.title("💰 CÔNG CỤ TÍNH LÃI GỬI TIẾT KIỆM")
st.caption("Ứng dụng tính lãi đơn và lãi kép - Tài chính Tiền tệ")

# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def format_vnd(value):
    return f"{value:,.0f} VND".replace(",", ".")


# =========================
# NHẬP DỮ LIỆU
# =========================
st.subheader("1. Nhập thông tin tiền gửi")

col1, col2 = st.columns(2)

with col1:
    principal = st.number_input(
        "Số tiền gửi (VND)",
        min_value=0,
        value=100_000_000,
        step=10_000_000,
        format="%d"
    )

    term_months = st.number_input(
        "Kỳ hạn gửi (tháng)",
        min_value=1,
        max_value=600,
        value=12,
        step=1
    )

with col2:
    annual_rate = st.number_input(
        "Lãi suất năm (%)",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.1,
        format="%.2f"
    )

    interest_type = st.selectbox(
        "Phương pháp tính lãi",
        ["Lãi đơn", "Lãi kép"]
    )

payout = st.radio(
    "Hình thức nhận lãi",
    ["Cuối kỳ", "Hàng tháng", "Hàng quý"],
    horizontal=True
)

# =========================
# TÍNH TOÁN
# =========================
if st.button("🧮 TÍNH LÃI TIẾT KIỆM", type="primary",
             use_container_width=True):

    if principal <= 0:
        st.error("Vui lòng nhập số tiền gửi lớn hơn 0.")
        st.stop()

    rate = annual_rate / 100
    total_months = int(term_months)

    # Xác định độ dài kỳ nhận lãi
    if payout == "Hàng tháng":
        interval = 1
    elif payout == "Hàng quý":
        interval = 3
    else:
        interval = total_months

    # Chia kỳ hạn thành các kỳ tính lãi
    periods = []
    elapsed = 0
    balance = float(principal)
    total_interest = 0.0

    while elapsed < total_months:
        months = min(interval, total_months - elapsed)
        period_rate = rate * months / 12

        if interest_type == "Lãi đơn":
            interest = principal * period_rate
        else:
            interest = balance * period_rate

        total_interest += interest
        balance += interest
        elapsed += months

        periods.append({
            "Kỳ": len(periods) + 1,
            "Thời gian (tháng)": months,
            "Thời điểm (tháng)": elapsed,
            "Tiền lãi kỳ này (VND)": interest,
            "Lãi lũy kế (VND)": total_interest,
            "Số dư cuối kỳ (VND)": balance
        })

    # =========================
    # HIỂN THỊ KẾT QUẢ
    # =========================
    st.divider()
    st.subheader("2. Kết quả tính toán")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Tổng tiền lãi",
            format_vnd(total_interest)
        )

    with col2:
        st.metric(
            "Tiền lãi kỳ đầu",
            format_vnd(periods[0]["Tiền lãi kỳ này (VND)"])
        )

    with col3:
        st.metric(
            "Tổng gốc và lãi",
            format_vnd(balance)
        )

    st.info(
        f"""
        **Thông tin khoản tiền gửi**

        - Số tiền gốc: {format_vnd(principal)}
        - Kỳ hạn: {total_months} tháng
        - Lãi suất: {annual_rate:.2f}%/năm
        - Phương pháp: {interest_type}
        - Hình thức nhận lãi: {payout}
        """
    )

    # =========================
    # BẢNG CHI TIẾT
    # =========================
    st.subheader("3. Bảng tính lãi theo từng kỳ")

    df = pd.DataFrame(periods)

    # Định dạng số để dễ đọc
    display_df = df.copy()

    money_cols = [
        "Tiền lãi kỳ này (VND)",
        "Lãi lũy kế (VND)",
        "Số dư cuối kỳ (VND)"
    ]

    for col in money_cols:
        display_df[col] = display_df[col].apply(
            lambda x: f"{x:,.0f}".replace(",", ".")
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # BIỂU ĐỒ TĂNG TRƯỞNG
    # =========================
    st.subheader("4. Biểu đồ tăng trưởng tiền gửi")

    chart_data = pd.DataFrame({
        "Tháng": [0] + df["Thời điểm (tháng)"].tolist(),
        "Vốn gốc": [principal] * (len(df) + 1),
        "Tổng gốc và lãi": [principal] +
            df["Số dư cuối kỳ (VND)"].tolist()
    })

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        chart_data["Tháng"],
        chart_data["Tổng gốc và lãi"],
        marker="o",
        label="Tổng gốc và lãi",
        color="#1677C8"
    )

    ax.plot(
        chart_data["Tháng"],
        chart_data["Vốn gốc"],
        linestyle="--",
        label="Vốn gốc",
        color="#F39C12"
    )

    ax.set_xlabel("Thời gian (tháng)")
    ax.set_ylabel("Số tiền (VND)")
    ax.set_title("Biến động giá trị khoản tiền gửi")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.ticklabel_format(
        style="plain",
        axis="y",
        useOffset=False
    )

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # =========================
    # TẢI KẾT QUẢ
    # =========================
    st.subheader("5. Xuất bảng tính")

    csv = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 Tải bảng kết quả CSV",
        data=csv,
        file_name="ket_qua_tinh_lai_tiet_kiem.csv",
        mime="text/csv",
        use_container_width=True
    )

# =========================
# GHI CHÚ
# =========================
st.divider()
st.caption(
    """
    **Lưu ý về mô hình tính toán:**
    
    - Lãi suất đầu vào là lãi suất danh nghĩa năm.
    - Lãi đơn: tiền lãi tính trên vốn gốc ban đầu.
    - Lãi kép: tiền lãi kỳ sau tính trên số dư đã bao gồm
      lãi các kỳ trước.
    - Hình thức cuối kỳ được mô phỏng như một kỳ tính lãi
      duy nhất trong toàn bộ kỳ hạn.
    - Hình thức hàng tháng và hàng quý được tính theo
      lãi suất năm phân bổ tương ứng theo số tháng.
    - Chưa xét thuế, phí, ngày gửi thực tế, quy tắc làm tròn
      của ngân hàng hoặc việc tái đầu tư lãi đã nhận.
    """
)
