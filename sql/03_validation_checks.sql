/* Deployment/data-quality gates: every result should be zero rows or zero failures. */
SELECT TransactionID,COUNT(*) DuplicateCount FROM analytics.FactTransaction GROUP BY TransactionID HAVING COUNT(*)>1;
SELECT COUNT(*) AS OrphanAccounts FROM analytics.DimAccount a LEFT JOIN analytics.DimCustomer c ON c.CustomerKey=a.CustomerKey WHERE c.CustomerKey IS NULL;
SELECT COUNT(*) AS FailedBalanceReconciliations FROM analytics.vw_BalanceReconciliation WHERE ReconciliationStatus='FAIL';
SELECT RiskBand,MIN(RiskScore) MinScore,MAX(RiskScore) MaxScore,COUNT(*) Customers FROM analytics.vw_CustomerRiskRanking GROUP BY RiskBand ORDER BY MinScore DESC;
SELECT TOP (50) * FROM analytics.vw_CustomerRiskRanking WHERE Top5PctFlag=1 ORDER BY RiskRank;
