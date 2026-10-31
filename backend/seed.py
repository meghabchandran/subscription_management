from datetime import date, timedelta
from decimal import Decimal

from pwdlib import PasswordHash

from database import SessionLocal

from models import (
    User, Customer, Product, ProductVariant, Plan,
    Quotation, QuotationItem, Subscription, SubscriptionItem,
    Invoice, InvoiceItem, Payment, Discount, DiscountUsage, Tax
)

password_hasher = PasswordHash.recommended()


def seed_database():
    db = SessionLocal()

    try:
        # Avoid inserting duplicate sample data
        if db.query(Customer).first():
            print("Sample data already exists!")
            return

        today = date.today()

        # -------------------------------------------------
        # 1. CUSTOMERS - 5 RECORDS
        # -------------------------------------------------

        customers = [
            Customer(company_name="ABC Technologies", contact_person="Arun Kumar",
                     email="abc@company.com", phone="9876543210",
                     address="MG Road", city="Kochi", state="Kerala",
                     country="India", postal_code="682016",
                     tax_number="GSTABC001", status="Active"),

            Customer(company_name="Nova Solutions", contact_person="Priya Nair",
                     email="nova@company.com", phone="9876543211",
                     address="Infopark", city="Kochi", state="Kerala",
                     country="India", postal_code="682042",
                     tax_number="GSTNOVA002", status="Active"),

            Customer(company_name="TechWorld Pvt Ltd", contact_person="Rahul Das",
                     email="techworld@company.com", phone="9876543212",
                     address="Electronic City", city="Bangalore",
                     state="Karnataka", country="India", postal_code="560100",
                     tax_number="GSTTECH003", status="Active"),

            Customer(company_name="Skyline Enterprises", contact_person="Anjali Menon",
                     email="skyline@company.com", phone="9876543213",
                     address="Anna Salai", city="Chennai", state="Tamil Nadu",
                     country="India", postal_code="600002",
                     tax_number="GSTSKY004", status="Active"),

            Customer(company_name="GreenByte Systems", contact_person="Vishnu Raj",
                     email="greenbyte@company.com", phone="9876543214",
                     address="Technopark", city="Trivandrum", state="Kerala",
                     country="India", postal_code="695581",
                     tax_number="GSTGREEN005", status="Active"),
        ]

        db.add_all(customers)
        db.flush()

        # -------------------------------------------------
        # 2. USERS - 5 RECORDS
        # -------------------------------------------------

        users = [
            User(full_name="Brightloop Admin",
                 email="admin@brightloop.com",
                 password_hash=password_hasher.hash("Admin@123"),
                 phone="9000000001", role="Admin",
                 is_active=True),

            User(full_name="Brightloop Staff",
                 email="staff@brightloop.com",
                 password_hash=password_hasher.hash("Staff@123"),
                 phone="9000000002", role="Staff",
                 is_active=True),

            User(full_name="Arun Kumar",
                 email="abc@company.com",
                 password_hash=password_hasher.hash("Customer@123"),
                 phone="9876543210", role="Customer",
                 customer_id=customers[0].id, is_active=True),

            User(full_name="Priya Nair",
                 email="nova@company.com",
                 password_hash=password_hasher.hash("Customer@123"),
                 phone="9876543211", role="Customer",
                 customer_id=customers[1].id, is_active=True),

            User(full_name="Rahul Das",
                 email="techworld@company.com",
                 password_hash=password_hasher.hash("Customer@123"),
                 phone="9876543212", role="Customer",
                 customer_id=customers[2].id, is_active=True),
        ]

        db.add_all(users)
        db.flush()

        # -------------------------------------------------
        # 3. PRODUCTS - 5 RECORDS
        # -------------------------------------------------

        products = [
            Product(product_name="Accounting Software",
                    product_code="PROD001",
                    description="Business accounting and billing software",
                    category="Finance", base_price=Decimal("1000"),
                    status="Active"),

            Product(product_name="CRM Software",
                    product_code="PROD002",
                    description="Customer relationship management system",
                    category="Business", base_price=Decimal("1500"),
                    status="Active"),

            Product(product_name="HR Management System",
                    product_code="PROD003",
                    description="Employee and payroll management software",
                    category="HR", base_price=Decimal("2000"),
                    status="Active"),

            Product(product_name="Inventory Manager",
                    product_code="PROD004",
                    description="Inventory and stock tracking software",
                    category="Management", base_price=Decimal("1200"),
                    status="Active"),

            Product(product_name="Project Management Tool",
                    product_code="PROD005",
                    description="Project and task management software",
                    category="Productivity", base_price=Decimal("1800"),
                    status="Active"),
        ]

        db.add_all(products)
        db.flush()

        # -------------------------------------------------
        # 4. PRODUCT VARIANTS - 5 RECORDS
        # -------------------------------------------------

        variants = [
            ProductVariant(product_id=products[0].id,
                           variant_name="Basic", variant_code="VAR001",
                           description="Basic accounting features",
                           additional_price=Decimal("0"), status="Active"),

            ProductVariant(product_id=products[1].id,
                           variant_name="Professional", variant_code="VAR002",
                           description="Advanced CRM features",
                           additional_price=Decimal("500"), status="Active"),

            ProductVariant(product_id=products[2].id,
                           variant_name="Enterprise", variant_code="VAR003",
                           description="Complete HR features",
                           additional_price=Decimal("1000"), status="Active"),

            ProductVariant(product_id=products[3].id,
                           variant_name="Standard", variant_code="VAR004",
                           description="Standard inventory features",
                           additional_price=Decimal("300"), status="Active"),

            ProductVariant(product_id=products[4].id,
                           variant_name="Premium", variant_code="VAR005",
                           description="Premium project management features",
                           additional_price=Decimal("700"), status="Active"),
        ]

        db.add_all(variants)
        db.flush()

        # -------------------------------------------------
        # 5. PLANS - 5 RECORDS
        # -------------------------------------------------

        plans = [
            Plan(product_id=products[0].id, plan_name="Basic Monthly",
                 description="Monthly accounting subscription",
                 billing_cycle="Monthly", billing_interval=1,
                 price=Decimal("1000"), minimum_quantity=1,
                 maximum_quantity=100, trial_days=7,
                 auto_renew=True, status="Active"),

            Plan(product_id=products[1].id, plan_name="CRM Monthly",
                 description="Monthly CRM subscription",
                 billing_cycle="Monthly", billing_interval=1,
                 price=Decimal("1500"), minimum_quantity=1,
                 maximum_quantity=100, trial_days=7,
                 auto_renew=True, status="Active"),

            Plan(product_id=products[2].id, plan_name="HR Yearly",
                 description="Annual HR management subscription",
                 billing_cycle="Yearly", billing_interval=1,
                 price=Decimal("20000"), minimum_quantity=1,
                 maximum_quantity=100, trial_days=14,
                 auto_renew=True, status="Active"),

            Plan(product_id=products[3].id, plan_name="Inventory Monthly",
                 description="Monthly inventory subscription",
                 billing_cycle="Monthly", billing_interval=1,
                 price=Decimal("1200"), minimum_quantity=1,
                 maximum_quantity=100, trial_days=7,
                 auto_renew=False, status="Active"),

            Plan(product_id=products[4].id, plan_name="Project Quarterly",
                 description="Quarterly project management subscription",
                 billing_cycle="Quarterly", billing_interval=1,
                 price=Decimal("5000"), minimum_quantity=1,
                 maximum_quantity=100, trial_days=14,
                 auto_renew=True, status="Active"),
        ]

        db.add_all(plans)
        db.flush()

        # -------------------------------------------------
        # 6. QUOTATIONS - 5 RECORDS
        # -------------------------------------------------

        quantities = [2, 3, 2, 4, 2]
        quotation_items = []
        quotations = []

        for i in range(5):
            subtotal = plans[i].price * quantities[i]
            tax = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))

            quotation = Quotation(
                quotation_number=f"QT00{i+1}",
                customer_id=customers[i].id,
                created_by=users[1].id,
                quotation_date=today,
                valid_until=today + timedelta(days=30),
                subtotal=subtotal,
                discount_amount=Decimal("0"),
                tax_amount=tax,
                total_amount=subtotal + tax,
                status="Accepted",
                notes="Sample quotation"
            )

            quotations.append(quotation)

        db.add_all(quotations)
        db.flush()

        # -------------------------------------------------
        # 7. QUOTATION ITEMS - 5 RECORDS
        # -------------------------------------------------

        for i in range(5):
            subtotal = plans[i].price * quantities[i]
            tax = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))

            quotation_items.append(
                QuotationItem(
                    quotation_id=quotations[i].id,
                    product_id=products[i].id,
                    plan_id=plans[i].id,
                    variant_id=variants[i].id,
                    quantity=quantities[i],
                    unit_price=plans[i].price,
                    discount_amount=Decimal("0"),
                    tax_amount=tax,
                    total_amount=subtotal + tax
                )
            )

        db.add_all(quotation_items)
        db.flush()

        # -------------------------------------------------
        # 8. SUBSCRIPTIONS - 5 RECORDS
        # -------------------------------------------------

        subscriptions = []

        for i in range(5):
            start = today - timedelta(days=10)
            end = start + timedelta(days=365 if i == 2 else 30)

            subscriptions.append(
                Subscription(
                    subscription_number=f"SUB00{i+1}",
                    customer_id=customers[i].id,
                    quotation_id=quotations[i].id,
                    start_date=start,
                    end_date=end,
                    billing_start_date=start,
                    next_billing_date=today + timedelta(days=20),
                    billing_cycle=plans[i].billing_cycle,
                    status="Active",
                    auto_renew=plans[i].auto_renew
                )
            )

        db.add_all(subscriptions)
        db.flush()

        # -------------------------------------------------
        # 9. SUBSCRIPTION ITEMS - 5 RECORDS
        # -------------------------------------------------

        subscription_items = []

        for i in range(5):
            subtotal = plans[i].price * quantities[i]
            tax = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))

            subscription_items.append(
                SubscriptionItem(
                    subscription_id=subscriptions[i].id,
                    product_id=products[i].id,
                    plan_id=plans[i].id,
                    variant_id=variants[i].id,
                    quantity=quantities[i],
                    unit_price=plans[i].price,
                    discount_amount=Decimal("0"),
                    tax_amount=tax,
                    total_amount=subtotal + tax
                )
            )

        db.add_all(subscription_items)
        db.flush()

        # -------------------------------------------------
        # 10. INVOICES - 5 RECORDS
        # -------------------------------------------------

        invoices = []

        for i in range(5):
            subtotal = plans[i].price * quantities[i]
            tax = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
            total = subtotal + tax

            invoices.append(
                Invoice(
                    invoice_number=f"INV00{i+1}",
                    customer_id=customers[i].id,
                    subscription_id=subscriptions[i].id,
                    invoice_date=today,
                    due_date=today + timedelta(days=15),
                    billing_period_start=today,
                    billing_period_end=today + timedelta(days=30),
                    subtotal=subtotal,
                    discount_amount=Decimal("0"),
                    tax_amount=tax,
                    total_amount=total,
                    amount_paid=total,
                    balance_due=Decimal("0"),
                    status="Paid",
                    notes="Sample subscription invoice"
                )
            )

        db.add_all(invoices)
        db.flush()

        # -------------------------------------------------
        # 11. INVOICE ITEMS - 5 RECORDS
        # -------------------------------------------------

        invoice_items = []

        for i in range(5):
            subtotal = plans[i].price * quantities[i]
            tax = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))

            invoice_items.append(
                InvoiceItem(
                    invoice_id=invoices[i].id,
                    product_id=products[i].id,
                    description=f"{products[i].product_name} - {plans[i].plan_name}",
                    quantity=quantities[i],
                    unit_price=plans[i].price,
                    discount_amount=Decimal("0"),
                    tax_amount=tax,
                    total_amount=subtotal + tax
                )
            )

        db.add_all(invoice_items)
        db.flush()

        # -------------------------------------------------
        # 12. PAYMENTS - 5 RECORDS
        # -------------------------------------------------

        payment_methods = ["UPI", "Card", "Bank Transfer", "UPI", "Card"]

        payments = []

        for i in range(5):
            payments.append(
                Payment(
                    payment_number=f"PAY00{i+1}",
                    invoice_id=invoices[i].id,
                    customer_id=customers[i].id,
                    payment_date=today,
                    amount=invoices[i].total_amount,
                    payment_method=payment_methods[i],
                    transaction_reference=f"TXN1000{i+1}",
                    payment_status="Completed",
                    notes="Sample payment"
                )
            )

        db.add_all(payments)
        db.flush()

        # -------------------------------------------------
        # 13. DISCOUNTS - 5 RECORDS
        # -------------------------------------------------

        discounts = [
            Discount(discount_name="New Customer Offer",
                     discount_code="NEW10", description="10% off for new customers",
                     discount_type="Percentage", discount_value=Decimal("10"),
                     minimum_purchase=Decimal("1000"), minimum_quantity=1,
                     maximum_discount=Decimal("1000"),
                     start_date=today, end_date=today + timedelta(days=90),
                     usage_limit=100, usage_count=1,
                     applicable_product_id=products[0].id, status="Active"),

            Discount(discount_name="Annual Subscription Offer",
                     discount_code="YEAR500", description="Flat 500 off",
                     discount_type="Fixed", discount_value=Decimal("500"),
                     minimum_purchase=Decimal("5000"), minimum_quantity=1,
                     maximum_discount=Decimal("500"),
                     start_date=today, end_date=today + timedelta(days=90),
                     usage_limit=50, usage_count=1,
                     applicable_product_id=products[2].id, status="Active"),

            Discount(discount_name="CRM Special Offer",
                     discount_code="CRM15", description="15% CRM discount",
                     discount_type="Percentage", discount_value=Decimal("15"),
                     minimum_purchase=Decimal("1500"), minimum_quantity=1,
                     maximum_discount=Decimal("1500"),
                     start_date=today, end_date=today + timedelta(days=60),
                     usage_limit=100, usage_count=1,
                     applicable_product_id=products[1].id, status="Active"),

            Discount(discount_name="Inventory Discount",
                     discount_code="STOCK200", description="Flat 200 off",
                     discount_type="Fixed", discount_value=Decimal("200"),
                     minimum_purchase=Decimal("2000"), minimum_quantity=2,
                     maximum_discount=Decimal("200"),
                     start_date=today, end_date=today + timedelta(days=60),
                     usage_limit=75, usage_count=1,
                     applicable_product_id=products[3].id, status="Active"),

            Discount(discount_name="Project Tool Offer",
                     discount_code="PROJECT20", description="20% off project tool",
                     discount_type="Percentage", discount_value=Decimal("20"),
                     minimum_purchase=Decimal("3000"), minimum_quantity=1,
                     maximum_discount=Decimal("2000"),
                     start_date=today, end_date=today + timedelta(days=90),
                     usage_limit=100, usage_count=1,
                     applicable_product_id=products[4].id, status="Active"),
        ]

        db.add_all(discounts)
        db.flush()

        # -------------------------------------------------
        # 14. DISCOUNT USAGE - 5 RECORDS
        # -------------------------------------------------

        discount_usages = []

        for i in range(5):
            discount_usages.append(
                DiscountUsage(
                    discount_id=discounts[i].id,
                    customer_id=customers[i].id,
                    invoice_id=invoices[i].id,
                    subscription_id=subscriptions[i].id,
                    discount_amount=Decimal("0"),
                    applied_at=today
                )
            )

        db.add_all(discount_usages)
        db.flush()

        # -------------------------------------------------
        # 15. TAXES - 5 RECORDS
        # -------------------------------------------------

        taxes = [
            Tax(tax_name="GST", tax_type="Percentage",
                tax_rate=Decimal("18"), description="Standard GST",
                is_active=True),

            Tax(tax_name="CGST", tax_type="Percentage",
                tax_rate=Decimal("9"), description="Central GST",
                is_active=True),

            Tax(tax_name="SGST", tax_type="Percentage",
                tax_rate=Decimal("9"), description="State GST",
                is_active=True),

            Tax(tax_name="IGST", tax_type="Percentage",
                tax_rate=Decimal("18"), description="Integrated GST",
                is_active=True),

            Tax(tax_name="Reduced Tax", tax_type="Percentage",
                tax_rate=Decimal("5"), description="Reduced tax rate example",
                is_active=True),
        ]

        db.add_all(taxes)

        # Save all records
        db.commit()

        print("SUCCESS: Sample data inserted!")
        print("5 records added to each of the 15 tables.")

        print("\nDemo login credentials:")
        print("Admin: admin@brightloop.com / Admin@123")
        print("Staff: staff@brightloop.com / Staff@123")
        print("Customer: abc@company.com / Customer@123")

    except Exception as e:
        db.rollback()
        print("Error inserting sample data:", e)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()