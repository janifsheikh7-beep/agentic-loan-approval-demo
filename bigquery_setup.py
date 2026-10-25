"""Generate synthetic personal-loan data and load it into BigQuery.

Setup (free BigQuery sandbox is enough):
  pip install faker pandas google-cloud-bigquery pandas-gbq
  gcloud auth application-default login
  python bigquery_setup.py --project YOUR_PROJECT_ID

Creates datasets: bronze, silver, gold. All data is synthetic.
"""
import argparse, random
import numpy as np, pandas as pd
from faker import Faker

fake = Faker("en_IN"); random.seed(7); np.random.seed(7)
N = 600
EMPLOYERS = [("TCS", "A"), ("Infosys", "A"), ("HDFC Bank", "A"), ("Govt of Karnataka", "A"),
             ("Mid-size IT firm", "B"), ("Local manufacturer", "B"), ("Unlisted trading firm", "C")]

def emi(p, r, n):
    r = r / 1200
    return p * r * (1 + r) ** n / ((1 + r) ** n - 1)

def build():
    cust, acc, loans, rep, bureau = [], [], [], [], []
    for i in range(N):
        cid = f"C{i:05d}"
        emp, cat = random.choice(EMPLOYERS)
        inc = int(np.clip(np.random.lognormal(10.9, 0.45), 18000, 250000))
        risk = random.random()  # hidden risk driver: higher = riskier
        cust.append(dict(customer_id=cid, name=fake.name(), pan=fake.bothify("?????####?").upper(),
                         age=random.randint(23, 58), city=fake.city(), employer=emp, employer_cat=cat,
                         net_monthly_income=inc, years_in_job=round(random.uniform(0.3, 15), 1),
                         salary_account=random.random() < 0.6))
        acc.append(dict(account_id=f"A{i:05d}", customer_id=cid,
                        avg_balance=int(inc * random.uniform(0.2, 3) * (1.2 - risk)),
                        bounces_6m=int(np.random.poisson(3 * risk ** 2))))
        existing = 0
        for j in range(np.random.choice([0, 1, 2], p=[.45, .4, .15])):
            p = random.randint(50000, 800000); n = random.choice([24, 36, 48, 60]); r = random.uniform(10.5, 18)
            e = emi(p, r, n); existing += e
            lid = f"L{i:05d}{j}"
            loans.append(dict(loan_id=lid, customer_id=cid, principal=p, rate=round(r, 2), tenure_m=n, emi=round(e)))
            for m in range(1, 13):
                late = max(0, int(np.random.poisson(25 * risk ** 2))) if random.random() < risk else 0
                rep.append(dict(loan_id=lid, month=m, due=round(e), paid=round(e), days_past_due=late))
        score = int(np.clip(rng_score(risk), 300, 900))
        bureau.append(dict(customer_id=cid, cibil_score=score, enquiries_6m=int(np.random.poisson(1 + 5 * risk)),
                           active_unsecured=int(len(loans) and random.randint(0, 3)),
                           written_off=risk > 0.93, existing_emi=round(existing)))
    return [pd.DataFrame(x) for x in (cust, acc, loans, rep, bureau)]

def rng_score(risk):
    return np.random.normal(800 - 260 * risk, 25)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--project", required=True); a = ap.parse_args()
    from google.cloud import bigquery
    import pandas_gbq
    cust, acc, loans, rep, bureau = build()
    bq = bigquery.Client(project=a.project)
    for ds in ("bronze", "silver", "gold"):
        bq.create_dataset(f"{a.project}.{ds}", exists_ok=True)
    for name, df in dict(customers=cust, accounts=acc, loans=loans, repayments=rep, bureau_mock=bureau).items():
        pandas_gbq.to_gbq(df, f"silver.{name}", project_id=a.project, if_exists="replace")
    bq.query(f"""
    CREATE OR REPLACE VIEW `{a.project}.gold.customer_360` AS
    SELECT c.*, a.avg_balance, a.bounces_6m, b.cibil_score, b.enquiries_6m, b.existing_emi,
           SAFE_DIVIDE(b.existing_emi, c.net_monthly_income) AS current_foir
    FROM `{a.project}.silver.customers` c
    JOIN `{a.project}.silver.accounts` a USING (customer_id)
    JOIN `{a.project}.silver.bureau_mock` b USING (customer_id)""").result()
    print(f"Loaded {len(cust)} customers, {len(loans)} loans, {len(rep)} repayment rows. View: gold.customer_360")

if __name__ == "__main__":
    main()
