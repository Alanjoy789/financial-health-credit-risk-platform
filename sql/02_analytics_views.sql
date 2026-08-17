/* CTEs, windows, rolling averages, risk ranking, aggregation and reconciliation. */
CREATE OR ALTER VIEW analytics.vw_CustomerMonthlyCashflow AS
WITH monthly AS (
 SELECT c.CustomerKey, c.CustomerID, d.CalendarYear, d.MonthNumber, d.YearMonth,
   SUM(CASE WHEN t.Amount > 0 THEN t.Amount ELSE 0 END) AS Inflows,
   -SUM(CASE WHEN t.Amount < 0 THEN t.Amount ELSE 0 END) AS Outflows,
   SUM(t.Amount) AS NetCashflow
 FROM analytics.FactTransaction t JOIN analytics.DimAccount a ON a.AccountKey=t.AccountKey
 JOIN analytics.DimCustomer c ON c.CustomerKey=a.CustomerKey JOIN analytics.DimDate d ON d.DateKey=t.DateKey
 WHERE t.IsReversed=0 GROUP BY c.CustomerKey,c.CustomerID,d.CalendarYear,d.MonthNumber,d.YearMonth
)
SELECT *, AVG(NetCashflow) OVER(PARTITION BY CustomerKey ORDER BY CalendarYear,MonthNumber ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS Rolling3MAvgNetCashflow,
 AVG(Outflows) OVER(PARTITION BY CustomerKey ORDER BY CalendarYear,MonthNumber ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS Rolling6MAvgOutflows
FROM monthly;
GO
CREATE OR ALTER VIEW analytics.vw_CustomerRiskRanking AS
WITH latest AS (
 SELECT *, ROW_NUMBER() OVER(PARTITION BY CustomerKey ORDER BY SnapshotDateKey DESC,LoanSnapshotKey DESC) AS rn
 FROM analytics.FactLoanSnapshot
), scored AS (
 SELECT c.CustomerID,c.Region,c.Segment,l.OutstandingBalance,l.UtilisationRatio,l.DaysPastDue,l.MissedPayments12M,l.RiskScore,rb.RiskBand,
   DENSE_RANK() OVER(ORDER BY l.RiskScore DESC) AS RiskRank,
   NTILE(20) OVER(ORDER BY l.RiskScore DESC) AS RiskVentile
 FROM latest l JOIN analytics.DimCustomer c ON c.CustomerKey=l.CustomerKey JOIN analytics.DimRiskBand rb ON rb.RiskBandKey=l.RiskBandKey WHERE l.rn=1
)
SELECT *, IIF(RiskVentile=1,1,0) AS Top5PctFlag FROM scored;
GO
CREATE OR ALTER VIEW analytics.vw_ExecutiveRiskMI AS
SELECT Region,RiskBand,COUNT_BIG(*) AS Customers,SUM(OutstandingBalance) AS Exposure,
 AVG(RiskScore) AS AverageRiskScore, SUM(CASE WHEN DaysPastDue>=30 THEN OutstandingBalance ELSE 0 END) AS Exposure30PlusDPD,
 CAST(SUM(CASE WHEN DaysPastDue>=30 THEN 1.0 ELSE 0 END)/NULLIF(COUNT_BIG(*),0) AS decimal(9,4)) AS CustomerArrearsRate
FROM analytics.vw_CustomerRiskRanking GROUP BY Region,RiskBand;
GO
CREATE OR ALTER VIEW analytics.vw_BalanceReconciliation AS
WITH movement AS (
 SELECT a.AccountKey,a.AccountID,a.OpeningBalance,SUM(CASE WHEN t.IsReversed=0 THEN t.Amount ELSE 0 END) NetMovement
 FROM analytics.DimAccount a LEFT JOIN analytics.FactTransaction t ON t.AccountKey=a.AccountKey GROUP BY a.AccountKey,a.AccountID,a.OpeningBalance
), latest AS (
 SELECT AccountKey,ClosingBalance,ROW_NUMBER() OVER(PARTITION BY AccountKey ORDER BY SnapshotDateKey DESC,BalanceSnapshotKey DESC) rn FROM analytics.FactBalanceSnapshot
)
SELECT m.AccountID,m.OpeningBalance,m.NetMovement,l.ClosingBalance AS ReportedClosingBalance,
 m.OpeningBalance+m.NetMovement AS CalculatedClosingBalance,
 (m.OpeningBalance+m.NetMovement)-l.ClosingBalance AS Difference,
 CASE WHEN ABS((m.OpeningBalance+m.NetMovement)-l.ClosingBalance)<=0.01 THEN 'PASS' ELSE 'FAIL' END AS ReconciliationStatus
FROM movement m JOIN latest l ON l.AccountKey=m.AccountKey AND l.rn=1;
GO
