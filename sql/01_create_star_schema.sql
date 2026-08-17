/* Microsoft SQL Server / Fabric Warehouse DDL. All records are synthetic. */
CREATE SCHEMA analytics;
GO
CREATE TABLE analytics.DimDate (
  DateKey int NOT NULL PRIMARY KEY, CalendarDate date NOT NULL, CalendarYear smallint NOT NULL,
  MonthNumber tinyint NOT NULL, MonthName varchar(12) NOT NULL, YearMonth char(7) NOT NULL,
  QuarterNumber tinyint NOT NULL
);
CREATE TABLE analytics.DimCustomer (
  CustomerKey int IDENTITY PRIMARY KEY, CustomerID varchar(20) NOT NULL UNIQUE,
  FullName varchar(100) NOT NULL, Region varchar(30) NOT NULL, Segment varchar(30) NOT NULL,
  AnnualIncome decimal(18,2) NOT NULL, TenureMonths int NOT NULL, VulnerabilityFlag bit NOT NULL,
  DataClassification varchar(20) NOT NULL CHECK (DataClassification='SYNTHETIC')
);
CREATE TABLE analytics.DimAccount (
  AccountKey int IDENTITY PRIMARY KEY, AccountID varchar(20) NOT NULL UNIQUE,
  CustomerKey int NOT NULL REFERENCES analytics.DimCustomer(CustomerKey),
  AccountType varchar(30), OpenDate date, AccountStatus varchar(20), OpeningBalance decimal(18,2)
);
CREATE TABLE analytics.DimRiskBand (
  RiskBandKey tinyint PRIMARY KEY, RiskBand varchar(12) UNIQUE, MinimumScore decimal(5,1), MaximumScore decimal(5,1), SortOrder tinyint
);
CREATE TABLE analytics.FactTransaction (
  TransactionKey bigint IDENTITY PRIMARY KEY, TransactionID varchar(30) NOT NULL UNIQUE,
  AccountKey int NOT NULL REFERENCES analytics.DimAccount(AccountKey), DateKey int NOT NULL REFERENCES analytics.DimDate(DateKey),
  Amount decimal(18,2) NOT NULL, BalanceAfter decimal(18,2), Category varchar(40), Channel varchar(30), IsReversed bit NOT NULL
);
CREATE TABLE analytics.FactLoanSnapshot (
  LoanSnapshotKey bigint IDENTITY PRIMARY KEY, LoanID varchar(20), CustomerKey int REFERENCES analytics.DimCustomer(CustomerKey),
  SnapshotDateKey int REFERENCES analytics.DimDate(DateKey), OutstandingBalance decimal(18,2), CreditLimit decimal(18,2),
  UtilisationRatio decimal(9,4), DaysPastDue int, MissedPayments12M int, RiskScore decimal(5,1), RiskBandKey tinyint REFERENCES analytics.DimRiskBand(RiskBandKey)
);
CREATE TABLE analytics.FactBalanceSnapshot (
  BalanceSnapshotKey bigint IDENTITY PRIMARY KEY, AccountKey int REFERENCES analytics.DimAccount(AccountKey),
  SnapshotDateKey int REFERENCES analytics.DimDate(DateKey), ClosingBalance decimal(18,2)
);
GO
