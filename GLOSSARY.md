# Domain Glossary

Read this before the code. It's about fifteen minutes, and it defines the handful
of lending terms the codebase assumes you already know — `posting`, `allocation`,
`hold`, `accrual`, and the rules that tie them together.

This describes **the domain**, not the implementation. It's the mental model the
code is *supposed* to follow. How faithfully the code follows it is your problem to
find out.

The setting: a small invented lender that issues fixed-term loans and services the
repayments. No real company, no real data.

---

## The ledger

Everything financial in this system is recorded as double-entry bookkeeping. Three
nouns:

**Account** — a bucket that money is tracked against: `cash`,
`principal_receivable`, `interest_receivable`, `fees_receivable`. (Receivable = the
borrower owes us this; it's an asset to the lender.)

**Transaction** — one financial event, made of two or more Postings that balance.

**Posting** — a single signed entry against one Account, belonging to one
Transaction.

**Sign convention:** amounts are signed. **A debit is positive, a credit is
negative.** Within a Transaction, **the Postings must sum to exactly zero** — every
value that goes in comes from somewhere. A Transaction whose Postings don't sum to
zero is not a valid Transaction.

**Balance is derived.** An Account's balance is the sum of its Postings. It is not
a number you store and mutate; it is a number you compute from the ledger. If you
ever want to know what an account holds, you add up its Postings.

> Example — disbursing a $10,000 loan, principal only:
> `cash` −10,000 (credit; money leaves the lender) and
> `principal_receivable` +10,000 (debit; the borrower now owes it).
> Sum: zero. Valid.

---

## Loans and repayment

**Loan** — a fixed-term advance to a borrower, carrying principal, an interest
rate, and any fees. Over its life it accrues interest (below) and is paid down by
repayments.

**Repayment** — money the borrower sends to reduce what they owe. A repayment is
recorded as a Transaction: `cash` is debited for the amount received, and the
receivable accounts are credited for the portions the **Waterfall** assigns to
them.

### The Waterfall

A repayment rarely lines up neatly with one balance, so it is **allocated** across
what's owed in a fixed priority order:

**fees → interest → principal.**

Fees are paid first, then interest, then principal, each absorbing as much of the
payment as it can before the next takes the remainder. The **allocation** is the
breakdown of a single payment into those three portions.

**The allocation must sum to exactly the payment.** Not a cent more, not a cent
less. If $150 comes in, the fee portion plus the interest portion plus the
principal portion equal $150. This is the invariant that makes a repayment
trustworthy.

> Example — a $150 payment on a loan owing $5 fees, $12.50 interest, and $2,000
> principal: $5 to fees, $12.50 to interest, $132.50 to principal. Sum: $150.

---

## Money and rounding

**Amounts are held to whole cents** — two decimal places. There are no sub-cent
balances anywhere in the system.

This matters because allocations and interest don't divide cleanly. When a value
has to be split into parts that must sum back to an exact total, the leftover
cent(s) have to go *somewhere*, and the policy is fixed:

**Residual cents are added to the earliest instalments, never the last.** A borrower
must never receive a final instalment that is *larger* than the earlier ones — a
bigger last payment reads as a surprise penalty. So when a total won't divide
evenly, the first payment carries the extra cent.

> Example — $100.00 split into 3 equal instalments: **$33.34, $33.33, $33.33**
> (not $33.33, $33.33, $33.34). The three sum to exactly $100.00, and the first
> one carries the odd cent.

Because balances are held to whole cents and Postings must sum to zero (above),
any rounding in an allocation has to be resolved **before** the Postings are
written — a set of Postings that only *nearly* sums to zero is not valid.

---

## Interest accrual

**Accrual** — interest builds up daily on the outstanding principal, whether or not
a payment is made.

**Day-count convention: Actual/360.** Interest for a period is charged on the
*actual* number of days elapsed, over a **360-day** year. One day's interest is:

```
outstanding_principal × annual_rate / 360
```

> Example — $10,000 outstanding at 12% annual, over 30 actual days:
> 10,000 × 0.12 / 360 = $3.3333… per day × 30 = **$100.00** for the period.

Actual/360 is a standard lending convention (it charges slightly more than a naïve
365-day year — that's the point of naming it). If you see interest arithmetic, this
is the convention it should be using.

---

## Credit and holds

Some loans draw against a credit limit, and not every commitment has settled yet.
Three terms:

**Settled** — amounts that have fully posted to the ledger.

**Hold** — an amount reserved against the limit but not yet settled — a
pending draw, an authorised-but-not-captured commitment.

**Available credit** — what the borrower can still draw:

```
available_credit = limit − settled − holds
```

Holds count against available credit even though they haven't settled, because the
money is spoken for. This keeps a borrower from spending the same headroom twice
while a draw is in flight.

---

## The four rules, in one place

If you remember nothing else:

1. **Double-entry** — Postings in a Transaction sum to zero; balance is the sum of
   Postings, derived not stored.
2. **Waterfall** — a repayment allocates fees → interest → principal, and the
   allocation sums to exactly the payment.
3. **Available credit** — limit minus settled minus holds.
4. **Accrual** — daily interest, Actual/360.

Your task touches the first two directly. The other two are part of the world your
task lives in — worth understanding, whether or not you touch them.

Now open the code.
