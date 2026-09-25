import datetime
import pandas as pd
import streamlit as st

# Initialize session state
if "username" not in st.session_state:
    st.session_state.username = ""
if "date" not in st.session_state:
    st.session_state.date = datetime.date.today()
if "address" not in st.session_state:
    st.session_state.address = ""
if "total_bill" not in st.session_state:
    st.session_state.total_bill = 0.0
if "tenant_breakdown" not in st.session_state:
    st.session_state.tenant_breakdown = []
if "month" not in st.session_state:
    st.session_state.month = "OCTOBER"

# ------ SideBar -------
with st.sidebar:
    if st.button("➕ New Calculation", use_container_width=True, type="primary"):
        st.session_state.total_bill = 0.0
        st.session_state.tenant_breakdown = []
        st.rerun()

    st.divider()

    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "Select a page",
        ["Profile Overview", "Calculator", "Print Result", "Settings"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Water Bill Calculator v1.0")
    st.caption("Developed by Horizon Ideas💡")

# Main content area logic based on navigation
if page == "Profile Overview":
    st.title("👤 Profile Overview")
    st.subheader("Profile Overview")

    st.markdown(f"**Date:** {st.session_state.date}")
    st.markdown(
        f"**Welcome back,** {st.session_state.username if st.session_state.username else 'Guest'}"
    )
    st.markdown(
        f"**Address:** {st.session_state.address if st.session_state.address else 'Not provided'}"
    )

    st.markdown("---")

    st.text_input("Your Name", key="username")
    st.date_input("Date", key="date")
    st.text_input(
        "Postal Address",
        key="address",
        help="It should be in this format e.g. GA-XXX-XXXXX",
    )

    if st.session_state.address:
        if len(st.session_state.address) == 11:
            st.success("Valid Ghana Post GPS Address!")
        else:
            st.warning(
                f"Current length is {len(st.session_state.address)}. It must be 11 characters (e.g., GA-123-4567)."
            )

elif page == "Calculator":
    st.title("💧 Household Water Bill Calculator")
    st.subheader("Enter Bill Details & Tenant Headcounts")

    month_input = st.text_input(
        "Enter the Month", value=st.session_state.month
    ).upper()
    total_amount = st.number_input(
        "Total Bill Amount (GHS ₵)", min_value=0.0, value=150.0, step=10.0
    )

    st.markdown("---")
    st.markdown("### 👥 Tenant Names & Headcounts")
    st.info(
        "Enter tenant names below (one per line), then set how many slots/persons are assigned to each."
    )

    default_tenants = ""
    tenants_input = st.text_area(
        "Tenant Names (One per line)",
        value=default_tenants,
        height=150,
        placeholder="Example:\nBrother Rich\nAuntie Rose\nMr. Akoto",
    )

    # Parse names line by line
    tenant_names = [
        name.strip() for name in tenants_input.split("\n") if name.strip()
    ]

    tenant_counts = {}
    if tenant_names:
        cols = st.columns(2)
        for idx, name in enumerate(tenant_names):
            col_target = cols[idx % 2]
            with col_target:
                tenant_counts[name] = st.number_input(
                    f"{name}", min_value=0, value=1, step=1, key=f"tenant_{name}"
                )

    if st.button("Calculate & Save Results", type="primary"):
        total_persons = sum(tenant_counts.values())
        if total_persons > 0:
            average_rate = total_amount / total_persons

            # Save breakdown into session state
            st.session_state.total_bill = total_amount
            st.session_state.month = month_input

            breakdown_list = []
            for name, count in tenant_counts.items():
                breakdown_list.append(
                    {
                        "name": name,
                        "count": count,
                        "amount": count * average_rate,
                    }
                )
            st.session_state.tenant_breakdown = breakdown_list
            st.success(
                "Calculations successfully saved! Go to 'Print Result' to view and print."
            )
        else:
            st.error("Please enter at least one tenant and headcount.")

elif page == "Print Result":
    st.title("📄 Water Bill Statement & Receipt")

    if (
        not st.session_state.tenant_breakdown
        or st.session_state.total_bill == 0
    ):
        st.warning(
            "⚠️ No calculation data found. Please complete the **Calculator** page first."
        )
    else:
        month = st.session_state.month
        amount = st.session_state.total_bill
        username = st.session_state.username or "Administrator"
        address = st.session_state.address or "Accra, Ghana"
        gen_date = st.session_state.date

        # Display on-screen preview container
        with st.container(border=True):
            st.markdown(
                f"<h3 style='text-align: center;'>WATER BILL FOR THE MONTH OF {month}</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<h4 style='text-align: center;'>BILL AMOUNT = GHS {amount:,.2f}</h4>",
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Prepared By:** {username}")
                st.write(f"**Address:** {address}")
            with col2:
                st.write(f"**Date Generated:** {gen_date}")

            st.divider()

            table_data = []
            for idx, item in enumerate(
                st.session_state.tenant_breakdown, start=1
            ):
                count_display = "-" if item["count"] == 0 else item["count"]
                table_data.append(
                    {
                        "No.": idx,
                        "NAME": item["name"].upper(),
                        "INDIVIDUAL COUNT": count_display,
                        "TOTAL AMOUNT": f"GHS {item['amount']:.2f}",
                    }
                )

            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown(
                "<p style='text-align: center; font-weight: bold;'>============================================ THANK YOU ALL ============================================</p>",
                unsafe_allow_html=True,
            )

        # --- Commercial-Grade Download Solution with No Headers/Footers ---
        rows_html = ""
        for idx, item in enumerate(st.session_state.tenant_breakdown, start=1):
            count_display = "-" if item["count"] == 0 else item["count"]
            rows_html += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{item['name'].upper()}</td>
                    <td>{count_display}</td>
                    <td>GHS {item['amount']:.2f}</td>
                </tr>
            """

        print_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Water Bill Statement - {month}</title>
            <style>
                /* This removes the file path / URL and page number print stamps */
                @page {{
                    size: auto;
                    margin: 15mm;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    color: #000; 
                    background: #fff; 
                }}
                h3, h4 {{ text-align: center; margin: 5px 0; }}
                .header-info {{ display: flex; justify-content: space-between; margin-top: 25px; margin-bottom: 25px; font-size: 14px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ border: 1px solid #333; padding: 12px; text-align: left; font-size: 14px; }}
                th {{ background-color: #f2f2f2; }}
                .footer {{ text-align: center; margin-top: 40px; font-weight: bold; font-size: 13px; }}
            </style>
        </head>
        <body>
            <h3>WATER BILL FOR THE MONTH OF {month}</h3>
            <h4>BILL AMOUNT = GHS {amount:,.2f}</h4>
            <div class="header-info">
                <div>
                    <p><b>Prepared By:</b> {username}</p>
                    <p><b>Address:</b> {address}</p>
                </div>
                <div>
                    <p><b>Date Generated:</b> {gen_date}</p>
                </div>
            </div>
            <hr style="border: 0.5px solid #333;">
            <table>
                <thead>
                    <tr>
                        <th>No.</th>
                        <th>NAME</th>
                        <th>INDIVIDUAL COUNT</th>
                        <th>TOTAL AMOUNT</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <div class="footer">========== THANK YOU ALL ==========</div>
            <script>
                window.onload = function() {{
                    window.print();
                }}
            </script>
        </body>
        </html>
        """

        st.markdown("")
        st.markdown("### 📥 Export Bill for Printing")
        st.download_button(
            label="🖨️ Download Printable Bill (Clean PDF)",
            data=print_html,
            file_name=f"Water_Bill_{month}.html",
            mime="text/html",
            type="primary",
            use_container_width=True,
        )

else:
    st.title("⚙️ Settings")
    st.markdown("App configurations and preferences can be managed here.")
