import pandas as pd
import yfinance as yf
import streamlit as st

# Input fields
st.title("Mini Strategy Analysis")
ticker = st.text_input("Ticker")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
volume_threshold = st.number_input("Volume Breakout Threshold (%)", value=200)
price_threshold = st.number_input("Daily Change Threshold (%)", value=2)
holding_period = st.number_input("Holding Period (Days)", value=10)

if st.button("Generate Report"):
    # Fetch data
    data = yf.download(ticker, start=start_date, end=end_date)
    data['AvgVolume20'] = data[('Volume',ticker)].rolling(window=20).mean()
    
    # Identify breakouts
    data['VolumeBreakout'] = data[('Volume',ticker)] > (volume_threshold / 100) * data['AvgVolume20']
    data['PriceChange'] = (data[('Close',ticker)] / data[('Close',ticker)].shift(1)) - 1
    data['PriceBreakout'] = data['PriceChange'] > (price_threshold / 100)
    data['Breakout'] = data['VolumeBreakout'] & data['PriceBreakout']
    
    # Simulate strategy
    results = []
    for i in range(len(data)):
        if data['Breakout'].iloc[i]:
            breakout_date = data.index[i]
            close_price = data[('Close',ticker)].iloc[i]
            end_holding_idx = i + holding_period
            if end_holding_idx < len(data):
                holding_return = (data[('Close',ticker)].iloc[end_holding_idx] / close_price) - 1
                results.append([breakout_date, close_price, holding_return,data[('Volume',ticker)].iloc[i],data['AvgVolume20'].iloc[i]])
    
    # Save report
    report = pd.DataFrame(results, columns=["Date", "Close Price", "Holding Period Return","Volume","AvgVolume20"])
    st.dataframe(report)
    csv_data = report.to_csv( index=False)
    print(csv_data)
    #st.download_button("Download CSV", data=report,file_name= "strategy_report.csv", mime="text/csv")
    st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="strategy_report.csv",
    mime="text/csv"
    )
