from pathlib import Path
import csv, random, math, json, shutil, zipfile
from datetime import date, timedelta, datetime

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
SEED = 20260816
rng = random.Random(SEED)

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def generate():
    for target in (RAW, PROCESSED):
        if target.exists(): shutil.rmtree(target)
    RAW.mkdir(parents=True); PROCESSED.mkdir(parents=True)
    regions = ["Dublin", "Leinster", "Munster", "Connacht", "Ulster (ROI)"]
    segments = ["Mass Market", "Emerging Affluent", "Affluent"]
    today = date(2026, 6, 30)
    customers=[]; accounts=[]; loans=[]; tx=[]; snapshots=[]
    for i in range(1,1001):
        cid=f"C{i:06d}"; age=rng.randint(21,78); income=round(max(22000,rng.lognormvariate(10.55,.45)),2)
        region=rng.choices(regions,[.32,.24,.19,.14,.11])[0]; segment=rng.choices(segments,[.70,.22,.08])[0]
        tenure=rng.randint(1,240); vulnerability=rng.random()<.11
        customers.append(dict(customer_id=cid,full_name=f"Synthetic Customer {i:04d}",birth_year=today.year-age,region=region,segment=segment,annual_income=income,tenure_months=tenure,vulnerability_flag=int(vulnerability),data_classification="SYNTHETIC"))
        aid=f"A{i:06d}"; base=round(rng.uniform(250,18000),2)
        accounts.append(dict(account_id=aid,customer_id=cid,account_type=rng.choice(["Current","Current","Savings"]),open_date=(today-timedelta(days=tenure*30)).isoformat(),status="Active",opening_balance=base))
        # Risk drivers intentionally correlated but not deterministically labelled.
        util=min(.99,max(.03,rng.betavariate(2.2,3.2)+(0.15 if vulnerability else 0)))
        missed=max(0,int(rng.expovariate(1.2))-(1 if income>65000 else 0)); days_past=max(0,missed*rng.choice([0,15,30,45,60]))
        principal=round(rng.uniform(3000,45000),2); outstanding=round(principal*rng.uniform(.15,.95),2)
        loans.append(dict(loan_id=f"L{i:06d}",customer_id=cid,product_type=rng.choice(["Personal Loan","Credit Card","Auto Finance"]),original_principal=principal,outstanding_balance=outstanding,interest_rate=round(rng.uniform(.045,.179),4),monthly_payment=round(outstanding/rng.randint(18,72),2),days_past_due=days_past,missed_payments_12m=missed,credit_limit=round(max(2000,outstanding/max(util,.05)),2),utilisation_ratio=round(util,4)))
        bal=base
        for m in range(12):
            month_index=6+m
            month_start=date(2025+month_index//12,month_index%12+1,1)
            inflow=round(income/12*rng.uniform(.85,1.15),2); outflow=round(inflow*rng.uniform(.65,1.18)+(450 if vulnerability else 0),2)
            for kind, amount, cat in [("Credit",inflow,"Salary"),("Debit",-outflow*.35,"Housing"),("Debit",-outflow*.25,"Everyday"),("Debit",-outflow*.20,"Bills"),("Debit",-outflow*.20,"Discretionary")]:
                amount=round(amount,2); tid=f"T{len(tx)+1:09d}"; d=month_start+timedelta(days=rng.randint(0,27)); bal=round(bal+amount,2)
                tx.append(dict(transaction_id=tid,account_id=aid,transaction_date=d.isoformat(),transaction_type=kind,category=cat,amount=amount,balance_after=bal,channel=rng.choice(["Mobile","Card","Direct Debit","Branch"]),is_reversed=0))
            snapshots.append(dict(snapshot_date=(month_start+timedelta(days=27)).isoformat(),account_id=aid,closing_balance=bal))
    # Deliberate DQ exceptions for pipeline demonstration.
    tx.append(tx[77].copy())
    tx[120]["category"]=""
    bad=customers[55].copy(); bad["customer_id"]=""; customers.append(bad)
    write_csv(RAW/"customers.csv",customers,list(customers[0])); write_csv(RAW/"accounts.csv",accounts,list(accounts[0])); write_csv(RAW/"loans.csv",loans,list(loans[0])); write_csv(RAW/"transactions.csv",tx,list(tx[0])); write_csv(RAW/"balance_snapshots.csv",snapshots,list(snapshots[0]))

def clean_and_model():
    def read(name):
        with (RAW/name).open(encoding="utf-8") as f:return list(csv.DictReader(f))
    customers=[r for r in read("customers.csv") if r["customer_id"]]
    accounts=read("accounts.csv"); loans=read("loans.csv"); transactions=read("transactions.csv"); snaps=read("balance_snapshots.csv")
    seen=set(); clean_tx=[]; duplicates=0
    for r in transactions:
        if r["transaction_id"] in seen: duplicates+=1; continue
        seen.add(r["transaction_id"]); r["category"]=r["category"] or "Unclassified"; clean_tx.append(r)
    c_by={r["customer_id"]:r for r in customers}; a_by={r["account_id"]:r for r in accounts}
    tx_by={}
    for r in clean_tx: tx_by.setdefault(r["account_id"],[]).append(r)
    latest={}
    for s in snaps:
        if s["account_id"] not in latest or s["snapshot_date"]>latest[s["account_id"]]["snapshot_date"]: latest[s["account_id"]]=s
    reconciliation=[]
    for aid,a in a_by.items():
        calc=round(float(a["opening_balance"])+sum(float(t["amount"]) for t in tx_by.get(aid,[])),2); reported=float(latest[aid]["closing_balance"]); diff=round(calc-reported,2)
        reconciliation.append(dict(account_id=aid,calculated_closing_balance=calc,reported_closing_balance=reported,difference=diff,status="PASS" if abs(diff)<=.01 else "FAIL"))
    profiles=[]
    for l in loans:
        c=c_by[l["customer_id"]]; aid=f"A{int(c['customer_id'][1:]):06d}"; rows=tx_by[aid]
        credits=sum(float(t["amount"]) for t in rows if float(t["amount"])>0); debits=-sum(float(t["amount"]) for t in rows if float(t["amount"])<0)
        income=float(c["annual_income"]); util=float(l["utilisation_ratio"]); dpd=int(l["days_past_due"]); missed=int(l["missed_payments_12m"]); out=float(l["outstanding_balance"])
        affordability=debits/max(credits,1); score=min(100,round(42*util+25*min(dpd/90,1)+18*min(missed/4,1)+10*min(affordability/1.1,1)+5*int(c["vulnerability_flag"]),1))
        band="Critical" if score>=75 else "High" if score>=60 else "Medium" if score>=40 else "Low"
        action="Specialist support and arrears review" if band=="Critical" else "Proactive affordability contact" if band=="High" else "Digital budgeting nudge" if band=="Medium" else "Maintain and monitor"
        profiles.append(dict(customer_id=c["customer_id"],full_name=c["full_name"],region=c["region"],segment=c["segment"],annual_income=income,vulnerability_flag=int(c["vulnerability_flag"]),loan_id=l["loan_id"],outstanding_balance=out,utilisation_ratio=util,days_past_due=dpd,missed_payments_12m=missed,annual_inflows=round(credits,2),annual_outflows=round(debits,2),affordability_ratio=round(affordability,4),risk_score=score,risk_band=band,recommended_action=action))
    profiles.sort(key=lambda x:(-x["risk_score"],-x["outstanding_balance"])); n=max(1,math.ceil(len(profiles)*.05))
    for rank,p in enumerate(profiles,1): p["risk_rank"]=rank; p["top_5pct_flag"]=int(rank<=n)
    write_csv(PROCESSED/"dim_customer.csv",customers,list(customers[0])); write_csv(PROCESSED/"dim_account.csv",accounts,list(accounts[0])); write_csv(PROCESSED/"fact_loan_snapshot.csv",loans,list(loans[0])); write_csv(PROCESSED/"fact_transaction.csv",clean_tx,list(clean_tx[0])); write_csv(PROCESSED/"fact_balance_snapshot.csv",snaps,list(snaps[0])); write_csv(PROCESSED/"customer_risk_profile.csv",profiles,list(profiles[0])); write_csv(PROCESSED/"balance_reconciliation.csv",reconciliation,list(reconciliation[0]))
    dates=[]
    for offset in range((date(2026,7,1)-date(2025,7,1)).days):
        d=date(2025,7,1)+timedelta(days=offset)
        dates.append(dict(date_key=int(d.strftime("%Y%m%d")),date=d.isoformat(),calendar_year=d.year,month_number=d.month,month_name=d.strftime("%B"),year_month=d.strftime("%Y-%m"),quarter_number=(d.month-1)//3+1))
    write_csv(PROCESSED/"dim_date.csv",dates,list(dates[0]))
    report={"run_timestamp_utc":datetime.utcnow().isoformat()+"Z","seed":SEED,"raw_customer_rows":len(customers)+1,"valid_customers":len(customers),"raw_transaction_rows":len(transactions),"clean_transaction_rows":len(clean_tx),"duplicate_transactions_removed":duplicates,"missing_categories_imputed":1,"reconciliation_failures":sum(r["status"]=="FAIL" for r in reconciliation),"top_5pct_customers":n}
    (PROCESSED/"data_quality_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")

if __name__=="__main__": generate(); clean_and_model(); print(ROOT)
