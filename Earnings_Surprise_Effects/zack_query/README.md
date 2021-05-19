# Task 1
Earnings research: sort stocks from Russell 1000 into 3 groups based on their earnings and EPS Estimate based Zacks.

## Details
- From Zacks, use a query (a MATLAB script is provided for this purpose) to pull 2020 3rd quarter earnings releases (if a company’s 3rd quarter is too far away from the 3rd calendar quarter of 2021, select a quarterly earning close to 3rd calendar quarter of 2021) for all Russell 1000 stocks, sort and divide them into 3 groups (You could exclude the stocks without enough earning information). Save the results in a CSV file(s) for using by your C++ application.
- Calculate earnings surprise for each stock:
Surprise % = (Reported EPS – EPS Estimate) / abs(EPS Estimate)
Note: You could use the Surprise % from Zacks (see
http://zacks.thestreet.com/CompanyView.php for examples).
- Sort all the surprises in ascending order, and split all the stocks into 3 groups
with relatively equivalent numbers of stocks:
  1. Highest surprise group: Beat Estimate Group
  2. Lowest surprise group: Miss Estimate Group
  3. The rest stocks in between: Meet Estimate Group

## Files
**GetEPS.m**: main script to query data and split data.

**scrapeEarningsZacks.m**: lib to query data from Zacks.

**FilterEPS.m**: filter and split data based on all_surprises.csv.

**all_surprises.csv**: ungrouped data.

**Miss.csv**: Miss estimate group data.

**Meet.csv**: Meat estimate group data.

**Beat.csv**: Beat estimate group data.

**Russell_1000_component_stocks.csv**: Russell 1000 stock names.

## Format of Data
| Ticker | Announcement Date | Period Ending | Estimate | Reported | Surprise | Surprise% |
|--------|-------------|---------------|----------|----------|----------|-----------|
| AAPL   | 27-JAN-2021 | Oct 2020      | 1.41     | 1.68     | 0.27     | 19.15     |
| AI     | 29-OCT-2020 | Sep 2020      | 0.69     | 0.73     | 0.04     | 5.80      |