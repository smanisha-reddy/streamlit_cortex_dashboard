import streamlit as st
import pandas as pd
import snowflake.connector

# --- Changed: enhanced page config with icon ---
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon=":material/analytics:",
    layout="wide",
)

# --- Changed: polished page header and subheader ---
st.title(":material/analytics: Sales dashboard")
st.caption("Executive overview  ·  Streamlit + Snowflake + Cortex")

data_totp_code = st.sidebar.text_input("Enter MFA code for data load", type="password")
summary_totp_code = st.sidebar.text_input("Enter fresh MFA code for AI summary", type="password")

# --- Changed: added error handling around Snowflake connection ---
@st.cache_data(show_spinner=False)
def load_data(data_totp_code: str):
    try:
        conn = snowflake.connector.connect(
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["password"],
            account=st.secrets["snowflake"]["account"],
            warehouse=st.secrets["snowflake"]["warehouse"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"],
            role=st.secrets["snowflake"]["role"],
            authenticator="username_password_mfa",
            passcode=data_totp_code,
        )
    except Exception as e:
        st.error(
            f"Could not connect to Snowflake. Check your credentials and MFA code.\n\n`{e}`",
            icon=":material/error:",
        )
        st.stop()

    query = """
        SELECT
            ORDER_ID,
            ORDER_DATE,
            REGION,
            PRODUCT,
            CATEGORY,
            CUSTOMER_TYPE,
            SALES_CHANNEL,
            QUANTITY,
            UNIT_PRICE,
            DISCOUNT,
            SALES_AMOUNT
        FROM STREAMLIT_DEMO_DB.APP_SCHEMA.SALES_DASHBOARD
        ORDER BY ORDER_DATE, ORDER_ID
    """

    try:
        cur = conn.cursor()
        cur.execute(query)
        df = cur.fetch_pandas_all()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(
            f"Failed to load sales data.\n\n`{e}`",
            icon=":material/error:",
        )
        st.stop()

    df["ORDER_DATE"] = pd.to_datetime(df["ORDER_DATE"])
    return df


# --- Changed: added error handling around AI summary generation ---
def generate_cortex_summary(summary_totp_code: str, prompt_text: str) -> str:
    try:
        conn = snowflake.connector.connect(
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["password"],
            account=st.secrets["snowflake"]["account"],
            warehouse=st.secrets["snowflake"]["warehouse"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"],
            role=st.secrets["snowflake"]["role"],
            authenticator="username_password_mfa",
            passcode=summary_totp_code,
        )
    except Exception as e:
        raise ConnectionError(f"Snowflake connection failed: {e}") from e

    sql = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'claude-4-sonnet',
            %s
        ) AS RESPONSE
    """

    try:
        cur = conn.cursor()
        cur.execute(sql, (prompt_text,))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
    except Exception as e:
        raise RuntimeError(f"Cortex AI query failed: {e}") from e

    return result


if data_totp_code:
    data = load_data(data_totp_code)

    st.sidebar.header("Filters")

    region_options = ["All"] + sorted(data["REGION"].dropna().unique().tolist())
    category_options = ["All"] + sorted(data["CATEGORY"].dropna().unique().tolist())
    customer_options = ["All"] + sorted(data["CUSTOMER_TYPE"].dropna().unique().tolist())
    channel_options = ["All"] + sorted(data["SALES_CHANNEL"].dropna().unique().tolist())

    selected_region = st.sidebar.selectbox("Region", region_options)
    selected_category = st.sidebar.selectbox("Category", category_options)
    selected_customer = st.sidebar.selectbox("Customer Type", customer_options)
    selected_channel = st.sidebar.selectbox("Sales Channel", channel_options)

    min_date = data["ORDER_DATE"].min().date()
    max_date = data["ORDER_DATE"].max().date()
    selected_dates = st.sidebar.date_input("Order Date Range", value=(min_date, max_date))

    filtered_data = data.copy()

    if selected_region != "All":
        filtered_data = filtered_data[filtered_data["REGION"] == selected_region]
    if selected_category != "All":
        filtered_data = filtered_data[filtered_data["CATEGORY"] == selected_category]
    if selected_customer != "All":
        filtered_data = filtered_data[filtered_data["CUSTOMER_TYPE"] == selected_customer]
    if selected_channel != "All":
        filtered_data = filtered_data[filtered_data["SALES_CHANNEL"] == selected_channel]

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
        filtered_data = filtered_data[
            (filtered_data["ORDER_DATE"].dt.date >= start_date) &
            (filtered_data["ORDER_DATE"].dt.date <= end_date)
        ]

    total_sales = round(filtered_data["SALES_AMOUNT"].sum(), 2)
    total_orders = int(filtered_data["ORDER_ID"].nunique())
    total_quantity = int(filtered_data["QUANTITY"].sum())
    avg_order_value = round(filtered_data["SALES_AMOUNT"].mean(), 2) if not filtered_data.empty else 0

    # --- Changed: KPI metrics in a bordered horizontal container ---
    st.subheader(":material/query_stats: Key metrics")
    with st.container(horizontal=True):
        st.metric("Total sales", f"${total_sales:,.2f}", border=True)
        st.metric("Total orders", f"{total_orders:,}", border=True)
        st.metric("Total quantity", f"{total_quantity:,}", border=True)
        st.metric("Avg order value", f"${avg_order_value:,.2f}", border=True)

    # --- Changed: empty-state guard for the entire filtered dataset ---
    if filtered_data.empty:
        st.info(
            "No orders match the current filters. Try broadening your selection.",
            icon=":material/filter_list:",
        )
        st.stop()

    # --- Changed: charts wrapped in bordered containers with headings ---
    st.subheader(":material/bar_chart: Regional and category breakdown")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Sales by region**")
            region_sales = (
                filtered_data.groupby("REGION", as_index=False)["SALES_AMOUNT"]
                .sum()
                .sort_values("SALES_AMOUNT", ascending=False)
            )
            if not region_sales.empty:
                st.bar_chart(region_sales.set_index("REGION")["SALES_AMOUNT"])
            else:
                st.caption("No region data available.")

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Sales by category**")
            category_sales = (
                filtered_data.groupby("CATEGORY", as_index=False)["SALES_AMOUNT"]
                .sum()
                .sort_values("SALES_AMOUNT", ascending=False)
            )
            if not category_sales.empty:
                st.bar_chart(category_sales.set_index("CATEGORY")["SALES_AMOUNT"])
            else:
                st.caption("No category data available.")

    # --- Changed: trend chart in bordered container ---
    st.subheader(":material/trending_up: Sales trend")
    with st.container(border=True):
        daily_sales = (
            filtered_data.groupby("ORDER_DATE", as_index=False)["SALES_AMOUNT"]
            .sum()
            .sort_values("ORDER_DATE")
        )
        if not daily_sales.empty:
            st.line_chart(daily_sales.set_index("ORDER_DATE")["SALES_AMOUNT"])
        else:
            st.caption("No trend data available for the selected range.")

    # --- Changed: bottom charts in bordered containers with empty states ---
    st.subheader(":material/inventory_2: Products and channels")
    bottom_col1, bottom_col2 = st.columns(2)

    with bottom_col1:
        with st.container(border=True):
            st.markdown("**Top 10 products**")
            product_sales = (
                filtered_data.groupby("PRODUCT", as_index=False)["SALES_AMOUNT"]
                .sum()
                .sort_values("SALES_AMOUNT", ascending=False)
                .head(10)
            )
            if not product_sales.empty:
                st.bar_chart(product_sales.set_index("PRODUCT")["SALES_AMOUNT"])
            else:
                st.caption("No product data available.")

    with bottom_col2:
        with st.container(border=True):
            st.markdown("**Sales by channel**")
            channel_sales = (
                filtered_data.groupby("SALES_CHANNEL", as_index=False)["SALES_AMOUNT"]
                .sum()
                .sort_values("SALES_AMOUNT", ascending=False)
            )
            if not channel_sales.empty:
                st.bar_chart(channel_sales.set_index("SALES_CHANNEL")["SALES_AMOUNT"])
            else:
                st.caption("No channel data available.")

    # --- Changed: data table in bordered container ---
    st.subheader(":material/table_chart: Filtered sales data")
    with st.container(border=True):
        st.dataframe(filtered_data, use_container_width=True, hide_index=True)

    # --- Changed: AI summary section with error handling and empty-state messages ---
    st.subheader(":material/smart_toy: AI sales summary")
    with st.container(border=True):
        if st.button("Generate AI summary", icon=":material/auto_awesome:"):
            if filtered_data.empty:
                st.warning(
                    "No data available for the selected filters.",
                    icon=":material/warning:",
                )
            elif not summary_totp_code:
                st.warning(
                    "Enter a fresh MFA code for AI summary in the sidebar.",
                    icon=":material/key:",
                )
            else:
                top_region = (
                    filtered_data.groupby("REGION")["SALES_AMOUNT"]
                    .sum()
                    .sort_values(ascending=False)
                    .index[0]
                )
                top_category = (
                    filtered_data.groupby("CATEGORY")["SALES_AMOUNT"]
                    .sum()
                    .sort_values(ascending=False)
                    .index[0]
                )
                top_product = (
                    filtered_data.groupby("PRODUCT")["SALES_AMOUNT"]
                    .sum()
                    .sort_values(ascending=False)
                    .index[0]
                )

                prompt = f"""
                You are a business analyst.
                Summarize the following filtered sales data in 5-7 concise bullet points.

                Total sales: {total_sales}
                Total orders: {total_orders}
                Total quantity: {total_quantity}
                Average order value: {avg_order_value}
                Top region: {top_region}
                Top category: {top_category}
                Top product: {top_product}

                Mention trends, strongest area, and one recommendation.
                """

                with st.spinner("Generating Cortex summary..."):
                    try:
                        summary = generate_cortex_summary(summary_totp_code, prompt)
                        st.write(summary)
                    except (ConnectionError, RuntimeError) as e:
                        st.error(
                            f"Could not generate AI summary.\n\n`{e}`",
                            icon=":material/error:",
                        )

# --- Changed: friendly empty state when no MFA code entered ---
else:
    st.info(
        "Enter the MFA code for data load in the sidebar to get started.",
        icon=":material/key:",
    )